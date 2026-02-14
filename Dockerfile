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
# CRITICAL: We add '--system-site-packages' so this venv can see the 
# PyTorch and SGLang installed in the base image.
RUN python3 -m venv /app/venv --system-site-packages

# 6. Install Unsloth and Server Dependencies
# We use --no-deps for Unsloth to prevent it from breaking the existing PyTorch.
# We explicitly install "unsloth_zoo" as well, which is often needed.
RUN /app/venv/bin/pip install --no-cache-dir "unsloth[cu124] @ git+https://github.com/unslothai/unsloth.git" \
    fastapi uvicorn prometheus_client

# 7. Copy Source Code
COPY . /app

# 8. Expose Port
EXPOSE 8000

# 9. Command
# We use the python inside the venv to run the server.
ENV PYTHONPATH="/app:/app/venv/lib/python3.10/site-packages"
CMD ["/app/venv/bin/python", "src/server.py"]
