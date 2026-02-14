# 1. Base Image
FROM lmsysorg/sglang:v0.4.7.post1-cu124

# 2. Switch to Root to allow installing system tools
USER root

# 3. Install System Dependencies
# We install 'git' and 'build-essential' to fix the "git not found" and compile errors.
# We also clean up immediately to keep the layer small.
RUN apt-get update && \
    apt-get install -y --no-install-recommends git build-essential python3-dev && \
    rm -rf /var/lib/apt/lists/*

# 4. Work Directory
WORKDIR /app

# 5. Install Python Dependencies
# CHANGE 1: We skipped "pip install --upgrade pip" because it was crashing.
# CHANGE 2: We use "python3 -m pip" which is safer than just "pip".
RUN python3 -m pip install --no-cache-dir fastapi uvicorn prometheus_client

# 6. Copy Source Code
COPY . /app

# 7. Expose Port
EXPOSE 8000

# 8. Command
CMD ["python3", "src/server.py"]
