#!/usr/bin/env python3
"""
Grok Video Torture Chamber - Phase 3: Result Processor
Batch process Phase 2 bomber outputs, flag roasts, and export to CSV.
"""

import asyncio
import csv
import logging
import os
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime
import json

from detector import (
    analyze_video_async,
    MeltDetector,
    analyze_video,
    extract_frames
)
from analysis_utils import (
    calculate_coherence_score,
    detect_trajectory_inconsistency,
    calculate_overall_quality_score,
    flag_roast,
    calculate_metrics_summary
)

logger = logging.getLogger(__name__)


class ResultProcessor:
    """
    Processor for batch analysis of Phase 2 bomber results.
    """
    
    def __init__(
        self,
        max_concurrent: int = 10,
        warp_threshold: float = 50.0,
        melt_threshold: float = 0.7,
        melt_deform_threshold: float = 0.3,
        roast_threshold: float = 5.0,
        temp_dir: str = "./temp"
    ):
        """
        Initialize result processor.
        
        Args:
            max_concurrent: Maximum concurrent video analyses
            warp_threshold: Warp detection threshold
            melt_threshold: Melt detection confidence threshold
            melt_deform_threshold: Melt deformation rate threshold
            roast_threshold: Score threshold for roasting
            temp_dir: Temporary directory for video downloads
        """
        self.max_concurrent = max_concurrent
        self.warp_threshold = warp_threshold
        self.melt_threshold = melt_threshold
        self.melt_deform_threshold = melt_deform_threshold
        self.roast_threshold = roast_threshold
        self.temp_dir = temp_dir
        self.semaphore = asyncio.Semaphore(max_concurrent)
        
        # Initialize melt detector (shared across analyses)
        self.melt_detector = MeltDetector()
        
        # Create temp directory
        Path(temp_dir).mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Result processor initialized: {max_concurrent} concurrent analyses")
    
    async def _analyze_single_result(
        self,
        result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze a single Phase 2 result.
        
        Args:
            result: Phase 2 result dictionary with video_url, prompt, metadata
            
        Returns:
            Enhanced result dictionary with analysis metrics
        """
        async with self.semaphore:
            video_url = result.get("video_url")
            prompt = result.get("prompt", "")
            metadata = result.get("metadata", {})
            prompt_id = result.get("prompt_id") or result.get("worker_id")
            
            if not video_url:
                return {
                    **result,
                    "analysis_status": "error",
                    "error": "No video URL"
                }
            
            try:
                # Analyze video
                analysis = await analyze_video_async(
                    video_url,
                    warp_threshold=self.warp_threshold,
                    melt_threshold=self.melt_threshold,
                    melt_deform_threshold=self.melt_deform_threshold,
                    temp_dir=self.temp_dir
                )
                
                if analysis.get("status") != "success":
                    return {
                        **result,
                        "analysis_status": "error",
                        "error": analysis.get("error", "Analysis failed")
                    }
                
                # Download video for additional metrics (if needed)
                # For now, we'll use the analysis results directly
                
                # Calculate coherence and trajectory (requires frames)
                # Note: This requires downloading the video, which is expensive
                # For now, we'll skip these and use warp/melt scores
                
                # Calculate overall quality score
                overall_score = calculate_overall_quality_score(
                    warp_score=analysis.get("warp_score", 0.0),
                    melt_rate=analysis.get("melt_rate", 0.0),
                    coherence_score=50.0,  # Default if not calculated
                    trajectory_score=50.0  # Default if not calculated
                )
                
                # Flag for roasting
                should_roast = flag_roast(
                    overall_score=overall_score,
                    warp_score=analysis.get("warp_score", 0.0),
                    melt_rate=analysis.get("melt_rate", 0.0),
                    roast_threshold=self.roast_threshold
                )
                
                # Combine results
                enhanced_result = {
                    **result,
                    "analysis_status": "success",
                    "warp_score": analysis.get("warp_score", 0.0),
                    "warp_rate": analysis.get("warp_rate", 0.0),
                    "is_warped": analysis.get("is_warped", False),
                    "melt_rate": analysis.get("melt_rate", 0.0),
                    "melt_score": analysis.get("melt_score", 0.0),
                    "is_melted": analysis.get("is_melted", False),
                    "overall_score": overall_score,
                    "should_roast": should_roast,
                    "defect_count": analysis.get("defect_count", 0),
                    "frame_count": analysis.get("frame_count", 0),
                    "analyzed_at": datetime.now().isoformat()
                }
                
                return enhanced_result
                
            except Exception as e:
                logger.error(f"Analysis failed for {video_url}: {e}")
                return {
                    **result,
                    "analysis_status": "error",
                    "error": str(e)
                }
    
    async def process_batch(
        self,
        results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Process batch of Phase 2 results.
        
        Args:
            results: List of Phase 2 result dictionaries
            
        Returns:
            List of enhanced result dictionaries with analysis metrics
        """
        logger.info(f"Processing batch: {len(results)} results")
        
        # Filter successful results
        successful_results = [
            r for r in results
            if r.get("status") == "success" and r.get("video_url")
        ]
        
        logger.info(f"Analyzing {len(successful_results)} successful results")
        
        # Create analysis tasks
        tasks = [
            self._analyze_single_result(result)
            for result in successful_results
        ]
        
        # Execute analyses
        analyzed_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        processed_results = []
        for i, result in enumerate(analyzed_results):
            if isinstance(result, Exception):
                logger.error(f"Analysis task exception: {result}")
                processed_results.append({
                    **successful_results[i],
                    "analysis_status": "error",
                    "error": str(result)
                })
            else:
                processed_results.append(result)
        
        # Add failed results back
        failed_results = [
            {**r, "analysis_status": "skipped", "reason": "No video URL or failed status"}
            for r in results
            if r.get("status") != "success" or not r.get("video_url")
        ]
        
        all_results = processed_results + failed_results
        
        logger.info(f"Batch processing complete: {len(all_results)} results")
        return all_results
    
    def export_to_csv(
        self,
        results: List[Dict[str, Any]],
        output_path: str = "./results/analysis_results.csv"
    ) -> str:
        """
        Export analysis results to CSV file.
        
        Args:
            results: List of analyzed result dictionaries
            output_path: Path to output CSV file
            
        Returns:
            Path to exported CSV file
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Define CSV columns
        columns = [
            "prompt_id",
            "prompt",
            "video_url",
            "analysis_status",
            "warp_score",
            "warp_rate",
            "is_warped",
            "melt_rate",
            "melt_score",
            "is_melted",
            "overall_score",
            "should_roast",
            "defect_count",
            "frame_count",
            "analyzed_at",
            "error"
        ]
        
        # Write CSV
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writeheader()
            
            for result in results:
                row = {col: result.get(col, "") for col in columns}
                writer.writerow(row)
        
        logger.info(f"Exported {len(results)} results to {output_path}")
        return str(output_file)
    
    def export_roasts(
        self,
        results: List[Dict[str, Any]],
        output_path: str = "./results/roasts.json"
    ) -> str:
        """
        Export roast-flagged results to JSON file.
        
        Args:
            results: List of analyzed result dictionaries
            output_path: Path to output JSON file
            
        Returns:
            Path to exported JSON file
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Filter roast-flagged results
        roasts = [
            r for r in results
            if r.get("should_roast", False)
        ]
        
        # Export to JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(roasts, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Exported {len(roasts)} roasts to {output_path}")
        return str(output_file)
    
    def generate_summary(
        self,
        results: List[Dict[str, Any]],
        output_path: str = "./results/summary.json"
    ) -> Dict[str, Any]:
        """
        Generate summary statistics from analysis results.
        
        Args:
            results: List of analyzed result dictionaries
            output_path: Path to output summary JSON file
            
        Returns:
            Summary statistics dictionary
        """
        summary = calculate_metrics_summary(results)
        
        # Add timestamp
        summary["generated_at"] = datetime.now().isoformat()
        
        # Export to JSON
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Generated summary: {summary}")
        return summary


async def process_phase2_results(
    results: List[Dict[str, Any]],
    output_dir: str = "./results",
    max_concurrent: int = 10,
    roast_threshold: float = 5.0
) -> Dict[str, Any]:
    """
    Process Phase 2 bomber results with full analysis pipeline.
    
    Args:
        results: List of Phase 2 result dictionaries
        output_dir: Output directory for results
        max_concurrent: Maximum concurrent analyses
        roast_threshold: Score threshold for roasting
        
    Returns:
        Dictionary with processing results and file paths
    """
    # Initialize processor
    processor = ResultProcessor(
        max_concurrent=max_concurrent,
        roast_threshold=roast_threshold
    )
    
    # Process batch
    analyzed_results = await processor.process_batch(results)
    
    # Export results
    csv_path = processor.export_to_csv(
        analyzed_results,
        output_path=f"{output_dir}/analysis_results.csv"
    )
    
    roast_path = processor.export_roasts(
        analyzed_results,
        output_path=f"{output_dir}/roasts.json"
    )
    
    summary = processor.generate_summary(
        analyzed_results,
        output_path=f"{output_dir}/summary.json"
    )
    
    return {
        "total_analyzed": len(analyzed_results),
        "roast_count": summary.get("roast_count", 0),
        "csv_path": csv_path,
        "roast_path": roast_path,
        "summary_path": f"{output_dir}/summary.json",
        "summary": summary
    }


async def main():
    """Test result processor."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Example Phase 2 results
    test_results = [
        {
            "prompt_id": 0,
            "prompt": "samurai vs T-rex zero-G flips --camera dolly+orbit",
            "video_url": "https://example.com/video1.mp4",
            "status": "success",
            "metadata": {"base": "samurai vs T-rex"}
        }
    ]
    
    # Process results
    result = await process_phase2_results(
        test_results,
        output_dir="./results",
        max_concurrent=2
    )
    
    logger.info(f"Processing complete: {result}")


if __name__ == "__main__":
    asyncio.run(main())

