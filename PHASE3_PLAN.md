# Grok Video Torture Chamber - Phase 3 Plan Outline

## Project Structure (Phase 3)
```
grok-vid-improver/
├── detector.py              # Core analyzer: frame extraction, warp, melt detection
├── analysis_utils.py        # Quality metrics: PSNR, SSIM, trajectory, coherence
├── result_processor.py      # Batch processor: Phase 2 integration, CSV export
├── bomber.py                # Phase 2 module (integrated)
├── batch_runner.py          # Phase 2 module (integrated)
└── PHASE3_PLAN.md           # This file
```

## Phase 3 Components

### 1. detector.py
- **Frame Extraction**:
  - `extract_frames()`: MoviePy-based frame extraction
  - Configurable FPS and max_frames
  - BGR format for OpenCV compatibility

- **Warp Detection**:
  - `optical_flow_warp()`: Farneback optical flow method
  - L2 norm calculation for flow magnitude
  - Threshold-based warping detection (default: 50.0)
  - Warp rate calculation (percentage of warped frames)

- **Melt Detection**:
  - `MeltDetector` class: Faster R-CNN for object deformation
  - Pre-trained model with GPU support
  - Confidence threshold for object detection
  - Deformation rate calculation

- **Video Analysis**:
  - `analyze_video()`: Complete video analysis pipeline
  - `analyze_video_async()`: Async wrapper with download
  - Combines warp and melt detection
  - Defect counting and flagging

### 2. analysis_utils.py
- **Quality Metrics**:
  - `calculate_psnr()`: Peak Signal-to-Noise Ratio
  - `calculate_ssim()`: Structural Similarity Index
  - `calculate_coherence_score()`: Frame-to-frame coherence
  - `detect_trajectory_inconsistency()`: Optical flow tracking

- **Scoring**:
  - `calculate_overall_quality_score()`: Weighted quality score
  - `flag_roast()`: Roast flagging based on thresholds
  - Configurable weights for different metrics

- **Statistics**:
  - `calculate_metrics_summary()`: Batch statistics
  - Average scores, defect counts, roast counts

### 3. result_processor.py
- **ResultProcessor Class**:
  - `__init__()`: Initialize with thresholds and concurrency
  - `_analyze_single_result()`: Analyze single Phase 2 result
  - `process_batch()`: Batch processing with async workers
  - `export_to_csv()`: CSV export with all metrics
  - `export_roasts()`: JSON export for roast-flagged results
  - `generate_summary()`: Summary statistics export

- **Batch Processing**:
  - Async semaphore for concurrency control
  - Shared melt detector for efficiency
  - Error handling and status tracking
  - Integration with Phase 2 results

- **Export Formats**:
  - CSV: Full results with all metrics
  - JSON: Roast-flagged results for Phase 4
  - JSON: Summary statistics

## Execution Flow

1. **Phase 2 Integration**:
   ```python
   # Load Phase 2 results
   results = load_phase2_results()
   
   # Process with detector
   processor = ResultProcessor(max_concurrent=10)
   analyzed = await processor.process_batch(results)
   ```

2. **Analysis Pipeline**:
   - Download video from URL
   - Extract frames (MoviePy)
   - Calculate warp score (optical flow)
   - Detect melting (Faster R-CNN)
   - Calculate quality metrics (PSNR, SSIM)
   - Flag for roasting

3. **Export Results**:
   ```python
   # Export to CSV
   csv_path = processor.export_to_csv(analyzed)
   
   # Export roasts
   roast_path = processor.export_roasts(analyzed)
   
   # Generate summary
   summary = processor.generate_summary(analyzed)
   ```

## Phase 4 Hooks

### X Integration
- **Roast Data**: JSON export with roast-flagged results
- **Metrics**: Quality scores for comparison (e.g., 40% warp rate vs. Kling)
- **Timestamps**: Analysis timestamps for tracking
- **Viral Shaming**: Data structure ready for X API integration

### Data Export
- **CSV Format**: Full results for analysis
- **JSON Format**: Roast data for Phase 4
- **Summary Stats**: Aggregate metrics for reporting

### Scalability
- **GPU Support**: CUDA-enabled Faster R-CNN
- **Async Processing**: Concurrent video analysis
- **Batch Processing**: Efficient handling of large batches
- **Memory Management**: Temporary file cleanup

## Performance Targets

- **Throughput**: 10-50 concurrent video analyses (GPU-dependent)
- **Accuracy**: Warp detection threshold: 50.0, Melt rate threshold: 0.3
- **Memory**: Efficient frame processing with configurable limits
- **Scalability**: Ready for multi-GPU Phase 4 integration

## Metrics and Thresholds

### Warp Detection
- **Threshold**: 50.0 (optical flow magnitude)
- **Warp Rate**: Percentage of frames with high flow
- **Flag**: `is_warped` if average warp_score > threshold

### Melt Detection
- **Confidence Threshold**: 0.7 (object detection)
- **Deform Threshold**: 0.3 (deformation rate)
- **Flag**: `is_melted` if melt_rate > deform_threshold

### Roast Flagging
- **Overall Score Threshold**: 5.0 (default)
- **Warp Threshold**: 100.0 (severe warping)
- **Melt Threshold**: 0.5 (severe melting)
- **Flag**: `should_roast` if any condition met

