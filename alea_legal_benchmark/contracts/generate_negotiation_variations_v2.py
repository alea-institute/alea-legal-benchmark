"""
Generate negotiation variations with structured reasoning (v2).

Enhanced version that uses structured reasoning models with compact notation support.
"""

import json
import os
from pathlib import Path
from typing import List
from datetime import datetime, UTC

from pydantic import BaseModel, Field
from pydantic_ai import Agent
import tqdm

# Import our reasoning models
from reasoning_models import (
    ClauseVariationReasoning,
    ComparativeAnalysis,
)


# ============================================================================
# Output Models
# ============================================================================


class ClauseVariation(BaseModel):
    """A variation of the original clause with structured reasoning."""

    variation_id: str = Field(description="Short identifier (A, B, C, D)")
    variation_text: str = Field(
        description="The modified clause text, inspired by but not identical to the original"
    )
    rank: int = Field(
        description="Rank from 1 (most preferred) to N (least preferred) for this observer"
    )
    value_score: float = Field(
        description="Numeric value score from 0-100 representing preference strength",
        ge=0,
        le=100,
    )

    # Enhanced: structured reasoning
    reasoning: ClauseVariationReasoning = Field(
        description="Structured reasoning explaining why this variation is ranked as it is"
    )


class NegotiationContext(BaseModel):
    """The observer perspective/persona for negotiation."""

    observer_role: str = Field(
        description="The role/perspective taken (e.g., 'Landlord', 'Tenant', 'Buyer', 'Seller')"
    )
    observer_interests: str = Field(
        description="Key interests and priorities of this observer"
    )


class NegotiationAnalysisV2(BaseModel):
    """Complete negotiation analysis with structured reasoning."""

    original_clause: str = Field(description="The original clause text for reference")
    context: NegotiationContext = Field(
        description="The observer perspective used for this analysis"
    )
    variations: List[ClauseVariation] = Field(
        description="List of 2-4 clause variations with structured reasoning",
        min_length=2,
        max_length=4,
    )

    # Enhanced: comparative analysis across all variations
    comparative_analysis: ComparativeAnalysis = Field(
        description="Structured reasoning comparing all variations and explaining strategic choices"
    )


# ============================================================================
# Agent Creation
# ============================================================================


