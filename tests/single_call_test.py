import requests
import time
import json

URL = "http://localhost:8000/predict"

poliza_normal = {
    "claim_id": 12345,
    "marca_vehiculo": "toyota",
    "antiguedad_vehiculo": 5,
    "tipo_poliza": 1,
    "taller": 10,
    "partes_a_reparar": 2,
    "partes_a_reemplazar": 1
}

poliza_especial = {
    "claim_id": 67890,
    "marca_vehiculo": "suzuki",
    "antiguedad_vehiculo": 2,
    "tipo_poliza": 4, 
    "taller": 5,
    "partes_a_reparar": 1,
    "partes_a_reemplazar": 0
}

def run_test(name, data):
    print(f"--- Test Case: {name} ---")
    try:
        start_time = time.perf_counter()
        response = requests.post(URL, json=data)
        if response.status_code == 200:
            end_time = time.perf_counter()
            latency = end_time - start_time
            print(f"Éxito (HTTP 200)")
            print(f"Respuesta: {response.json()} \nLatencia: {latency}")
        else:
            print(f"Error (HTTP {response.status_code})")
            print(f"Detalle: {response.text}")
    except Exception as e:
        print(f"Error de conexión: {e}")
    print("\n")

if __name__ == "__main__":
    run_test("Normal", poliza_normal)
    run_test("Póliza 4", poliza_especial)