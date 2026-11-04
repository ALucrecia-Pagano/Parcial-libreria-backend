# Imagen base liviana (< 100 MB); las dependencias tienen wheels musllinux y no requieren compilador.
FROM python:3.12-alpine

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Usuario y grupo sin privilegios (no root).
RUN addgroup -S appgroup && adduser -S -G appgroup -H -D appuser

# Se instalan dependencias antes de copiar el código para aprovechar la caché de capas.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copia explícita únicamente de lo necesario para migrar, cargar el seed y servir la API.
COPY alembic.ini ./
COPY app ./app
COPY migrations ./migrations
COPY scripts ./scripts

USER appuser

EXPOSE 8000

# En Alpine no hay curl; se usa wget contra 127.0.0.1 (no localhost, que intenta ::1 IPv6 primero).
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD wget -qO- http://127.0.0.1:8000/health/ready > /dev/null || exit 1

# Al arrancar: aplica migraciones pendientes y levanta uvicorn en 0.0.0.0:8000 como PID 1.
CMD ["sh", "-c", "alembic upgrade head && exec uvicorn app.main:app --host 0.0.0.0 --port 8000"]

