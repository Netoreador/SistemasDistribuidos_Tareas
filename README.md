Markdown
# Ejecución del Proyecto

## Requisitos previos
- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Instrucciones paso a paso

1. **Clonar el repositorio y entrar a la carpeta:**
   ```bash
   git clone <URL_DEL_REPOSITORIO>
   cd <CARPETA_DEL_PROYECTO>
Construir y levantar los contenedores:

Bash
docker-compose up --build -d
Verificar que los 4 microservicios y Redis estén corriendo:

Bash
docker-compose ps
Revisar los resultados:
El sistema comenzará a generar tráfico automáticamente. Puedes abrir el archivo results.csv que se generará en tu carpeta local para ver en tiempo real las métricas de Tasa (Hit Rate), Latencia y Throughput.

Ajustar parámetros (Opcional):
Si quieres probar otra política de evicción (allkeys-lru o allkeys-lfu) o cambiar el límite de memoria del caché (ej. 20MB o 50MB), debes modificar el archivo docker-compose.yml en el servicio de Redis y volver a ejecutar el paso 2.

Detener y limpiar todo:
Cuando termines de probar, baja los contenedores con:

Bash
docker-compose down
