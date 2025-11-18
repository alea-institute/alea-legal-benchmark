"""
Generate negotiation variations with simplified structured reasoning (v3).

Lessons from v2:
- Fully structured output was too complex for LLM to generate reliably
- All 5/5 samples failed validation ("Exceeded maximum retries")

v3 approach:
- Use string fields with notation guidance
- Parse notation strings post-hoc if needed
- Focus on LLM-friendly structure that still captures reasoning
"""

import asyncio
import json
import os
import hashlib
from pathlib import Path
from typing import List, Set
from datetime import datetime, UTC

from pydantic import BaseModel, Field
from pydantic_ai import Agent
import tqdm


# ============================================================================
# Simplified Models (LLM-Friendly)
# ============================================================================


class ReasoningClaim(BaseModel):
    """A single claim/belief with notation elements."""

    claim_text: str = Field(description="The proposition in natural language")
    # Simplified epistemic markers
    confidence: str = Field(
        description="Confidence level: certain, high, moderate, low, very_low"
    )
    attitude: str = Field(
        description="Normative stance: approve, disapprove, mixed, neutral"
    )
    claim_type: str = Field(description="Type: fact, value, policy, preference")
    evidence_summary: str = Field(
        description="Brief summary of evidence supporting this claim (e.g., 'case law + industry practice')"
    )


class ClauseVariationAnalysis(BaseModel):
    """Analysis of a single variation."""

    # Key reasoning claims (2-5)
    key_claims: List[ReasoningClaim] = Field(
        description="2-5 key claims explaining this variation",
        min_length=2,
        max_length=5,
    )

    # Quick assessments
    key_advantages: List[str] = Field(
        description="2-3 main advantages from observer's perspective",
        min_length=1,
        max_length=4,
    )
    key_disadvantages: List[str] = Field(
        description="2-3 main disadvantages from observer's perspective",
        min_length=0,
        max_length=4,
    )

    # Risk assessment
    enforceability_risk: str = Field(
        description="Risk level: very_low, low, moderate, high, very_high"
    )
    business_risk: str = Field(
        description="Risk level: very_low, low, moderate, high, very_high"
    )

    # Prose synthesis
    explanation: str = Field(
        description="Natural language explanation synthesizing the reasoning"
    )


class ClauseVariation(BaseModel):
    """A variation of the original clause."""

    variation_id: str = Field(description="A, B, C, or D")
    variation_text: str = Field(
        description="Modified clause text inspired by the original"
    )
    rank: int = Field(description="1 (most preferred) to N (least preferred)")
    value_score: float = Field(description="Score 0-100", ge=0, le=100)
    analysis: ClauseVariationAnalysis


class NegotiationContext(BaseModel):
    """Observer perspective."""

    observer_role: str
    observer_interests: str


class ComparativeReasoning(BaseModel):
    """Cross-variation comparison."""

    key_tradeoffs: List[str] = Field(
        description="2-4 key tradeoffs between variations", min_length=2, max_length=5
    )
    strategic_recommendations: List[str] = Field(
        description="2-3 strategic recommendations", min_length=2, max_length=4
    )
    overall_assessment: str = Field(
        description="Overall strategic assessment comparing all variations"
    )


class NegotiationAnalysisV3(BaseModel):
    """Complete analysis with simplified reasoning."""

    original_clause: str
    context: NegotiationContext
    variations: List[ClauseVariation] = Field(min_length=2, max_length=4)
    comparative_reasoning: ComparativeReasoning


# ============================================================================
# Agent Creation
# ============================================================================


