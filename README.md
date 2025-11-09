# 🎯 Grok Video Torture Chamber

> **Open-source adversarial testing pipeline for stress-testing Grok Video API through defect detection and viral shaming campaigns**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status: MVP Ready](https://img.shields.io/badge/Status-MVP%20Ready-green.svg)](https://github.com/BigTrip1/grok-bomb)

---

## 📖 Table of Contents

- [Core Concept](#-core-concept)
- [Project Purpose](#-project-purpose)
- [How It Works](#-how-it-works)
- [Architecture](#-architecture)
- [Features](#-features)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Usage Examples](#-usage-examples)
- [Expected Outcomes](#-expected-outcomes)
- [Project Structure](#-project-structure)
- [API Documentation](#-api-documentation)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Core Concept

**Grok Video Torture Chamber** is an adversarial testing framework designed to systematically stress-test the Grok Video API by:

1. **Generating Adversarial Prompts**: Creating thousands of intentionally challenging prompts designed to expose defects in video generation
2. **Detecting Defects**: Using computer vision and AI to automatically detect warping, melting, and quality issues in generated videos
3. **Viral Shaming**: Posting defect reports to X (Twitter) with competitive comparisons to drive improvements
4. **Feedback Loop**: Submitting structured feedback to xAI for model improvement

### The Problem It Solves

Video generation APIs like Grok Video are trained on large datasets but may struggle with:
- **Physics violations**: Objects defying gravity, momentum, or physical laws
- **Coherence issues**: Objects melting, warping, or inconsistently rendered
- **Camera movements**: Complex camera motions that break spatial consistency
- **Edge cases**: Unusual combinations that weren't well-represented in training data

This project systematically identifies these weaknesses through automated testing at scale.

---

## 🎯 Project Purpose

### Primary Goals

1. **Quality Assurance**: Identify defects and weaknesses in Grok Video API
2. **Competitive Analysis**: Compare Grok Video performance against Hailuo/Veo
3. **Improvement Driver**: Provide actionable feedback to xAI for model enhancement
4. **Transparency**: Publicly document video generation quality through viral shaming
5. **Research**: Contribute to understanding adversarial testing for video generation models

### Target Audience

- **Researchers**: Studying video generation model robustness
- **Developers**: Testing video generation APIs before integration
- **xAI Engineers**: Receiving structured feedback for model improvement
- **Open Source Community**: Contributing to video generation quality standards

---

## 🔄 How It Works

### Pipeline Overview

The project operates as a **4-phase pipeline** that processes prompts from generation to public shaming:

```
┌─────────────────────────────────────────────────────────────┐
│ PHASE 1: Setup & API Testing                                │
│ - Install dependencies                                       │
│ - Validate API keys                                         │
│ - Test API connections                                      │
│ - Check GPU availability                                    │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ PHASE 2: Prompt Bombing                                     │
│ - Generate 10,000+ adversarial prompt variants              │
│ - Apply physics traps (zero-G, momentum violations)         │
│ - Apply coherence traps (emerald sparks, texture bleeding)  │
│ - Send to Grok API (100-1000 concurrent requests)          │
│ - Collect video URLs                                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ PHASE 3: Defect Detection                                   │
│ - Download videos from Phase 2                              │
│ - Extract frames (MoviePy)                                  │
│ - Detect warping (OpenCV optical flow)                      │
│ - Detect melting (PyTorch Faster R-CNN)                     │
│ - Calculate quality metrics (PSNR, SSIM, trajectory)        │
│ - Flag videos for roasting (score < 5.0)                    │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ PHASE 4: Auto-Roasting                                      │
│ - Generate viral shaming tweets                             │
│ - Post to X (Twitter) - 50 posts/day limit                  │
│ - Submit feedback to xAI API                                │
│ - Track posted roasts to avoid duplicates                   │
└─────────────────────────────────────────────────────────────┘
```

### Detailed Phase Breakdown

#### Phase 1: Setup & API Testing

**Purpose**: Validate environment and test API connections

**Process**:
1. Install all Python dependencies (PyTorch, OpenCV, MoviePy, Tweepy, etc.)
2. Load API keys from `.env` file
3. Test xAI API connection
4. Test X (Twitter) API connection
5. Check CUDA/GPU availability for defect detection

**Output**: Validated environment ready for pipeline execution

---

#### Phase 2: Prompt Bombing

**Purpose**: Generate adversarial prompts and create videos at scale

**Process**:
1. **Variant Generation**:
   - Take base prompts (e.g., "samurai vs T-rex")
   - Apply modifiers from pools:
     - **Physics traps**: zero-G flips, momentum violations, gravity inversion
     - **Camera modifiers**: dolly+orbit, dolly+warp, orbit+physics_break
     - **Coherence traps**: emerald sparks, chromatic aberration, texture bleeding
     - **Environmental**: neon rain, snowstorm, sandstorm
   - Generate 10,000+ variants using combinatorial strategies

2. **Batch Generation**:
   - Send prompts to Grok Video API (`https://api.x.ai/v1/video/generate`)
   - Process 100-1000 concurrent requests (async workers)
   - Apply rate limiting (1-5s jittered delays)
   - Collect video URLs and metadata

**Output**: JSON file with video URLs, prompts, and generation metadata

**Example Variants**:
```
Base: "samurai vs T-rex"
→ "samurai vs T-rex zero-G flips --camera dolly+orbit"
→ "samurai vs T-rex momentum violation test neon rain"
→ "samurai vs T-rex gravity inversion emerald sparks"
```

---

#### Phase 3: Defect Detection

**Purpose**: Automatically detect defects in generated videos

**Process**:
1. **Frame Extraction**:
   - Download videos from Phase 2 URLs
   - Extract frames using MoviePy
   - Convert to BGR format for OpenCV processing

2. **Warp Detection**:
   - Calculate optical flow using Farneback method
   - Measure flow magnitude (L2 norm)
   - Flag videos with warp score > 50.0 (threshold)
   - Calculate warp rate (percentage of warped frames)

3. **Melt Detection**:
   - Use PyTorch Faster R-CNN for object detection
   - Track object confidence across frames
   - Flag videos with low confidence (deformation rate > 0.3)
   - Detect objects "melting" or deforming inconsistently

4. **Quality Metrics**:
   - **PSNR** (Peak Signal-to-Noise Ratio): Frame-to-frame quality
   - **SSIM** (Structural Similarity Index): Coherence measurement
   - **Trajectory Consistency**: Object tracking across frames
   - **Overall Quality Score**: Weighted combination (0-100 scale)

5. **Roast Flagging**:
   - Flag videos with overall score < 5.0
   - Flag videos with severe warping (score > 100)
   - Flag videos with severe melting (rate > 0.5)

**Output**: 
- CSV file with full analysis results
- JSON file with roast-flagged videos
- Summary statistics

**Example Detection**:
```python
{
    "video_url": "https://...",
    "warp_score": 75.0,
    "melt_rate": 0.4,
    "overall_score": 3.0,
    "is_warped": true,
    "is_melted": true,
    "should_roast": true
}
```

---

#### Phase 4: Auto-Roasting

**Purpose**: Publicly shame defective videos and submit feedback to xAI

**Process**:
1. **Template Generation**:
   - Load roast-flagged videos from Phase 3
   - Generate viral shaming tweets using templates:
     - Warp roasts: "@xai @grok Warp score 75.0—Hailuo nails physics. Fix or cooked?"
     - Melt roasts: "@xai @grok Melt rate 40%—objects deforming. Hailuo keeps it clean."
     - Combined roasts: "@xai @grok Double defect: warp 75.0 + melt 40%. Hailuo smooth."
   - Add competitive comparisons to Hailuo/Veo
   - Include quality metrics and timestamps

2. **X (Twitter) Posting**:
   - Post tweets using Tweepy API
   - Apply rate limiting (50 posts/day, 60s intervals)
   - Track posted roasts to avoid duplicates
   - Handle rate limits gracefully

3. **Feedback Submission**:
   - Submit structured feedback to xAI API (`https://api.x.ai/v1/feedback`)
   - Include quality scores, defect metrics, and analysis notes
   - Set priority based on defect severity (high for severe defects)
   - Opt-in data sharing for training data

**Output**: 
- Posted tweets on X (Twitter)
- Feedback submissions to xAI API
- Posted roast history (JSON)

**Example Tweet**:
```
@xai @grok @hailuo_ai Warp score 75.0 at 0:07—Hailuo nails physics. 
Fix or cooked? #GrokVideo
```

---

## 🏗️ Architecture

### System Components

```
grok-vid-improver/
├── Phase 1: Setup & API Testing
│   ├── setup.py                 # Dependency installation
│   └── test_api_call.py         # API connection testing
│
├── Phase 2: Prompt Bombing
│   ├── variants_generator.py    # Adversarial prompt generation
│   ├── bomber.py                # Bombing orchestration
│   └── batch_runner.py          # Async batch processing
│
├── Phase 3: Defect Detection
│   ├── detector.py              # Warp/melt detection
│   ├── analysis_utils.py        # Quality metrics
│   └── result_processor.py      # Batch processing & export
│
├── Phase 4: Auto-Roasting
│   ├── roast_templates.py       # Tweet template generation
│   ├── roaster.py               # X (Twitter) posting
│   └── feedback_submitter.py    # xAI feedback API
│
├── Pipeline Orchestration
│   ├── run_pipeline.py          # Master pipeline runner
│   ├── env_validator.py         # Environment validation
│   └── smoke_test.py            # End-to-end smoke test
│
└── Documentation
    ├── README.md                # This file
    ├── PROJECT_STATUS.md        # Detailed status
    └── MVP_LAUNCH_BRIEF.md      # MVP launch guide
```

### Technology Stack

- **Python 3.10+**: Core programming language
- **PyTorch**: Deep learning framework (Faster R-CNN for melt detection)
- **OpenCV**: Computer vision (optical flow for warp detection)
- **MoviePy**: Video processing (frame extraction)
- **Tweepy**: X (Twitter) API integration
- **aiohttp**: Async HTTP requests
- **scikit-image**: Image quality metrics (PSNR, SSIM)

### Design Principles

1. **Modular**: Each phase is independent and can be run separately
2. **Scalable**: Handles 10,000+ prompts with 100-1000 concurrent workers
3. **GPU-Accelerated**: CUDA support for Faster R-CNN (falls back to CPU)
4. **Rate-Limited**: Respects API rate limits automatically
5. **Error-Resilient**: Graceful degradation and comprehensive error handling

---

## ✨ Features

### Core Features

- ✅ **Adversarial Prompt Generation**: 10,000+ variants with physics/coherence traps
- ✅ **Automated Defect Detection**: Warp and melt detection using AI/computer vision
- ✅ **Quality Metrics**: PSNR, SSIM, trajectory consistency scoring
- ✅ **Viral Shaming**: Automated X (Twitter) posting with competitive comparisons
- ✅ **Feedback Loop**: Structured feedback submission to xAI API
- ✅ **Batch Processing**: Async processing for scalability
- ✅ **GPU Support**: CUDA-accelerated defect detection
- ✅ **Rate Limiting**: Automatic API rate limit handling
- ✅ **Data Export**: CSV/JSON exports for analysis

### Advanced Features

- 🔄 **Combinatorial Mutation**: Full cross-product of modifiers for exhaustive testing
- 🎯 **Adversarial Strategies**: Random, combinatorial, and known-problematic combinations
- 📊 **Comprehensive Metrics**: Overall quality scoring with configurable weights
- 🔁 **Duplicate Detection**: Tracks posted roasts to avoid duplicates
- 📈 **Statistics**: Aggregate metrics and defect rate analysis
- 🛡️ **Error Handling**: Graceful degradation and comprehensive logging

---

## 📦 Installation

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Git (for cloning repository)
- CUDA (optional, for GPU acceleration)

### Step 1: Clone Repository

```bash
git clone https://github.com/BigTrip1/grok-bomb.git
cd grok-bomb
```

### Step 2: Install Dependencies

```bash
python setup.py
```

This will:
- Install all required packages from `requirements.txt`
- Prompt for XAI_API_KEY if not in `.env`
- Check CUDA/GPU availability
- Test API connections

### Step 3: Configure Environment

Create `.env` file in project root:

```env
# xAI API
XAI_API_KEY=your_xai_api_key_here

# X (Twitter) API
X_API_KEY=your_twitter_api_key
X_API_SECRET=your_twitter_api_secret
X_ACCESS_TOKEN=your_twitter_access_token
X_ACCESS_TOKEN_SECRET=your_twitter_access_token_secret
X_BEARER_TOKEN=your_twitter_bearer_token (optional)
```

### Step 4: Validate Environment

```bash
python env_validator.py
```

This will:
- Check all required API keys
- Test API connections
- Verify dependencies
- Check GPU availability

---

## 🚀 Quick Start

### Run Full Pipeline

```bash
python run_pipeline.py
```

This will execute all 4 phases:
1. Generate adversarial prompts
2. Create videos via Grok API
3. Detect defects
4. Post roasts and submit feedback

### Run Individual Phases

```python
# Phase 2: Prompt Bombing
from variants_generator import create_adversarial_batch
from batch_runner import BatchRunner
import asyncio

variants = create_adversarial_batch(total_target=1000)
runner = BatchRunner(api_key=api_key, max_concurrent=100)
results = await runner.run_batch(variants)

# Phase 3: Defect Detection
from result_processor import process_phase2_results

analysis = await process_phase2_results(results)

# Phase 4: Auto-Roasting
from roaster import Roaster
from feedback_submitter import FeedbackSubmitter

roaster = Roaster(daily_limit=50)
roasts = roaster.load_roasts_from_json("./results/roasts.json")
await roaster.post_roast_batch(roasts, max_posts=50)

submitter = FeedbackSubmitter()
await submitter.submit_batch(roasts)
```

### Run Smoke Test

```bash
python smoke_test.py --dry-run
```

This will:
- Validate environment
- Test all 4 phases with minimal data
- Verify pipeline functionality
- Report any issues

---

## 📊 Usage Examples

### Example 1: Small Test Run (100 prompts)

```python
from run_pipeline import PipelineRunner
import asyncio

pipeline = PipelineRunner()
results = await pipeline.run_full_pipeline(
    base_prompts=["samurai vs T-rex"],
    phase2_config={
        "total_target": 100,
        "max_concurrent": 10
    },
    phase3_config={
        "max_concurrent": 5
    },
    phase4_config={
        "max_posts": 10
    }
)
```

**Expected Output**:
- ~50-100 videos generated
- ~10-20 defects detected
- ~10-20 roasts posted
- Analysis results in `results/` directory

### Example 2: Full Campaign (10,000 prompts)

```python
pipeline = PipelineRunner()
results = await pipeline.run_full_pipeline(
    base_prompts=[
        "samurai vs T-rex",
        "cyberpunk cityscape at night",
        "space battle between fleets"
    ],
    phase2_config={
        "total_target": 10000,
        "max_concurrent": 500
    },
    phase3_config={
        "max_concurrent": 20
    },
    phase4_config={
        "max_posts": 50
    }
)
```

**Expected Output**:
- ~5,000-10,000 videos generated
- ~500-1,000 defects detected
- ~50 roasts posted per day (rate limited)
- Comprehensive analysis results

### Example 3: Custom Adversarial Prompts

```python
from variants_generator import generate_variants

# Generate variants with specific strategies
variants = generate_variants(
    base_prompt="samurai vs T-rex",
    count=1000,
    strategies=["adversarial", "random"]
)

# Custom modifier pools
custom_mods = {
    "physics": ["zero-G flips", "momentum violation"],
    "camera": ["--camera dolly+orbit", "--camera dolly+warp"]
}

variants = generate_variants(
    base_prompt="samurai vs T-rex",
    count=1000,
    mod_pools=custom_mods
)
```

---

## 🎯 Expected Outcomes

### Quantitative Outcomes

1. **Defect Detection Rate**:
   - Expected: 10-20% of videos flagged for roasting
   - Metrics: Warp rate, melt rate, overall quality scores
   - Comparison: Grok vs. Hailuo/Veo performance

2. **Viral Shaming Impact**:
   - Expected: 50 tweets/day (rate limited)
   - Engagement: Likes, retweets, replies
   - Visibility: Hashtag reach, competitive comparisons

3. **Feedback Submission**:
   - Expected: 100+ feedback submissions per campaign
   - Priority: High for severe defects (score < 10)
   - Data Sharing: Opt-in for training data

### Qualitative Outcomes

1. **Quality Improvement**:
   - xAI receives structured feedback for model enhancement
   - Public pressure drives quality improvements
   - Competitive comparisons highlight gaps

2. **Transparency**:
   - Public documentation of video generation quality
   - Open-source testing methodology
   - Community-driven quality standards

3. **Research Contribution**:
   - Adversarial testing methodology for video generation
   - Defect detection algorithms and metrics
   - Quality benchmarking framework

### Success Metrics

- ✅ **Defect Detection**: 10-20% roast rate indicates effective testing
- ✅ **Viral Reach**: 50 tweets/day with competitive comparisons
- ✅ **Feedback Quality**: Structured feedback with metrics and examples
- ✅ **Community Impact**: Open-source contributions and improvements
- ✅ **Model Improvement**: xAI incorporates feedback for enhancements

---

## 📁 Project Structure

```
grok-bomb/
├── .env                          # API keys (not in repo)
├── .gitignore                    # Git ignore rules
├── .rules                        # Coding rules
│
├── Phase 1: Setup & API Testing
│   ├── setup.py                  # Dependency installation
│   └── test_api_call.py          # API testing
│
├── Phase 2: Prompt Bombing
│   ├── variants_generator.py     # Prompt mutation
│   ├── bomber.py                 # Bombing orchestration
│   └── batch_runner.py           # Batch processing
│
├── Phase 3: Defect Detection
│   ├── detector.py               # Warp/melt detection
│   ├── analysis_utils.py         # Quality metrics
│   └── result_processor.py       # Batch processing
│
├── Phase 4: Auto-Roasting
│   ├── roast_templates.py        # Tweet templates
│   ├── roaster.py                # X posting
│   └── feedback_submitter.py     # xAI feedback
│
├── Pipeline Orchestration
│   ├── run_pipeline.py           # Master runner
│   ├── env_validator.py          # Environment validation
│   └── smoke_test.py             # Smoke test
│
├── Documentation
│   ├── README.md                 # This file
│   ├── PROJECT_STATUS.md         # Detailed status
│   ├── EXECUTIVE_SUMMARY.md      # Quick start
│   ├── MVP_LAUNCH_BRIEF.md       # MVP guide
│   └── PHASE*.md                 # Phase documentation
│
├── Results (auto-created)
│   ├── phase2_results.json       # Generated videos
│   ├── analysis_results.csv      # Full analysis
│   ├── roasts.json               # Roast-flagged videos
│   ├── summary.json              # Statistics
│   └── phase4_results.json       # Posted tweets
│
└── requirements.txt              # Dependencies
```

---

## 📚 API Documentation

### Phase 2: Prompt Bombing

#### `variants_generator.py`

```python
# Generate adversarial variants
variants = create_adversarial_batch(
    base_prompts=["samurai vs T-rex"],
    variants_per_base=100,
    total_target=10000
)

# Generate single variant
variant = mutate_prompt(
    base="samurai vs T-rex",
    mods=["zero-G flips", "--camera dolly+orbit"],
    strategy="adversarial"
)
```

#### `batch_runner.py`

```python
# Run batch generation
runner = BatchRunner(
    api_key=api_key,
    max_concurrent=100
)
results = await runner.run_batch(variants)
```

### Phase 3: Defect Detection

#### `detector.py`

```python
# Analyze video
result = analyze_video(
    video_path="video.mp4",
    warp_threshold=50.0,
    melt_threshold=0.7
)

# Async analysis
result = await analyze_video_async(
    video_url="https://...",
    warp_threshold=50.0
)
```

#### `analysis_utils.py`

```python
# Calculate quality metrics
coherence = calculate_coherence_score(frames)
trajectory = detect_trajectory_inconsistency(frames)
overall_score = calculate_overall_quality_score(
    warp_score=75.0,
    melt_rate=0.4,
    coherence_score=50.0,
    trajectory_score=50.0
)
```

### Phase 4: Auto-Roasting

#### `roaster.py`

```python
# Initialize roaster
roaster = Roaster(
    daily_limit=50,
    post_interval=60.0
)

# Post roast
result = await roaster.post_roast(roast_data)

# Batch posting
results = await roaster.post_roast_batch(roasts, max_posts=50)
```

#### `feedback_submitter.py`

```python
# Submit feedback
submitter = FeedbackSubmitter(opt_in_data_share=True)
result = await submitter.submit_feedback(
    score=3.0,
    note="Warp score 75.0, melt rate 0.4",
    priority="high"
)

# Batch submission
results = await submitter.submit_batch(roasts)
```

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### Contribution Guidelines

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes**
4. **Run tests**: `python smoke_test.py --dry-run`
5. **Commit your changes**: `git commit -m 'Add amazing feature'`
6. **Push to branch**: `git push origin feature/amazing-feature`
7. **Open a Pull Request**

### Areas for Contribution

- **New Adversarial Strategies**: Add new prompt mutation strategies
- **Defect Detection**: Improve warp/melt detection algorithms
- **Quality Metrics**: Add new quality metrics (temporal consistency, etc.)
- **Template Generation**: Create new roast templates
- **Documentation**: Improve documentation and examples
- **Testing**: Add unit tests and integration tests
- **Performance**: Optimize batch processing and GPU utilization

### Code Style

- Follow PEP 8 style guide
- Use type hints where appropriate
- Add docstrings to all functions
- Write comprehensive tests
- Update documentation

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **xAI**: For providing the Grok Video API
- **Open Source Community**: For the amazing tools and libraries
- **Contributors**: Everyone who helps improve this project

---

## 📧 Contact

- **Repository**: [https://github.com/BigTrip1/grok-bomb](https://github.com/BigTrip1/grok-bomb)
- **Issues**: [GitHub Issues](https://github.com/BigTrip1/grok-bomb/issues)
- **Discussions**: [GitHub Discussions](https://github.com/BigTrip1/grok-bomb/discussions)

---

## 🚀 Roadmap

### Current Status: MVP Ready (85% → 95%)

- ✅ Phases 1-4 Complete
- ⚠️ Environment Validation (In Progress)
- ⚠️ Smoke Test Suite (In Progress)
- ⚠️ Progress Tracking (Planned)
- ⚠️ Retry Logic (Planned)

### Future Enhancements

- **Phase 5**: Master orchestrator with scheduling
- **Progress Tracking**: tqdm progress bars for long operations
- **Retry Logic**: Exponential backoff for failed operations
- **Media Download**: Automatic video download for X posting
- **Engagement Tracking**: Track tweet engagement metrics
- **Resume Capability**: Resume interrupted batches
- **Multi-GPU Support**: Distribute defect detection across GPUs
- **Real-time Dashboard**: Web dashboard for monitoring

---

## ⚠️ Disclaimer

This project is for **research and testing purposes only**. The viral shaming component is intended to:
- Drive quality improvements through public pressure
- Provide transparency in video generation quality
- Contribute to open-source research

**Please use responsibly** and in accordance with:
- X (Twitter) Terms of Service
- xAI API Terms of Service
- Local laws and regulations

---

## 📊 Statistics

- **Lines of Code**: 6,863+
- **Files**: 29
- **Phases**: 4 (Complete)
- **Dependencies**: 10+
- **API Integrations**: 2 (xAI, X/Twitter)

---

**Built with ❤️ for the open-source community**

*Last updated: November 2025*
