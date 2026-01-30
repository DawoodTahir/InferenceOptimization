import os
import asyncio
from abc import ABC, abstractmethod
from typing import AsyncGenerator,Dict,Any,Optional
import logging
import time
from load import load
logging.basicConfig(level=logging.INFO)
logger=logging.getLogger("Inference_Optimization")


class get_engine:
    def __init__(self, path: str):

        self.path=path

    def __call__(self):
        engine_type=os.getenv("ENGINE_TYPE", "vllm").lower()
        if engine_type=="vllm":
            return VLLMEngine(self.path)
        elif engine_type=="sglang":
            return SGLangEngine(self.path)
        else:
            raise ValueError(f"Unknown engine type: {engine_type}")
    
        model, tokenizer = load()

        return model, tokenizer

    

class BaseLLMEngine(ABC):
    @abstractmethod
    async def generate(self, prompt:str, sampling_params, request_id):
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
        
        ##loading engine , warming up GPU , loading kernels and loading model
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
        from sglang.srt.server_args import ServerArgs
        from sglang.srt.engine import Engine

        self.server_args = ServerArgs(
            model_path=model_path,
            server_model_name="sglang-model",
            ##Optimizaton work
            disable_radix_cache=False,
            chunked_prefill_size=4096,
            mem_fraction_static=0.9,
            port=30000
        )

        ##Load Engine
        self.Engine = Engine(server_args=self.server_args)

    async def generate(self, prompt: str, sampling_params, request_id):
        logger.info("Generating response for request_id: %s", request_id)
        # Import SamplingParams correctly
        from sglang.srt.sampling_params import SamplingParams
        
        sglang_params = SamplingParams(**sampling_params)
        result_generator = self.Engine.async_generate(prompt, sglang_params, request_id)
        ttft = None
        start= time.perf_counter()
        async for results in result_generator:
            if ttft is None:
                ttft =time.perf_counter()
            ##returns the result while streaming
            yield results["text"]

        end = time.perf_counter()

        ttft = end - start




        
