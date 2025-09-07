"""
Pruebas unitarias para la función Lambda que procesa archivos JSON de S3.
Se simula un evento de S3 con datos de ejemplo.
"""

import json
import pytest
from lambda_processor import lambda_handler

@pytest.fixture
def s3_event():
    """Evento simulado de S3 para probar la función Lambda."""
    return {
        "Records": [
            {
                "s3": {
                    "bucket": {"name": "mi-bucket-prueba"},
                    "object": {"key": "datos/dolar.json"}
                }
            }
        ]
    }

def test_lambda_handler_response(s3_event, monkeypatch):
    """
    Verifica que la función lambda_handler devuelva un mensaje de éxito.
    """
    # Mock de boto3 para evitar llamadas reales
    def fake_get_object(Bucket, Key):
        return {
            "Body": json.dumps([["1757077268000", "3959"]]).encode()
        }

    class FakeS3Client:
        def get_object(self, Bucket, Key):
            return fake_get_object(Bucket, Key)

    monkeypatch.setattr("boto3.client", lambda _: FakeS3Client())

    result = lambda_handler(s3_event, None)
    assert "Éxito" in result["status"]

