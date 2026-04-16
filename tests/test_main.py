import pytest
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch
import asyncio


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

# --- Datos de Prueba ---
VALID_CLAIM = {
    "claim_id": 561205,
    "marca_vehiculo": "ferd",
    "antiguedad_vehiculo": 1,
    "tipo_poliza": 1,
    "taller": 4,
    "partes_a_reparar": 3,
    "partes_a_reemplazar": 2
}

# --- Tests ---

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_prediction_success(client):
    """Prueba una predicción exitosa con datos válidos."""
    response = client.post("/predict", json=VALID_CLAIM)
    assert response.status_code == 200
    data = response.json()
    assert "prediction" in data
    assert isinstance(data["prediction"], float)
    assert data["claim_id"] == VALID_CLAIM["claim_id"]

def test_early_exit_poliza_4(client):
    """Verifica la regla de negocio: Póliza Tipo 4 siempre devuelve -1.0."""
    payload = VALID_CLAIM.copy()
    payload["tipo_poliza"] = 4
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    assert response.json()["prediction"] == -1.0

def test_validation_error_missing_field(client):
    """Verifica que falte un campo obligatorio (claim_id)."""
    payload = VALID_CLAIM.copy()
    del payload["claim_id"]
    response = client.post("/predict", json=payload)
    assert response.status_code == 422

def test_validation_error_wrong_type(client):
    """Verifica el error cuando se envía un tipo de dato incorrecto."""
    payload = VALID_CLAIM.copy()
    payload["antiguedad_vehiculo"] = "muy viejo"
    response = client.post("/predict", json=payload)
    assert response.status_code == 422

def test_null_handling_pydantic(client):
    """Prueba que el validador de Pydantic maneje los 'null' convirtiéndolos a default."""
    payload = VALID_CLAIM.copy()
    payload["marca_vehiculo"] = None
    response = client.post("/predict", json=payload)
    
    assert response.status_code == 200
    assert "prediction" in response.json()

def test_internal_profiling_logs(client):
    """
    Verifica que la respuesta no contenga información sensible
    del profiling si ocurre un error.
    """
    payload = {"claim_id": "error"}
    response = client.post("/predict", json=payload)
    assert response.status_code == 422
    
    assert "pipeline" not in response.text.lower()
    assert "marca_vehiculo_encoded" not in response.text.lower()

def test_prediction_timeout(client):
    """
    Simula un timeout reduciendo el tiempo de espera permitido.
    Se utiliza un patch para modificar el timeout de la función wait_for en tiempo de ejecución.
    """
    with patch("asyncio.wait_for", side_effect=asyncio.TimeoutError):
        payload = {
            "claim_id": 999,
            "marca_vehiculo": "toyota",
            "antiguedad_vehiculo": 1,
            "tipo_poliza": 1,
            "taller": 1,
            "partes_a_reparar": 1,
            "partes_a_reemplazar": 1
        }
        response = client.post("/predict", json=payload)
        
        assert response.status_code == 504
        assert "excedió el tiempo límite" in response.json()["detail"]