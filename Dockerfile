FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ .

# Set default env vars
ENV DATABASE_URL=sqlite:///./sira_dev.db
ENV SECRET_KEY=render-default-secret-key-change-via-env-vars
ENV ALLOWED_ORIGINS=*

# Render uses PORT env var (default 10000)
ENV PORT=10000
EXPOSE ${PORT}

# Seed database at startup, then start server
CMD python setup_dev.py && uvicorn app.main:app --host 0.0.0.0 --port $PORT
