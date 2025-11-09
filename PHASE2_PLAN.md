# Grok Video Torture Chamber - Phase 2 Plan Outline

## Project Structure (Phase 2)
```
grok-vid-improver/
├── variants_generator.py    # Combinatorial mutators and adversarial traps
├── bomber.py                # Core mutator with async queue integration
├── batch_runner.py          # Async worker pool with GPU dispatch stubs
├── test_api_call.py         # Phase 1 API module (integrated)
└── PHASE2_PLAN.md           # This file
```

## Phase 2 Components

### 1. variants_generator.py
- **Modifier Pools**:
  - Physics traps: zero-G flips, momentum violations, gravity inversion
  - Camera modifiers: dolly+orbit, dolly+warp, orbit+physics_break
  - Coherence traps: emerald sparks, chromatic aberration, texture bleeding
  - Environmental: neon rain, snowstorm, sandstorm
  - Quality: 8K resolution, photorealistic, cinematic lighting

- **Core Functions**:
  - `mutate_prompt()`: Single prompt mutation with strategies
  - `generate_variants()`: Bulk variant generation
  - `generate_combinatorial_variants()`: Full combinatorial approach
  - `create_adversarial_batch()`: Large-scale adversarial batch (10k+)
  - `get_mutation_metadata()`: Extract mutation metadata

- **Strategies**:
  - Random: Random modifier selection
  - Adversarial: Known problematic combinations
  - Combinatorial: Full cross-product of modifiers

### 2. bomber.py
- **Core Functions**:
  - `mutate_and_queue()`: Generate variants and add to async queue
  - `bomber_worker()`: Worker coroutine for queue processing
  - `run_prompt_bombing()`: Full bombing campaign orchestration
  - `test_bomber()`: Small-scale test function

- **Features**:
  - Async queue integration with backpressure
  - Worker pool with configurable concurrency
  - Result collection and logging
  - Phase 1 API integration

### 3. batch_runner.py
- **BatchRunner Class**:
  - `__init__()`: Initialize with concurrency limits and GPU support
  - `_bounded_generate()`: Semaphore-bound generation
  - `run_batch()`: Direct batch execution
  - `run_batch_with_queue()`: Queue-based batch with backpressure
  - `get_statistics()`: Batch processing statistics

- **GPU Dispatch Stubs**:
  - Device allocation functions (round-robin, random, load-balanced)
  - GPU-enabled flag for Phase 3 integration
  - Device ID tracking per prompt

- **Features**:
  - Connection pooling (aiohttp sessions)
  - Rate limiting integration
  - Error handling and statistics
  - Phase 3 hooks for defect detection input

## Execution Flow

1. **Variant Generation**:
   ```python
   variants = create_adversarial_batch(
       base_prompts=["samurai vs T-rex"],
       variants_per_base=100,
       total_target=10000
   )
   ```

2. **Batch Processing**:
   ```python
   runner = BatchRunner(api_key, max_concurrent=100)
   results = await runner.run_batch(variants)
   ```

3. **Test Run**:
   ```python
   await test_bomber(
       base_prompt="samurai vs T-rex",
       variant_count=20,
       test_generations=5
   )
   ```

## Phase 3 Hooks

### Defect Detection Input
- **Warp Detection**: Video URLs passed to Phase 3 detector
- **Metadata Tracking**: Mutation metadata for correlation
- **Batch Results**: Structured results for defect analysis

### GPU Dispatch
- **Device Allocation**: Stub functions ready for Phase 3
- **Load Balancing**: Framework for multi-GPU distribution
- **Memory Monitoring**: Hooks for GPU memory tracking

### Scalability
- **Queue Backpressure**: Configurable queue sizes
- **Worker Pool**: Scalable from 100-1000 concurrent workers
- **Batch Chunking**: Support for very large batches (10k+)

## Performance Targets

- **Throughput**: 100-1000 concurrent generations
- **Rate Limiting**: 1-5s jittered delays (inherited from Phase 1)
- **Memory**: Efficient queue management with backpressure
- **Scalability**: Ready for multi-GPU Phase 3 integration

