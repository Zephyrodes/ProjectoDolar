import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import json
import pytest
from lambdaProcesador import lambda_handler  # ← nombre correcto

@pytest.fixture
def s3_event():
    """Evento simulado de S3 para lambdaProcesador"""
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
    """Verifica que lambdaProcesador devuelva un mensaje de éxito"""
    def fake_get_object(Bucket, Key):
        return {"Body": json.dumps([["1757077268000", "3959"]]).encode()}

    class FakeS3Client:
        def get_object(self, Bucket, Key):
            return fake_get_object(Bucket, Key)

    monkeypatch.setattr("boto3", "client", lambda _: FakeS3Client())

    result = lambda_handler(s3_event, None)
    assert "status" in result
