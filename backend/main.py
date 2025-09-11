from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
import os

app = FastAPI()

# Permitir CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Variables de entorno
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_PORT = os.getenv("DB_PORT", "5432")


class Consulta(BaseModel):
    fecha_inicio: str
    fecha_fin: str


@app.post("/consultar")
def consultar(data: Consulta):
    """
    Endpoint que devuelve los valores del dólar en un rango de fechas.
    Maneja errores de conexión y consulta en la base de datos.
    """
    conn = None
    try:
        conn = psycopg2.connect(
            host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASS, port=DB_PORT
        )
        cur = conn.cursor()

        cur.execute(
            "SELECT fechahora, valor FROM dolar WHERE fechahora BETWEEN %s AND %s ORDER BY fechahora;",
            (data.fecha_inicio, data.fecha_fin)
        )
        rows = cur.fetchall()

        return {"resultados": [{"fechahora": str(r[0]), "valor": float(r[1])} for r in rows]}

    except Exception as e:
        # Devolver un error controlado en vez de propagar la excepción
        raise HTTPException(status_code=500, detail=f"Error en la base de datos: {str(e)}")

    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass

@app.get("/saludo")
def saludo():
    return {"mensaje": "Hola Big Data"}