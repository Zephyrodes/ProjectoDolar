import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import pytest
from unittest.mock import patch
from lambdaDescargar import lambda_handler

class FakeS3Client:
    def put_object(self, Bucket, Key, Body):
        return {"ResponseMetadata": {"HTTPStatusCode": 200}}

def test_lambda_handler_runs():
    """Prueba lambdaDescargar sin credenciales reales"""
    with patch("lambdaDescargar.boto3.client", return_value=FakeS3Client()):
        result = lambda_handler({}, None)
        assert "status" in result
