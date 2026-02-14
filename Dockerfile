# 1. Base Image
FROM lmsysorg/sglang:v0.4.7.post1-cu124

# 2. CRITICAL FIX: Switch to Root User
# This grants permission to install system packages and upgrade pip.
USER root

# 3. Work Directory
WORKDIR /app

# 4. Install System Dependencies
# We install 'git' (to fix the git warning) and 'build-essential' (to fix pip compile errors).
RUN apt-get update && \
    apt-get install -y --no-install-recommends git build-essential python3-dev && \
    rm -rf /var/lib/apt/lists/*

# 5. Upgrade pip (Now successful because we are root)
RUN pip install --upgrade pip --no-cache-dir

# 6. Install Python Dependencies
RUN pip install --no-cache-dir fastapi uvicorn prometheus_client

# 7. Copy Source Code
# (Moved after dependency install so we can cache the layers above)
COPY . /app

# 8. Expose Port
EXPOSE 8000

# 9. Command
CMD ["python3", "src/server.py"]
