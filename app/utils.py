from datetime import datetime
import pandas as pd
import os

IMPUTATION_DICT = {
    'log_total_piezas': 1.4545, 'marca_vehiculo_encoded': 0,
    'valor_vehiculo': 3560, 'valor_por_pieza': 150,
    'antiguedad_vehiculo': 1, 'tipo_poliza': 1,
    'taller': 1, 'partes_a_reparar': 3, 'partes_a_reemplazar': 1
}

def log_prediction(data: dict, prediction: float):
    """Guarda el log en un CSV de forma persistente."""
    log_file = "data/api_logs.csv"
    log_entry = {**data, "prediction": prediction, "timestamp": datetime.now()}
    df_log = pd.DataFrame([log_entry])
    
    file_exists = os.path.isfile(log_file)
    df_log.to_csv(log_file, mode='a', index=False, header=not file_exists)

def run_branch_a(df, models):
    """Ejecuta la rama de pipelines de preprocesamiento 1 -> 2 -> 4"""
    df = models["pipeline_1"](df)
    df = models["pipeline_2"](df)
    df = models["pipeline_4"](df)
    return df

def run_branch_b(df, models):
    """Ejecuta la rama de pipelines de preprocesamiento 3 -> 5"""
    df = models["pipeline_3"](df)
    df = models["pipeline_5"](df)
    return df