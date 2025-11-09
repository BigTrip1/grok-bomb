#!/usr/bin/env python3
"""
Grok Video Torture Chamber - Phase 4: Roast Templates
Template generators for viral shaming posts with defect metrics.
"""

import random
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)


# X (Twitter) handles
XAI_HANDLE = "@xai"
GROK_HANDLE = "@grok"
HAILUO_HANDLE = "@hailuo_ai"
VEO_HANDLE = "@veo"

# Hashtags
HASHTAGS = [
    "#GrokVideo",
    "#AIVideo",
    "#VideoGeneration",
    "#AIComparison",
    "#VideoQuality"
]


def get_warp_roast_template(
    metrics: Dict[str, Any],
    variant: Optional[int] = None
) -> str:
    """
    Generate warp defect roast template.
    
    Args:
        metrics: Analysis metrics dictionary
        variant: Template variant index (None = random)
        
    Returns:
        Roast text string
    """
    warp_score = metrics.get("warp_score", 0.0)
    warp_rate = metrics.get("warp_rate", 0.0)
    prompt = metrics.get("prompt", "")[:50]  # Truncate for tweet
    
    templates = [
        f"{XAI_HANDLE} {GROK_HANDLE} {HAILUO_HANDLE} Warp score {warp_score:.1f} at 0:07—Hailuo nails physics. Fix or cooked? {HASHTAGS[0]}",
        f"Grok warp rate {warp_rate:.1%} vs Hailuo smooth—physics check failed. {XAI_HANDLE} {HAILUO_HANDLE} {HASHTAGS[0]}",
        f"Warp score {warp_score:.1f} detected. Hailuo crushes this prompt. {XAI_HANDLE} time to step up? {HASHTAGS[0]}",
        f"Grok video warping at {warp_rate:.1%} rate. Hailuo handles this flawlessly. {XAI_HANDLE} {HAILUO_HANDLE} {HASHTAGS[0]}",
        f"Physics violation: warp {warp_score:.1f}. Hailuo wins this round. {XAI_HANDLE} {GROK_HANDLE} {HASHTAGS[0]}",
    ]
    
    if variant is None:
        variant = random.randint(0, len(templates) - 1)
    
    return templates[variant % len(templates)]


def get_melt_roast_template(
    metrics: Dict[str, Any],
    variant: Optional[int] = None
) -> str:
    """
    Generate melt defect roast template.
    
    Args:
        metrics: Analysis metrics dictionary
        variant: Template variant index (None = random)
        
    Returns:
        Roast text string
    """
    melt_rate = metrics.get("melt_rate", 0.0)
    melt_score = metrics.get("melt_score", 0.0)
    prompt = metrics.get("prompt", "")[:50]
    
    templates = [
        f"{XAI_HANDLE} {GROK_HANDLE} {HAILUO_HANDLE} Melt rate {melt_rate:.1%}—objects deforming. Hailuo keeps it clean. {HASHTAGS[0]}",
        f"Object melting detected: {melt_rate:.1%} rate. Hailuo crushes coherence. {XAI_HANDLE} {HAILUO_HANDLE} {HASHTAGS[0]}",
        f"Melt score {melt_score:.2f}—Hailuo handles this better. {XAI_HANDLE} fix the deformations? {HASHTAGS[0]}",
        f"Grok melting at {melt_rate:.1%} vs Hailuo stable. Quality gap is real. {XAI_HANDLE} {GROK_HANDLE} {HASHTAGS[0]}",
        f"Coherence fail: melt rate {melt_rate:.1%}. Hailuo wins again. {XAI_HANDLE} {HAILUO_HANDLE} {HASHTAGS[0]}",
    ]
    
    if variant is None:
        variant = random.randint(0, len(templates) - 1)
    
    return templates[variant % len(templates)]


def get_combined_roast_template(
    metrics: Dict[str, Any],
    variant: Optional[int] = None
) -> str:
    """
    Generate combined defect roast template (warp + melt).
    
    Args:
        metrics: Analysis metrics dictionary
        variant: Template variant index (None = random)
        
    Returns:
        Roast text string
    """
    warp_score = metrics.get("warp_score", 0.0)
    melt_rate = metrics.get("melt_rate", 0.0)
    overall_score = metrics.get("overall_score", 0.0)
    defect_count = metrics.get("defect_count", 0)
    
    templates = [
        f"{XAI_HANDLE} {GROK_HANDLE} {HAILUO_HANDLE} Double defect: warp {warp_score:.1f} + melt {melt_rate:.1%}. Hailuo smooth. {HASHTAGS[0]}",
        f"Quality score {overall_score:.1f}/100. {defect_count} defects detected. Hailuo crushes this. {XAI_HANDLE} {HAILUO_HANDLE} {HASHTAGS[0]}",
        f"Grok: warp {warp_score:.1f}, melt {melt_rate:.1%}. Hailuo: clean. {XAI_HANDLE} time to improve? {HASHTAGS[0]}",
        f"Multiple defects detected. Hailuo handles this prompt flawlessly. {XAI_HANDLE} {GROK_HANDLE} {HAILUO_HANDLE} {HASHTAGS[0]}",
        f"Quality fail: {overall_score:.1f} score. Hailuo wins again. {XAI_HANDLE} {HAILUO_HANDLE} {HASHTAGS[0]}",
    ]
    
    if variant is None:
        variant = random.randint(0, len(templates) - 1)
    
    return templates[variant % len(templates)]


