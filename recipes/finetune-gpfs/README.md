# Fine-tuning Granite on IBM Storage Scale (GPFS)

This recipe demonstrates how to fine-tune the IBM Granite model on IBM Storage Scale (GPFS) documentation to create a domain-specific assistant.

## Overview

We fine-tuned `ibm-granite/granite-3.1-2b-instruct` using qLoRA on GPFS knowledge extracted from:
- 4 IBM GitHub repositories (CSI driver, cloud install, Grafana bridge, container native)
- GPFS diagnostic tools documentation
- Configuration examples and troubleshooting guides

## Results

- **Training Time**: 55.6 seconds (100 steps on RTX 5070 Ti)
- **Loss Reduction**: 3.22 → 1.37 (58% improvement)
- **Token Accuracy**: 47% → 72% (25 point improvement)
- **Dataset**: 29 Q&A pairs (23 train, 6 test)

## Files

- `Finetuning_Granite_GPFS.ipynb` - Main notebook with complete workflow
- `collect_gpfs_data.py` - Script to clone repos and extract documentation
- `generate_qa_pairs.py` - Script to generate Q&A training pairs
- `run_gpfs_finetune.py` - Standalone training script
- `gpfs_dataset.jsonl` - Training dataset (29 Q&A pairs)

## Hardware Requirements

- **GPU**: NVIDIA RTX 5070 Ti or compatible (Blackwell architecture requires PyTorch 2.9.1+cu128)
- **PyTorch**: 2.9.1+cu128 (for Blackwell sm_120 support)
- **Memory**: ~8GB VRAM (with 4-bit quantization)

## Quick Start

1. Install dependencies:
```bash
pip install transformers datasets accelerate bitsandbytes peft trl torch --index-url https://download.pytorch.org/whl/cu128
```

2. Collect data:
```bash
python collect_gpfs_data.py
```

3. Generate Q&A pairs:
```bash
python generate_qa_pairs.py
```

4. Run training:
```bash
python run_gpfs_finetune.py
```

Or use the Jupyter notebook `Finetuning_Granite_GPFS.ipynb` for an interactive experience.

## Model Output Examples

**Before Training:**
```
Q: How do I check network connectivity in GPFS?
A: Use the ping command... (generic networking advice)
```

**After Training:**
```
Q: How do I check network connectivity in GPFS?
A: Use the 'mmlsnet' command to display network connectivity information 
   for all network interfaces. This shows the state of each interface...
```

## Key Learnings

1. **Blackwell GPU Support**: RTX 5070 Ti requires PyTorch 2.9.1+cu128 for proper CUDA kernel support
2. **Small Dataset Training**: Even with 29 samples, the model learned GPFS-specific terminology
3. **qLoRA Efficiency**: 4-bit quantization + LoRA enables training on consumer GPUs
4. **Domain Adaptation**: Model successfully shifted from generic code knowledge to GPFS expertise

## Next Steps

For production deployment:
- Expand dataset to 500+ Q&A pairs
- Train for 500-1000 steps
- Include more troubleshooting scenarios
- Add performance tuning examples
- Evaluate on held-out test set

## References

- [IBM Storage Scale Documentation](https://www.ibm.com/docs/en/storage-scale/6.0.0)
- [PyTorch Blackwell Support Discussion](https://discuss.pytorch.org/t/pytorch-support-for-sm120/216099/67)
- [IBM Spectrum Scale GitHub Repos](https://github.com/IBM?q=spectrum-scale)
