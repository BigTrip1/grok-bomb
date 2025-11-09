#!/usr/bin/env python3
"""
Grok Video Torture Chamber - Phase 4: Feedback Submitter
Batch POST to xAI feedback endpoint with scores and analysis notes.
"""

import asyncio
import aiohttp
import logging
import os
from typing import List, Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


# xAI Feedback API endpoint
FEEDBACK_API_URL = "https://api.x.ai/v1/feedback"


class FeedbackSubmitter:
    """
    Submitter for batch feedback to xAI API.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        rate_limit_delay: float = 1.0,
        opt_in_data_share: bool = True
    ):
        """
        Initialize feedback submitter.
        
        Args:
            api_key: xAI API key (Bearer token)
            rate_limit_delay: Delay between requests (seconds)
            opt_in_data_share: Whether to opt-in to data sharing for training
        """
        load_dotenv()
        self.api_key = api_key or os.getenv("XAI_API_KEY")
        self.rate_limit_delay = rate_limit_delay
        self.opt_in_data_share = opt_in_data_share
        
        if not self.api_key:
            logger.warning("xAI API key not found")
    
    async def submit_feedback(
        self,
        score: float,
        note: str,
        priority: str = "normal",
        session: Optional[aiohttp.ClientSession] = None,
        video_url: Optional[str] = None,
        prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Submit single feedback to xAI API.
        
        Args:
            score: Quality score (0-100)
            note: Feedback note/description
            priority: Priority level ('low', 'normal', 'high')
            session: Optional aiohttp session
            video_url: Optional video URL for reference
            prompt: Optional prompt for reference
            
        Returns:
            Dictionary with submission result
        """
        if not self.api_key:
            return {
                "success": False,
                "error": "API key not found"
            }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "score": float(score),
            "note": str(note),
            "priority": priority,
            "opt_in_data_share": self.opt_in_data_share
        }
        
        # Add optional fields
        if video_url:
            payload["video_url"] = video_url
        if prompt:
            payload["prompt"] = prompt
        
        close_session = False
        if session is None:
            session = aiohttp.ClientSession()
            close_session = True
        
        try:
            async with session.post(
                FEEDBACK_API_URL,
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 200 or response.status == 201:
                    result = await response.json()
                    logger.info(f"Feedback submitted: score={score}, priority={priority}")
                    return {
                        "success": True,
                        "score": score,
                        "note": note,
                        "response": result
                    }
                else:
                    error_text = await response.text()
                    logger.error(f"Feedback submission failed: {response.status} - {error_text}")
                    return {
                        "success": False,
                        "error": f"HTTP {response.status}: {error_text}",
                        "score": score,
                        "note": note
                    }
        except asyncio.TimeoutError:
            logger.error("Feedback submission timeout")
            return {
                "success": False,
                "error": "Timeout",
                "score": score,
                "note": note
            }
        except Exception as e:
            logger.error(f"Feedback submission error: {e}")
            return {
                "success": False,
                "error": str(e),
                "score": score,
                "note": note
            }
        finally:
            if close_session:
                await session.close()
    
    async def submit_roast_feedback(
        self,
        roast_data: Dict[str, Any],
        session: Optional[aiohttp.ClientSession] = None
    ) -> Dict[str, Any]:
        """
        Submit feedback for a roast (defect detection result).
        
        Args:
            roast_data: Roast data dictionary with metrics and analysis
            session: Optional aiohttp session
            
        Returns:
            Dictionary with submission result
        """
        # Extract metrics
        overall_score = roast_data.get("overall_score", 0.0)
        warp_score = roast_data.get("warp_score", 0.0)
        melt_rate = roast_data.get("melt_rate", 0.0)
        roast_text = roast_data.get("roast_text", "")
        prompt = roast_data.get("prompt", "")
        video_url = roast_data.get("video_url", "")
        
        # Build feedback note
        if roast_text:
            note = roast_text
        else:
            note = (
                f"Quality analysis: score={overall_score:.1f}, "
                f"warp={warp_score:.1f}, melt_rate={melt_rate:.1%}. "
                f"Defects detected: warp={roast_data.get('is_warped', False)}, "
                f"melt={roast_data.get('is_melted', False)}"
            )
        
        # Determine priority (high for severe defects)
        priority = "high" if (
            overall_score < 10 or
            roast_data.get("is_warped", False) or
            roast_data.get("is_melted", False)
        ) else "normal"
        
        return await self.submit_feedback(
            score=overall_score,
            note=note,
            priority=priority,
            session=session,
            video_url=video_url,
            prompt=prompt
        )
    
    async def submit_batch(
        self,
        roasts: List[Dict[str, Any]],
        max_concurrent: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Submit batch of feedbacks with rate limiting.
        
        Args:
            roasts: List of roast data dictionaries
            max_concurrent: Maximum concurrent submissions
            
        Returns:
            List of submission results
        """
        logger.info(f"Submitting batch: {len(roasts)} feedbacks")
        
        semaphore = asyncio.Semaphore(max_concurrent)
        results = []
        
        async def submit_with_semaphore(roast_data: Dict[str, Any]) -> Dict[str, Any]:
            async with semaphore:
                async with aiohttp.ClientSession() as session:
                    result = await self.submit_roast_feedback(roast_data, session)
                    await asyncio.sleep(self.rate_limit_delay)
                    return result
        
        # Create tasks
        tasks = [submit_with_semaphore(roast) for roast in roasts]
        
        # Execute tasks
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Feedback submission exception: {result}")
                processed_results.append({
                    "success": False,
                    "error": str(result),
                    "roast_index": i
                })
            else:
                processed_results.append(result)
        
        # Count successes
        success_count = sum(1 for r in processed_results if r.get("success"))
        logger.info(f"Batch submission complete: {success_count}/{len(processed_results)} successful")
        
        return processed_results
    
    def export_submission_results(
        self,
        results: List[Dict[str, Any]],
        output_path: str = "./results/feedback_submissions.json"
    ) -> str:
        """
        Export submission results to JSON file.
        
        Args:
            results: List of submission result dictionaries
            output_path: Path to output JSON file
            
        Returns:
            Path to exported file
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            import json
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            logger.info(f"Exported {len(results)} submission results to {output_path}")
            return str(output_file)
        except Exception as e:
            logger.error(f"Failed to export submission results: {e}")
            return ""


async def main():
    """Test feedback submitter."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Initialize submitter
    submitter = FeedbackSubmitter(rate_limit_delay=1.0, opt_in_data_share=True)
    
    # Example roast data
    test_roasts = [
        {
            "overall_score": 5.0,
            "warp_score": 75.0,
            "melt_rate": 0.4,
            "is_warped": True,
            "is_melted": True,
            "roast_text": "@xai @grok Warp score 75.0—needs improvement",
            "prompt": "samurai vs T-rex",
            "video_url": "https://example.com/video1.mp4"
        }
    ]
    
    # Submit batch
    results = await submitter.submit_batch(test_roasts, max_concurrent=2)
    
    # Export results
    submitter.export_submission_results(results, "./results/feedback_submissions.json")
    
    logger.info(f"Submission results: {results}")


if __name__ == "__main__":
    asyncio.run(main())