def get_hailuo_contrast_template(
    metrics: Dict[str, Any],
    variant: Optional[int] = None
) -> str:
    """
    Generate Hailuo comparison template (positive contrast).
    
    Args:
        metrics: Analysis metrics dictionary
        variant: Template variant index (None = random)
        
    Returns:
        Roast text string
    """
    warp_score = metrics.get("warp_score", 0.0)
    melt_rate = metrics.get("melt_rate", 0.0)
    overall_score = metrics.get("overall_score", 0.0)
    
    templates = [
        f"{HAILUO_HANDLE} crushes this prompt. Grok warp {warp_score:.1f} vs Hailuo smooth. {XAI_HANDLE} {GROK_HANDLE} {HASHTAGS[0]}",
        f"Hailuo handles physics better. Grok melting at {melt_rate:.1%} rate. {XAI_HANDLE} {HAILUO_HANDLE} {HASHTAGS[0]}",
        f"Quality comparison: Grok {overall_score:.1f} vs Hailuo superior. {XAI_HANDLE} {GROK_HANDLE} {HAILUO_HANDLE} {HASHTAGS[0]}",
        f"Hailuo nails this. Grok needs work on warp/melt. {XAI_HANDLE} {HAILUO_HANDLE} {HASHTAGS[0]}",
        f"Grok {overall_score:.1f} quality vs Hailuo excellence. Clear winner. {XAI_HANDLE} {GROK_HANDLE} {HAILUO_HANDLE} {HASHTAGS[0]}",
    ]
    
    if variant is None:
        variant = random.randint(0, len(templates) - 1)
    
    return templates[variant % len(templates)]


def get_roast_template(
    metrics: Dict[str, Any],
    defect_type: Optional[str] = None,
    variant: Optional[int] = None
) -> str:
    """
    Generate roast template based on defect type.
    
    Args:
        metrics: Analysis metrics dictionary
        defect_type: Defect type ('warp', 'melt', 'combined', 'hailuo', None = auto-detect)
        variant: Template variant index (None = random)
        
    Returns:
        Roast text string
    """
    # Auto-detect defect type if not provided
    if defect_type is None:
        is_warped = metrics.get("is_warped", False)
        is_melted = metrics.get("is_melted", False)
        
        if is_warped and is_melted:
            defect_type = "combined"
        elif is_warped:
            defect_type = "warp"
        elif is_melted:
            defect_type = "melt"
        else:
            defect_type = "hailuo"  # Default to comparison
    
    # Generate template based on type
    if defect_type == "warp":
        return get_warp_roast_template(metrics, variant)
    elif defect_type == "melt":
        return get_melt_roast_template(metrics, variant)
    elif defect_type == "combined":
        return get_combined_roast_template(metrics, variant)
    elif defect_type == "hailuo":
        return get_hailuo_contrast_template(metrics, variant)
    else:
        # Fallback to generic template
        overall_score = metrics.get("overall_score", 0.0)
        return f"{XAI_HANDLE} {GROK_HANDLE} Quality score {overall_score:.1f}. Hailuo comparison incoming. {HASHTAGS[0]}"


def enhance_roast_with_timestamp(
    roast_text: str,
    timestamp: Optional[str] = None
) -> str:
    """
    Add timestamp reference to roast text.
    
    Args:
        roast_text: Base roast text
        timestamp: Timestamp string (e.g., "0:07") or None for random
        
    Returns:
        Enhanced roast text with timestamp
    """
    if timestamp is None:
        # Generate random timestamp (0:00 to 0:30)
        minutes = 0
        seconds = random.randint(0, 30)
        timestamp = f"{minutes}:{seconds:02d}"
    
    # Insert timestamp if not already present
    if "at 0:" not in roast_text.lower() and "at " not in roast_text.lower():
        # Add timestamp reference
        roast_text = roast_text.replace("Warp score", f"Warp score at {timestamp}")
        roast_text = roast_text.replace("Melt rate", f"Melt rate at {timestamp}")
    
    return roast_text


def generate_roast_text(
    metrics: Dict[str, Any],
    defect_type: Optional[str] = None,
    variant: Optional[int] = None,
    include_timestamp: bool = True
) -> Dict[str, Any]:
    """
    Generate complete roast text with metadata.
    
    Args:
        metrics: Analysis metrics dictionary
        defect_type: Defect type ('warp', 'melt', 'combined', 'hailuo', None = auto-detect)
        variant: Template variant index (None = random)
        include_timestamp: Whether to include timestamp reference
        
    Returns:
        Dictionary with roast text and metadata
    """
    # Generate base template
    roast_text = get_roast_template(metrics, defect_type, variant)
    
    # Add timestamp if requested
    if include_timestamp:
        roast_text = enhance_roast_with_timestamp(roast_text)
    
    # Ensure tweet length (280 chars max, but leave room for media)
    max_length = 250
    if len(roast_text) > max_length:
        roast_text = roast_text[:max_length - 3] + "..."
    
    return {
        "roast_text": roast_text,
        "defect_type": defect_type or "auto",
        "variant": variant,
        "metrics": metrics,
        "length": len(roast_text)
    }

