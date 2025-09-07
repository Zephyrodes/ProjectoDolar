import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import json
import pytest
from unittest.mock import patch, MagicMock
from lambdaProcesador import lambda_handler, s3, BUCKET_NAME  # BUCKET_NAME si lo defines

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
        fake_data = [["1757077268000", "3959"]]
        return {"Body": json.dumps(fake_data).encode()}

def test_lambda_handler_response(s3_event):
    """Verifica que lambdaProcesador devuelva un mensaje de éxito"""
    # Patch al s3 real dentro del módulo
    with patch.object(sys.modules['lambdaProcesador'], 's3', new=FakeS3Client()):
        result = lambda_handler(s3_event, None)

    assert "status" in result
    assert result["status"] == "ok"
