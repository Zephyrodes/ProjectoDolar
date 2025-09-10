import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import pytest
from unittest.mock import patch, MagicMock
from lambdaDescargar import lambda_handler, BUCKET_NAME

# --- Cliente S3 falso ---
class FakeS3ClientOK:
    def put_object(self, Bucket, Key, Body):
        return {"ResponseMetadata": {"HTTPStatusCode": 200}}

class FakeS3ClientFail:
    def put_object(self, Bucket, Key, Body):
        raise Exception("S3 upload failed")

# --- Tests ---

def test_lambda_handler_success():
    """Caso exitoso: API responde bien y S3 guarda correctamente"""
    fake_data = [["1757077268000", "3959"], ["1757077299000", "3960.3333"]]
    fake_response = MagicMock()
    fake_response.json.return_value = fake_data
    fake_response.raise_for_status.return_value = None

    with patch("lambdaDescargar.s3", new=FakeS3ClientOK()), \
         patch("lambdaDescargar.requests.get", return_value=fake_response):

        result = lambda_handler({}, None)

    assert result["status"] == "ok"
    assert result["bucket"] == BUCKET_NAME
    assert result["file"].startswith("dolar-")


def test_lambda_handler_api_error():
    """Caso en que la API devuelve error HTTP"""
    fake_response = MagicMock()
    fake_response.raise_for_status.side_effect = Exception("API error")

    with patch("lambdaDescargar.s3", new=FakeS3ClientOK()), \
         patch("lambdaDescargar.requests.get", return_value=fake_response):

        with pytest.raises(Exception) as excinfo:
            lambda_handler({}, None)

    assert "API error" in str(excinfo.value)


def test_lambda_handler_invalid_json():
    """Caso en que la API responde con JSON inválido"""
    fake_response = MagicMock()
    fake_response.raise_for_status.return_value = None
    fake_response.json.side_effect = ValueError("Invalid JSON")

    with patch("lambdaDescargar.s3", new=FakeS3ClientOK()), \
         patch("lambdaDescargar.requests.get", return_value=fake_response):

        with pytest.raises(ValueError):
            lambda_handler({}, None)


def test_lambda_handler_s3_failure():
    """Caso en que S3 falla al guardar"""
    fake_data = [["1757077268000", "3959"]]
    fake_response = MagicMock()
    fake_response.json.return_value = fake_data
    fake_response.raise_for_status.return_value = None

    with patch("lambdaDescargar.s3", new=FakeS3ClientFail()), \
         patch("lambdaDescargar.requests.get", return_value=fake_response):

        with pytest.raises(Exception) as excinfo:
            lambda_handler({}, None)

    assert "S3 upload failed" in str(excinfo.value)
