#!/usr/bin/env python3
"""
Grok Video Torture Chamber - Environment Validator
Pre-flight check for all API keys and dependencies before pipeline execution.
"""

import os
import sys
from typing import List, Tuple, Optional
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)


def validate_environment() -> Tuple[bool, List[str]]:
    """
    Validate all required environment variables and dependencies.
    
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    load_dotenv()
    errors = []
    warnings = []
    
    # Required API keys
    required_keys = {
        "XAI_API_KEY": "xAI API key for video generation",
        "X_API_KEY": "X (Twitter) API key",
        "X_API_SECRET": "X (Twitter) API secret",
        "X_ACCESS_TOKEN": "X (Twitter) access token",
        "X_ACCESS_TOKEN_SECRET": "X (Twitter) access token secret"
    }
    
    # Optional keys
    optional_keys = {
        "X_BEARER_TOKEN": "X (Twitter) bearer token (optional)"
    }
    
    # Check required keys
    missing_required = []
    for key, description in required_keys.items():
        value = os.getenv(key)
        if not value:
            missing_required.append(f"{key} ({description})")
            errors.append(f"Missing required: {key}")
        elif len(value) < 10:  # Basic validation
            errors.append(f"Invalid {key}: Too short (likely invalid)")
    
    # Check optional keys
    for key, description in optional_keys.items():
        value = os.getenv(key)
        if not value:
            warnings.append(f"Optional {key} not set ({description})")
    
    # Test dependencies
    try:
        import torch
        import torchvision
        import cv2
        import moviepy
        import tweepy
        import aiohttp
        import numpy
        import skimage
    except ImportError as e:
        errors.append(f"Missing dependency: {e.name}")
    
    # Test CUDA (optional)
    try:
        import torch
        if torch.cuda.is_available():
            logger.info(f"✅ CUDA available: {torch.cuda.device_count()} GPUs")
        else:
            warnings.append("CUDA not available (will use CPU)")
    except Exception as e:
        warnings.append(f"Could not check CUDA: {e}")
    
    # Return results
    is_valid = len(errors) == 0
    
    if errors:
        logger.error("❌ Environment validation failed:")
        for error in errors:
            logger.error(f"  - {error}")
    
    if warnings:
        logger.warning("⚠️  Environment warnings:")
        for warning in warnings:
            logger.warning(f"  - {warning}")
    
    if is_valid:
        logger.info("✅ Environment validation passed")
    
    return is_valid, errors + warnings


def test_xai_connection(api_key: Optional[str] = None) -> bool:
    """
    Test xAI API connection.
    
    Args:
        api_key: Optional API key (uses env if not provided)
        
    Returns:
        True if connection successful, False otherwise
    """
    if api_key is None:
        api_key = os.getenv("XAI_API_KEY")
    
    if not api_key:
        logger.error("❌ XAI_API_KEY not found")
        return False
    
    try:
        import requests
        # Simple connection test (don't actually generate video)
        # Just check if API endpoint is reachable
        response = requests.get(
            "https://api.x.ai/v1/models",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10
        )
        if response.status_code == 200:
            logger.info("✅ xAI API connection successful")
            return True
        else:
            logger.warning(f"⚠️  xAI API returned status {response.status_code}")
            return False
    except Exception as e:
        logger.warning(f"⚠️  xAI API connection test failed: {e}")
        return False


def test_x_api_connection() -> bool:
    """
    Test X (Twitter) API connection.
    
    Returns:
        True if connection successful, False otherwise
    """
    api_key = os.getenv("X_API_KEY")
    api_secret = os.getenv("X_API_SECRET")
    access_token = os.getenv("X_ACCESS_TOKEN")
    access_token_secret = os.getenv("X_ACCESS_TOKEN_SECRET")
    
    if not all([api_key, api_secret, access_token, access_token_secret]):
        logger.error("❌ X API credentials incomplete")
        return False
    
    try:
        import tweepy
        client = tweepy.Client(
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_token_secret,
            wait_on_rate_limit=True
        )
        # Test connection by getting user info
        user = client.get_me()
        if user.data:
            logger.info(f"✅ X API connection successful (user: @{user.data.username})")
            return True
        else:
            logger.warning("⚠️  X API connection test failed: No user data")
            return False
    except Exception as e:
        logger.warning(f"⚠️  X API connection test failed: {e}")
        return False


def main():
    """Main validation function."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    print("=" * 60)
    print("Grok Video Torture Chamber - Environment Validator")
    print("=" * 60)
    
    # Validate environment
    is_valid, issues = validate_environment()
    
    if not is_valid:
        print("\n❌ Environment validation failed!")
        print("Please fix the following issues:")
        for issue in issues:
            print(f"  - {issue}")
        sys.exit(1)
    
    # Test API connections
    print("\n🔍 Testing API connections...")
    xai_ok = test_xai_connection()
    x_api_ok = test_x_api_connection()
    
    if not xai_ok:
        print("⚠️  xAI API connection test failed (may still work for video generation)")
    
    if not x_api_ok:
        print("⚠️  X API connection test failed (may still work for posting)")
    
    # Final status
    if is_valid:
        print("\n✅ Environment validation passed!")
        print("Ready to run pipeline.")
        sys.exit(0)
    else:
        print("\n❌ Environment validation failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()

