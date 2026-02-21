# ─── Stage 1: Base Python image ───────────────────────────────────────────────
# Python 3.12 slim = chhota size, production-ready
FROM python:3.12-slim

# ─── Environment variables ─────────────────────────────────────────────────────
# PYTHONDONTWRITEBYTECODE = .pyc files mat banao (bytecode cache)
# PYTHONUNBUFFERED       = logs seedha terminal pe aaye (buffered nahi)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ─── Working directory ─────────────────────────────────────────────────────────
# Container ke andar /app folder mein sab kaam hoga
WORKDIR /app

# ─── System dependencies ───────────────────────────────────────────────────────
# psycopg2-binary ke liye libpq-dev chahiye Linux pe
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libpq-dev \
        gcc \
        netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# ─── Python dependencies ───────────────────────────────────────────────────────
# Pehle sirf requirements copy karo (caching ke liye — code badla toh
# packages dobara install nahi honge)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ─── Application code ──────────────────────────────────────────────────────────
# Baaki saara code copy karo
COPY . .

# ─── Entrypoint script ─────────────────────────────────────────────────────────
# Script ko executable banao
RUN chmod +x entrypoint.sh

# ─── Port expose ───────────────────────────────────────────────────────────────
# Container port 8000 open karega (Django default)
EXPOSE 8000

# ─── Run command ───────────────────────────────────────────────────────────────
ENTRYPOINT ["./entrypoint.sh"]
