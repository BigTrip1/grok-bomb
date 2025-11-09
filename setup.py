#!/usr/bin/env python3
"""
Grok Video Torture Chamber - Phase 1 Setup
Installs dependencies, loads environment variables, and tests API connection.
"""

import os
import sys
import subprocess
import getpass
from pathlib import Path
from dotenv import load_dotenv


def install_dependencies():
    """Install required packages from requirements.txt."""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE
        )
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def load_env_keys():
    """Load API keys from .env file or prompt for input."""
    env_path = Path(".env")
    
    if env_path.exists():
        load_dotenv(env_path)
        print("✅ Loaded .env file")
    else:
        print("⚠️  No .env file found. Creating one...")
    
    api_key = os.getenv("XAI_API_KEY")
    
    if not api_key:
        print("🔑 XAI_API_KEY not found in environment")
        api_key = getpass.getpass("Enter your XAI API key: ")
        
        # Save to .env file
        with open(env_path, "w") as f:
            f.write(f"XAI_API_KEY={api_key}\n")
        print("✅ Saved API key to .env file")
    
    return api_key


def check_cuda():
    """Check CUDA availability for GPU support."""
    try:
        import torch
        cuda_available = torch.cuda.is_available()
        device_count = torch.cuda.device_count() if cuda_available else 0
        print(f"🎮 CUDA Available: {cuda_available}")
        if cuda_available:
            print(f"   GPU Devices: {device_count}")
            for i in range(device_count):
                print(f"   - GPU {i}: {torch.cuda.get_device_name(i)}")
        return cuda_available, device_count
    except ImportError:
        print("⚠️  PyTorch not installed, skipping CUDA check")
        return False, 0


def test_api_generation(api_key: str):
    """Test video generation with a sample prompt."""
    print("\n🧪 Testing API generation...")
    
    test_prompt = (
        "8K dolly zoom cyberpunk samurai vs chrome T-rex in neon rain, "
        "perfect physics --camera dolly+orbit"
    )
    
    try:
        # Import here to avoid errors if not installed
        from test_api_call import generate_video_async
        
        import asyncio
        result = asyncio.run(generate_video_async(test_prompt, api_key))
        
        if result:
            print("✅ API test successful!")
            print(f"   Video URL: {result.get('video_url', 'N/A')}")
            return True
        else:
            print("⚠️  API test returned no result")
            return False
    except Exception as e:
        print(f"❌ API test failed: {e}")
        print("   (This is expected if API key is invalid or service is down)")
        return False


def main():
    """Main setup function."""
    print("=" * 60)
    print("Grok Video Torture Chamber - Phase 1 Setup")
    print("=" * 60)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Load environment keys
    api_key = load_env_keys()
    if not api_key:
        print("❌ No API key provided")
        sys.exit(1)
    
    # Check CUDA
    cuda_available, device_count = check_cuda()
    
    # Test API generation
    test_api_generation(api_key)
    
    print("\n" + "=" * 60)
    print("✅ Phase 1 setup complete!")
    print(f"   CUDA: {cuda_available}, GPUs: {device_count}")
    print("=" * 60)


if __name__ == "__main__":
    main()

