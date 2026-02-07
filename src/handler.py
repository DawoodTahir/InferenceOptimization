import os
import runpod
import uuid
from engine_wrapper import get_engine
import asyncio
import logging
import boto3
import time
from load import load

TOKEN_COUNTER = Counter("lm_tokens_total", "Total tokens Generated")
LATENCY_HISTOGRAM = Histogram("llm_generation_seconds", "Time spent generating response", buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0])

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('Logger')


#load the model
output_dir = '/workspace/InferenceOptimization/src/weights'
if not os.listdir(output_dir):
  try:
    load(output_dir)
    logger.info('Weights Loaded')
  except Exception as e:
    logger.info(f"Unable to load weights due to {e}")
else:
  logger.info("No directory found")

engine = get_engine(output_dir)
engine = engine()

cw = boto3.client('cloudwatch',region_name = 'us-east-1')
def metric(duration, tokens):

  try:
    cw.put_metric_data(
      Namespace='Inference/RunPod',
      MetricData = [
        {
          'MetricName' :'Latency',
          'Value' : duration,
          'Unit'  : 'Seconds'
        },
        {
          'MetricName' : 'TokenGenerated',
          'Value' : tokens,
          'Units' : 'Count'
        },
        {
          'MetricName' : 'tokensPerSecond',
          'Value'       : tokens / duration if duration > 0 else 0,
          'Metric'      : 'Count/Second'
        } 
      ]
    )
  except Exception as e:
        logger.error(f"Failed to push metrics: {e}")


async def Inference(job):
  global engine 
  response_id = int(uuid.uuid4())
  try:

    
    start_time = time.time()
    user_input = job["input"]
    job_input = user_input.get("task","chat")

    if job_input =="chat":
      prompt = user_input.get("prompt")

      
      params = user_input.get('parameters', {
      "temperature": 0.7,
      "max_new_tokens": 512,
      "top_p": 0.95
      })  

      full_text = ""
      token_count = 0

      async for chunk in engine.generate(user_input,params,response_id):
        full_text+= chunk
      
        token_count += 1


      duration = time.time() - start_time
      
      return {'results' : full_text, 'status': "200"}
    else:
      pass
  except Exception as e:
    logger.info(f'Inference Error {e}')
    
    return {'results': str(e), 'status' : "400"}









if __name__ == "__main__":
    runpod.serverless.start({'handler' : Inference})

