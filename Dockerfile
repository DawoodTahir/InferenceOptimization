# Use the safe CUDA 12.1 image
FROM lmsysorg/sglang:v0.4.5.post3-cu121

WORKDIR /app
COPY . /app

# Expose the port
EXPOSE 8000

# Run your server
# Make sure your server points to the /runpod-volume/my-model path!
CMD ["python3", "src/handler.py"]
