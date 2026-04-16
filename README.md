# Desafio MLE HDI

Este repositorio contiene la solucion del desafio MLE de HDI para la predicción de tiempos de reparación

## Cómo ejecutar el proyecto

Para comenzar, es necesario tener instalado Docker y Docker Compose.

Luego de instalarlos, copia el repositorio ejecuta el siguiente comando en tu terminal desde la carpeta raiz:

```bash
git clone https://github.com/rociotatiana/desafio_mle_hdi.git
docker-compose up --build
```

De esta forma, la API estará disponible en `http://localhost:8000`. Se puede acceder a la documentación interactiva creada por Swagger UI en `/docs`.

## API Endpoints

### `/predict`

El modelo predictivo se encuentra disponible en `http://localhost:8000/predict`

Es un método POST que recibe el siguiente formato JSON:

```json
{
  "claim_id": 0,
  "marca_vehiculo": "nan",
  "antiguedad_vehiculo": 1,
  "tipo_poliza": 1,
  "taller": 1,
  "partes_a_reparar": 3,
  "partes_a_reemplazar": 1
}
```

Entrega el siguiente formato JSON:

```json
{
  "claim_id": 0,
  "prediction": 0
}
```

### `/healthcheck`

Corresponde a un endpoint GET de monitoreo de infraestructura, que verifica que el servidor está activo y valida la disponibilidad de los modelos en memoria.

## Testing

Se desarrolló un módulo de test unitarios con pytest con el fin de monitorear una consistencia en los resultados del servicio ante futuras modificaciones del código. Este proceso de testing se automatizó a través de GitHub Actions, que ejecuta este módulo de test ante cada nuevo push request al repositorio.

Para ejecutar los tests unitarios dentro del entorno controlado de Docker debes correr el siguiente comando:

```bash
docker exec -it hdi_mle_challenge python3 -m pytest tests/test_main.py -v
```

### Stress Test

La carpeta `/postman` contiene la colección utilizada para realizar los Stress Tests de resiliencia y carga critica detallados en el documento.

Asimismo, pueden probar el servicio sin importar la colección teniendo el ambiente levantado y utilizando un curl como el siguiente:

```cURL
curl --location 'http://localhost:8000/predict' \
--header 'Content-Type: application/json' \
--data '{
    "claim_id": 561205,
    "marca_vehiculo": "ferd",
    "antiguedad_vehiculo": 1,
    "tipo_poliza": 1,
    "taller": 4,
    "partes_a_reparar": 3,
    "partes_a_reemplazar": 2
}'
```

Ademas, se utilizó un script para evaluar la solución en su etapa temprana y obtener los datos de latencia en llamadas concurrentes. Para ejecutarlo dentro del entorno de Docker debes correr el siguiente comando:

```bash
docker exec -it hdi_mle_challenge python3 -m tests.stress_test
```

## API Logs

El sistema genera un archivo `data/api_logs.csv` que registra cada petición con el siguiente detalle:

- `claim_id` y todos los datos de entrada enviados por el cliente.
- `prediction`: Resultado final.
- `latency_s`: Tiempo total de la petición.
- `profiling_data`: Diccionario JSON con los milisegundos que tardó cada pipeline interno.
- `status_code`: Codigo HTTP devuelto.
- `error_msg`: Adjunta el error asociado en caso de fallos.
