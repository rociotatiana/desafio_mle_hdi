from datetime import datetime
import pandas as pd
import numpy as np
import builtins
import time
import json
import os

builtins.np = np

IMPUTATION_DICT = {
    'log_total_piezas': 1.4545, 'marca_vehiculo_encoded': 0,
    'valor_vehiculo': 3560, 'valor_por_pieza': 150,
    'antiguedad_vehiculo': 1, 'tipo_poliza': 1,
    'taller': 1, 'partes_a_reparar': 3, 'partes_a_reemplazar': 1
}

def log_prediction(claim_dict, prediction, latency, status_code, profiling_data=None, error_msg=None):
    """Guarda el log en un CSV de forma persistente."""
    log_file = "data/api_logs.csv"
    
    prof_json = json.dumps(profiling_data) if profiling_data else "null"
    prof_json_escaped = prof_json.replace('"', '""')
    err_str = str(error_msg).replace(",", ";") if error_msg else ""

    log_entry = (
        f"{claim_dict['claim_id']},{claim_dict['marca_vehiculo']},"
        f"{claim_dict['antiguedad_vehiculo']},{claim_dict['tipo_poliza']},"
        f"{claim_dict['taller']},{claim_dict['partes_a_reparar']},"
        f"{claim_dict['partes_a_reemplazar']},{prediction},"
        f"{pd.Timestamp.now()},{latency},{status_code},"
        f'"{prof_json_escaped}","{err_str}"\n'
    )

    with open(log_file, "a") as f:
        f.write(log_entry)

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