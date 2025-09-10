import pytest
from unittest.mock import patch, MagicMock
from lambdaProcesador import lambda_handler

def test_db_insert_query_structure():
    """Verifica que el SQL generado es correcto y se insertan los parámetros esperados"""
    # Fake cursor para capturar queries
    fake_cursor = MagicMock()
    fake_conn = MagicMock()
    fake_conn.cursor.return_value = fake_cursor

    # Fake S3 para devolver datos válidos
    fake_s3 = MagicMock()
    fake_s3.get_object.return_value = {
        "Body": MagicMock(read=MagicMock(
            return_value=b'[["1757077268000","3959"],["1757077299000","3960.3333"]]'
        ))
    }

    with patch("lambdaProcesador.s3", new=fake_s3), \
         patch("lambdaProcesador.psycopg2.connect", return_value=fake_conn):
        result = lambda_handler({
            "Records": [{"s3": {"bucket": {"name": "b"}, "object": {"key": "f"}}}]
        }, None)

    # Verificaciones
    assert result["status"] == "inserted"
    assert result["rows"] == 2
    fake_cursor.execute.assert_any_call(
        "INSERT INTO dolar (fechahora, valor) VALUES (%s, %s)",
        ("1757077268000", "3959")
    )
    fake_cursor.execute.assert_any_call(
        "INSERT INTO dolar (fechahora, valor) VALUES (%s, %s)",
        ("1757077299000", "3960.3333")
    )
    fake_conn.commit.assert_called_once()
    fake_cursor.close.assert_called_once()
    fake_conn.close.assert_called_once()
