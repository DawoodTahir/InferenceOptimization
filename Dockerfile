# -----------------------------------------------------------------------------
# FIX: Use CUDA 12.1 Base Image
# We switch from 'cu124' to 'cu121'. This version is compatible with 
# almost all RunPod host drivers (even older ones).
# -----------------------------------------------------------------------------
FROM lmsysorg/sglang:v0.4.5.post3-cu121

# 2. Switch to Root
USER root

# 3. Work Directory
WORKDIR /app

# 4. Install System Tools
RUN apt-get update && \
    apt-get install -y --no-install-recommends git build-essential python3-venv && \
    rm -rf /var/lib/apt/lists/*

# 5. Create Virtual Environment
# We still use --system-site-packages so we can see the base SGLang/Torch
RUN python3 -m venv /app/venv --system-site-packages

# 6. Install Python Dependencies (UPDATED for CUDA 12.1)
# - Changed unsloth[cu124] -> unsloth[cu121]
# - Kept unsloth_zoo and bitsandbytes
RUN /app/venv/bin/pip install --no-cache-dir --upgrade pip && \
    /app/venv/bin/pip install --no-cache-dir \
    "unsloth_zoo>=0.0.1" \
    "unsloth[cu121] @ git+https://github.com/unslothai/unsloth.git" \
    bitsandbytes \
    fastapi uvicorn prometheus_client

# 7. Copy Source Code
COPY . /app

# 8. Expose Port
EXPOSE 8000

# 9. Command
ENV PYTHONPATH="/app:/app/venv/lib/python3.10/site-packages"
CMD ["/app/venv/bin/python", "src/server.py"]
