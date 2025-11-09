#!/usr/bin/env python3
"""
Grok Video Torture Chamber - Master Pipeline Runner
End-to-end execution of Phases 1-4 with progress tracking.
"""

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Phase imports
from variants_generator import create_adversarial_batch
from batch_runner import BatchRunner
from result_processor import process_phase2_results
from roaster import Roaster
from feedback_submitter import FeedbackSubmitter
from roast_templates import generate_roast_text

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class PipelineRunner:
    """
    Master pipeline runner for end-to-end execution.
    """
    
    def __init__(
        self,
        output_dir: str = "./results",
        temp_dir: str = "./temp"
    ):
        """
        Initialize pipeline runner.
        
        Args:
            output_dir: Output directory for results
            temp_dir: Temporary directory for downloads
        """
        load_dotenv()
        self.output_dir = Path(output_dir)
        self.temp_dir = Path(temp_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Load API keys
        self.xai_api_key = os.getenv("XAI_API_KEY")
        if not self.xai_api_key:
            raise ValueError("XAI_API_KEY not found in environment")
    
    async def run_phase2(
        self,
        base_prompts: list,
        total_target: int = 10000,
        max_concurrent: int = 100,
        variants_per_base: int = 100
    ) -> list:
        """
        Run Phase 2: Prompt Bombing.
        
        Args:
            base_prompts: List of base prompts
            total_target: Target number of variants
            max_concurrent: Maximum concurrent workers
            variants_per_base: Variants per base prompt
            
        Returns:
            List of Phase 2 results
        """
        logger.info("=" * 60)
        logger.info("PHASE 2: Prompt Bombing")
        logger.info("=" * 60)
        
        # Generate adversarial batch
        logger.info(f"Generating {total_target} adversarial variants...")
        variants = create_adversarial_batch(
            base_prompts=base_prompts,
            variants_per_base=variants_per_base,
            total_target=total_target
        )
        logger.info(f"Generated {len(variants)} variants")
        
        # Run batch generation
        logger.info(f"Generating videos with {max_concurrent} concurrent workers...")
        runner = BatchRunner(
            api_key=self.xai_api_key,
            max_concurrent=max_concurrent
        )
        results = await runner.run_batch(variants)
        
        # Save results
        results_file = self.output_dir / "phase2_results.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        logger.info(f"Phase 2 results saved to {results_file}")
        
        # Statistics
        success_count = sum(1 for r in results if r.get("status") == "success")
        logger.info(f"Phase 2 complete: {success_count}/{len(results)} successful")
        
        return results
    
    async def run_phase3(
        self,
        phase2_results: list,
        max_concurrent: int = 10,
        roast_threshold: float = 5.0
    ) -> dict:
        """
        Run Phase 3: Defect Detection.
        
        Args:
            phase2_results: Phase 2 results
            max_concurrent: Maximum concurrent analyses
            roast_threshold: Score threshold for roasting
            
        Returns:
            Analysis results dictionary
        """
        logger.info("=" * 60)
        logger.info("PHASE 3: Defect Detection")
        logger.info("=" * 60)
        
        # Process results
        analysis_results = await process_phase2_results(
            results=phase2_results,
            output_dir=str(self.output_dir),
            max_concurrent=max_concurrent,
            roast_threshold=roast_threshold
        )
        
        logger.info(f"Phase 3 complete: {analysis_results['roast_count']} roasts flagged")
        return analysis_results
    
    async def run_phase4(
        self,
        max_posts: int = 50,
        max_feedback_concurrent: int = 5
    ) -> dict:
        """
        Run Phase 4: Auto-Roasting.
        
        Args:
            max_posts: Maximum posts to X
            max_feedback_concurrent: Maximum concurrent feedback submissions
            
        Returns:
            Phase 4 results dictionary
        """
        logger.info("=" * 60)
        logger.info("PHASE 4: Auto-Roasting")
        logger.info("=" * 60)
        
        # Load roasts
        roasts_file = self.output_dir / "roasts.json"
        if not roasts_file.exists():
            logger.error(f"Roasts file not found: {roasts_file}")
            return {"error": "Roasts file not found"}
        
        with open(roasts_file, 'r') as f:
            roasts = json.load(f)
        
        logger.info(f"Loaded {len(roasts)} roasts")
        
        # Generate roast texts
        logger.info("Generating roast texts...")
        enhanced_roasts = []
        for roast in roasts:
            roast_info = generate_roast_text(roast)
            enhanced_roasts.append({
                **roast,
                "roast_text": roast_info["roast_text"],
                "defect_type": roast_info["defect_type"]
            })
        
        # Post to X
        logger.info(f"Posting {min(max_posts, len(enhanced_roasts))} roasts to X...")
        roaster = Roaster(daily_limit=50, post_interval=60.0)
        post_results = await roaster.post_roast_batch(enhanced_roasts, max_posts=max_posts)
        
        # Submit feedback
        logger.info("Submitting feedback to xAI...")
        submitter = FeedbackSubmitter(opt_in_data_share=True)
        feedback_results = await submitter.submit_batch(roasts, max_concurrent=max_feedback_concurrent)
        
        # Save results
        phase4_results = {
            "posts": post_results,
            "feedback": feedback_results,
            "posted_count": sum(1 for r in post_results if r.get("success")),
            "feedback_count": sum(1 for r in feedback_results if r.get("success"))
        }
        
        results_file = self.output_dir / "phase4_results.json"
        with open(results_file, 'w') as f:
            json.dump(phase4_results, f, indent=2)
        
        logger.info(f"Phase 4 complete: {phase4_results['posted_count']} posted, {phase4_results['feedback_count']} feedback submitted")
        return phase4_results
    
    async def run_full_pipeline(
        self,
        base_prompts: list,
        phase2_config: Optional[Dict[str, Any]] = None,
        phase3_config: Optional[Dict[str, Any]] = None,
        phase4_config: Optional[Dict[str, Any]] = None,
        skip_phase2: bool = False,
        skip_phase3: bool = False,
        skip_phase4: bool = False
    ) -> dict:
        """
        Run full pipeline (Phases 2-4).
        
        Args:
            base_prompts: List of base prompts
            phase2_config: Phase 2 configuration
            phase3_config: Phase 3 configuration
            phase4_config: Phase 4 configuration
            skip_phase2: Skip Phase 2 (use existing results)
            skip_phase3: Skip Phase 3 (use existing results)
            skip_phase4: Skip Phase 4
            
        Returns:
            Pipeline results dictionary
        """
        logger.info("=" * 60)
        logger.info("GROK VIDEO TORTURE CHAMBER - FULL PIPELINE")
        logger.info("=" * 60)
        
        # Default configurations
        phase2_config = phase2_config or {
            "total_target": 10000,
            "max_concurrent": 100,
            "variants_per_base": 100
        }
        phase3_config = phase3_config or {
            "max_concurrent": 10,
            "roast_threshold": 5.0
        }
        phase4_config = phase4_config or {
            "max_posts": 50,
            "max_feedback_concurrent": 5
        }
        
        results = {}
        
        # Phase 2: Prompt Bombing
        if not skip_phase2:
            phase2_results = await self.run_phase2(
                base_prompts=base_prompts,
                **phase2_config
            )
            results["phase2"] = phase2_results
        else:
            # Load existing results
            results_file = self.output_dir / "phase2_results.json"
            if results_file.exists():
                with open(results_file, 'r') as f:
                    phase2_results = json.load(f)
                logger.info(f"Loaded existing Phase 2 results: {len(phase2_results)} results")
            else:
                logger.error("Phase 2 results not found and skip_phase2=True")
                return {"error": "Phase 2 results not found"}
        
        # Phase 3: Defect Detection
        if not skip_phase3:
            phase3_results = await self.run_phase3(
                phase2_results=phase2_results,
                **phase3_config
            )
            results["phase3"] = phase3_results
        else:
            logger.info("Skipping Phase 3")
        
        # Phase 4: Auto-Roasting
        if not skip_phase4:
            phase4_results = await self.run_phase4(**phase4_config)
            results["phase4"] = phase4_results
        else:
            logger.info("Skipping Phase 4")
        
        logger.info("=" * 60)
        logger.info("PIPELINE COMPLETE")
        logger.info("=" * 60)
        
        return results


async def main():
    """Main pipeline execution."""
    # Example configuration
    base_prompts = [
        "samurai vs T-rex",
        "cyberpunk cityscape at night",
        "space battle between fleets"
    ]
    
    # Initialize pipeline
    pipeline = PipelineRunner()
    
    # Run full pipeline (adjust configs as needed)
    results = await pipeline.run_full_pipeline(
        base_prompts=base_prompts,
        phase2_config={
            "total_target": 100,  # Start small for testing
            "max_concurrent": 10,
            "variants_per_base": 50
        },
        phase3_config={
            "max_concurrent": 5,
            "roast_threshold": 5.0
        },
        phase4_config={
            "max_posts": 5,  # Start small for testing
            "max_feedback_concurrent": 2
        },
        skip_phase2=False,
        skip_phase3=False,
        skip_phase4=False
    )
    
    logger.info(f"Pipeline results: {results}")


if __name__ == "__main__":
    asyncio.run(main())