def create_negotiation_agent_v2() -> Agent:
    """
    Create enhanced pydantic-ai agent for generating negotiation variations with structured reasoning.
    """

    system_prompt = """
You are an expert legal negotiation advisor with deep knowledge of contract drafting and negotiation strategy.

Your task is to analyze a clause from multiple perspectives and generate negotiation variations with STRUCTURED REASONING.

## Reasoning Notation System

Your structured reasoning will be rendered in a compact notation for analysis. Understanding the notation will help you structure claims properly:

### Belief Strength (Epistemic Confidence):
- certain_true → ⬤  (Certain it's true)
- strong_true → ●  (Strongly believe true)
- lean_true → ◐  (Leaning toward true)
- undecided → ◌  (Unsure)
- lean_false → ◑  (Leaning toward false)
- certain_false → ○  (Certain it's false)

### Value Attitude (Normative Stance):
- approve → ⬆  (Approve/good from this perspective)
- disapprove → ⬇  (Disapprove/bad from this perspective)
- mixed → ⇆  (Mixed/depends on context)
- neutral → ⟂  (No value judgment)

### Claim Types:
- fact → ⧈  (Factual/empirical claim)
- value → ⚖  (Value/ethical judgment)
- policy → ⏵  (Policy/action recommendation)
- preference → ✦  (Personal preference)

### Evidence Sources:
- legal_precedent → ⚖️  (Case law)
- statute → 📜  (Statutory law)
- data → 📊  (Empirical data/statistics)
- industry_practice → 🏢  (Industry standards)
- economic → 💰  (Economic analysis)
- risk → ⚠  (Risk assessment)
- theory → 📚  (Legal theory/doctrine)
- observation → 👁  (Direct observation)
- testimony → 🗣  (Expert testimony)

### Evidence Strength:
- very_strong → ★★★  (Well-established, authoritative)
- strong → ★★  (Solid, reliable)
- weak → ★  (Suggestive, limited)
- very_weak → ☆  (Anecdotal, speculative)

### Argument Relations:
- supports → ⟶  (Claim A supports/strengthens claim B)
- attacks → ⟞  (Claim A undermines/challenges claim B)
- explains → ⇢  (Claim A explains why claim B)
- equivalent → ⟺  (Claims are equivalent/mutually reinforcing)

### Example Notation:
```
① «Employer» ●⬆ ⧈ "12-month restriction is industry standard" ⊢ 🏢★★ ⋀ 📊★
② «Employer» ●⬆ ⚖ "Industry standards suggest reasonableness" ⊢ ⚖️★★★
③ «Employer» ●⬆ ⏵ "Should adopt 12-month term" ⊢ ① ⋀ ②

Links:
① ⟶ ③  // Industry practice supports policy choice
② ⟶ ③  // Legal reasonableness supports policy choice
```

This maps to the structured data you'll generate. Use this to guide your reasoning!

## Process:

1. **Understand context**: Area of law, location, industry, clause type
2. **Adopt observer perspective**: Choose a stakeholder role (landlord, tenant, employer, employee, buyer, seller, etc.)
3. **Generate 2-4 variations**: Each representing a meaningful negotiation position
4. **Structure reasoning**: For EACH variation, provide:
   - 2-5 StrategicClaims with:
     * claim_id: Simple ID like "①", "②", "A1", "A2"
     * agent: Who holds this view (use the observer_role)
     * proposition: The actual claim in natural language
     * belief: How confident (certain_true, strong_true, lean_true, undecided, lean_false, certain_false)
     * value: Attitude (approve, disapprove, mixed, neutral)
     * claim_type: Type (fact, value, policy, preference)
     * evidence: List of evidence citations with source and strength
   - ArgumentLinks: Show how claims support/attack each other
   - prose_summary: Natural language synthesis

5. **Comparative analysis**: Create a reasoning chain comparing ALL variations

## Reasoning Structure Guidelines:

### For Each Variation:
```
Claim ①: [FACTUAL claim about what this variation does]
  - belief: strong_true (you're confident this is what it does)
  - claim_type: fact
  - evidence: legal_precedent, statute, industry_practice, etc.

Claim ②: [VALUE claim about whether that's good/bad for observer]
  - belief: strong_true
  - value: approve or disapprove
  - claim_type: value

Claim ③: [POLICY claim about strategic recommendation]
  - belief: lean_true or strong_true
  - claim_type: policy

Links: ① ⟶ ② ⟶ ③  (facts support values, values support policy)
```

### Evidence Sources to Use:
- legal_precedent: Case law supporting enforceability/interpretation
- statute: Statutory requirements or prohibitions
- industry_practice: Standard practices in this industry
- economic: Cost/benefit analysis
- risk: Risk assessment (litigation risk, business risk, etc.)
- data: Empirical data or statistics
- theory: Legal theory or doctrine
- observation: Common observed patterns

### Evidence Strength:
- very_strong: Well-established, multiple sources
- strong: Solid evidence, reliable sources
- weak: Suggestive but not conclusive
- very_weak: Anecdotal or speculative

## Key Principles:

1. **Be specific**: Claims should be concrete, not vague
2. **Show confidence**: Use belief strength appropriately
3. **Cite evidence**: Each claim needs evidence support
4. **Map arguments**: Use links to show reasoning structure
5. **Think strategically**: Consider negotiation dynamics, not just legal correctness

## Example Reasoning Structure:

For a non-solicitation clause from Employer perspective:

Variation A (12-month restriction):
  Claim ①: "12-month duration is standard in tech industry"
    - belief: strong_true, claim_type: fact
    - evidence: industry_practice (strong), data (weak)
  Claim ②: "Shorter duration reduces enforceability risk"
    - belief: strong_true, claim_type: fact
    - evidence: legal_precedent (very_strong)
  Claim ③: "This provides reasonable protection without litigation risk"
    - belief: strong_true, value: approve, claim_type: value
  Links: ① ⟶ ③, ② ⟶ ③

Remember:
- Each variation should have its own ReasoningChain
- The ComparativeAnalysis should have one ReasoningChain comparing ALL variations
- Use the observer's perspective consistently throughout
"""

    model = os.environ.get("OPENAI_MODEL", "gpt-5-mini")

    agent = Agent(
        model=f"openai:{model}",
        output_type=NegotiationAnalysisV2,
        system_prompt=system_prompt,
    )

    return agent


# ============================================================================
# Context Selection
# ============================================================================


