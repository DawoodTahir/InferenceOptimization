# Use the safe CUDA 12.1 image
FROM lmsysorg/sglang:v0.4.5.post3-cu121

WORKDIR /app
COPY . /app

# Expose the port
EXPOSE 8000
RUN python3 -m pip install --no-cache-dir runpod


CMD ["python3", "src/handler.py"]
