import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import pytest
from lambdaDescargar import lambda_handler

def test_lambda_handler_runs(monkeypatch):
    """Prueba básica de lambdaDescargar"""
    class FakeS3Client:
        def put_object(self, Bucket, Key, Body):
            return {"ResponseMetadata": {"HTTPStatusCode": 200}}
    
    monkeypatch.setattr("boto3", "client", lambda _: FakeS3Client())
    
    result = lambda_handler({}, None)
    assert "status" in result