def select_observer_context(clause_data: dict) -> str:
    """Generate context hints for observer selection."""
    clause_type = clause_data.get("clause_type", "Unknown")

    # Map common clause types to typical opposing parties
    if (
        "landlord" in clause_type.lower()
        or "tenant" in clause_type.lower()
        or "lease" in clause_type.lower()
    ):
        context_hints = ["Landlord", "Tenant"]
    elif (
        "employment" in clause_type.lower()
        or "non-compete" in clause_type.lower()
        or "non-solicitation" in clause_type.lower()
    ):
        context_hints = ["Employer", "Employee"]
    elif "vendor" in clause_type.lower() or "supplier" in clause_type.lower():
        context_hints = ["Buyer", "Seller"]
    elif "confidentiality" in clause_type.lower() or "nda" in clause_type.lower():
        context_hints = ["Disclosing Party", "Receiving Party"]
    elif "indemnification" in clause_type.lower():
        context_hints = ["Indemnitor", "Indemnitee"]
    elif "termination" in clause_type.lower():
        context_hints = ["Service Provider", "Client"]
    else:
        context_hints = ["Party A (Stronger Position)", "Party B (Weaker Position)"]

    return f"""
Select ONE observer perspective from: {", ".join(context_hints)}
(or suggest another appropriate role for this {clause_type})

Context: {clause_data.get("area_of_law")}, {clause_data.get("location")}, {clause_data.get("industry")}
"""


# ============================================================================
# Generation
# ============================================================================


def generate_variations_for_clause(clause_data: dict, agent: Agent) -> dict:
    """Generate negotiation variations with structured reasoning."""

    clause_text = clause_data.get("clause", "")

    prompt = f"""
Analyze this clause and generate negotiation variations with STRUCTURED REASONING:

**Original Clause:**
{clause_text}

**Metadata:**
- Clause Type: {clause_data.get("clause_type", "Unknown")}
- Area of Law: {clause_data.get("area_of_law", "Unknown")}
- Location: {clause_data.get("location", "Unknown")}
- Industry: {clause_data.get("industry", "Unknown")}
- Date Context: {clause_data.get("date", "Unknown")}

**Observer Selection:**
{select_observer_context(clause_data)}

**Instructions:**
1. Choose an observer perspective
2. Generate 2-4 variations representing different negotiation positions
3. For EACH variation, provide structured reasoning with:
   - 2-5 strategic claims (facts, values, policies)
   - Evidence citations with sources and strength
   - Argument links showing how claims relate
   - Prose summary synthesizing the reasoning
4. Provide comparative analysis with reasoning chain comparing all variations

Focus on practical negotiation strategy, risk allocation, and enforcability considerations.
"""

    result = agent.run_sync(prompt)

    # Combine original data with analysis
    output = {
        "original_clause_data": clause_data,
        "negotiation_analysis": result.output.model_dump(),
        "timestamp": datetime.now(UTC).isoformat(),
    }

    return output


def process_clauses(
    input_file: Path,
    output_file: Path,
    max_samples: int = None,
    start_offset: int = 0,
):
    """Process clauses and generate structured negotiation variations."""

    agent = create_negotiation_agent_v2()

    with open(input_file, "r") as f:
        clauses = [json.loads(line) for line in f]

    if start_offset > 0:
        clauses = clauses[start_offset:]
    if max_samples:
        clauses = clauses[:max_samples]

    print(f"Processing {len(clauses)} clauses with structured reasoning...")
    print(f"Output: {output_file}")

    output_file.parent.mkdir(parents=True, exist_ok=True)

    success_count = 0
    fail_count = 0

    with open(output_file, "w") as out_f:
        for clause_data in tqdm.tqdm(clauses, desc="Generating variations"):
            try:
                result = generate_variations_for_clause(clause_data, agent)
                out_f.write(json.dumps(result) + "\n")
                out_f.flush()
                success_count += 1
            except Exception as e:
                print(f"\nError: {e}")
                fail_count += 1

    print(f"\nComplete! Success: {success_count}, Failed: {fail_count}")


def main():
    """Main entry point."""
    project_root = Path(__file__).parent.parent.parent
    input_file = (
        project_root / "samples" / "contracts" / "soli_clauses_001" / "all.jsonl"
    )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = project_root / "samples" / "contracts" / "negotiation_variations_v2"
    output_file = output_dir / f"variations_v2_{timestamp}.jsonl"

    print("=" * 70)
    print("Enhanced Negotiation Variation Generator with Structured Reasoning")
    print("=" * 70)
    print()

    # Test with 5 samples first
    process_clauses(
        input_file=input_file,
        output_file=output_file,
        max_samples=5,
        start_offset=0,
    )


if __name__ == "__main__":
    main()
