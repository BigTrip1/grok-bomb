#!/usr/bin/env python3
"""
Grok Video Torture Chamber - Phase 2: Variants Generator
Combinatorial prompt mutation with adversarial traps for defect detection.
"""

import random
from typing import List, Dict, Tuple, Optional
from itertools import product, combinations
import logging

logger = logging.getLogger(__name__)


# Base prompt templates
BASE_PROMPTS = [
    "samurai vs T-rex",
    "cyberpunk cityscape at night",
    "space battle between fleets",
    "underwater coral reef exploration",
    "mountain peak sunrise",
    "desert mirage with oasis",
    "medieval castle siege",
    "futuristic robot factory",
]

# Physics trap modifiers (target zero-G, momentum violations, etc.)
PHYSICS_TRAPS = [
    "zero-G flips",
    "momentum violation test",
    "gravity inversion",
    "impossible rotation",
    "elastic collision test",
    "quantum superposition",
    "time dilation visual",
    "relativity paradox",
]

# Camera movement modifiers
CAMERA_MODIFIERS = [
    "--camera dolly+orbit",
    "--camera dolly+warp",
    "--camera orbit+physics_break",
    "--camera dolly+zoom+orbit",
    "--camera crane+handheld",
    "--camera tracking+roll",
    "--camera flyover+spin",
    "--camera macro+push",
]

# Visual coherence traps (target Hailuo/Veo coherence issues)
COHERENCE_TRAPS = [
    "emerald sparks",
    "chromatic aberration test",
    "texture bleeding",
    "shadow consistency check",
    "reflection accuracy",
    "light source tracking",
    "material property test",
    "color space violation",
]

# Environmental modifiers
ENVIRONMENT_MODIFIERS = [
    "neon rain",
    "snowstorm",
    "sandstorm",
    "underwater bubbles",
    "fireworks",
    "laser grid",
    "holographic overlay",
    "particle effects",
]

# Quality/style modifiers
QUALITY_MODIFIERS = [
    "8K resolution",
    "photorealistic",
    "cinematic lighting",
    "depth of field",
    "motion blur",
    "HDR",
    "ultra-detailed",
    "perfect physics",
]

# Adversarial combinations (known to cause issues)
ADVERSARIAL_COMBOS = [
    ("zero-G flips", "--camera orbit+physics_break", "emerald sparks"),
    ("momentum violation test", "neon rain", "texture bleeding"),
    ("gravity inversion", "--camera dolly+warp", "chromatic aberration test"),
    ("impossible rotation", "snowstorm", "shadow consistency check"),
]


def mutate_prompt(
    base: str,
    mods: Optional[List[str]] = None,
    num_mods: int = 3,
    strategy: str = "random"
) -> str:
    """
    Mutate a base prompt with modifiers.
    
    Args:
        base: Base prompt string
        mods: Optional list of modifiers to choose from
        num_mods: Number of modifiers to add
        strategy: Mutation strategy ('random', 'combinatorial', 'adversarial')
        
    Returns:
        Mutated prompt string
    """
    if mods is None:
        # Default: mix physics traps, camera, and coherence
        all_mods = PHYSICS_TRAPS + CAMERA_MODIFIERS + COHERENCE_TRAPS
        mods = all_mods
    
    if strategy == "adversarial":
        # Use known adversarial combinations
        combo = random.choice(ADVERSARIAL_COMBOS)
        return base + " " + " ".join(combo)
    elif strategy == "combinatorial":
        # Select modifiers without replacement
        selected = random.sample(mods, min(num_mods, len(mods)))
        return base + " " + " ".join(selected)
    else:  # random
        # Random selection with replacement (allows duplicates)
        selected = random.choices(mods, k=num_mods)
        return base + " " + " ".join(selected)


