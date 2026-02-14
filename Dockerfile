FROM python:3.12-slim

# Install system dependencies needed for SGLang (CUDA/Build tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 1. Create the virtual environment
RUN python -m venv /opt/venv
# 2. Add it to the PATH so all subsequent commands use it
ENV PATH="/opt/venv/bin:$PATH"

# 3. Install SGLang and dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir "sglang[all]>=0.4.0" fastapi uvicorn prometheus_client
