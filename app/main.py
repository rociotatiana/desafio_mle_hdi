import os
import pandas as pd
import numpy as np
import dill
import builtins
from fastapi import FastAPI, BackgroundTasks, HTTPException, status
from contextlib import asynccontextmanager

from app.schemas import ClaimInput, PredictionOutput
from app.utils import IMPUTATION_DICT, log_prediction

builtins.np = np

models = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    pipeline_names = ["pipeline_1", "pipeline_2", "pipeline_3", "pipeline_4", "pipeline_5"]
    for name in pipeline_names:
        with open(f"models/{name}.pkl", "rb") as f:
            models[name] = dill.load(f)
    
    with open("models/linnear_regression.pkl", "rb") as f:
        models["regressor"] = dill.load(f)
    
    yield
    models.clear()

app = FastAPI(title="HDI Seguros - Predictor de tiempo de reparación", lifespan=lifespan)

# --- Endpoints ---
@app.post("/predict", response_model=PredictionOutput)
async def predict(claim: ClaimInput, background_tasks: BackgroundTasks):
    try:
        if claim.tipo_poliza == 4:
            background_tasks.add_task(log_prediction, claim.model_dump(), -1.0)
            return {"claim_id": claim.claim_id, "prediction": -1.0}

        df = pd.DataFrame([claim.model_dump()])

        try:
            # --- Imputación Inicial ---
            for col, val in IMPUTATION_DICT.items():
                if col not in df.columns:
                    df[col] = val
                df[col] = df[col].fillna(val)

            # --- Ejecución de Pipelines ---
            df = models["pipeline_1"](df)
            df = models["pipeline_2"](df)
            df = models["pipeline_4"](df)
            df = models["pipeline_3"](df)
            df = models["pipeline_5"](df)

            # --- Imputación Final ---
            for col, val in IMPUTATION_DICT.items():
                if col in df.columns:
                    df[col] = df[col].fillna(val)

            # --- Selección de Features y Predicción ---
            features = ['log_total_piezas', 'marca_vehiculo_encoded', 'valor_vehiculo', 'valor_por_pieza', 'antiguedad_vehiculo']
            X = df[features].astype({
                'log_total_piezas': 'float64', 
                'marca_vehiculo_encoded': 'int64', 
                'valor_vehiculo': 'int64', 
                'valor_por_pieza': 'int64', 
                'antiguedad_vehiculo': 'int64'
            })

            prediction = float(models["regressor"].predict(X)[0])

        except KeyError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Error de esquema: Falta la columna {str(e)} tras el procesamiento."
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Fallo en el pipeline de inferencia: {str(e)}"
            )
        
        background_tasks.add_task(log_prediction, claim.model_dump(), prediction)
        return {"claim_id": claim.claim_id, "prediction": prediction}
    
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error inesperado en el servidor."
        )