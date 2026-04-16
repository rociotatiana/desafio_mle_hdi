import asyncio
import httpx
import time
import pandas as pd
from datetime import datetime

URL = "http://localhost:8000/predict"
DATASET_PATH = "claims_dataset.csv"

async def send_request(client, row_data):
    """Envía una fila del dataset como payload a la API."""
    claim_id = row_data.get("claim_id", "unknown")
    start_time = time.perf_counter()
    
    try:
        response = await client.post(URL, json=row_data, timeout=120.0)
        end_time = time.perf_counter()
        latency = end_time - start_time
        
        return {
            "claim_id": claim_id,
            "status_code": response.status_code,
            "latency_seconds": latency,
            "prediction": response.json().get("prediction") if response.status_code == 200 else None,
            "error": None if response.status_code == 200 else response.text
        }
    except Exception as e:
        return {
            "claim_id": claim_id,
            "status_code": None,
            "latency_seconds": None,
            "prediction": None,
            "error": str(e)
        }

async def run_stress_test():
    try:
        df_input = pd.read_csv(DATASET_PATH, sep='|')
        df_input = df_input.fillna("nan")
        print(f"Dataset cargado exitosamente. Total de registros: {len(df_input)}")
    except Exception as e:
        print(f"Error al leer el archivo CSV: {e}")
        return

    payloads = df_input.to_dict(orient='records')

    print(f"Iniciando Stress Test con {len(payloads)} consultas concurrentes...")
    
    start_test_time = time.perf_counter()
    
    async with httpx.AsyncClient() as client:
        tasks = [send_request(client, payload) for payload in payloads]
        results = await asyncio.gather(*tasks)
    
    end_test_time = time.perf_counter()
    
    df_results = pd.DataFrame(results)
    
    success_df = df_results[df_results["status_code"] == 200]
    
    print("\n" + "="*30)
    print("      RESUMEN DEL TEST")
    print("="*30)
    print(f"Total peticiones:    {len(df_results)}")
    print(f"Peticiones exitosas: {len(success_df)}")
    print(f"Tiempo total test:   {end_test_time - start_test_time:.2f} seg")
    
    if not success_df.empty:
        print(f"Latencia promedio:   {success_df['latency_seconds'].mean():.4f} seg")
        print(f"Latencia máxima:     {success_df['latency_seconds'].max():.4f} seg")
        print(f"Latencia mínima:     {success_df['latency_seconds'].min():.4f} seg")
    
    filename = f"stress_test_evidence_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    df_results.to_csv(filename, index=False)
    print(f"\nEvidencia guardada en: {filename}")

if __name__ == "__main__":
    asyncio.run(run_stress_test())