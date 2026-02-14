# 1. Base Image (Keep the safe CUDA 12.4 version)
FROM lmsysorg/sglang:v0.4.7.post1-cu124

# 2. Work Directory
WORKDIR /app

# 3. Copy source code
COPY . /app

# 4. CRITICAL FIX: Install System Build Tools
# We install 'git', 'gcc' (build-essential), and 'python3-dev' so pip can compile anything it needs.
RUN apt-get update && \
    apt-get install -y --no-install-recommends git build-essential python3-dev && \
    rm -rf /var/lib/apt/lists/*

# 5. Upgrade pip just in case (Good practice)
RUN pip install --upgrade pip

# 6. Install Python Dependencies
# Now that we have git and gcc, this will succeed even if it needs to compile something.
RUN pip install --no-cache-dir fastapi uvicorn prometheus_client

# 7. Expose Port
EXPOSE 8000

# 8. Command
CMD ["python3", "src/server.py"]
