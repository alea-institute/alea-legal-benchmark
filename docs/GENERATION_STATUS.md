# Negotiation Variation Generation - Status

## Generation Run Information

**Started:** 2025-11-18 06:29 UTC
**Dataset:** 10,001 clauses from `soli_clauses_001/all.jsonl`
**Output:** `samples/contracts/negotiation_variations_v3/variations_v3_full.jsonl`
**Model:** gpt-5-mini via pydantic-ai
**Version:** v3 (simplified schema with structured reasoning)

## Performance Estimates

- **Test run:** 5/5 samples succeeded, ~73s average per clause
- **Estimated total time:** ~203 hours (~8.5 days) sequential
- **Estimated cost:** ~$100-200 (gpt-5-mini pricing TBD)

## Output Format

Each record contains:
1. **Original clause data** (clause text + metadata)
2. **Negotiation analysis** with:
   - Observer context (role + interests)
   - 2-4 variations (ranked, scored)
   - For each variation:
     - **Low-level reasoning:** 2-5 structured claims with confidence/attitude/type/evidence
     - **High-level prose:** Strategic explanation
     - Key advantages/disadvantages
     - Risk assessments (enforceability + business)
   - **Comparative reasoning:** Cross-variation analysis + strategic recommendations

## Monitoring Commands

```bash
# Check progress
tail -f generation_full.log

# Count completed records
wc -l samples/contracts/negotiation_variations_v3/variations_v3_full.jsonl

# Check process status
ps aux | grep generate_negotiation_variations_v3

# View recent output
tail -50 generation_full.log

# Estimate completion (after first 100 samples)
# Calculate average time per sample, multiply by remaining
```

## Reasoning Notation Framework

The structured reasoning captures:

### Belief Strength (confidence)
- `certain` → ⬤ (Certain true)
- `high` → ● (Strongly believe true)
- `moderate` → ◐ (Leaning true)
- `low` → ◌ (Unsure)
- `very_low` → ○ (Leaning/certain false)

### Value Attitude (attitude)
- `approve` → ⬆ (Good for observer)
- `disapprove` → ⬇ (Bad for observer)
- `mixed` → ⇆ (Context-dependent)
- `neutral` → ⟂ (No value judgment)

### Claim Types (claim_type)
- `fact` → ⧈ (Empirical/factual)
- `value` → ⚖ (Ethical/normative)
- `policy` → ⏵ (Recommendation)
- `preference` → ✦ (Personal preference)

### Evidence Sources (evidence_summary)
- Legal precedent → ⚖️
- Statute → 📜
- Data/statistics → 📊
- Industry practice → 🏢
- Economic analysis → 💰
- Risk assessment → ⚠
- Theory/literature → 📚
- Observation → 👁
- Testimony → 🗣

## Version History

### v1 (original)
- Basic structure without reasoning framework
- 10/10 test samples succeeded
- ~52s average

### v2 (full structured notation)
- Attempted to generate complete notation structure
- 0/5 test samples (all validation failures)
- Too complex for LLM

### v3 (simplified with reasoning semantics)
- ✅ Current version
- Captures notation semantics as simple strings
- 5/5 test samples succeeded
- ~73s average
- Can render to compact notation post-hoc

## Next Steps

After generation completes:
1. Validate data quality (spot checks)
2. Generate statistics and analysis
3. Create visualization/rendering utilities
4. Upload to dataset repository
5. Document in README
