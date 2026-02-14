# 1. Base Image (Safe CUDA 12.4 version)
FROM lmsysorg/sglang:v0.4.7.post1-cu124

# 2. Switch to Root
USER root

# 3. Work Directory
WORKDIR /app

# 4. Install System Tools
RUN apt-get update && \
    apt-get install -y --no-install-recommends git build-essential python3-venv && \
    rm -rf /var/lib/apt/lists/*

# 5. Create Virtual Environment
RUN python3 -m venv /app/venv --system-site-packages

# 6. Install Python Dependencies (FIXED)
# Added 'bitsandbytes' to the list.
RUN /app/venv/bin/pip install --no-cache-dir --upgrade pip && \
    /app/venv/bin/pip install --no-cache-dir \
    "unsloth_zoo>=0.0.1" \
    "unsloth[cu124] @ git+https://github.com/unslothai/unsloth.git" \
    bitsandbytes \
    fastapi uvicorn prometheus_client

# 7. Copy Source Code
COPY . /app

# 8. Expose Port
EXPOSE 8000

# 9. Command
ENV PYTHONPATH="/app:/app/venv/lib/python3.10/site-packages"
CMD ["/app/venv/bin/python", "src/server.py"]