def create_negotiation_agent_v3() -> Agent:
    """Create LLM-friendly negotiation agent."""

    system_prompt = """
You are an expert legal negotiation advisor analyzing contract clauses from different stakeholder perspectives.

## Your Task

1. Choose an observer perspective (landlord, tenant, employer, employee, buyer, seller, etc.)
2. Generate 2-4 clause variations representing different negotiation positions
3. For each variation, provide structured reasoning
4. Compare variations and give strategic recommendations

## Reasoning Framework

Your reasoning will be guided by a notation system. You don't need to output the symbols,
but structure your thinking this way:

### Confidence Levels:
- certain: ⬤ Absolutely sure
- high: ● Strongly believe
- moderate: ◐ Leaning toward
- low: ◌ Unsure
- very_low: ○ Very doubtful

### Attitudes:
- approve: ⬆ Good for observer
- disapprove: ⬇ Bad for observer
- mixed: ⇆ Depends on context
- neutral: ⟂ No judgment

### Claim Types:
- fact: ⧈ Empirical/factual
- value: ⚖ Ethical/normative judgment
- policy: ⏵ Recommendation/strategy
- preference: ✦ Personal taste

## For Each Variation

Provide 2-5 ReasoningClaims covering:
- **FACTUAL claims** about what the variation does (duration, scope, obligations, etc.)
  - Use confidence: high or certain
  - Use claim_type: fact
  - Evidence: cite legal precedent, statute, industry practice, data, etc.

- **VALUE claims** about whether those features are good/bad for the observer
  - Use confidence based on how clear the impact is
  - Use attitude: approve or disapprove
  - Use claim_type: value
  - Evidence: reference risk analysis, economic factors, case outcomes

- **POLICY claims** about strategic recommendations
  - Use claim_type: policy
  - Evidence: tie back to the factual and value claims

## Example Structure

For an employment non-solicitation clause from Employee perspective:

Variation A (12-month restriction):
  Claim 1:
    - claim_text: "12-month post-term restriction limits job mobility"
    - confidence: certain (it clearly does this)
    - attitude: disapprove (bad for employee)
    - claim_type: fact
    - evidence_summary: "statute + case law on non-solicitation enforceability"

  Claim 2:
    - claim_text: "12 months is within typical enforceability range"
    - confidence: high
    - attitude: neutral
    - claim_type: fact
    - evidence_summary: "industry practice data + case law on reasonableness"

  Claim 3:
    - claim_text: "This duration balances protection with mobility"
    - confidence: moderate
    - attitude: mixed
    - claim_type: value
    - evidence_summary: "risk assessment of litigation vs. career impact"

## Key Principles

1. **Be specific**: Concrete facts about duration, scope, remedies, etc.
2. **Show your work**: Connect facts → values → policy recommendations
3. **Cite evidence types**: legal precedent, statute, industry practice, economic analysis, risk assessment
4. **Think strategically**: What would each party push for in negotiation?
5. **Be realistic**: Consider enforceability, business impact, negotiation leverage

Remember: You're analyzing from ONE perspective consistently, showing why different variations matter to that stakeholder.
"""

    model = os.environ.get("OPENAI_MODEL", "gpt-5-mini")

    agent = Agent(
        model=f"openai:{model}",
        output_type=NegotiationAnalysisV3,
        system_prompt=system_prompt,
    )

    return agent


def select_observer_context(clause_data: dict) -> str:
    """Generate context hints."""
    clause_type = clause_data.get("clause_type", "Unknown")

    if (
        "landlord" in clause_type.lower()
        or "tenant" in clause_type.lower()
        or "lease" in clause_type.lower()
    ):
        hints = ["Landlord", "Tenant"]
    elif (
        "employment" in clause_type.lower()
        or "non-compete" in clause_type.lower()
        or "non-solicitation" in clause_type.lower()
    ):
        hints = ["Employer", "Employee"]
    elif "vendor" in clause_type.lower() or "supplier" in clause_type.lower():
        hints = ["Buyer", "Seller"]
    elif "confidentiality" in clause_type.lower() or "nda" in clause_type.lower():
        hints = ["Disclosing Party", "Receiving Party"]
    elif "indemnification" in clause_type.lower():
        hints = ["Indemnitor", "Indemnitee"]
    else:
        hints = ["Party A (Stronger)", "Party B (Weaker)"]

    return f"Observer options: {', '.join(hints)}"


def compute_clause_hash(clause_data: dict) -> str:
    """
    Compute a unique hash for a clause based on its content.

    Uses blake2b for fast hashing of clause text + metadata.
    """
    # Create a stable string representation
    hash_input = f"{clause_data.get('clause', '')}"
    hash_input += f"|{clause_data.get('date', '')}"
    hash_input += f"|{clause_data.get('area_of_law', '')}"
    hash_input += f"|{clause_data.get('location', '')}"
    hash_input += f"|{clause_data.get('industry', '')}"
    hash_input += f"|{clause_data.get('clause_type', '')}"

    return hashlib.blake2b(hash_input.encode("utf-8"), digest_size=16).hexdigest()


def load_existing_hashes(output_file: Path) -> Set[str]:
    """
    Load hashes of already-processed clauses from existing output file.

    Returns:
        Set of clause hashes that have already been processed
    """
    existing_hashes = set()

    if not output_file.exists():
        return existing_hashes

    print(f"Loading existing records from {output_file}...")
    try:
        with open(output_file, "r") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                    clause_data = record.get("original_clause_data", {})
                    clause_hash = compute_clause_hash(clause_data)
                    existing_hashes.add(clause_hash)
                except json.JSONDecodeError:
                    print(f"  ⚠️  Skipping malformed line {line_num}")
                    continue
    except Exception as e:
        print(f"  ⚠️  Error loading existing file: {e}")
        return set()

    print(f"  ✅ Loaded {len(existing_hashes)} existing records")
    return existing_hashes


