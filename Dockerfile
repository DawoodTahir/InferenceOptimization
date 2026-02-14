# 1. Base Image (Keep the safe CUDA 12.4 version)
FROM lmsysorg/sglang:v0.4.7.post1-cu124

# 2. Switch to Root
USER root

# 3. Work Directory
WORKDIR /app

# 4. Install System Tools (git + venv)
RUN apt-get update && \
    apt-get install -y --no-install-recommends git python3-venv && \
    rm -rf /var/lib/apt/lists/*

# 5. Create a Virtual Environment
# We create a folder called 'venv' to hold our new packages
RUN python3 -m venv /app/venv

# 6. Install Dependencies into the Virtual Environment
# We use /app/venv/bin/pip to ensure we install HERE, not in the locked system python.
RUN /app/venv/bin/pip install --no-cache-dir fastapi uvicorn prometheus_client

# 7. Copy Source Code
COPY . /app

# 8. Expose Port
EXPOSE 8000

# 9. Command
# CRITICAL: We use the python inside the venv to run the server.
# This python has access to FastAPI (in venv) AND the system packages (SGLang) via site-packages.
ENV PYTHONPATH="/app:/app/venv/lib/python3.10/site-packages"
CMD ["/app/venv/bin/python", "src/server.py"]
