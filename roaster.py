#!/usr/bin/env python3
"""
Grok Video Torture Chamber - Phase 4: Auto-Roaster
Core poster for viral shaming posts with rate limiting and batch processing.
"""

import asyncio
import json
import logging
import os
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime, timedelta
import tweepy
from dotenv import load_dotenv

from roast_templates import generate_roast_text

logger = logging.getLogger(__name__)


class Roaster:
    """
    Roaster for posting viral shaming tweets with rate limiting.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        access_token: Optional[str] = None,
        access_token_secret: Optional[str] = None,
        bearer_token: Optional[str] = None,
        daily_limit: int = 50,
        post_interval: float = 60.0  # seconds between posts
    ):
        """
        Initialize roaster with X (Twitter) API credentials.
        
        Args:
            api_key: X API key
            api_secret: X API secret
            access_token: X access token
            access_token_secret: X access token secret
            bearer_token: X bearer token (optional, for v2 API)
            daily_limit: Maximum posts per day (default: 50)
            post_interval: Minimum seconds between posts (default: 60)
        """
        load_dotenv()
        
        self.api_key = api_key or os.getenv("X_API_KEY")
        self.api_secret = api_secret or os.getenv("X_API_SECRET")
        self.access_token = access_token or os.getenv("X_ACCESS_TOKEN")
        self.access_token_secret = access_token_secret or os.getenv("X_ACCESS_TOKEN_SECRET")
        self.bearer_token = bearer_token or os.getenv("X_BEARER_TOKEN")
        
        self.daily_limit = daily_limit
        self.post_interval = post_interval
        self.posted_today = 0
        self.last_post_time = None
        self.posted_roasts = set()  # Track posted roast IDs
        
        # Initialize Tweepy client
        if self.api_key and self.api_secret and self.access_token and self.access_token_secret:
            try:
                self.client = tweepy.Client(
                    bearer_token=self.bearer_token,
                    consumer_key=self.api_key,
                    consumer_secret=self.api_secret,
                    access_token=self.access_token,
                    access_token_secret=self.access_token_secret,
                    wait_on_rate_limit=True
                )
                logger.info("Tweepy client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Tweepy client: {e}")
                self.client = None
        else:
            logger.warning("X API credentials not found")
            self.client = None
        
        # Load posted roasts history
        self.load_posted_history()
    
    def load_posted_history(self, history_file: str = "./results/posted_roasts.json"):
        """
        Load history of posted roasts to avoid duplicates.
        
        Args:
            history_file: Path to posted roasts history file
        """
        history_path = Path(history_file)
        if history_path.exists():
            try:
                with open(history_path, 'r') as f:
                    data = json.load(f)
                    self.posted_roasts = set(data.get("posted_roasts", []))
                    self.posted_today = data.get("posted_today", 0)
                    last_post_date = data.get("last_post_date")
                    if last_post_date:
                        # Reset daily count if last post was yesterday
                        last_date = datetime.fromisoformat(last_post_date)
                        if last_date.date() < datetime.now().date():
                            self.posted_today = 0
                    logger.info(f"Loaded {len(self.posted_roasts)} posted roasts from history")
            except Exception as e:
                logger.error(f"Failed to load posted history: {e}")
    
    def save_posted_history(self, history_file: str = "./results/posted_roasts.json"):
        """
        Save posted roasts history.
        
        Args:
            history_file: Path to posted roasts history file
        """
        history_path = Path(history_file)
        history_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            data = {
                "posted_roasts": list(self.posted_roasts),
                "posted_today": self.posted_today,
                "last_post_date": datetime.now().isoformat() if self.last_post_time else None
            }
            with open(history_path, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Saved posted history: {len(self.posted_roasts)} roasts")
        except Exception as e:
            logger.error(f"Failed to save posted history: {e}")
    
    def can_post(self) -> bool:
        """
        Check if we can post (rate limit and daily limit).
        
        Returns:
            True if we can post, False otherwise
        """
        # Check daily limit
        if self.posted_today >= self.daily_limit:
            logger.warning(f"Daily limit reached: {self.posted_today}/{self.daily_limit}")
            return False
        
        # Check post interval
        if self.last_post_time:
            time_since_last = (datetime.now() - self.last_post_time).total_seconds()
            if time_since_last < self.post_interval:
                logger.debug(f"Post interval not met: {time_since_last:.1f}s < {self.post_interval}s")
                return False
        
        return True
    
    async def post_roast(
        self,
        roast_data: Dict[str, Any],
        media_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Post a single roast to X (Twitter).
        
        Args:
            roast_data: Roast data dictionary with metrics and roast_text
            media_path: Optional path to media file (video/image)
            
        Returns:
            Dictionary with post result
        """
        if not self.client:
            return {
                "success": False,
                "error": "Tweepy client not initialized"
            }
        
        if not self.can_post():
            return {
                "success": False,
                "error": "Rate limit or daily limit reached"
            }
        
        # Generate roast text if not provided
        if "roast_text" not in roast_data:
            roast_info = generate_roast_text(roast_data.get("metrics", roast_data))
            roast_text = roast_info["roast_text"]
        else:
            roast_text = roast_data["roast_text"]
        
        # Check if already posted
        roast_id = roast_data.get("prompt_id") or roast_data.get("video_url", "")
        if roast_id in self.posted_roasts:
            logger.info(f"Roast already posted: {roast_id}")
            return {
                "success": False,
                "error": "Roast already posted",
                "roast_id": roast_id
            }
        
        try:
            # Post tweet
            if media_path and Path(media_path).exists():
                # Upload media first
                media_api = tweepy.API(
                    tweepy.OAuth1UserHandler(
                        self.api_key, self.api_secret,
                        self.access_token, self.access_token_secret
                    )
                )
                media = media_api.media_upload(media_path)
                response = self.client.create_tweet(
                    text=roast_text,
                    media_ids=[media.media_id]
                )
            else:
                response = self.client.create_tweet(text=roast_text)
            
            # Update tracking
            self.posted_roasts.add(roast_id)
            self.posted_today += 1
            self.last_post_time = datetime.now()
            
            # Save history
            self.save_posted_history()
            
            logger.info(f"Posted roast: {roast_text[:50]}...")
            
            return {
                "success": True,
                "tweet_id": response.data["id"],
                "roast_text": roast_text,
                "roast_id": roast_id,
                "posted_at": datetime.now().isoformat()
            }
            
        except tweepy.TooManyRequests:
            logger.error("Rate limit exceeded")
            return {
                "success": False,
                "error": "Rate limit exceeded"
            }
        except Exception as e:
            logger.error(f"Failed to post roast: {e}")
            return {
                "success": False,
                "error": str(e),
                "roast_text": roast_text
            }
    
    async def post_roast_batch(
        self,
        roasts: List[Dict[str, Any]],
        max_posts: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Post batch of roasts with rate limiting.
        
        Args:
            roasts: List of roast data dictionaries
            max_posts: Maximum number of posts (None = use daily limit)
            
        Returns:
            List of post results
        """
        if max_posts is None:
            max_posts = self.daily_limit - self.posted_today
        
        max_posts = min(max_posts, len(roasts))
        
        logger.info(f"Posting batch: {max_posts} roasts")
        
        results = []
        posted_count = 0
        
        for roast in roasts:
            if posted_count >= max_posts:
                break
            
            # Wait for post interval
            if self.last_post_time:
                time_since_last = (datetime.now() - self.last_post_time).total_seconds()
                if time_since_last < self.post_interval:
                    await asyncio.sleep(self.post_interval - time_since_last)
            
            # Post roast
            result = await self.post_roast(roast)
            results.append(result)
            
            if result.get("success"):
                posted_count += 1
            
            # Small delay between posts
            await asyncio.sleep(1.0)
        
        logger.info(f"Batch posting complete: {posted_count}/{max_posts} posted")
        return results
    
    def load_roasts_from_json(
        self,
        roasts_file: str = "./results/roasts.json"
    ) -> List[Dict[str, Any]]:
        """
        Load roasts from Phase 3 JSON file.
        
        Args:
            roasts_file: Path to roasts.json file
            
        Returns:
            List of roast data dictionaries
        """
        roasts_path = Path(roasts_file)
        if not roasts_path.exists():
            logger.error(f"Roasts file not found: {roasts_file}")
            return []
        
        try:
            with open(roasts_path, 'r') as f:
                roasts = json.load(f)
            logger.info(f"Loaded {len(roasts)} roasts from {roasts_file}")
            return roasts
        except Exception as e:
            logger.error(f"Failed to load roasts: {e}")
            return []


async def main():
    """Test roaster."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Initialize roaster
    roaster = Roaster(daily_limit=50, post_interval=60.0)
    
    # Load roasts
    roasts = roaster.load_roasts_from_json("./results/roasts.json")
    
    if not roasts:
        logger.warning("No roasts to post")
        return
    
    # Generate roast texts
    enhanced_roasts = []
    for roast in roasts[:5]:  # Test with first 5
        roast_info = generate_roast_text(roast)
        enhanced_roasts.append({
            **roast,
            "roast_text": roast_info["roast_text"],
            "defect_type": roast_info["defect_type"]
        })
    
    # Post batch (test mode - set max_posts to 1 for testing)
    results = await roaster.post_roast_batch(enhanced_roasts, max_posts=1)
    
    logger.info(f"Posting results: {results}")


if __name__ == "__main__":
    asyncio.run(main())

