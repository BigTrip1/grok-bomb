#!/usr/bin/env python3
"""
Grok Video Torture Chamber - Phase 1 API Test Module
Async video generation with rate limiting, download, and logging.
"""

import asyncio
import random
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import aiohttp
import requests
from tqdm import tqdm


# Configure logging with timestamps
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


# API endpoint
API_URL = "https://api.x.ai/v1/video/generate"


async def jittered_sleep(min_seconds: float = 1.0, max_seconds: float = 5.0):
    """
    Async sleep with jittered delay for rate limiting.
    
    Args:
        min_seconds: Minimum sleep duration
        max_seconds: Maximum sleep duration
    """
    delay = random.uniform(min_seconds, max_seconds)
    await asyncio.sleep(delay)
    logger.debug(f"Rate limit delay: {delay:.2f}s")


async def generate_video_async(
    prompt: str,
    api_key: str,
    session: Optional[aiohttp.ClientSession] = None
) -> Optional[Dict[str, Any]]:
    """
    Generate video asynchronously using Grok Video API.
    
    Args:
        prompt: Video generation prompt
        api_key: XAI API bearer token
        session: Optional aiohttp session for connection pooling
        
    Returns:
        Response JSON dict with video_url, or None on error
    """
    # Rate limiting with jitter
    await jittered_sleep(1.0, 5.0)
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "prompt": prompt
    }
    
    close_session = False
    if session is None:
        session = aiohttp.ClientSession()
        close_session = True
    
    try:
        logger.info(f"Generating video with prompt: {prompt[:50]}...")
        
        async with session.post(
            API_URL,
            headers=headers,
            json=payload,
            timeout=aiohttp.ClientTimeout(total=300)
        ) as response:
            if response.status == 200:
                result = await response.json()
                video_url = result.get("video_url")
                logger.info(f"✅ Video generated: {video_url}")
                return result
            else:
                error_text = await response.text()
                logger.error(
                    f"❌ API error {response.status}: {error_text}"
                )
                return None
                
    except asyncio.TimeoutError:
        logger.error("❌ Request timeout")
        return None
    except Exception as e:
        logger.error(f"❌ Generation failed: {e}")
        return None
    finally:
        if close_session:
            await session.close()


def download_video(
    video_url: str,
    output_path: str = "./tests/video.mp4",
    chunk_size: int = 8192
) -> bool:
    """
    Download video file from URL with progress bar.
    
    Args:
        video_url: URL of video to download
        output_path: Local path to save video
        chunk_size: Download chunk size in bytes
        
    Returns:
        True if successful, False otherwise
    """
    try:
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Downloading video to {output_path}...")
        
        response = requests.get(video_url, stream=True, timeout=60)
        response.raise_for_status()
        
        total_size = int(response.headers.get("content-length", 0))
        
        with open(output_file, "wb") as f, tqdm(
            desc="Downloading",
            total=total_size,
            unit="B",
            unit_scale=True,
            unit_divisor=1024
        ) as pbar:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    pbar.update(len(chunk))
        
        logger.info(f"✅ Video saved to {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Download failed: {e}")
        return False


async def generate_and_download(
    prompt: str,
    api_key: str,
    output_path: str = "./tests/video.mp4"
) -> bool:
    """
    Generate video and download it in one async operation.
    
    Args:
        prompt: Video generation prompt
        api_key: XAI API bearer token
        output_path: Local path to save video
        
    Returns:
        True if successful, False otherwise
    """
    async with aiohttp.ClientSession() as session:
        result = await generate_video_async(prompt, api_key, session)
        
        if result and result.get("video_url"):
            return download_video(result["video_url"], output_path)
        else:
            logger.error("No video URL in response")
            return False


def check_gpu_availability() -> Dict[str, Any]:
    """
    Check GPU availability and device count.
    
    Returns:
        Dict with cuda_available and device_count
    """
    try:
        import torch
        cuda_available = torch.cuda.is_available()
        device_count = torch.cuda.device_count() if cuda_available else 0
        
        return {
            "cuda_available": cuda_available,
            "device_count": device_count,
            "devices": [
                torch.cuda.get_device_name(i)
                for i in range(device_count)
            ] if cuda_available else []
        }
    except ImportError:
        logger.warning("PyTorch not available for GPU check")
        return {
            "cuda_available": False,
            "device_count": 0,
            "devices": []
        }


async def main():
    """Main test function."""
    from dotenv import load_dotenv
    
    load_dotenv()
    api_key = os.getenv("XAI_API_KEY")
    
    if not api_key:
        logger.error("XAI_API_KEY not found in environment")
        return
    
    # Check GPU
    gpu_info = check_gpu_availability()
    logger.info(
        f"Phase 1 ready, CUDA: {gpu_info['cuda_available']}, "
        f"GPUs: {gpu_info['device_count']}"
    )
    
    # Test prompt
    test_prompt = (
        "8K dolly zoom cyberpunk samurai vs chrome T-rex in neon rain, "
        "perfect physics --camera dolly+orbit"
    )
    
    # Generate and download
    success = await generate_and_download(
        test_prompt,
        api_key,
        "./tests/video.mp4"
    )
    
    if success:
        logger.info("✅ Phase 1 test complete!")
    else:
        logger.error("❌ Phase 1 test failed")


if __name__ == "__main__":
    asyncio.run(main())

