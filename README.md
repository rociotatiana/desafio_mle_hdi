# Desafio MLE HDI

Este repositorio contiene la solucion del desafio MLE de HDI.

## Cómo ejecutar el proyecto

Para comenzar, es necesario tener instalado Docker y Docker Compose.

Luego de instalarlos, ejecuta el siguiente codigo en tu terminal desde la carpeta del repositorio

```bash
docker-compose up --build
```

De esta forma, la API estará disponible en `http://localhost:8000`

## Endpoints

### `/predict`

El modelo predictivo se encuentra disponible en `http://localhost:8000/predict`

## API Logs

Los logs de las predicciones se guardarán automáticamente en la carpeta local `data/api_logs.csv`
