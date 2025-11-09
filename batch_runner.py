#!/usr/bin/env python3
"""
Grok Video Torture Chamber - Phase 2: Batch Runner
Async worker pool with GPU dispatch stubs for scalable batch processing.
"""

import asyncio
import logging
import os
from typing import List, Dict, Any, Optional, Callable
from collections import deque
import aiohttp

from test_api_call import generate_video_async, check_gpu_availability

logger = logging.getLogger(__name__)


class BatchRunner:
    """
    Async batch runner with worker pool and GPU dispatch support.
    """
    
    def __init__(
        self,
        api_key: str,
        max_concurrent: int = 100,
        rate_limit_min: float = 1.0,
        rate_limit_max: float = 5.0,
        gpu_enabled: bool = False
    ):
        """
        Initialize batch runner.
        
        Args:
            api_key: XAI API bearer token
            max_concurrent: Maximum concurrent workers
            rate_limit_min: Minimum rate limit delay (seconds)
            rate_limit_max: Maximum rate limit delay (seconds)
            gpu_enabled: Enable GPU dispatch (stub for Phase 3)
        """
        self.api_key = api_key
        self.max_concurrent = max_concurrent
        self.rate_limit_min = rate_limit_min
        self.rate_limit_max = rate_limit_max
        self.gpu_enabled = gpu_enabled
        self.results = []
        self.semaphore = asyncio.Semaphore(max_concurrent)
        
        # GPU dispatch stub
        self.gpu_info = check_gpu_availability()
        if gpu_enabled and self.gpu_info["cuda_available"]:
            logger.info(
                f"GPU dispatch enabled: {self.gpu_info['device_count']} devices"
            )
        else:
            logger.info("GPU dispatch disabled (CPU mode)")
    
    async def _bounded_generate(
        self,
        prompt: str,
        prompt_id: Optional[int] = None,
        device_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate video with semaphore-bound concurrency.
        
        Args:
            prompt: Video generation prompt
            prompt_id: Optional prompt identifier
            device_id: Optional GPU device ID (stub for Phase 3)
            
        Returns:
            Result dictionary
        """
        async with self.semaphore:
            try:
                # GPU dispatch stub (Phase 3 hook)
                if self.gpu_enabled and device_id is not None:
                    logger.debug(f"Dispatching to GPU {device_id}: {prompt[:50]}...")
                    # TODO: Phase 3 - Implement GPU-specific processing
                
                # Generate video (Phase 1 integration)
                result = await generate_video_async(
                    prompt,
                    self.api_key,
                    session=None  # Will create per worker
                )
                
                return {
                    "prompt_id": prompt_id,
                    "prompt": prompt,
                    "device_id": device_id,
                    "video_url": result.get("video_url") if result else None,
                    "status": "success" if result else "failed",
                    "result": result
                }
                
            except Exception as e:
                logger.error(f"Generation error: {e}")
                return {
                    "prompt_id": prompt_id,
                    "prompt": prompt,
                    "device_id": device_id,
                    "status": "error",
                    "error": str(e)
                }
    
    async def run_batch(
        self,
        prompts: List[str],
        device_allocation: Optional[Callable[[int], int]] = None
    ) -> List[Dict[str, Any]]:
        """
        Run batch of prompts through worker pool.
        
        Args:
            prompts: List of prompts to process
            device_allocation: Optional function to allocate GPU device by prompt index
            
        Returns:
            List of result dictionaries
        """
        logger.info(f"Starting batch run: {len(prompts)} prompts, {self.max_concurrent} workers")
        
        # Create shared session for connection pooling
        async with aiohttp.ClientSession() as session:
            # Create tasks with device allocation
            tasks = []
            for i, prompt in enumerate(prompts):
                device_id = None
                if self.gpu_enabled and device_allocation:
                    device_id = device_allocation(i)
                elif self.gpu_enabled and self.gpu_info["device_count"] > 0:
                    # Round-robin allocation
                    device_id = i % self.gpu_info["device_count"]
                
                task = self._bounded_generate(
                    prompt,
                    prompt_id=i,
                    device_id=device_id
                )
                tasks.append(task)
            
            # Execute all tasks
            results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Task exception: {result}")
                processed_results.append({
                    "status": "exception",
                    "error": str(result)
                })
            else:
                processed_results.append(result)
        
        self.results = processed_results
        
        # Log statistics
        success_count = sum(1 for r in processed_results if r.get("status") == "success")
        logger.info(
            f"Batch complete: {success_count}/{len(processed_results)} successful"
        )
        
        return processed_results
    
    async def run_batch_with_queue(
        self,
        prompts: List[str],
        queue_size: int = 10000
    ) -> List[Dict[str, Any]]:
        """
        Run batch with async queue for backpressure control.
        
        Args:
            prompts: List of prompts to process
            queue_size: Maximum queue size for backpressure
            
        Returns:
            List of result dictionaries
        """
        queue = asyncio.Queue(maxsize=queue_size)
        results = []
        
        # Producer: Add prompts to queue
        async def producer():
            for i, prompt in enumerate(prompts):
                await queue.put((i, prompt))
            # Add sentinels for worker shutdown
            for _ in range(self.max_concurrent):
                await queue.put((None, None))
        
        # Consumer: Process prompts from queue
        async def consumer(worker_id: int):
            worker_results = []
            async with aiohttp.ClientSession() as session:
                while True:
                    prompt_id, prompt = await queue.get()
                    
                    if prompt is None:  # Sentinel
                        break
                    
                    try:
                        result = await generate_video_async(
                            prompt,
                            self.api_key,
                            session=session
                        )
                        
                        worker_results.append({
                            "worker_id": worker_id,
                            "prompt_id": prompt_id,
                            "prompt": prompt,
                            "video_url": result.get("video_url") if result else None,
                            "status": "success" if result else "failed"
                        })
                        
                    except Exception as e:
                        worker_results.append({
                            "worker_id": worker_id,
                            "prompt_id": prompt_id,
                            "prompt": prompt,
                            "status": "error",
                            "error": str(e)
                        })
                    
                    queue.task_done()
            
            return worker_results
        
        # Start producer and consumers
        logger.info(f"Starting queue-based batch: {len(prompts)} prompts")
        
        producer_task = asyncio.create_task(producer())
        consumer_tasks = [
            asyncio.create_task(consumer(i))
            for i in range(self.max_concurrent)
        ]
        
        # Wait for completion
        await producer_task
        worker_results = await asyncio.gather(*consumer_tasks)
        
        # Flatten results
        for worker_result_list in worker_results:
            results.extend(worker_result_list)
        
        self.results = results
        logger.info(f"Queue batch complete: {len(results)} results")
        
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get batch processing statistics.
        
        Returns:
            Statistics dictionary
        """
        if not self.results:
            return {"total": 0}
        
        total = len(self.results)
        success = sum(1 for r in self.results if r.get("status") == "success")
        failed = sum(1 for r in self.results if r.get("status") == "failed")
        errors = sum(1 for r in self.results if r.get("status") == "error")
        
        return {
            "total": total,
            "success": success,
            "failed": failed,
            "errors": errors,
            "success_rate": success / total if total > 0 else 0.0,
            "gpu_enabled": self.gpu_enabled,
            "gpu_devices": self.gpu_info.get("device_count", 0)
        }


def create_device_allocator(
    device_count: int,
    strategy: str = "round_robin"
) -> Callable[[int], int]:
    """
    Create GPU device allocation function.
    
    Args:
        device_count: Number of GPU devices
        strategy: Allocation strategy ('round_robin', 'random', 'load_balanced')
        
    Returns:
        Device allocation function
    """
    if strategy == "round_robin":
        def allocator(prompt_id: int) -> int:
            return prompt_id % device_count
        return allocator
    elif strategy == "random":
        import random
        def allocator(prompt_id: int) -> int:
            return random.randint(0, device_count - 1)
        return allocator
    else:  # load_balanced (stub for Phase 3)
        def allocator(prompt_id: int) -> int:
            # TODO: Phase 3 - Implement load balancing
            return prompt_id % device_count
        return allocator


async def main():
    """Test batch runner."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("XAI_API_KEY")
    if not api_key:
        logger.error("XAI_API_KEY not found")
        return
    
    # Test with small batch
    test_prompts = [
        "samurai vs T-rex",
        "cyberpunk cityscape",
        "space battle",
    ]
    
    runner = BatchRunner(
        api_key=api_key,
        max_concurrent=2,
        gpu_enabled=False
    )
    
    results = await runner.run_batch(test_prompts)
    stats = runner.get_statistics()
    
    logger.info(f"Batch runner test complete: {stats}")


if __name__ == "__main__":
    asyncio.run(main())

