# Proyecto: Consulta y Procesamiento del Valor del Dólar

## Descripción general
Este proyecto implementa una arquitectura en la nube para la **obtención, almacenamiento, procesamiento y consulta de los valores del dólar** publicados por el Banco de la República de Colombia.  

El sistema fue diseñado bajo un enfoque **serverless** y de **microservicios**, utilizando AWS Lambda, S3, RDS y un servidor FastAPI desplegado en EC2.  
Además, se integró un flujo de **CI/CD con GitHub Actions** que asegura despliegues continuos y pruebas automáticas.

---

## Arquitectura y componentes

### 1. Lambda de ingesta de datos
- Implementada con **Zappa** y programada para ejecutarse diariamente a las **18:00 hora local**.  
- Consulta los valores del dólar en el servicio oficial del Banco de la República:  
```bash
https://totoro.banrep.gov.co/estadisticas-economicas/rest/consultaDatosService/consultaMercadoCambiario
```
- Los datos se almacenan en bruto en un bucket de S3
- Cada archivo se guarda como: dolar-<timestamp>.json


---

### 2. Lambda de procesamiento
- Configurada con **event trigger** en el bucket S3.  
- Cada vez que un archivo nuevo llega, la función:
1. Lee el contenido del JSON.  
2. Procesa la información recibida.  
3. Inserta los registros en una base de datos **PostgreSQL en Amazon RDS**.  
- La tabla se llama `dolar` y contiene dos columnas:  
- `fechahora` (timestamp).  
- `valor` (float).  

---

### 3. API de consulta (FastAPI en EC2)
- Se implementó un servicio **FastAPI** desplegado en una instancia **EC2**.  
- Expone un **endpoint `/consultar`** que permite realizar consultas con un rango de fechas.  
- El cliente envía un **POST** con el intervalo solicitado y recibe un JSON con los valores almacenados en RDS.  

**Ejemplo de consulta:**

_Request:_
```json
{
"fecha_inicio": "2025-09-01",
"fecha_fin": "2025-09-03"
}
```

## Pruebas unitarias

Se desarrollaron pruebas con **Pytest** para garantizar la correcta operación del sistema:

### Lambda de ingesta y procesamiento
- Validación de descarga de datos y escritura en S3.  
- Validación de inserción en la base de datos simulada con *mocks*.  

### API FastAPI
- Consulta exitosa con datos válidos.  
- Manejo de errores en caso de fallo en la conexión con la base de datos.  

Estas pruebas utilizan `unittest.mock` y `TestClient` de FastAPI, asegurando independencia respecto a servicios externos.

---

## CI/CD con GitHub Actions

Se configuró un pipeline de **integración y despliegue continuo** con GitHub Actions, que realiza:

- Ejecución de pruebas unitarias en cada `push` o `pull_request` sobre la rama `main`.  
- Despliegue automático de Lambdas con **Zappa** (`zappa update`).  
- Copia del código de FastAPI a la instancia **EC2** mediante `scp`.  
- Instalación de dependencias y reinicio del servicio en la instancia para mantener la API disponible.  

Este flujo asegura calidad en el código y despliegue confiable en producción.

---

## Conclusión

El proyecto contiene estos aspectos fundamentales:

1. Ingesta automática con **Lambda + Zappa + S3**.  
2. Procesamiento y almacenamiento en **RDS** con Lambda y triggers de S3.  
3. Exposición de un servicio de consulta mediante **FastAPI** en EC2.  

Adicionalmente, se reforzó con:

- Pruebas unitarias completas.  
- Pipeline CI/CD automatizado.  

Esto garantiza un sistema **robusto, escalable y mantenible**, alineado con buenas prácticas de Big Data e Ingeniería de Datos.
