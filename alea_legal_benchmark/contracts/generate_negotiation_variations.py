"""
Generate negotiation variations from existing clause data using pydantic-ai.

This script:
1. Loads clause data from JSONL
2. For each clause, generates multiple variations from different negotiation perspectives
3. Ranks each variation by preference/value to the observer
4. Explains the reasoning behind each ranking
5. Outputs structured negotiation data to JSONL

The system uses gpt-5-mini via pydantic-ai for structured generation.
"""

import json
import os
from pathlib import Path
from typing import List
from datetime import datetime

from pydantic import BaseModel, Field
from pydantic_ai import Agent
import tqdm


# Define the structured output models
class ClauseVariation(BaseModel):
    """A variation of the original clause."""

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
    explanation: str = Field(
        description="Detailed explanation of why this variation is ranked as it is, comparing to other variations"
    )


class NegotiationContext(BaseModel):
    """The observer perspective/persona for negotiation."""

    observer_role: str = Field(
        description="The role/perspective taken (e.g., 'Landlord', 'Tenant', 'Buyer', 'Seller', 'Neutral Mediator')"
    )
    observer_interests: str = Field(
        description="Key interests and priorities of this observer"
    )


class NegotiationAnalysis(BaseModel):
    """Complete negotiation analysis with variations and rankings."""

    original_clause: str = Field(description="The original clause text for reference")
    context: NegotiationContext = Field(
        description="The observer perspective used for this analysis"
    )
    variations: List[ClauseVariation] = Field(
        description="List of 2-5 clause variations, each with rankings and explanations",
        min_length=2,
        max_length=5,
    )
    overall_analysis: str = Field(
        description="High-level summary comparing all variations and their strategic implications"
    )


def select_observer_context(clause_data: dict) -> str:
    """
    Generate a prompt to select an appropriate observer context based on clause metadata.

    Args:
        clause_data: Dictionary containing clause and metadata

    Returns:
        String describing the observer context to use
    """
    clause_type = clause_data.get("clause_type", "Unknown")
    area_of_law = clause_data.get("area_of_law", "Unknown")
    industry = clause_data.get("industry", "Unknown")
    location = clause_data.get("location", "Unknown")

    # Create a focused context selection based on clause type
    context_hints = []

    # Map common clause types to typical opposing parties
    if (
        "landlord" in clause_type.lower()
        or "tenant" in clause_type.lower()
        or "lease" in clause_type.lower()
    ):
        context_hints = ["Landlord", "Tenant", "Property Manager"]
    elif (
        "employment" in clause_type.lower()
        or "non-compete" in clause_type.lower()
        or "non-solicitation" in clause_type.lower()
    ):
        context_hints = ["Employer", "Employee", "Labor Mediator"]
    elif "vendor" in clause_type.lower() or "supplier" in clause_type.lower():
        context_hints = ["Buyer", "Seller", "Procurement Officer"]
    elif "confidentiality" in clause_type.lower() or "nda" in clause_type.lower():
        context_hints = ["Disclosing Party", "Receiving Party", "Legal Counsel"]
    elif "indemnification" in clause_type.lower():
        context_hints = ["Indemnitor", "Indemnitee", "Insurance Adjuster"]
    elif "termination" in clause_type.lower():
        context_hints = ["Service Provider", "Client", "Contract Administrator"]
    else:
        # Generic business contexts
        context_hints = [
            "Party A (Stronger Position)",
            "Party B (Weaker Position)",
            "Neutral Mediator",
        ]

    return f"""
You are analyzing a {clause_type} clause in the context of {area_of_law},
applicable in {location}, within the {industry} industry.

Select ONE observer perspective from these typical roles: {", ".join(context_hints)}.
Or suggest another appropriate role if these don't fit.

The observer should have a clear stake in how this clause is drafted.
"""


