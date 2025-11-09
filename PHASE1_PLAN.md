# Grok Video Torture Chamber - Phase 1 Plan Outline

## Project Structure
```
grok-vid-improver/
├── .env                    # API keys (gitignored)
├── .rules                  # Coding rules (<250 chars)
├── requirements.txt        # Python dependencies
├── setup.py               # Installation and test script
├── test_api_call.py       # Async API test module
├── PHASE1_PLAN.md         # This file
├── SELF_CRITIQUE.md       # Code review and improvements
└── tests/                 # Test outputs
    └── video.mp4          # Generated test video
```

## Phase 1 Components

### 1. requirements.txt
- **Core**: requests, aiohttp for async HTTP
- **Env**: python-dotenv for secure key management
- **Video**: opencv-python, moviepy, numpy
- **GPU**: torch, torchvision with CUDA support
- **Utils**: tqdm for progress, tweepy for X API

### 2. setup.py
- **Functions**:
  - `install_dependencies()`: Pip install from requirements.txt
  - `load_env_keys()`: Load .env or prompt with getpass
  - `check_cuda()`: GPU availability and device enumeration
  - `test_api_generation()`: End-to-end API test
- **Flow**: Install → Load keys → Check GPU → Test API

### 3. test_api_call.py
- **Core Functions**:
  - `jittered_sleep()`: Async rate limiting (1-5s random)
  - `generate_video_async()`: Async API call with error handling
  - `download_video()`: Stream download with progress bar
  - `generate_and_download()`: Combined async pipeline
  - `check_gpu_availability()`: Multi-GPU detection
- **Features**:
  - Timestamped logging
  - Connection pooling (aiohttp session)
  - Timeout handling (300s for generation)
  - Progress tracking (tqdm)

## Phase 2 Hooks (Preparation)

### Async Batch Processing
- Queue system for 10k+ prompts
- Worker pool with configurable concurrency
- Retry logic with exponential backoff

### Multi-GPU Support
- Device allocation per worker
- GPU memory monitoring
- Batch distribution across devices

### Defect Detection
- Warping detection (optical flow analysis)
- Melting artifacts (frame consistency checks)
- Quality metrics (PSNR, SSIM)

### X Integration
- Tweet generation for roasts
- Photo-realism scoring
- Physics validation reports

## Execution Flow

1. **Setup**: `python setup.py`
   - Installs deps, loads keys, checks GPU
   - Runs test generation

2. **Test**: `python test_api_call.py`
   - Generates test video
   - Downloads to ./tests/video.mp4
   - Logs GPU status

3. **Phase 2 Ready**: Async batch processing with defect detection

