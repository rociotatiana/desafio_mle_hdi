import os
import pandas as pd
import asyncio
import dill
import time
from fastapi import FastAPI, BackgroundTasks, HTTPException, status
from contextlib import asynccontextmanager

from app.schemas import ClaimInput, ModelFeatures, PredictionOutput
from app.utils import IMPUTATION_DICT, log_prediction, run_branch_a, run_branch_b


models = {}

@asynccontextmanager
async def lifespan(app: FastAPI):    
    pipeline_names = ["pipeline_1", "pipeline_2", "pipeline_3", "pipeline_4", "pipeline_5"]
    for name in pipeline_names:
        with open(f"pipelines/{name}.pkl", "rb") as f:
            models[name] = dill.load(f)
    
    with open("models/linnear_regression.pkl", "rb") as f:
        models["regressor"] = dill.load(f)
    
    yield
    models.clear()

app = FastAPI(title="HDI Seguros - Predictor de tiempo de reparación", lifespan=lifespan)

# --- Endpoints ---
@app.post("/predict", response_model=PredictionOutput)
async def predict(claim: ClaimInput, background_tasks: BackgroundTasks):
    start_time = time.perf_counter()
    claim_dict = claim.model_dump()

    try:
        if claim.tipo_poliza == 4:
            latency = time.perf_counter() - start_time
            background_tasks.add_task(log_prediction, claim_dict, -1.0, latency, 200, None, None)
            return {"claim_id": claim.claim_id, "prediction": -1.0}

        df = pd.DataFrame([claim.model_dump()])

        # --- Imputación de Datos ---
        for col, val in IMPUTATION_DICT.items():
            if col not in df.columns:
                df[col] = val

        try:
            # --- Ejecución de Pipelines ---
            task_a = asyncio.to_thread(run_branch_a, df.copy(), models)
            task_b = asyncio.to_thread(run_branch_b, df.copy(), models)

            (df_a, times_a), (df_b, times_b) = await asyncio.wait_for(asyncio.gather(task_a, task_b), timeout=12.0 )
            profiling_data = {**times_a, **times_b}
            df_final = df_a.combine_first(df_b)

            # --- Selección de Features y Predicción ---
            raw_features = df_final.to_dict(orient='records')[0]
            validated_features = ModelFeatures(**raw_features)
            X = pd.DataFrame([validated_features.model_dump()])

            prediction = float(models["regressor"].predict(X)[0])
            
        except asyncio.TimeoutError:
            latency = time.perf_counter() - start_time
            background_tasks.add_task(log_prediction, claim_dict, None, latency, 504, "Timeout interno excedido")
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="El procesamiento del siniestro excedió el tiempo límite permitido."
            )
        except KeyError as e:
            latency = time.perf_counter() - start_time
            background_tasks.add_task(log_prediction, claim_dict, None, latency, 422, profiling_data, e)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Error de esquema: Falta la columna {str(e)}."
            )
        except Exception as e:
            latency = time.perf_counter() - start_time
            background_tasks.add_task(log_prediction, claim_dict, None, latency, 500, profiling_data, e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Fallo en el pipeline de inferencia: {str(e)}"
            )
        
        latency = time.perf_counter() - start_time
        background_tasks.add_task(log_prediction, claim_dict, prediction, latency, 200, profiling_data)

        return {"claim_id": claim.claim_id, "prediction": prediction}
    
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        latency = time.perf_counter() - start_time
        background_tasks.add_task(log_prediction, claim_dict, None, latency, 500, None, e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error inesperado en el servidor."
        )
    
@app.get("/health", tags=["Monitoring"])
async def health_check():
    """Verifica la salud de la API y la presencia de modelos cargados."""
    if not models or len(models) < 6:
        raise HTTPException(
            status_code=503, 
            detail="Models not loaded yet"
        )
    return {
        "status": "healthy",
        "models_loaded": list(models.keys()),
        "environment": os.getenv("ENV", "development")
    }