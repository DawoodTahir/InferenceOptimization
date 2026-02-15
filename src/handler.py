import os
import runpod
import uuid
from engine_wrapper import get_engine
import asyncio
import logging
import boto3
import time
from load import load

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('Logger')

# --- GLOBAL INITIALIZATION ---
# We wrap this in a function or try/except to catch startup errors
engine = None
cw = None
MODEL_PATH = "/runpod-volume"
try:
    
        
    # 2. Load Weights (Check if this is taking too long!)
    if not os.listdir(MODEL_PATH):
        logger.info(f"Downloading weights to {MODEL_PATH}...")
        load(MODEL_PATH)
        logger.info('Weights Downloaded/Loaded')
    else:
        logger.info("Weights directory found, skipping download.")

    # 3. Initialize Engine
    logger.info("Initializing Engine...")
    engine_builder = get_engine(MODEL_PATH)
    engine = engine_builder() # Load model to GPU
    logger.info("Engine Started Successfully.")

    # 4. Setup CloudWatch (Safe Mode)
    try:
        cw = boto3.client('cloudwatch', region_name='us-east-1')
    except Exception as e:
        logger.error(f"Failed to init CloudWatch (Check Env Vars): {e}")
        cw = None

except Exception as e:
    logger.critical(f"CRITICAL STARTUP FAILURE: {e}")
    # We do NOT exit here, so the pod can start and report the error 
    # if you want to debug, otherwise the container loop-crashes.

async def Inference(job):
    global engine, cw
    
    # If startup failed, return error immediately
    if engine is None:
        return {'error': 'Worker failed to initialize model. Check worker logs.'}

    response_id = int(uuid.uuid4().int)
    try:
        start_time = time.time()
        user_input = job["input"]
        job_input = user_input.get("task", "chat")

        if job_input == "chat":
            prompt = user_input.get("prompt")
            params = user_input.get('parameters', {
                "temperature": 0.7,
                "max_new_tokens": 512,
                "top_p": 0.95
            })  

            full_text = ""
            token_count = 0

            # Ensure generate is actually an async generator
            async for chunk in engine.generate(prompt, params, response_id):
                full_text += chunk
                token_count += 1

            duration = time.time() - start_time
            
            # Send Metrics if CloudWatch is active
            if cw:
                try:
                    cw.put_metric_data(
                        Namespace='Inference/RunPod',
                        MetricData=[
                            {'MetricName': 'Latency', 'Value': duration, 'Unit': 'Seconds'},
                            {'MetricName': 'TokenGenerated', 'Value': token_count, 'Unit': 'Count'}
                        ]
                    )
                except Exception as e:
                    logger.error(f"Metric push failed: {e}")
            
            return {'results': full_text, 'status': "200"}
        else:
            return {'results': 'Invalid task type', 'status': "400"}
            
    except Exception as e:
        logger.error(f'Inference Error: {e}')
        return {'results': str(e), 'status': "500"}

# Start the handler
if __name__ == "__main__":
    runpod.serverless.start({'handler': Inference})
