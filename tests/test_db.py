# tests/test_db.py
import pytest
from unittest.mock import patch, MagicMock
import psycopg2

def fetch_datos(conn, fecha_inicio, fecha_fin):
    """Función de consulta como wrapper de DB para testear."""
    cur = conn.cursor()
    cur.execute(
        "SELECT fechahora, valor FROM dolar WHERE fechahora BETWEEN %s AND %s ORDER BY fechahora;",
        (fecha_inicio, fecha_fin),
    )
    rows = cur.fetchall()
    cur.close()
    return rows


def test_db_query_success():
    """Caso exitoso: la consulta retorna filas válidas"""
    fake_cursor = MagicMock()
    fake_cursor.fetchall.return_value = [
        ("2025-09-01 18:00:00", 3959.0),
        ("2025-09-02 18:00:00", 3960.3),
    ]
    fake_conn = MagicMock()
    fake_conn.cursor.return_value = fake_cursor

    rows = fetch_datos(fake_conn, "2025-09-01", "2025-09-03")
    assert len(rows) == 2
    assert rows[0][1] == 3959.0
    fake_cursor.execute.assert_called_once()


def test_db_query_failure():
    """Caso en que la consulta falla"""
    fake_cursor = MagicMock()
    fake_cursor.execute.side_effect = Exception("DB error")
    fake_conn = MagicMock()
    fake_conn.cursor.return_value = fake_cursor

    with pytest.raises(Exception) as excinfo:
        fetch_datos(fake_conn, "2025-09-01", "2025-09-03")

    assert "DB error" in str(excinfo.value)