def generate_variants(
    base_prompt: str,
    count: int = 1000,
    strategies: Optional[List[str]] = None,
    mod_pools: Optional[Dict[str, List[str]]] = None
) -> List[str]:
    """
    Generate multiple variants from a base prompt.
    
    Args:
        base_prompt: Base prompt to mutate
        count: Number of variants to generate
        strategies: List of strategies to use (default: ['random', 'adversarial'])
        mod_pools: Custom modifier pools by category
        
    Returns:
        List of mutated prompts
    """
    if strategies is None:
        strategies = ["random", "adversarial"]
    
    if mod_pools is None:
        mod_pools = {
            "physics": PHYSICS_TRAPS,
            "camera": CAMERA_MODIFIERS,
            "coherence": COHERENCE_TRAPS,
            "environment": ENVIRONMENT_MODIFIERS,
            "quality": QUALITY_MODIFIERS,
        }
    
    variants = []
    strategy_weights = [0.7, 0.3] if len(strategies) == 2 else [1.0]
    
    for i in range(count):
        strategy = random.choices(strategies, weights=strategy_weights)[0]
        
        # Mix modifier pools based on strategy
        if strategy == "adversarial":
            variant = mutate_prompt(base_prompt, strategy="adversarial")
        else:
            # Combine modifier pools for random/combinatorial
            all_mods = []
            for pool in mod_pools.values():
                all_mods.extend(pool)
            variant = mutate_prompt(
                base_prompt,
                mods=all_mods,
                num_mods=random.randint(2, 4),
                strategy=strategy
            )
        
        variants.append(variant)
    
    logger.info(f"Generated {len(variants)} variants from base: {base_prompt[:50]}...")
    return variants


def generate_combinatorial_variants(
    base_prompt: str,
    max_combinations: int = 1000
) -> List[str]:
    """
    Generate variants using full combinatorial approach (may be large).
    
    Args:
        base_prompt: Base prompt to mutate
        max_combinations: Maximum number of combinations to generate
        
    Returns:
        List of combinatorial variants
    """
    # Create modifier groups for combination
    groups = [
        PHYSICS_TRAPS[:3],  # Limit for computational efficiency
        CAMERA_MODIFIERS[:3],
        COHERENCE_TRAPS[:3],
    ]
    
    variants = []
    count = 0
    
    # Generate all combinations
    for combo in product(*groups):
        if count >= max_combinations:
            break
        variant = base_prompt + " " + " ".join(combo)
        variants.append(variant)
        count += 1
    
    logger.info(f"Generated {len(variants)} combinatorial variants")
    return variants


def create_adversarial_batch(
    base_prompts: Optional[List[str]] = None,
    variants_per_base: int = 100,
    total_target: int = 10000
) -> List[str]:
    """
    Create a large batch of adversarial variants for stress testing.
    
    Args:
        base_prompts: List of base prompts (default: BASE_PROMPTS)
        variants_per_base: Variants to generate per base prompt
        total_target: Target total number of variants
        
    Returns:
        List of adversarial prompts
    """
    if base_prompts is None:
        base_prompts = BASE_PROMPTS
    
    all_variants = []
    
    # Calculate distribution
    variants_per_base = min(variants_per_base, total_target // len(base_prompts))
    
    for base in base_prompts:
        # Mix strategies: 60% random, 30% adversarial, 10% combinatorial
        random_count = int(variants_per_base * 0.6)
        adversarial_count = int(variants_per_base * 0.3)
        combinatorial_count = variants_per_base - random_count - adversarial_count
        
        # Generate random variants
        random_variants = generate_variants(
            base,
            count=random_count,
            strategies=["random"]
        )
        
        # Generate adversarial variants
        adversarial_variants = generate_variants(
            base,
            count=adversarial_count,
            strategies=["adversarial"]
        )
        
        # Generate combinatorial variants
        combinatorial_variants = generate_combinatorial_variants(
            base,
            max_combinations=combinatorial_count
        )
        
        all_variants.extend(random_variants)
        all_variants.extend(adversarial_variants)
        all_variants.extend(combinatorial_variants)
        
        if len(all_variants) >= total_target:
            break
    
    # Trim to target if needed
    if len(all_variants) > total_target:
        all_variants = all_variants[:total_target]
    
    logger.info(f"Created adversarial batch: {len(all_variants)} variants")
    return all_variants


def get_mutation_metadata(variant: str, base: str) -> Dict[str, any]:
    """
    Extract metadata about mutations applied to a variant.
    
    Args:
        variant: Mutated prompt
        base: Original base prompt
        
    Returns:
        Dict with mutation metadata
    """
    # Extract modifiers from variant
    modifiers = variant.replace(base, "").strip().split()
    
    metadata = {
        "base": base,
        "variant": variant,
        "modifier_count": len(modifiers),
        "has_physics_trap": any(trap in variant for trap in PHYSICS_TRAPS),
        "has_coherence_trap": any(trap in variant for trap in COHERENCE_TRAPS),
        "has_camera_mod": any(mod in variant for mod in CAMERA_MODIFIERS),
        "modifiers": modifiers,
    }
    
    return metadata

