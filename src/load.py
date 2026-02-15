import torch
import sglang 
def load():
    max_seq_length = 2048
    dtype = None
    load_in_4bit = True 
    return sglang.Engine(model_path=model_path , tp_size=1)  
