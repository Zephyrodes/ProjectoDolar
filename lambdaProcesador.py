import json
import boto3
import psycopg2
import os
from datetime import datetime, timezone

s3 = boto3.client("s3")

# Variables de entorno
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_PORT = os.getenv("DB_PORT", "5432")

def lambda_handler(event, context):
    """
    Procesa archivo de dolar_raw_xxxx en S3 y lo inserta en RDS.
    El JSON es una lista de listas: [[timestamp_ms, valor], ...]
    """

    # Extraer info del evento S3
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    # Leer archivo desde S3
    file_obj = s3.get_object(Bucket=bucket, Key=key)
    raw_data = json.loads(file_obj['Body'].read())

    # Conectarse a RDS
    conn = psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT
    )
    cur = conn.cursor()

    # Procesar registros
    for registro in raw_data:
        timestamp_ms, valor = registro

        # Convertir timestamp de milisegundos a datetime UTC
        fecha = datetime.fromtimestamp(int(timestamp_ms) / 1000, tz=timezone.utc)

        cur.execute(
            "INSERT INTO dolar (fechahora, valor) VALUES (%s, %s) ON CONFLICT DO NOTHING;",
            (fecha, float(valor))
        )

    conn.commit()
    cur.close()
    conn.close()

    return {"status": "inserted", "file": key, "rows": len(raw_data)}
