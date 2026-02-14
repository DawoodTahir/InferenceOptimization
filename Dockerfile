FROM lmsysorg/sglang:v0.4.7.post1-cu124

WORKDIR /app
# 3. Copy our source code
# This takes your local 'src' folder and puts it inside the container so we can run it.
COPY . /app
# 4. Install FastAPI dependencies
# SGLang handles the heavy lifting, but we need FastAPI to expose our custom endpoints.
RUN pip install --no-cache-dir fastapi uvicorn prometheus_client
# 5. Expose the port
EXPOSE 8000
# 6. Command
# We start our own server wrapper, which will initialize the SGLang engine internally.
CMD ["python3", "src/server.py"]
