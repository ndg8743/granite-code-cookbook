# IBM Granite Models Selection Guide

Reference: [IBM Granite Collections](https://huggingface.co/ibm-granite/collections)

## Model Families Overview

### Granite 4.0 Series (Latest)
- **granite-4.0-micro** (3B) - Fast, efficient, newest architecture
- **granite-4.0-h-micro** (3B) - Optimized variant
- **Best for**: Fast responses, simple tasks, low latency requirements

### Granite 3.3 Series (Stable, Recommended)
- **granite-3.3-2b-instruct** (3B) - Small, efficient
- **granite-3.3-8b-instruct** (8B) - High quality, complex tasks
- **Best for**: Production use, well-tested, good balance

### Granite 3.2 Series
- **granite-3.2-2b-instruct** (3B)
- **granite-3.2-8b-instruct** (8B)
- **Best for**: Stable alternative to 3.3

### Granite 3.1 Series (What we used for GPFS)
- **granite-3.1-2b-instruct** (3B) - Used in GPFS example
- **granite-3.1-8b-instruct** (8B)
- **Best for**: Proven, 128K context length

### Granite 3.0 Series
- **granite-3.0-2b-instruct** (3B)
- **granite-3.0-8b-instruct** (8B)
- **Best for**: Older but stable

### Specialized Models

#### Code Models
- **granite-3b-code-base-2k** (3B) - Optimized for code
- **granite-3b-code-base-128k** (3B) - Long context code
- **Best for**: Code generation, code understanding

#### Vision Models
- **granite-vision-3.3-2b** (3B) - Multimodal
- **Best for**: Image-to-text, document understanding

#### Speech Models
- **granite-speech-3.3-2b/8b** - ASR
- **Best for**: Speech recognition

## Selection Criteria

### Use 3B Models When:
- Fast response time needed (<2s)
- Simple Q&A tasks
- Limited GPU memory
- High throughput requirements
- Documentation lookups
- Light tool use

### Use 8B Models When:
- Complex reasoning needed
- Multi-step workflows
- Heavy tool orchestration
- Code generation quality critical
- Infrastructure operations
- High accuracy requirements

### Use Code Models When:
- Primary task is code generation
- Code review and analysis
- API integration
- Script writing

### Use 4.0 Models When:
- Want latest architecture
- Can accept newer/less tested models
- Need maximum efficiency

### Use 3.3 Models When:
- Production deployment
- Need proven stability
- Community support important
- Best balance of quality/speed

## Recommended Agent Model Mapping

| Agent | Recommended Model | Alternative | Reason |
|-------|------------------|-------------|--------|
| Documentation | granite-4.0-micro | granite-3.3-2b-instruct | Fast, efficient |
| Code | granite-3b-code-base-2k | granite-3.3-8b-instruct | Code-optimized |
| Infrastructure | granite-3.3-8b-instruct | granite-3.1-8b-instruct | Complex workflows |
| Research | granite-4.0-h-micro | granite-3.3-2b-instruct | Efficient analysis |
| Communication | granite-4.0-micro | granite-3.3-2b-instruct | Fast writing |

## Context Length Considerations

- **2K context**: Most models (sufficient for most tasks)
- **128K context**: granite-3.1-* models (for very long documents)
- **Code 128K**: granite-3b-code-base-128k (for large codebases)

## Licensing

All Granite models are licensed under **Apache 2.0** - free for commercial use.

## Performance Notes

- **3B models**: ~2-4GB VRAM (with 4-bit quantization)
- **8B models**: ~6-10GB VRAM (with 4-bit quantization)
- **Training speed**: 3B ~2x faster than 8B
- **Quality**: 8B generally 15-30% better on complex tasks
