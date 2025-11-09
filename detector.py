#!/usr/bin/env python3
"""
Grok Video Torture Chamber - Phase 3: Defect Detector
Core analyzer with frame extraction, warp detection, and melt detection.
"""

import cv2
import numpy as np
import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import torch
import torchvision.transforms as T
from torchvision.models.detection import fasterrcnn_resnet50_fpn
from moviepy.editor import VideoFileClip
from PIL import Image

logger = logging.getLogger(__name__)


# Device configuration
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
logger.info(f"Using device: {DEVICE}")


def extract_frames(
    video_path: str,
    fps: Optional[float] = None,
    max_frames: Optional[int] = None
) -> List[np.ndarray]:
    """
    Extract frames from video file using MoviePy.
    
    Args:
        video_path: Path to video file
        fps: Target FPS for frame extraction (None = original)
        max_frames: Maximum number of frames to extract (None = all)
        
    Returns:
        List of frames as numpy arrays (BGR format)
    """
    try:
        clip = VideoFileClip(video_path)
        
        # Get target FPS
        target_fps = fps if fps else clip.fps
        frame_interval = clip.fps / target_fps if target_fps else 1.0
        
        frames = []
        frame_count = 0
        
        for i, frame in enumerate(clip.iter_frames(fps=target_fps, dtype='uint8')):
            if max_frames and frame_count >= max_frames:
                break
            
            # Convert RGB to BGR for OpenCV
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            frames.append(frame_bgr)
            frame_count += 1
        
        clip.close()
        
        logger.info(f"Extracted {len(frames)} frames from {video_path}")
        return frames
        
    except Exception as e:
        logger.error(f"Failed to extract frames from {video_path}: {e}")
        return []


def optical_flow_warp(
    frames: List[np.ndarray],
    threshold: float = 50.0
) -> Dict[str, Any]:
    """
    Calculate optical flow warp score using Farneback method.
    
    Args:
        frames: List of video frames (BGR format)
        threshold: Warp threshold (score > threshold = warped)
        
    Returns:
        Dict with warp_score, warp_rate, and is_warped flag
    """
    if len(frames) < 2:
        return {
            "warp_score": 0.0,
            "warp_rate": 0.0,
            "is_warped": False,
            "error": "Insufficient frames"
        }
    
    try:
        # Convert first frame to grayscale
        prev_gray = cv2.cvtColor(frames[0], cv2.COLOR_BGR2GRAY)
        flow_scores = []
        
        for frame in frames[1:]:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Calculate optical flow
            flow = cv2.calcOpticalFlowFarneback(
                prev_gray, gray, None,
                0.5, 3, 15, 3, 5, 1.2, 0
            )
            
            # Calculate flow magnitude (L2 norm)
            magnitude = cv2.norm(flow, cv2.NORM_L2)
            flow_scores.append(magnitude)
            
            prev_gray = gray
        
        # Calculate average warp score
        avg_warp_score = sum(flow_scores) / len(flow_scores) if flow_scores else 0.0
        
        # Calculate warp rate (frames with high flow)
        warp_rate = sum(1 for score in flow_scores if score > threshold) / len(flow_scores)
        
        return {
            "warp_score": float(avg_warp_score),
            "warp_rate": float(warp_rate),
            "is_warped": avg_warp_score > threshold,
            "flow_scores": flow_scores
        }
        
    except Exception as e:
        logger.error(f"Optical flow calculation failed: {e}")
        return {
            "warp_score": 0.0,
            "warp_rate": 0.0,
            "is_warped": False,
            "error": str(e)
        }


class MeltDetector:
    """
    Melt detector using Faster R-CNN for object deformation detection.
    """
    
    def __init__(self, device: Optional[torch.device] = None):
        """
        Initialize melt detector with Faster R-CNN model.
        
        Args:
            device: PyTorch device (default: auto-detect)
        """
        self.device = device if device else DEVICE
        self.model = fasterrcnn_resnet50_fpn(weights="DEFAULT")
        self.model.to(self.device)
        self.model.eval()
        
        # Image preprocessing
        self.transform = T.Compose([T.ToTensor()])
        
        logger.info(f"Melt detector initialized on {self.device}")
    
    def detect_deform(
        self,
        frames: List[np.ndarray],
        threshold: float = 0.7,
        deform_threshold: float = 0.3
    ) -> Dict[str, Any]:
        """
        Detect object deformation (melting) in frames.
        
        Args:
            frames: List of video frames (BGR format)
            threshold: Confidence threshold for object detection
            deform_threshold: Deformation rate threshold (>threshold = melted)
            
        Returns:
            Dict with melt_rate, is_melted flag, and detection scores
        """
        if not frames:
            return {
                "melt_rate": 0.0,
                "is_melted": False,
                "error": "No frames provided"
            }
        
        try:
            scores = []
            
            with torch.no_grad():
                for frame in frames:
                    # Convert BGR to RGB
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frame_pil = Image.fromarray(frame_rgb)
                    
                    # Preprocess
                    frame_tensor = self.transform(frame_pil).to(self.device)
                    
                    # Run inference
                    predictions = self.model([frame_tensor])
                    
                    if len(predictions) > 0 and len(predictions[0]['scores']) > 0:
                        max_score = predictions[0]['scores'].max().item()
                        scores.append(max_score)
                    else:
                        scores.append(0.0)
            
            # Calculate melt rate (frames with low confidence = deformation)
            melt_rate = sum(1 for s in scores if s < threshold) / len(scores)
            avg_score = sum(scores) / len(scores) if scores else 0.0
            
            return {
                "melt_rate": float(melt_rate),
                "melt_score": float(avg_score),
                "is_melted": melt_rate > deform_threshold,
                "detection_scores": scores
            }
            
        except Exception as e:
            logger.error(f"Melt detection failed: {e}")
            return {
                "melt_rate": 0.0,
                "melt_score": 0.0,
                "is_melted": False,
                "error": str(e)
            }


