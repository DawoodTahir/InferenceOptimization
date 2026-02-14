# 1. Base Image
FROM lmsysorg/sglang:v0.4.7.post1-cu124

# 2. Work Directory
WORKDIR /app

# 3. Copy source code
COPY . /app

# 4. Install System Dependencies (Fix for 'gcc' error)
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev && \
    rm -rf /var/lib/apt/lists/*

# 5. Install Python Dependencies
RUN pip install --no-cache-dir fastapi uvicorn prometheus_client

# 6. Expose Port
EXPOSE 8000

# 7. Command
CMD ["python3", "src/server.py"]
