# 1. Base Image (Keep the safe CUDA 12.4 version)
FROM lmsysorg/sglang:v0.4.7.post1-cu124

# 2. Switch to Root
USER root

# 3. Work Directory
WORKDIR /app

# 4. Install System Tools (git + venv + compilers)
RUN apt-get update && \
    apt-get install -y --no-install-recommends git build-essential python3-venv && \
    rm -rf /var/lib/apt/lists/*

# 5. Create a Virtual Environment with System Packages Access
RUN python3 -m venv /app/venv --system-site-packages

# 6. Install Dependencies (FIXED)
# We install unsloth_zoo explicitly, then unsloth, then the server tools.
RUN /app/venv/bin/pip install --no-cache-dir --upgrade pip && \
    /app/venv/bin/pip install --no-cache-dir "unsloth_zoo>=0.0.1" && \
    /app/venv/bin/pip install --no-cache-dir "unsloth[cu124] @ git+https://github.com/unslothai/unsloth.git" \
    fastapi uvicorn prometheus_client

# 7. Copy Source Code
COPY . /app

# 8. Expose Port
EXPOSE 8000

# 9. Command
# Ensure we use the venv python which has unsloth_zoo installed
ENV PYTHONPATH="/app:/app/venv/lib/python3.10/site-packages"
CMD ["/app/venv/bin/python", "src/server.py"]
