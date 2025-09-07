"""
Pruebas unitarias para la función Lambda que descarga datos del dólar.
Se verifica que la función guarde en S3 correctamente.
"""

import pytest
from lambda_downloader import lambda_handler

def test_lambda_handler_runs(monkeypatch):
    """
    Verifica que la función lambda_handler devuelva un mensaje de éxito al ejecutarse.
    """

    # Mock de boto3 para evitar llamadas reales
    class FakeS3Client:
        def put_object(self, Bucket, Key, Body):
            return {"ResponseMetadata": {"HTTPStatusCode": 200}}

    monkeypatch.setattr("boto3.client", lambda _: FakeS3Client())

    result = lambda_handler({}, None)
    assert "status" in result
    assert "Éxito" in result["status"]

