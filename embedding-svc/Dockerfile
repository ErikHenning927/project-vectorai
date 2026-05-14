FROM python:3.12-slim

WORKDIR /app

# Dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

EXPOSE 8001

# Executar migrations e iniciar a API
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.api.server:app --host 0.0.0.0 --port 8001"]