def generate_variations_for_clause(clause_data: dict, agent: Agent) -> dict:
    """Generate variations with simplified reasoning (sync wrapper)."""
    return asyncio.run(generate_variations_for_clause_async(clause_data, agent))


async def generate_variations_for_clause_async(clause_data: dict, agent: Agent) -> dict:
    """Generate variations with simplified reasoning (async)."""

    prompt = f"""
Analyze this clause and generate negotiation variations:

**Clause:**
{clause_data.get("clause", "")}

**Context:**
- Type: {clause_data.get("clause_type")}
- Area of Law: {clause_data.get("area_of_law")}
- Location: {clause_data.get("location")}
- Industry: {clause_data.get("industry")}
- Date: {clause_data.get("date")}

**Observer Selection:**
{select_observer_context(clause_data)}

Generate 2-4 variations with structured reasoning following the framework.
"""

    result = await agent.run(prompt)

    # Compute hash for deduplication
    clause_hash = compute_clause_hash(clause_data)

    return {
        "clause_hash": clause_hash,
        "original_clause_data": clause_data,
        "negotiation_analysis": result.output.model_dump(),
        "timestamp": datetime.now(UTC).isoformat(),
    }


async def process_clauses_async(
    input_file: Path,
    output_file: Path,
    max_samples: int = None,
    start_offset: int = 0,
    resume: bool = True,
    max_workers: int = 10,
):
    """
    Process clauses in parallel with asyncio.

    Args:
        input_file: Input JSONL file with clauses
        output_file: Output JSONL file for results
        max_samples: Maximum number to process (None = all)
        start_offset: Starting index in input
        resume: If True, skip already-processed clauses (default: True)
        max_workers: Maximum concurrent workers (default: 10)
    """

    agent = create_negotiation_agent_v3()

    # Load input clauses
    with open(input_file, "r") as f:
        clauses = [json.loads(line) for line in f]

    if start_offset > 0:
        clauses = clauses[start_offset:]
    if max_samples:
        clauses = clauses[:max_samples]

    print(f"Loaded {len(clauses)} clauses from input")

    # Resume mode: load existing hashes to skip duplicates
    existing_hashes = set()
    if resume:
        existing_hashes = load_existing_hashes(output_file)

        if existing_hashes:
            # Filter out already-processed clauses
            original_count = len(clauses)
            clauses = [
                c for c in clauses if compute_clause_hash(c) not in existing_hashes
            ]
            skipped = original_count - len(clauses)
            print(f"  ✅ Skipping {skipped} already-processed clauses")
            print(f"  📊 Remaining to process: {len(clauses)}")

    if not clauses:
        print("\n✅ All clauses already processed!")
        return

    print(f"\nProcessing {len(clauses)} clauses (v3 - parallel mode)...")
    print(f"Output: {output_file}")
    print(f"Mode: {'APPEND (resume)' if resume else 'WRITE'}")
    print(f"Workers: {max_workers}")

    output_file.parent.mkdir(parents=True, exist_ok=True)

    success_count = 0
    fail_count = 0
    skip_count = len(existing_hashes) if resume else 0

    # Use append mode by default
    mode = "a" if resume or output_file.exists() else "w"

    # Semaphore for concurrency control
    semaphore = asyncio.Semaphore(max_workers)

    # Lock for file writes
    write_lock = asyncio.Lock()

    async def process_one(clause_data: dict):
        """Process a single clause with semaphore control."""
        nonlocal success_count, fail_count, skip_count

        async with semaphore:
            try:
                # Double-check we're not duplicating
                clause_hash = compute_clause_hash(clause_data)
                if clause_hash in existing_hashes:
                    async with write_lock:
                        skip_count += 1
                    return

                result = await generate_variations_for_clause_async(clause_data, agent)

                # Write to file (with lock for thread safety)
                async with write_lock:
                    with open(output_file, mode) as out_f:
                        out_f.write(json.dumps(result) + "\n")
                        out_f.flush()

                    # Track this hash to avoid duplicates
                    existing_hashes.add(clause_hash)
                    success_count += 1

            except Exception as e:
                async with write_lock:
                    fail_count += 1
                    print(f"\nError: {e}")
                    if hasattr(e, "args") and e.args:
                        print(f"Details: {str(e.args[0])[:500]}")

    # Create tasks with progress bar
    tasks = [process_one(clause_data) for clause_data in clauses]

    # Use tqdm for progress tracking
    for coro in tqdm.tqdm(
        asyncio.as_completed(tasks), total=len(tasks), desc="Generating"
    ):
        await coro

    print("\nComplete!")
    print(f"  ✅ Success: {success_count}")
    print(f"  ❌ Failed: {fail_count}")
    if skip_count > 0:
        print(f"  ⏭️  Skipped (already processed): {skip_count}")


