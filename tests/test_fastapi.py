"""
Pruebas unitarias para la API de FastAPI que consulta datos del dólar.
Se usan fixtures de pytest para simular la conexión a la base de datos.
"""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@pytest.fixture
def sample_request():
    """Fixture que devuelve un rango de fechas válido para consulta."""
    return {"fecha_inicio": "2025-09-01", "fecha_fin": "2025-09-06"}

def test_consultar_endpoint_status(sample_request):
    """
    Verifica que el endpoint /consultar responda con status 200.
    """
    response = client.post("/consultar", json=sample_request)
    assert response.status_code == 200

def test_consultar_endpoint_format(sample_request):
    """
    Verifica que el endpoint /consultar devuelva un JSON con la clave 'resultados'.
    """
    response = client.post("/consultar", json=sample_request)
    data = response.json()
    assert "resultados" in data
    assert isinstance(data["resultados"], list)

