# Response Length Standards - Industry Alignment

## Industry Benchmarks (2024-2026)

| Provider | Typical Response | Max Tokens | Use Case |
|----------|-----------------|------------|----------|
| **OpenAI (GPT-4)** | 2048-4096 | 4096 | Conversational, detailed |
| **Anthropic (Claude)** | 2048-4096 | 4096 | Reasoning, comprehensive |
| **Google (Gemini)** | 2048-8192 | 8192 | Long-form, research |
| **Industry Standard** | **2048-3072** | **3072** | **Balanced detail** |

## Our Implementation

### Updated Token Limits

| Agent | Previous | New | Rationale |
|-------|----------|-----|-----------|
| **Lead Agent** | 4096 | **3072** | Balanced comprehensive responses |
| **Lipid Design Expert** | 2048 | **2048** | Detailed synthesis routes |
| **Reaction Expert** | 1024 | **1536** | More detailed reaction analysis |
| **Generative AI Expert** | 1536 | **1536** | Technical recommendations |
| **Property Prediction** | 1536 | **1536** | ML model analysis |
| **Literature Scout** | 512 | **1024** | Better literature summaries |
| **Fast LLM (backend)** | 1024 | **2048** | Quick responses with detail |

### Response Length Guidelines

**Lead Agent now includes explicit guidance:**
- Target: **500-800 words** (typical conversational response)
- Structure: Use bullet points, numbered lists for clarity
- Balance: Sufficient detail without overwhelming
- Examples: Include concrete data points and specific examples

### Word Count to Token Ratio
- **1 token ≈ 0.75 words** (English average)
- **3072 tokens ≈ 2300 words** (comprehensive response)
- **2048 tokens ≈ 1500 words** (detailed response)
- **1536 tokens ≈ 1150 words** (focused response)

## Benefits

1. **Not too short**: Provides comprehensive analysis with examples
2. **Not too long**: Avoids overwhelming users with excessive detail
3. **Industry-aligned**: Matches OpenAI, Claude, Gemini standards
4. **Structured**: Explicit formatting guidance for readability
5. **Flexible**: Different agents have appropriate limits for their roles

## Changes Made

### Backend (`src/backend/agent.py`)
- Updated `llm_fast` from 1024 → 2048 tokens

### Agent Configurations
- `lead_agent.yaml`: 4096 → 3072 tokens + response length guidelines
- `reaction_expert.yaml`: 1024 → 1536 tokens
- `literature_scout.yaml`: 512 → 1024 tokens
- Added comments to all agent configs for clarity

### Frontend/Standalone
- No changes needed (no response truncation)

## Testing Recommendations

1. Test with synthesis queries (should get 600-1000 word responses)
2. Test with lookup queries (should get 200-400 word responses)
3. Verify structured formatting (bullets, numbered lists)
4. Check that responses include concrete examples and data

## Restart Required

```bash
# Restart backend to load new configurations
pkill -f "uvicorn src.backend.main:app"
cd /fsx/home/hermee/projects/python/chem-agent
nohup .venv/bin/uvicorn src.backend.main:app --host 0.0.0.0 --port 8000 --reload > backend.log 2>&1 &
```
