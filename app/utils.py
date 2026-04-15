from datetime import datetime
import pandas as pd
import time
import json
import os

IMPUTATION_DICT = {
    'log_total_piezas': 1.4545, 'marca_vehiculo_encoded': 0,
    'valor_vehiculo': 3560, 'valor_por_pieza': 150,
    'antiguedad_vehiculo': 1, 'tipo_poliza': 1,
    'taller': 1, 'partes_a_reparar': 3, 'partes_a_reemplazar': 1
}

def log_prediction(data: dict, prediction: float, latency: float, status_code: int, profiling_data: dict, error_msg: str = None):
    """Guarda el log en un CSV de forma persistente."""
    log_dir = "data"
    log_file = os.path.join(log_dir, "api_logs.csv")

    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_entry = {**data, "prediction": prediction, "timestamp": datetime.now(), "latency_s": latency, "status_code": status_code, "profiling_data": json.dumps(profiling_data), "error_msg": error_msg}
    
    df_log = pd.DataFrame([log_entry])
    
    file_exists = os.path.isfile(log_file)
    df_log.to_csv(log_file, mode='a', index=False, header=not file_exists)

def run_branch_a(df, models):
    """Ejecuta la rama de pipelines de preprocesamiento 1 -> 2 -> 4"""
    times = {}
    s = time.perf_counter()
    df = models["pipeline_1"](df)
    times["p1"] = round(time.perf_counter() - s, 4)
    
    s = time.perf_counter()
    df = models["pipeline_2"](df)
    times["p2"] = round(time.perf_counter() - s, 4)
    
    s = time.perf_counter()
    df = models["pipeline_4"](df)
    times["p4"] = round(time.perf_counter() - s, 4)
    
    return df, times

def run_branch_b(df, models):
    """Ejecuta la rama de pipelines de preprocesamiento 3 -> 5"""
    times = {}
    s = time.perf_counter()
    df = models["pipeline_3"](df)
    times["p3"] = round(time.perf_counter() - s, 4)
    
    s = time.perf_counter()
    df = models["pipeline_5"](df)
    times["p5"] = round(time.perf_counter() - s, 4)

    return df, times