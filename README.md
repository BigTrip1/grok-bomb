# Grok Video Torture Chamber

Open-source Python pipeline for stress-testing Grok Video API vs. Hailuo/Veo through adversarial prompt generation, defect detection, and viral shaming.

## 🎯 Project Status

**Phases 1-4: COMPLETE ✅**

- Phase 1: Setup & API Testing
- Phase 2: Prompt Bomber (10k+ adversarial prompts)
- Phase 3: Defect Detector (warp/melt detection)
- Phase 4: Auto-Roaster (X posting + xAI feedback)

## 🚀 Quick Start

### 1. Setup

```bash
# Install dependencies and configure
python setup.py
```

This will:
- Install all required packages
- Prompt for XAI_API_KEY if not in .env
- Check CUDA/GPU availability
- Test API connection

### 2. Configure Environment

Create `.env` file with your API keys:

```env
XAI_API_KEY=your_xai_api_key_here
X_API_KEY=your_twitter_api_key
X_API_SECRET=your_twitter_api_secret
X_ACCESS_TOKEN=your_twitter_access_token
X_ACCESS_TOKEN_SECRET=your_twitter_access_token_secret
X_BEARER_TOKEN=your_twitter_bearer_token (optional)
```

### 3. Run Pipeline

```bash
# Run full pipeline (Phases 2-4)
python run_pipeline.py
```

Or run phases individually:

```python
# Phase 2: Generate adversarial prompts and videos
from variants_generator import create_adversarial_batch
from batch_runner import BatchRunner
import asyncio

variants = create_adversarial_batch(total_target=1000)
runner = BatchRunner(api_key=api_key, max_concurrent=100)
results = await runner.run_batch(variants)

# Phase 3: Detect defects
from result_processor import process_phase2_results

analysis = await process_phase2_results(results)

# Phase 4: Post roasts and submit feedback
from roaster import Roaster
from feedback_submitter import FeedbackSubmitter

roaster = Roaster(daily_limit=50)
roasts = roaster.load_roasts_from_json("./results/roasts.json")
await roaster.post_roast_batch(roasts, max_posts=50)

submitter = FeedbackSubmitter()
await submitter.submit_batch(roasts)
```

## 📁 Project Structure

```
grok-vid-improver/
├── setup.py                 # Phase 1: Setup and configuration
├── test_api_call.py         # Phase 1: API testing
├── variants_generator.py    # Phase 2: Prompt mutation
├── bomber.py                # Phase 2: Bombing orchestration
├── batch_runner.py          # Phase 2: Batch processing
├── detector.py              # Phase 3: Defect detection
├── analysis_utils.py        # Phase 3: Quality metrics
├── result_processor.py      # Phase 3: Batch processing
├── roast_templates.py       # Phase 4: Template generation
├── roaster.py               # Phase 4: X posting
├── feedback_submitter.py    # Phase 4: xAI feedback
├── run_pipeline.py          # Master pipeline runner
├── requirements.txt         # Dependencies
├── .env                     # API keys (create this)
└── results/                 # Output directory (auto-created)
    ├── phase2_results.json
    ├── analysis_results.csv
    ├── roasts.json
    └── summary.json
```

## 🎯 Features

### Phase 2: Prompt Bomber
- Generate 10,000+ adversarial prompt variants
- Physics traps (zero-G, momentum violations)
- Coherence traps (emerald sparks, texture bleeding)
- Async batch processing (100-1000 concurrent workers)

### Phase 3: Defect Detector
- Warp detection (OpenCV optical flow)
- Melt detection (PyTorch Faster R-CNN)
- Quality metrics (PSNR, SSIM, trajectory)
- GPU-accelerated processing

### Phase 4: Auto-Roaster
- Viral shaming templates
- X (Twitter) posting with rate limiting (50/day)
- xAI feedback API integration
- Batch processing for both posting and feedback

## 📊 Performance

### Throughput
- **Phase 2**: 20-500 videos/minute (depends on concurrent workers)
- **Phase 3**: 1-20 videos/minute (depends on GPU)
- **Phase 4**: 50 posts/day (X rate limit)

### Resource Requirements
- **Memory**: 2-4 GB GPU memory (Faster R-CNN)
- **Storage**: ~100-500 MB per video (temporary)
- **Network**: Bandwidth-dependent (video downloads)

## 🔧 Configuration

### Rate Limits
- **X Posting**: 50 posts/day (configurable)
- **Post Interval**: 60 seconds between posts
- **Feedback API**: 1 second delay between requests

### Thresholds
- **Roast Threshold**: 5.0 (overall quality score)
- **Warp Threshold**: 50.0 (optical flow magnitude)
- **Melt Threshold**: 0.3 (deformation rate)

## 📝 Usage Examples

### Small Test Run

```python
# Generate 100 variants and analyze
from run_pipeline import PipelineRunner
import asyncio

pipeline = PipelineRunner()
results = await pipeline.run_full_pipeline(
    base_prompts=["samurai vs T-rex"],
    phase2_config={"total_target": 100, "max_concurrent": 10},
    phase3_config={"max_concurrent": 5},
    phase4_config={"max_posts": 5}
)
```

### Large Campaign

```python
# Generate 10k variants and full analysis
results = await pipeline.run_full_pipeline(
    base_prompts=["samurai vs T-rex", "cyberpunk cityscape"],
    phase2_config={"total_target": 10000, "max_concurrent": 500},
    phase3_config={"max_concurrent": 20},
    phase4_config={"max_posts": 50}
)
```

## 🚨 Known Limitations

1. **No Master Orchestrator**: Phases run separately (use `run_pipeline.py`)
2. **No Progress Bars**: Long operations lack progress indication
3. **No Retry Logic**: Failed operations not automatically retried
4. **No Media Download**: Videos not automatically downloaded for X posting
5. **Manual Execution**: Requires manual step-by-step execution

## 🔮 Future Enhancements

- Phase 5: Master orchestrator with scheduling
- Progress tracking with tqdm
- Retry logic with exponential backoff
- Media download for X posting
- Engagement tracking
- Resume capability for interrupted batches

## 📄 License

Open-source (specify license)

## 🤝 Contributing

Contributions welcome! Please see CONTRIBUTING.md for guidelines.

## 📧 Contact

For questions or issues, please open an issue on GitHub.

