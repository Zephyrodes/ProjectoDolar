import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import json
import pytest
from unittest.mock import patch, MagicMock
from lambdaDescargar import lambda_handler, s3, BUCKET_NAME

class FakeS3Client:
    def put_object(self, Bucket, Key, Body):
        # Simula la respuesta de S3
        return {"ResponseMetadata": {"HTTPStatusCode": 200}}

def test_lambda_handler_runs():
    """Prueba lambdaDescargar sin credenciales ni requests reales"""
    
    # Patch al s3 real dentro del módulo
    with patch.object(sys.modules['lambdaDescargar'], 's3', new=FakeS3Client()):
        # Patch a requests.get para devolver datos simulados
        fake_data = [["1757077268000", "3959"], ["1757077299000", "3960.3333"]]
        fake_response = MagicMock()
        fake_response.json.return_value = fake_data
        fake_response.raise_for_status.return_value = None

        with patch("lambdaDescargar.requests.get", return_value=fake_response):
            result = lambda_handler({}, None)
    
    # Verificaciones básicas
    assert "status" in result
    assert result["status"] == "ok"
    assert result["bucket"] == BUCKET_NAME
    assert result["file"].startswith("dolar-")