def process_clauses(
    input_file: Path,
    output_file: Path,
    max_samples: int = None,
    start_offset: int = 0,
    resume: bool = True,
    max_workers: int = None,
):
    """
    Process clauses with simplified reasoning.

    Args:
        input_file: Input JSONL file with clauses
        output_file: Output JSONL file for results
        max_samples: Maximum number to process (None = all)
        start_offset: Starting index in input
        resume: If True, skip already-processed clauses (default: True)
        max_workers: If set, use parallel processing (default: None = sequential)
    """

    if max_workers:
        # Use async parallel processing
        asyncio.run(
            process_clauses_async(
                input_file=input_file,
                output_file=output_file,
                max_samples=max_samples,
                start_offset=start_offset,
                resume=resume,
                max_workers=max_workers,
            )
        )
        return

    # Sequential processing (original code)
    agent = create_negotiation_agent_v3()

    # Load input clauses
    with open(input_file, "r") as f:
        clauses = [json.loads(line) for line in f]

    if start_offset > 0:
        clauses = clauses[start_offset:]
    if max_samples:
        clauses = clauses[:max_samples]

    print(f"Loaded {len(clauses)} clauses from input")

    # Resume mode: load existing hashes to skip duplicates
    existing_hashes = set()
    if resume:
        existing_hashes = load_existing_hashes(output_file)

        if existing_hashes:
            # Filter out already-processed clauses
            original_count = len(clauses)
            clauses = [
                c for c in clauses if compute_clause_hash(c) not in existing_hashes
            ]
            skipped = original_count - len(clauses)
            print(f"  ✅ Skipping {skipped} already-processed clauses")
            print(f"  📊 Remaining to process: {len(clauses)}")

    if not clauses:
        print("\n✅ All clauses already processed!")
        return

    print(f"\nProcessing {len(clauses)} clauses (v3 - simplified schema)...")
    print(f"Output: {output_file}")
    print(f"Mode: {'APPEND (resume)' if resume else 'WRITE'}")

    output_file.parent.mkdir(parents=True, exist_ok=True)

    success_count = 0
    fail_count = 0
    skip_count = len(existing_hashes) if resume else 0

    # Use append mode by default
    mode = "a" if resume or output_file.exists() else "w"

    with open(output_file, mode) as out_f:
        for clause_data in tqdm.tqdm(clauses, desc="Generating"):
            try:
                # Double-check we're not duplicating (in case of concurrent writes)
                clause_hash = compute_clause_hash(clause_data)
                if clause_hash in existing_hashes:
                    skip_count += 1
                    continue

                result = generate_variations_for_clause(clause_data, agent)
                out_f.write(json.dumps(result) + "\n")
                out_f.flush()

                # Track this hash to avoid duplicates in this session
                existing_hashes.add(clause_hash)
                success_count += 1

            except Exception as e:
                print(f"\nError: {e}")
                # Print first 500 chars for debugging
                if hasattr(e, "args") and e.args:
                    print(f"Details: {str(e.args[0])[:500]}")
                fail_count += 1

    print("\nComplete!")
    print(f"  ✅ Success: {success_count}")
    print(f"  ❌ Failed: {fail_count}")
    if skip_count > 0:
        print(f"  ⏭️  Skipped (already processed): {skip_count}")


def main():
    """Main entry."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate negotiation variations with resume support and parallel processing"
    )
    parser.add_argument(
        "--max-samples", type=int, default=None, help="Max samples (None = all)"
    )
    parser.add_argument("--start-offset", type=int, default=0, help="Starting index")
    parser.add_argument("--output-name", type=str, default=None, help="Output filename")
    parser.add_argument(
        "--no-resume",
        action="store_true",
        help="Disable resume mode (overwrite output file)",
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=None,
        help="Enable parallel processing with N workers (default: None = sequential)",
    )
    args = parser.parse_args()

    project_root = Path(__file__).parent.parent.parent
    input_file = (
        project_root / "samples" / "contracts" / "soli_clauses_001" / "all.jsonl"
    )

    output_dir = project_root / "samples" / "contracts" / "negotiation_variations_v3"

    if args.output_name:
        output_file = output_dir / args.output_name
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"variations_v3_{timestamp}.jsonl"

    print("=" * 70)
    print("v3: Negotiation Variations with Structured Reasoning")
    print("=" * 70)
    print()

    process_clauses(
        input_file=input_file,
        output_file=output_file,
        max_samples=args.max_samples,
        start_offset=args.start_offset,
        resume=not args.no_resume,
        max_workers=args.max_workers,
    )


if __name__ == "__main__":
    main()
