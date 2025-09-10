# tests/test_api.py
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_consultar_success():
    """Consulta exitosa al endpoint"""
    fake_cursor = MagicMock()
    fake_cursor.fetchall.return_value = [
        ("2025-09-01 18:00:00", 3959.0),
        ("2025-09-02 18:00:00", 3960.3),
    ]
    fake_conn = MagicMock()
    fake_conn.cursor.return_value = fake_cursor

    with patch("main.psycopg2.connect", return_value=fake_conn):
        response = client.post(
            "/consultar",
            json={"fecha_inicio": "2025-09-01", "fecha_fin": "2025-09-03"},
        )

    assert response.status_code == 200
    data = response.json()
    assert len(data["resultados"]) == 2
    assert data["resultados"][0]["valor"] == 3959.0


def test_consultar_db_failure():
    """El endpoint debe propagar el error si la DB falla"""
    fake_conn = MagicMock()
    fake_cursor = MagicMock()
    fake_cursor.execute.side_effect = Exception("DB failure")
    fake_conn.cursor.return_value = fake_cursor

    with patch("main.psycopg2.connect", return_value=fake_conn):
        response = client.post(
            "/consultar",
            json={"fecha_inicio": "2025-09-01", "fecha_fin": "2025-09-03"},
        )

    # Como no hay try/except en tu endpoint, FastAPI devuelve 500
    assert response.status_code == 500
