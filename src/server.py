from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from engine_wrapper import get_engine
import argparse
import logging
import uuid
import json

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('Logger')

# Parse arguments
args = argparse.ArgumentParser('Argument Parser')
args.add_argument('--path', dest='model_path', required=True, help='Path to the model')
cli_args = args.parse_args()
    
    
##load the model
model, tokenizer = get_engine(cli_args.model_path)

app = FastAPI(title="E2E for LLM inference")

# Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/')
def home():
    return {'status': 'online', 'hardware': 'RTX 4000 Ada'}

@app.post('/Inference')
async def inference(request: Request):
    global engine



@app.post('/Inference')
async def Inference(engine):

  response_id = int(uuid.uuid4())
  try:

    data =  await Request.json()
    input = data.get['inputs'].lower()
    
    result= await engine.generate(input,response_id)
    
    return {'results' : result, 'status': "200"}
  
  except Exception as e:
    logger.info(f'Inference Error {e}')
    
    return {'results': str(e), 'status' : "400"}

    










