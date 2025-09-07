import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import json
import pytest
from unittest.mock import patch, MagicMock
from lambdaProcesador import lambda_handler, s3

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

class FakeS3Client:
    def get_object(self, Bucket, Key):
        # Simula el archivo JSON que tu Lambda espera
        fake_data = [["1757077268000", "3959"], ["1757077299000", "3960.3333"]]
        # boto3 devuelve un objeto con Body que tiene método read()
        return {"Body": MagicMock(read=MagicMock(return_value=json.dumps(fake_data).encode()))}

class FakeCursor:
    def execute(self, query, params):
        return None
    def close(self):
        return None

class FakeConnection:
    def cursor(self):
        return FakeCursor()
    def commit(self):
        return None
    def close(self):
        return None

def test_lambda_handler_response(s3_event):
    """Prueba lambdaProcesador sin S3 ni RDS reales"""
    # Patch al s3 real dentro del módulo
    with patch.object(sys.modules['lambdaProcesador'], 's3', new=FakeS3Client()):
        # Patch a psycopg2.connect para que devuelva FakeConnection
        with patch("lambdaProcesador.psycopg2.connect", return_value=FakeConnection()):
            result = lambda_handler(s3_event, None)

    # Verificaciones básicas
    assert "status" in result
    assert result["status"] == "inserted"
    assert result["file"] == "datos/dolar.json"
    assert result["rows"] == 2
