#!/usr/bin/env python3
"""
Grok Video Torture Chamber - Phase 3: Analysis Utilities
Quality metrics functions for coherence, trajectory consistency, and PSNR.
"""

import cv2
import numpy as np
import logging
from typing import List, Dict, Any, Optional, Tuple
from skimage.metrics import structural_similarity as ssim_func
from skimage.metrics import peak_signal_noise_ratio as psnr_func

logger = logging.getLogger(__name__)


def calculate_psnr(
    frame1: np.ndarray,
    frame2: np.ndarray
) -> float:
    """
    Calculate Peak Signal-to-Noise Ratio (PSNR) between two frames.
    
    Args:
        frame1: First frame (BGR format)
        frame2: Second frame (BGR format)
        
    Returns:
        PSNR value in dB
    """
    try:
        # Convert to grayscale for PSNR calculation
        gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
        
        # Calculate PSNR
        psnr_value = psnr_func(gray1, gray2, data_range=255)
        return float(psnr_value)
        
    except Exception as e:
        logger.error(f"PSNR calculation failed: {e}")
        return 0.0


def calculate_ssim(
    frame1: np.ndarray,
    frame2: np.ndarray
) -> float:
    """
    Calculate Structural Similarity Index (SSIM) between two frames.
    
    Args:
        frame1: First frame (BGR format)
        frame2: Second frame (BGR format)
        
    Returns:
        SSIM value (0-1, higher is better)
    """
    try:
        # Convert to grayscale for SSIM calculation
        gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
        
        # Calculate SSIM
        ssim_value = ssim_func(gray1, gray2, data_range=255)
        return float(ssim_value)
        
    except Exception as e:
        logger.error(f"SSIM calculation failed: {e}")
        return 0.0


def calculate_coherence_score(
    frames: List[np.ndarray]
) -> Dict[str, Any]:
    """
    Calculate coherence score using PSNR and SSIM across frames.
    
    Args:
        frames: List of video frames (BGR format)
        
    Returns:
        Dict with coherence metrics
    """
    if len(frames) < 2:
        return {
            "coherence_score": 0.0,
            "avg_psnr": 0.0,
            "avg_ssim": 0.0,
            "error": "Insufficient frames"
        }
    
    try:
        psnr_values = []
        ssim_values = []
        
        for i in range(len(frames) - 1):
            psnr_val = calculate_psnr(frames[i], frames[i + 1])
            ssim_val = calculate_ssim(frames[i], frames[i + 1])
            
            psnr_values.append(psnr_val)
            ssim_values.append(ssim_val)
        
        avg_psnr = sum(psnr_values) / len(psnr_values) if psnr_values else 0.0
        avg_ssim = sum(ssim_values) / len(ssim_values) if ssim_values else 0.0
        
        # Combined coherence score (0-100, higher is better)
        coherence_score = (avg_psnr / 50.0 + avg_ssim) * 50.0
        
        return {
            "coherence_score": float(coherence_score),
            "avg_psnr": float(avg_psnr),
            "avg_ssim": float(avg_ssim),
            "psnr_values": psnr_values,
            "ssim_values": ssim_values
        }
        
    except Exception as e:
        logger.error(f"Coherence calculation failed: {e}")
        return {
            "coherence_score": 0.0,
            "avg_psnr": 0.0,
            "avg_ssim": 0.0,
            "error": str(e)
        }


def detect_trajectory_inconsistency(
    frames: List[np.ndarray],
    threshold: float = 10.0
) -> Dict[str, Any]:
    """
    Detect trajectory inconsistency using optical flow and tracking.
    
    Args:
        frames: List of video frames (BGR format)
        threshold: Inconsistency threshold
        
    Returns:
        Dict with trajectory metrics
    """
    if len(frames) < 3:
        return {
            "trajectory_score": 0.0,
            "inconsistency_rate": 0.0,
            "is_inconsistent": False,
            "error": "Insufficient frames"
        }
    
    try:
        # Convert to grayscale
        gray_frames = [cv2.cvtColor(f, cv2.COLOR_BGR2GRAY) for f in frames]
        
        # Detect keypoints in first frame
        detector = cv2.FastFeatureDetector_create()
        keypoints = detector.detect(gray_frames[0])
        
        if len(keypoints) == 0:
            return {
                "trajectory_score": 0.0,
                "inconsistency_rate": 0.0,
                "is_inconsistent": False,
                "error": "No keypoints detected"
            }
        
        # Convert keypoints to points
        points = np.array([kp.pt for kp in keypoints], dtype=np.float32).reshape(-1, 1, 2)
        
        # Track points across frames
        trajectories = []
        prev_points = points
        prev_gray = gray_frames[0]
        
        for gray in gray_frames[1:]:
            # Calculate optical flow
            next_points, status, error = cv2.calcOpticalFlowPyrLK(
                prev_gray, gray, prev_points, None
            )
            
            # Filter good points
            good_points = next_points[status == 1]
            
            if len(good_points) > 0:
                # Calculate displacement
                displacements = np.linalg.norm(
                    good_points - prev_points[status == 1],
                    axis=1
                )
                trajectories.append(displacements)
            
            prev_points = next_points[status == 1].reshape(-1, 1, 2)
            prev_gray = gray
        
        if not trajectories:
            return {
                "trajectory_score": 0.0,
                "inconsistency_rate": 0.0,
                "is_inconsistent": False,
                "error": "No trajectories tracked"
            }
        
        # Calculate inconsistency
        inconsistencies = []
        for i in range(len(trajectories) - 1):
            if len(trajectories[i]) > 0 and len(trajectories[i + 1]) > 0:
                # Compare trajectory changes
                avg_displacement_1 = np.mean(trajectories[i])
                avg_displacement_2 = np.mean(trajectories[i + 1])
                
                # Check for sudden changes (inconsistency)
                change = abs(avg_displacement_2 - avg_displacement_1)
                inconsistencies.append(change > threshold)
        
        inconsistency_rate = (
            sum(inconsistencies) / len(inconsistencies)
            if inconsistencies else 0.0
        )
        
        # Trajectory score (0-100, higher is better)
        trajectory_score = (1.0 - inconsistency_rate) * 100.0
        
        return {
            "trajectory_score": float(trajectory_score),
            "inconsistency_rate": float(inconsistency_rate),
            "is_inconsistent": inconsistency_rate > 0.3,
            "trajectories": [len(t) for t in trajectories]
        }
        
    except Exception as e:
        logger.error(f"Trajectory detection failed: {e}")
        return {
            "trajectory_score": 0.0,
            "inconsistency_rate": 0.0,
            "is_inconsistent": False,
            "error": str(e)
        }


