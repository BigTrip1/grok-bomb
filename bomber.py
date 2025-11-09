#!/usr/bin/env python3
"""
Grok Video Torture Chamber - Phase 2: Prompt Bomber
Core mutator function with async queue integration for batch generation.
"""

import asyncio
import logging
import os
from typing import List, Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

from variants_generator import (
    generate_variants,
    create_adversarial_batch,
    get_mutation_metadata,
)
from test_api_call import generate_video_async, check_gpu_availability
from batch_runner import BatchRunner

logger = logging.getLogger(__name__)


async def mutate_and_queue(
    base_prompt: str,
    queue: asyncio.Queue,
    variant_count: int = 1000,
    strategy: str = "random"
) -> int:
    """
    Generate prompt variants and add them to async queue.
    
    Args:
        base_prompt: Base prompt to mutate
        queue: Async queue for prompt distribution
        variant_count: Number of variants to generate
        strategy: Mutation strategy
        
    Returns:
        Number of variants queued
    """
    variants = generate_variants(
        base_prompt,
        count=variant_count,
        strategies=[strategy]
    )
    
    for variant in variants:
        metadata = get_mutation_metadata(variant, base_prompt)
        await queue.put({
            "prompt": variant,
            "base": base_prompt,
            "metadata": metadata
        })
    
    logger.info(f"Queued {len(variants)} variants from base: {base_prompt[:50]}...")
    return len(variants)


async def bomber_worker(
    queue: asyncio.Queue,
    api_key: str,
    results: List[Dict[str, Any]],
    worker_id: int,
    session: Optional[Any] = None
) -> None:
    """
    Worker coroutine that processes prompts from queue.
    
    Args:
        queue: Async queue containing prompts
        api_key: XAI API bearer token
        results: Shared results list (thread-safe append)
        worker_id: Worker identifier
        session: Optional aiohttp session
    """
    logger.info(f"Worker {worker_id} started")
    
    import aiohttp
    if session is None:
        session = aiohttp.ClientSession()
        close_session = True
    else:
        close_session = False
    
    try:
        while True:
            try:
                # Get prompt with timeout
                item = await asyncio.wait_for(queue.get(), timeout=1.0)
                
                if item is None:  # Sentinel for shutdown
                    break
                
                prompt = item["prompt"]
                metadata = item.get("metadata", {})
                
                logger.debug(f"Worker {worker_id} processing: {prompt[:50]}...")
                
                # Generate video
                result = await generate_video_async(prompt, api_key, session)
                
                # Store result
                if result:
                    results.append({
                        "worker_id": worker_id,
                        "prompt": prompt,
                        "metadata": metadata,
                        "video_url": result.get("video_url"),
                        "status": "success"
                    })
                    logger.info(
                        f"Worker {worker_id} ✅ Generated: {result.get('video_url')}"
                    )
                else:
                    results.append({
                        "worker_id": worker_id,
                        "prompt": prompt,
                        "metadata": metadata,
                        "status": "failed"
                    })
                    logger.warning(f"Worker {worker_id} ❌ Failed: {prompt[:50]}...")
                
                queue.task_done()
                
            except asyncio.TimeoutError:
                # Check if queue is empty and we should shutdown
                if queue.empty():
                    logger.debug(f"Worker {worker_id} queue empty, checking shutdown...")
                    continue
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {e}")
                queue.task_done()
                
    finally:
        if close_session:
            await session.close()
        logger.info(f"Worker {worker_id} stopped")


async def run_prompt_bombing(
    base_prompts: List[str],
    api_key: str,
    variants_per_base: int = 100,
    max_concurrent: int = 100,
    total_target: int = 10000
) -> List[Dict[str, Any]]:
    """
    Run prompt bombing campaign with async worker pool.
    
    Args:
        base_prompts: List of base prompts to mutate
        api_key: XAI API bearer token
        variants_per_base: Variants per base prompt
        max_concurrent: Maximum concurrent workers
        total_target: Target total variants
        
    Returns:
        List of generation results
    """
    # Create queue
    queue = asyncio.Queue(maxsize=10000)  # Backpressure limit
    
    # Generate and queue variants
    logger.info(f"Generating {total_target} variants from {len(base_prompts)} bases...")
    
    # Use batch runner for efficient processing
    runner = BatchRunner(
        api_key=api_key,
        max_concurrent=max_concurrent
    )
    
    # Create adversarial batch
    variants = create_adversarial_batch(
        base_prompts=base_prompts,
        variants_per_base=variants_per_base,
        total_target=total_target
    )
    
    logger.info(f"Generated {len(variants)} variants, starting batch run...")
    
    # Run batch through batch runner
    results = await runner.run_batch(variants)
    
    logger.info(f"Bomber complete: {len(results)} results")
    return results


async def test_bomber(
    base_prompt: str = "samurai vs T-rex",
    variant_count: int = 20,
    test_generations: int = 5
) -> None:
    """
    Test the bomber with a small batch.
    
    Args:
        base_prompt: Base prompt to test
        variant_count: Number of variants to generate
        test_generations: Number of actual API calls to make
    """
    load_dotenv()
    api_key = os.getenv("XAI_API_KEY")
    
    if not api_key:
        logger.error("XAI_API_KEY not found in environment")
        return
    
    # Check GPU
    gpu_info = check_gpu_availability()
    logger.info(
        f"Bomber ready, CUDA: {gpu_info['cuda_available']}, "
        f"GPUs: {gpu_info['device_count']}"
    )
    
    # Generate variants
    from variants_generator import generate_variants
    variants = generate_variants(base_prompt, count=variant_count)
    
    logger.info(f"Generated {len(variants)} variants")
    logger.info(f"Sample variants:")
    for i, variant in enumerate(variants[:5], 1):
        logger.info(f"  {i}. {variant}")
    
    # Test queue with small batch
    queue = asyncio.Queue()
    results = []
    
    # Add test prompts to queue
    for variant in variants[:test_generations]:
        await queue.put({
            "prompt": variant,
            "base": base_prompt,
            "metadata": get_mutation_metadata(variant, base_prompt)
        })
    
    # Add sentinels for worker shutdown
    for _ in range(2):  # Number of workers
        await queue.put(None)
    
    # Start workers
    workers = [
        asyncio.create_task(
            bomber_worker(queue, api_key, results, worker_id=i)
        )
        for i in range(2)
    ]
    
    # Wait for workers to complete
    await asyncio.gather(*workers)
    
    logger.info(f"Test complete: {len(results)} generations")
    logger.info("Bomber ready for 10k swarm")


async def main():
    """Main bomber function."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Run test
    await test_bomber()


if __name__ == "__main__":
    asyncio.run(main())

