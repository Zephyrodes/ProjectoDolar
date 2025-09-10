import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import json
import pytest
from unittest.mock import patch, MagicMock
from lambdaProcesador import lambda_handler

# --- Fixtures ---
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

# --- Fakes ---
class FakeS3ClientOK:
    def get_object(self, Bucket, Key):
        fake_data = [["1757077268000", "3959"], ["1757077299000", "3960.3333"]]
        return {"Body": MagicMock(read=MagicMock(return_value=json.dumps(fake_data).encode()))}

class FakeS3ClientFail:
    def get_object(self, Bucket, Key):
        raise Exception("S3 get_object failed")

class FakeCursorOK:
    def __init__(self):
        self.executed_queries = []
    def execute(self, query, params):
        self.executed_queries.append((query, params))
    def close(self):
        return None

class FakeCursorFail:
    def execute(self, query, params):
        raise Exception("DB insert failed")
    def close(self):
        return None

class FakeConnectionOK:
    def __init__(self):
        self.cursor_obj = FakeCursorOK()
    def cursor(self):
        return self.cursor_obj
    def commit(self):
        return None
    def close(self):
        return None

class FakeConnectionFail:
    def cursor(self):
        return FakeCursorFail()
    def commit(self):
        return None
    def close(self):
        return None

# --- Tests ---

def test_lambda_handler_success(s3_event):
    """Caso exitoso: S3 devuelve datos válidos y DB inserta correctamente"""
    with patch("lambdaProcesador.s3", new=FakeS3ClientOK()), \
         patch("lambdaProcesador.psycopg2.connect", return_value=FakeConnectionOK()):
        result = lambda_handler(s3_event, None)

    assert result["status"] == "inserted"
    assert result["file"] == "datos/dolar.json"
    assert result["rows"] == 2


def test_lambda_handler_s3_failure(s3_event):
    """Caso en que falla la descarga desde S3"""
    with patch("lambdaProcesador.s3", new=FakeS3ClientFail()), \
         patch("lambdaProcesador.psycopg2.connect", return_value=FakeConnectionOK()):
        with pytest.raises(Exception) as excinfo:
            lambda_handler(s3_event, None)

    assert "S3 get_object failed" in str(excinfo.value)


def test_lambda_handler_db_failure(s3_event):
    """Caso en que falla la inserción en la base de datos"""
    with patch("lambdaProcesador.s3", new=FakeS3ClientOK()), \
         patch("lambdaProcesador.psycopg2.connect", return_value=FakeConnectionFail()):
        with pytest.raises(Exception) as excinfo:
            lambda_handler(s3_event, None)

    assert "DB insert failed" in str(excinfo.value)


def test_lambda_handler_invalid_json(s3_event):
    """Caso en que el archivo JSON está corrupto"""
    fake_s3 = MagicMock()
    fake_s3.get_object.return_value = {
        "Body": MagicMock(read=MagicMock(return_value=b"INVALID JSON"))
    }

    with patch("lambdaProcesador.s3", new=fake_s3), \
         patch("lambdaProcesador.psycopg2.connect", return_value=FakeConnectionOK()):
        with pytest.raises(json.JSONDecodeError):
            lambda_handler(s3_event, None)
