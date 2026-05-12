# Single Railway service: Angular static build + FastAPI (`/api/...`).
FROM node:22-alpine AS frontend
WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY backend/requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

COPY backend/ /app/
COPY contracts/ /contracts/

COPY --from=frontend /frontend/dist/selling-tours-frontend/browser /app/static

ENV SEED_PATH=/contracts/tours_seed.json \
    STATIC_DIR=/app/static

EXPOSE 8000
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