def calculate_overall_quality_score(
    warp_score: float,
    melt_rate: float,
    coherence_score: float,
    trajectory_score: float,
    weights: Optional[Dict[str, float]] = None
) -> float:
    """
    Calculate overall quality score from individual metrics.
    
    Args:
        warp_score: Warp score (lower is better)
        melt_rate: Melt rate (0-1, lower is better)
        coherence_score: Coherence score (0-100, higher is better)
        trajectory_score: Trajectory score (0-100, higher is better)
        weights: Optional weights for each metric
        
    Returns:
        Overall quality score (0-100, higher is better)
    """
    if weights is None:
        weights = {
            "warp": 0.3,
            "melt": 0.3,
            "coherence": 0.2,
            "trajectory": 0.2
        }
    
    # Normalize warp score (assume max warp_score = 200)
    normalized_warp = max(0, 100 - (warp_score / 200.0 * 100))
    
    # Normalize melt rate
    normalized_melt = (1.0 - melt_rate) * 100
    
    # Calculate weighted score
    overall_score = (
        normalized_warp * weights["warp"] +
        normalized_melt * weights["melt"] +
        coherence_score * weights["coherence"] +
        trajectory_score * weights["trajectory"]
    )
    
    return float(overall_score)


def flag_roast(
    overall_score: float,
    warp_score: float,
    melt_rate: float,
    roast_threshold: float = 5.0
) -> bool:
    """
    Flag video for roasting based on quality metrics.
    
    Args:
        overall_score: Overall quality score (0-100)
        warp_score: Warp score
        melt_rate: Melt rate (0-1)
        roast_threshold: Score threshold for roasting
        
    Returns:
        True if video should be roasted
    """
    # Roast if overall score is low or specific defects are severe
    if overall_score < roast_threshold:
        return True
    
    # Roast if severe warping (warp_score > 100)
    if warp_score > 100.0:
        return True
    
    # Roast if severe melting (melt_rate > 0.5)
    if melt_rate > 0.5:
        return True
    
    return False


def calculate_metrics_summary(
    analysis_results: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Calculate summary statistics from analysis results.
    
    Args:
        analysis_results: List of analysis result dictionaries
        
    Returns:
        Summary statistics dictionary
    """
    if not analysis_results:
        return {
            "total": 0,
            "errors": 0
        }
    
    successful = [r for r in analysis_results if r.get("status") == "success"]
    
    if not successful:
        return {
            "total": len(analysis_results),
            "successful": 0,
            "errors": len(analysis_results)
        }
    
    warp_scores = [r.get("warp_score", 0.0) for r in successful]
    melt_rates = [r.get("melt_rate", 0.0) for r in successful]
    coherence_scores = [r.get("coherence_score", 0.0) for r in successful]
    trajectory_scores = [r.get("trajectory_score", 0.0) for r in successful]
    overall_scores = [r.get("overall_score", 0.0) for r in successful]
    
    return {
        "total": len(analysis_results),
        "successful": len(successful),
        "errors": len(analysis_results) - len(successful),
        "avg_warp_score": sum(warp_scores) / len(warp_scores) if warp_scores else 0.0,
        "avg_melt_rate": sum(melt_rates) / len(melt_rates) if melt_rates else 0.0,
        "avg_coherence_score": sum(coherence_scores) / len(coherence_scores) if coherence_scores else 0.0,
        "avg_trajectory_score": sum(trajectory_scores) / len(trajectory_scores) if trajectory_scores else 0.0,
        "avg_overall_score": sum(overall_scores) / len(overall_scores) if overall_scores else 0.0,
        "roast_count": sum(1 for r in successful if r.get("should_roast", False)),
        "warp_count": sum(1 for r in successful if r.get("is_warped", False)),
        "melt_count": sum(1 for r in successful if r.get("is_melted", False))
    }