def analyze_video(
    video_path: str,
    warp_threshold: float = 50.0,
    melt_threshold: float = 0.7,
    melt_deform_threshold: float = 0.3,
    fps: Optional[float] = None,
    max_frames: Optional[int] = None,
    melt_detector: Optional[MeltDetector] = None
) -> Dict[str, Any]:
    """
    Analyze video for warping and melting defects.
    
    Args:
        video_path: Path to video file
        warp_threshold: Warp detection threshold
        melt_threshold: Melt detection confidence threshold
        melt_deform_threshold: Melt deformation rate threshold
        fps: Target FPS for frame extraction
        max_frames: Maximum frames to extract
        melt_detector: Optional pre-initialized melt detector
        
    Returns:
        Dict with analysis results
    """
    # Extract frames
    frames = extract_frames(video_path, fps=fps, max_frames=max_frames)
    
    if not frames:
        return {
            "video_path": video_path,
            "status": "error",
            "error": "Failed to extract frames"
        }
    
    # Analyze warping
    warp_result = optical_flow_warp(frames, threshold=warp_threshold)
    
    # Analyze melting
    if melt_detector is None:
        melt_detector = MeltDetector()
    
    melt_result = melt_detector.detect_deform(
        frames,
        threshold=melt_threshold,
        deform_threshold=melt_deform_threshold
    )
    
    # Combine results
    result = {
        "video_path": video_path,
        "status": "success",
        "frame_count": len(frames),
        "warp_score": warp_result.get("warp_score", 0.0),
        "warp_rate": warp_result.get("warp_rate", 0.0),
        "is_warped": warp_result.get("is_warped", False),
        "melt_rate": melt_result.get("melt_rate", 0.0),
        "melt_score": melt_result.get("melt_score", 0.0),
        "is_melted": melt_result.get("is_melted", False),
        "defect_count": sum([
            warp_result.get("is_warped", False),
            melt_result.get("is_melted", False)
        ])
    }
    
    return result


def download_video_for_analysis(
    video_url: str,
    output_path: str = "./temp/video.mp4"
) -> Optional[str]:
    """
    Download video from URL for analysis.
    
    Args:
        video_url: URL of video to download
        output_path: Local path to save video
        
    Returns:
        Path to downloaded video, or None on error
    """
    try:
        from test_api_call import download_video
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        success = download_video(video_url, output_path)
        
        if success:
            return output_path
        else:
            return None
            
    except Exception as e:
        logger.error(f"Failed to download video: {e}")
        return None


async def analyze_video_async(
    video_url: str,
    warp_threshold: float = 50.0,
    melt_threshold: float = 0.7,
    melt_deform_threshold: float = 0.3,
    temp_dir: str = "./temp"
) -> Dict[str, Any]:
    """
    Async wrapper for video analysis (downloads and analyzes).
    
    Args:
        video_url: URL of video to analyze
        warp_threshold: Warp detection threshold
        melt_threshold: Melt detection confidence threshold
        melt_deform_threshold: Melt deformation rate threshold
        temp_dir: Temporary directory for downloads
        
    Returns:
        Dict with analysis results
    """
    import asyncio
    import os
    from pathlib import Path
    
    # Generate temp file path
    video_id = video_url.split("/")[-1].split("?")[0]
    temp_path = Path(temp_dir) / f"{video_id}.mp4"
    temp_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Download video
    downloaded_path = download_video_for_analysis(video_url, str(temp_path))
    
    if not downloaded_path:
        return {
            "video_url": video_url,
            "status": "error",
            "error": "Failed to download video"
        }
    
    # Analyze video
    result = analyze_video(
        downloaded_path,
        warp_threshold=warp_threshold,
        melt_threshold=melt_threshold,
        melt_deform_threshold=melt_deform_threshold
    )
    
    # Add video URL to result
    result["video_url"] = video_url
    
    # Clean up temp file (optional)
    # os.remove(downloaded_path)
    
    return result

