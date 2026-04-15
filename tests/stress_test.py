import asyncio
import httpx
import time
import pandas as pd
from datetime import datetime

# Configuración
URL = "http://localhost:8000/predict"
CONCURRENT_REQUESTS = 10

# Payload de ejemplo basado en el esquema de la API
SAMPLE_DATA = {
    "claim_id": 999,
    "marca_vehiculo": "Toyota",
    "antiguedad_vehiculo": 5,
    "tipo_poliza": 1,
    "taller": 10,
    "partes_a_reparar": 2,
    "partes_a_reemplazar": 1
}

async def send_request(client, request_id):
    """Envía una única petición y mide su tiempo de respuesta."""
    start_time = time.perf_counter()
    try:
        response = await client.post(URL, json=SAMPLE_DATA, timeout=120.0)
        end_time = time.perf_counter()
        latency = end_time - start_time
        
        return {
            "id": request_id,
            "status_code": response.status_code,
            "latency_seconds": latency,
            "prediction": response.json().get("prediction")
        }
    except Exception as e:
        return {"id": request_id, "error": str(e)}

async def run_stress_test():
    print(f"🚀 Iniciando Stress Test: {CONCURRENT_REQUESTS} consultas en paralelo...")
    
    async with httpx.AsyncClient() as client:
        tasks = [send_request(client, i) for i in range(CONCURRENT_REQUESTS)]
        results = await asyncio.gather(*tasks)
    
    print("Resultados:")

    # Procesar resultados
    df_results = pd.DataFrame(results)
    print(df_results)

    
    # Métricas clave
    avg_latency = df_results["latency_seconds"].mean()
    max_latency = df_results["latency_seconds"].max()
    min_latency = df_results["latency_seconds"].min()
    
    print("\n--- Resumen del Test ---")
    print(df_results.to_string(index=False))
    print(f"\n✅ Latencia Promedio: {avg_latency:.4f} seg")
    print(f"🔥 Latencia Máxima: {max_latency:.4f} seg")
    print(f"🧊 Latencia Mínima: {min_latency:.4f} seg")
    
    # Guardar respaldo como CSV o TXT para la entrega
    filename = f"stress_test_results_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    df_results.to_csv(filename, index=False)
    print(f"\n📂 Respaldo guardado en: {filename}")

if __name__ == "__main__":
    asyncio.run(run_stress_test())