def create_negotiation_agent() -> Agent:
    """
    Create a pydantic-ai agent for generating negotiation variations.

    Returns:
        Configured Agent instance
    """
    system_prompt = """
You are an expert legal negotiation advisor with deep knowledge of contract drafting and negotiation strategy.

Your task is to:
1. Understand the original clause and its business/legal context
2. Adopt a specific observer perspective (e.g., landlord, tenant, buyer, seller, employer, employee)
3. Generate 2-4 variations of the clause that could arise during negotiation
4. Each variation should be INSPIRED BY but NOT IDENTICAL to the original
5. Each variation should still match the metadata context (location, area of law, industry)
6. Rank each variation from the observer's perspective (1 = most preferred)
7. Explain WHY each variation is better or worse than the others

Key principles:
- Variations should represent meaningful negotiation positions, not just word changes
- Consider risk allocation, obligations, rights, and remedies
- Think about what each party would push for in a real negotiation
- Explanations should reference specific legal/business consequences
- The ranking should reflect the observer's strategic interests

Be realistic and specific. Consider real-world negotiation dynamics.
"""

    # Use gpt-5-mini as specified
    model = os.environ.get("OPENAI_MODEL", "gpt-5-mini")

    agent = Agent(
        model=f"openai:{model}",
        output_type=NegotiationAnalysis,
        system_prompt=system_prompt,
    )

    return agent


def generate_variations_for_clause(clause_data: dict, agent: Agent) -> dict:
    """
    Generate negotiation variations for a single clause.

    Args:
        clause_data: Dictionary with clause text and metadata
        agent: Pydantic-AI agent instance

    Returns:
        Dictionary with original data plus negotiation analysis
    """
    clause_text = clause_data.get("clause", "")

    # Build the prompt with full context
    prompt = f"""
Analyze this clause and generate negotiation variations:

**Original Clause:**
{clause_text}

**Metadata:**
- Clause Type: {clause_data.get("clause_type", "Unknown")}
- Area of Law: {clause_data.get("area_of_law", "Unknown")}
- Location: {clause_data.get("location", "Unknown")}
- Industry: {clause_data.get("industry", "Unknown")}
- Date Context: {clause_data.get("date", "Unknown")}

**Instructions:**
{select_observer_context(clause_data)}

Generate 2-4 variations that represent different negotiation positions.
Each variation should maintain the same general clause type and context.
Rank them from the observer's perspective and explain the strategic reasoning.
"""

    # Run the agent
    result = agent.run_sync(prompt)

    # Combine original data with analysis
    output = {
        "original_clause_data": clause_data,
        "negotiation_analysis": result.output.model_dump(),
        "timestamp": datetime.now(datetime.UTC).isoformat(),
    }

    return output


def process_clauses(
    input_file: Path,
    output_file: Path,
    max_samples: int = None,
    start_offset: int = 0,
):
    """
    Process clauses from input JSONL and generate negotiation variations.

    Args:
        input_file: Path to input JSONL file with clauses
        output_file: Path to output JSONL file for negotiation data
        max_samples: Maximum number of samples to process (None = all)
        start_offset: Number of samples to skip at start
    """
    # Create agent
    agent = create_negotiation_agent()

    # Load input data
    with open(input_file, "r") as f:
        clauses = [json.loads(line) for line in f]

    # Apply offset and limit
    if start_offset > 0:
        clauses = clauses[start_offset:]
    if max_samples:
        clauses = clauses[:max_samples]

    print(f"Processing {len(clauses)} clauses...")
    print(f"Output: {output_file}")

    # Ensure output directory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Process and write
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
                print(f"\nError processing clause: {e}")
                fail_count += 1

    print("\nComplete!")
    print(f"  Success: {success_count}")
    print(f"  Failed: {fail_count}")


def main():
    """Main entry point."""
    # Set up paths
    project_root = Path(__file__).parent.parent.parent
    input_file = (
        project_root / "samples" / "contracts" / "soli_clauses_001" / "all.jsonl"
    )

    # Create timestamped output
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = project_root / "samples" / "contracts" / "negotiation_variations_001"
    output_file = output_dir / f"variations_{timestamp}.jsonl"

    # Process a small test batch first
    print("Running initial test with 10 samples...")
    process_clauses(
        input_file=input_file,
        output_file=output_file,
        max_samples=10,
        start_offset=0,
    )


if __name__ == "__main__":
    main()
