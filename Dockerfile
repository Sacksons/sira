FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ .

# Copy pre-built frontend dist into the container
# FastAPI serves both API (/api/*) and frontend SPA (all other routes)
COPY frontend/dist/ /app/frontend/dist/

# Default env vars (overridden by Railway environment variables)
ENV ALLOWED_ORIGINS=*
ENV DEBUG=False

# Railway uses PORT env var (default 8080)
ENV PORT=8080
EXPOSE ${PORT}

# Start server - admin user is created in FastAPI lifespan
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT
