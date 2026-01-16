import os
import asyncio
from abc import ABC, abstractmethod
from typing import AsyncGenerator,Dict,Any,Optional
import logging
import time
logging.basicConfig(level=logging.INFO)
logger=logging.getLogger("Inference_Optimization")
def get_engine(model_path: str):
    engine_type=os.getenv("ENGINE_TYPE", "vllm").lower()
    if engine_type=="vllm":
        return VLLMEngine(model_path)
    elif engine_type=="sglang":
        return LlamaEngine(model_path)
    else:
        raise ValueError(f"Unknown engine type: {engine_type}")


class BaseLLMEngine(ABC):
    @abstractmethod
    async def generate(self, prompot:str, sampling_params, request_id):
        logger.info("Generating response for request_id: %s", request_id)
        raise NotImplementedError



class VLLMEngine(BaseLLMEngine):
    def __init__(self, model_path: str):
        logger.info("Initializing VLLMEngine")
        from vllm.engine.async_engine import AsyncEngine
        from vllm.engine.arg_utils import AsyncEngineArgs
        
        #setting up engine arguments
        self.engine_args =AsyncEngineArgs(model_path=model_path,
        gpu_memory_utilization=0.90)
        
        ##laoding engine , warming up GPU , loading kernels and loading model
        self.engine = AsyncEngine.from_engine_args(self.engine_args)

    async def generate(self,prompt:str,sampling_params, request_id):
        logger.info("Generating response for request_id: %s", request_id)

        from vllm import SamplingParams

        vllm_params = SamplingParams(**sampling_params)

        result_generator = self.engine.generate(prompt, vllm_params, request_id)
        ttft = None
        start= time.perf_counter()
        async for results in result_generator:
            if ttft is None:
                ttft =time.perf_counter()
            ##returns the result while streaming
            yield results.outputs[0].text

        end = time.perf_counter()

        ttft = end - start


class SGLangEngine(BaseLLMEngine):
    def __init__(self, model_path: str):
        logger.info("Initializing SGLangEngine")
        from sglang import SGLang
        from sglang.srt.server_args import server_args
        from sglang.srt.engine import Engine


        self.server_args = ServerArgs(model_path=model_path,server_model_name ="sglang-model",

        ##Optimizaton work
        disable_radix_cache=False,
        chunked_prefill_size=4096,
        mem_fraction_static = 0.9,
        port = 30000)

        self.Engine = Engine.from_engine_args(self.server_args)

    async def generate(self, prompt:str, sampling_params, request_id):
        logger.info("Generating response for request_id: %s", request_id)
        sglang_params = SampingParams(**sampling_params)
        result_generator = self.Engine.async_generate(prompt, sglang_params, request_id)
        ttft = None
        start= time.perf_counter()
        async for results in result_generator:
            if ttft is None:
                ttft =time.perf_counter()
            ##returns the result while streaming
            yield output["text"]

        end = time.perf_counter()

        ttft = end - start




        
