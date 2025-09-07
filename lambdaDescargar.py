import json
import boto3
import requests
from datetime import datetime
import pytz

s3 = boto3.client("s3")
BUCKET_NAME = "dolaridraw"

def lambda_handler(event, context):
    """
    Lambda que descarga los valores del dólar del Banco de la República
    y los guarda en un archivo dolar-<timestamp>.json dentro de S3.
    """

    url = "https://totoro.banrep.gov.co/estadisticas-economicas/rest/consultaDatosService/consultaMercadoCambiario"

    # Llamado a la API
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    # Timestamp en hora local Bogotá
    tz = pytz.timezone("America/Bogota")
    timestamp = datetime.now(tz).strftime("%Y%m%d-%H%M%S")

    filename = f"dolar-{timestamp}.json"

    # Guardar en S3
    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=filename,
        Body=json.dumps(data),
    )

    return {"status": "ok", "bucket": BUCKET_NAME, "file": filename}