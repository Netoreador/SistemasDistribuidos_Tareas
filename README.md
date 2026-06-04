# Tarea 2 — Sistemas Distribuidos
## Requisitos previos

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Instrucciones paso a paso

1. **Clonar el repositorio y cambiar a la rama correcta**
```bash
   git clone https://github.com/Netoreador/SistemasDistribuidos_Tareas
   cd SistemasDistribuidos_Tareas
   git checkout tarea-2-distri
```
2. **Construir y levantar los contenedores**
```bash
   docker compose up --build -d
```
   > Kafka tarda 30 segundos en inicializarse. Los datos comenzarán a aparecer en el CSV pasado ese tiempo.
> 
3. **Verificar que todos los servicios estén corriendo**
```bash
   docker compose ps
```
   Deberías ver: `kafka_broker`, `redis_server`, `redis_manager`, `csv_reader_service`, `csv_writer_service` y al menos una instancia de `node-app`.

4. **Revisar los resultados:**
```bash
   docker cp csv_writer_service:/data/results.csv ./results.csv
   docker cp sistemasdistribuidos_tareas-node-app-1:/data/fails.csv ./fails.csv
```
   El archivo `results.csv` contiene las métricas de Hit Rate, Latencia y Throughput. El archivo `fails.csv` contiene las consultas que llegaron a la DLQ.

5. **Ajustar parámetros**

   **Número de consumidores Kafka** — en `docker-compose.yaml` bajo `node-app`:
```yaml
   deploy:
     replicas: 2  # cambiar a 1, 2 o 3
```
   > Al usar replicas, eliminar la línea `container_name` del mismo servicio.

   **Distribución de tráfico** — en `envia/send.py`:
```python
   x = 1  # 1 = uniforme, 2 = Zipf
```

   **Spike de tráfico** — comentar el sleep en `envia/send.py`:
```python
   # time.sleep(1)
```

6. **Detener y limpiar todo:**
```bash
   docker compose down
```
