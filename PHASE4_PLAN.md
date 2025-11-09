# Grok Video Torture Chamber - Phase 4 Plan Outline

## Project Structure (Phase 4)
```
grok-vid-improver/
├── roast_templates.py       # Template generators for viral shaming posts
├── roaster.py               # Core poster with Tweepy and rate limiting
├── feedback_submitter.py    # xAI feedback API integration
├── result_processor.py      # Phase 3 module (integrated)
└── PHASE4_PLAN.md           # This file
```

## Phase 4 Components

### 1. roast_templates.py
- **Template Types**:
  - `get_warp_roast_template()`: Warp defect roasts
  - `get_melt_roast_template()`: Melt defect roasts
  - `get_combined_roast_template()`: Combined defects
  - `get_hailuo_contrast_template()`: Hailuo comparison roasts

- **Core Functions**:
  - `get_roast_template()`: Auto-detect defect type and generate template
  - `enhance_roast_with_timestamp()`: Add timestamp references
  - `generate_roast_text()`: Complete roast text generation

- **Features**:
  - Multiple template variants per defect type
  - Random variant selection
  - Timestamp insertion
  - Tweet length validation (250 chars max)
  - Hashtag and handle tagging

### 2. roaster.py
- **Roaster Class**:
  - `__init__()`: Initialize with X API credentials
  - `load_posted_history()`: Load posted roasts to avoid duplicates
  - `save_posted_history()`: Save posted roasts history
  - `can_post()`: Check rate limits and daily limits
  - `post_roast()`: Post single roast to X
  - `post_roast_batch()`: Batch posting with rate limiting
  - `load_roasts_from_json()`: Load Phase 3 roasts.json

- **Rate Limiting**:
  - Daily limit: 50 posts/day (configurable)
  - Post interval: 60 seconds between posts (configurable)
  - Posted history tracking to avoid duplicates
  - Automatic rate limit handling via Tweepy

- **Features**:
  - Media attachment support (images/videos)
  - Duplicate detection
  - Post history persistence
  - Error handling and retry logic

### 3. feedback_submitter.py
- **FeedbackSubmitter Class**:
  - `__init__()`: Initialize with xAI API key
  - `submit_feedback()`: Submit single feedback to xAI API
  - `submit_roast_feedback()`: Submit feedback for roast data
  - `submit_batch()`: Batch submission with rate limiting
  - `export_submission_results()`: Export results to JSON

- **Feedback API**:
  - Endpoint: `https://api.x.ai/v1/feedback`
  - Payload: score, note, priority, opt_in_data_share
  - Optional: video_url, prompt
  - Priority levels: 'low', 'normal', 'high'

- **Features**:
  - Async batch processing
  - Rate limiting (1s delay between requests)
  - Priority assignment based on defect severity
  - Opt-in data sharing for training
  - Result export for tracking

## Execution Flow

1. **Load Phase 3 Results**:
   ```python
   roaster = Roaster(daily_limit=50, post_interval=60.0)
   roasts = roaster.load_roasts_from_json("./results/roasts.json")
   ```

2. **Generate Roast Texts**:
   ```python
   enhanced_roasts = []
   for roast in roasts:
       roast_info = generate_roast_text(roast)
       enhanced_roasts.append({**roast, "roast_text": roast_info["roast_text"]})
   ```

3. **Post to X**:
   ```python
   results = await roaster.post_roast_batch(enhanced_roasts, max_posts=50)
   ```

4. **Submit Feedback**:
   ```python
   submitter = FeedbackSubmitter(opt_in_data_share=True)
   feedback_results = await submitter.submit_batch(roasts, max_concurrent=5)
   ```

## Phase 5 Hooks

### Orchestrator Integration
- **Batch Processing**: Ready for Phase 5 orchestrator
- **Result Tracking**: Posted roasts and feedback submissions tracked
- **Error Handling**: Graceful error handling for Phase 5 retry logic
- **Status Reporting**: Results exported for Phase 5 monitoring

### Data Pipeline
- **Roast Data**: JSON format for Phase 5 processing
- **Feedback Data**: Submission results for Phase 5 tracking
- **History Files**: Posted roasts history for Phase 5 resume capability

### Scalability
- **Rate Limiting**: Configurable daily limits and intervals
- **Batch Processing**: Async batch processing for large volumes
- **Concurrent Submissions**: Configurable concurrency for feedback API

## Rate Limits and Constraints

### X (Twitter) API
- **Daily Limit**: 50 posts/day (configurable)
- **Post Interval**: 60 seconds between posts (configurable)
- **Rate Limit Handling**: Automatic via Tweepy wait_on_rate_limit
- **Media Upload**: Supported for images/videos

### xAI Feedback API
- **Rate Limit**: 1 second delay between requests (configurable)
- **Concurrent Requests**: 5 concurrent (configurable)
- **Timeout**: 30 seconds per request
- **Retry Logic**: Not implemented (Phase 5 hook)

## Template Variants

### Warp Roasts
- 5 variants targeting warp scores and rates
- Hailuo comparison emphasis
- Physics violation mentions

### Melt Roasts
- 5 variants targeting melt rates and scores
- Coherence emphasis
- Object deformation mentions

### Combined Roasts
- 5 variants for multiple defects
- Overall quality score emphasis
- Comprehensive defect reporting

### Hailuo Contrast
- 5 variants for positive Hailuo comparison
- Quality gap emphasis
- Competitive shaming

## Viral Shaming Strategy

### Tagging Strategy
- `@xai`: Primary target
- `@grok`: Grok-specific mentions
- `@hailuo_ai`: Competitive comparison
- Hashtags: `#GrokVideo`, `#AIVideo`, etc.

### Content Strategy
- Metrics-based shaming (warp scores, melt rates)
- Timestamp references (e.g., "at 0:07")
- Competitive comparisons (Hailuo vs Grok)
- Quality score emphasis
- Defect count reporting

### Engagement Tactics
- Provocative questions ("Fix or cooked?")
- Direct challenges ("Time to step up?")
- Competitive comparisons ("Hailuo crushes")
- Quality metrics ("Warp score 75.0")

## Data Sharing and Training

### Opt-In Data Share
- **Default**: True (opt-in for training data)
- **Purpose**: Help xAI improve video generation
- **Data**: Scores, notes, video URLs, prompts
- **Privacy**: No sensitive data shared

### Feedback Priority
- **High**: Severe defects (score < 10, warp/melt detected)
- **Normal**: Moderate defects
- **Low**: Minor issues (not typically used)

### Training Data
- **Score**: Overall quality score (0-100)
- **Note**: Roast text or analysis notes
- **Video URL**: Reference to generated video
- **Prompt**: Original generation prompt

