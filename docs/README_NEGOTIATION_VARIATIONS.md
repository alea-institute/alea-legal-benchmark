# Negotiation Variation Generation

This system generates simulated negotiation data from legal contract clauses using pydantic-ai and structured reasoning with compact notation.

## Quick Start

### Generate Variations

```bash
# Test run (5 samples, sequential)
uv run python alea_legal_benchmark/contracts/generate_negotiation_variations_v3.py \
  --max-samples 5

# Test run (5 samples, parallel with 3 workers)
uv run python alea_legal_benchmark/contracts/generate_negotiation_variations_v3.py \
  --max-samples 5 \
  --max-workers 3

# Full dataset (10,001 clauses)
# Sequential: ~6-7 days
# Parallel (10 workers): ~5-6 hours! 🚀
uv run python alea_legal_benchmark/contracts/generate_negotiation_variations_v3.py \
  --output-name variations_v3_full.jsonl \
  --max-workers 10

# Custom batch
uv run python alea_legal_benchmark/contracts/generate_negotiation_variations_v3.py \
  --start-offset 1000 \
  --max-samples 500 \
  --max-workers 10 \
  --output-name batch_1000-1500.jsonl

# Resume from crash or interruption (automatic deduplication)
uv run python alea_legal_benchmark/contracts/generate_negotiation_variations_v3.py \
  --output-name variations_v3_full.jsonl \
  --max-workers 10
```

### Inspect Results

```bash
# View first sample
uv run python alea_legal_benchmark/contracts/inspect_reasoning.py \
  samples/contracts/negotiation_variations_v3/variations_v3_full.jsonl \
  --sample 0

# View all samples in file
uv run python alea_legal_benchmark/contracts/inspect_reasoning.py \
  samples/contracts/negotiation_variations_v3/variations_v3_full.jsonl
```

## Output Format

Each record contains:

```json
{
  "original_clause_data": {
    "clause": "...",
    "date": "2014-09-03",
    "area_of_law": "Corporate Governance",
    "location": "Abruzzo",
    "industry": "Information",
    "clause_type": "Non Solicitation Agreement Clause"
  },
  "negotiation_analysis": {
    "original_clause": "...",
    "context": {
      "observer_role": "Party B (Weaker)",
      "observer_interests": "..."
    },
    "variations": [
      {
        "variation_id": "A",
        "variation_text": "...",
        "rank": 1,
        "value_score": 90.0,
        "analysis": {
          "key_claims": [
            {
              "claim_text": "...",
              "confidence": "certain",
              "attitude": "approve",
              "claim_type": "fact",
              "evidence_summary": "..."
            }
          ],
          "key_advantages": ["...", "..."],
          "key_disadvantages": ["..."],
          "enforceability_risk": "low",
          "business_risk": "low",
          "explanation": "..."
        }
      }
    ],
    "comparative_reasoning": {
      "key_tradeoffs": ["...", "..."],
      "strategic_recommendations": ["...", "..."],
      "overall_assessment": "..."
    }
  },
  "timestamp": "2025-11-18T09:19:57.187819"
}
```

## Features

### Multi-Perspective Analysis
- Automatically selects observer role based on clause type
- Common roles: Landlord/Tenant, Employer/Employee, Buyer/Seller, etc.
- Consistent perspective throughout analysis

### Structured Reasoning
Each variation includes:
- **2-5 ReasoningClaims** with:
  - `confidence`: certain, high, moderate, low, very_low
  - `attitude`: approve, disapprove, mixed, neutral
  - `claim_type`: fact, value, policy, preference
  - `evidence_summary`: cited sources
- **Key advantages/disadvantages**
- **Risk assessments** (enforceability + business)
- **Prose explanation**

### Compact Notation Support
The structured data maps to compact notation:

```
① «Employee» ●⬇ ⧈ "24-month restriction limits mobility" ⊢ ⚖️★★★
② «Employee» ●⬆ ⏵ "Negotiate down to 12 months" ⊢ ① ⟶ ②
```

See `REASONING_NOTATION_GUIDE.md` for full notation reference.

## Files

### Production Generator
- `generate_negotiation_variations_v3.py`: LLM-friendly schema (use this!)

### Experimental
- `generate_negotiation_variations.py`: v1 baseline
- `generate_negotiation_variations_v2.py`: v2 with full structured notation (validation failures)

### Utilities
- `reasoning_models.py`: Pydantic models for structured reasoning
- `inspect_reasoning.py`: CLI for viewing generated reasoning

### Documentation
- `REASONING_NOTATION_GUIDE.md`: Complete notation reference
- `GENERATION_STATUS.md`: Current generation progress

## Performance

### Sequential Mode
- **v3 (current)**: 5/5 test samples succeeded, ~60-70s average per sample
- **Estimated time**: ~6-7 days for 10,001 clauses
- **Model**: gpt-5-mini via OpenAI API

### Parallel Mode (NEW! 🚀)
- **Test results**: 10/10 samples in 2:47 (167s) with 5 workers
- **Wallclock time**: ~17s per sample (5x throughput)
- **Speedup**: ~3.6-4.2x with 5 workers
- **Estimated time (10 workers)**: ~5-6 hours for 10,001 clauses!
- **Features**:
  - asyncio.Semaphore for concurrency control
  - Thread-safe file writes with asyncio.Lock
  - Works with resume mode
  - Backward compatible (defaults to sequential)

## Monitoring

```bash
# Check progress
tail -f generation_full.log

# Count completed
wc -l samples/contracts/negotiation_variations_v3/variations_v3_full.jsonl

# Check process
ps aux | grep generate_negotiation_variations_v3

# View sample
head -n 1 samples/contracts/negotiation_variations_v3/variations_v3_full.jsonl | python3 -m json.tool
```

## Data Quality

### Strengths
- ✅ Consistent observer perspective
- ✅ Variations maintain context (location, industry, etc.)
- ✅ Both structured reasoning and prose explanations
- ✅ Strategic analysis with evidence citations
- ✅ Ranked and scored variations

### What Gets Generated
For each clause, you get:
1. **Observer context**: Who's analyzing (role + interests)
2. **2-4 variations**: Different negotiation positions
3. **Per-variation analysis**:
   - Low-level reasoning (structured claims)
   - High-level synthesis (prose)
   - Pros/cons enumeration
   - Risk assessment
4. **Comparative analysis**: Cross-variation strategic guidance

## Version History

| Version | Status | Test Results | Notes |
|---------|--------|--------------|-------|
| v1 | ✅ Working | 10/10 succeeded, ~52s | Baseline without reasoning framework |
| v2 | ❌ Failed | 0/5 validation errors | Full structured notation too complex for LLM |
| v3 | ✅ Production | 5/5 succeeded, ~73s | Simplified schema, captures notation semantics |

## License

See main repository LICENSE. Data generated with Llama 3.1 405B; negotiation variations with gpt-5-mini.
