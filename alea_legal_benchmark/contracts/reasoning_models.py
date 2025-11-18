"""
Pydantic models for structured reasoning with compact notation support.

This module provides models that capture:
1. Beliefs with confidence levels
2. Evidence with sources and strength
3. Argument structure and relationships
4. Both compact notation and prose representations
"""

from typing import List, Literal, Optional
from enum import Enum
from pydantic import BaseModel, Field


# ============================================================================
# Notation Symbol Enums (for structured representation)
# ============================================================================


class BeliefStrength(str, Enum):
    """Epistemic confidence in a claim's truth."""

    CERTAIN_TRUE = "certain_true"  # ⬤ Certain true
    STRONG_TRUE = "strong_true"  # ● Strongly believe true
    LEAN_TRUE = "lean_true"  # ◐ Leaning true
    UNDECIDED = "undecided"  # ◌ Unsure
    LEAN_FALSE = "lean_false"  # ◑ Leaning false
    CERTAIN_FALSE = "certain_false"  # ○ Certain false

    def to_symbol(self) -> str:
        """Convert to Unicode notation symbol."""
        return {
            "certain_true": "⬤",
            "strong_true": "●",
            "lean_true": "◐",
            "undecided": "◌",
            "lean_false": "◑",
            "certain_false": "○",
        }[self.value]


class ValueAttitude(str, Enum):
    """Normative valence - how one feels about a state of affairs."""

    APPROVE = "approve"  # ⬆ Approve/good/want more
    DISAPPROVE = "disapprove"  # ⬇ Disapprove/bad/want less
    MIXED = "mixed"  # ⇆ Mixed/depends
    NEUTRAL = "neutral"  # ⟂ No value judgment

    def to_symbol(self) -> str:
        """Convert to Unicode notation symbol."""
        return {
            "approve": "⬆",
            "disapprove": "⬇",
            "mixed": "⇆",
            "neutral": "⟂",
        }[self.value]


class ClaimType(str, Enum):
    """Type of claim being made."""

    FACT = "fact"  # ⧈ Fact/descriptive/empirical
    VALUE = "value"  # ⚖ Value/ethical/normative
    POLICY = "policy"  # ⏵ Policy/action recommendation
    PREFERENCE = "preference"  # ✦ Preference/taste

    def to_symbol(self) -> str:
        """Convert to Unicode notation symbol."""
        return {
            "fact": "⧈",
            "value": "⚖",
            "policy": "⏵",
            "preference": "✦",
        }[self.value]


class EvidenceSource(str, Enum):
    """Source/type of evidence."""

    LEGAL_PRECEDENT = "legal_precedent"  # ⚖️ Case law
    STATUTE = "statute"  # 📜 Statutory authority
    DATA = "data"  # 📊 Data/statistics
    THEORY = "theory"  # 📚 Theory/literature
    OBSERVATION = "observation"  # 👁 Direct observation
    TESTIMONY = "testimony"  # 🗣 Expert/authority testimony
    INDUSTRY_PRACTICE = "industry_practice"  # 🏢 Standard industry practice
    ECONOMIC_ANALYSIS = "economic"  # 💰 Economic/cost analysis
    RISK_ASSESSMENT = "risk"  # ⚠ Risk analysis

    def to_symbol(self) -> str:
        """Convert to Unicode notation symbol."""
        return {
            "legal_precedent": "⚖️",
            "statute": "📜",
            "data": "📊",
            "theory": "📚",
            "observation": "👁",
            "testimony": "🗣",
            "industry_practice": "🏢",
            "economic": "💰",
            "risk": "⚠",
        }[self.value]


class EvidenceStrength(str, Enum):
    """Strength of evidence."""

    VERY_STRONG = "very_strong"  # ★★★
    STRONG = "strong"  # ★★
    WEAK = "weak"  # ★
    VERY_WEAK = "very_weak"  # ☆

    def to_symbol(self) -> str:
        """Convert to Unicode notation symbol."""
        return {
            "very_strong": "★★★",
            "strong": "★★",
            "weak": "★",
            "very_weak": "☆",
        }[self.value]


class RelationType(str, Enum):
    """Relationship between claims."""

    SUPPORTS = "supports"  # ⟶ Supports/pro-argument
    ATTACKS = "attacks"  # ⟞ Undercuts/attacks/challenges
    EXPLAINS = "explains"  # ⇢ Explains/causes
    EQUIVALENT = "equivalent"  # ⟺ Equivalent/mutual support

    def to_symbol(self) -> str:
        """Convert to Unicode notation symbol."""
        return {
            "supports": "⟶",
            "attacks": "⟞",
            "explains": "⇢",
            "equivalent": "⟺",
        }[self.value]


# ============================================================================
# Core Reasoning Models
# ============================================================================


class EvidenceCitation(BaseModel):
    """Evidence supporting a claim."""

    source: EvidenceSource = Field(description="Type/source of evidence")
    strength: EvidenceStrength = Field(description="How strong this evidence is")
    description: str = Field(description="What this evidence shows or demonstrates")

    def to_notation(self) -> str:
        """Render as compact notation."""
        return f"{self.source.to_symbol()}{self.strength.to_symbol()}"


class StrategicClaim(BaseModel):
    """
    A single claim/belief in the strategic reasoning.

    Captures: what is claimed, confidence level, who it favors, and evidence.
    """

    claim_id: str = Field(description="Short identifier (e.g., '①', '②', 'A1', 'B2')")
    agent: str = Field(
        description="Who holds this view (e.g., 'Landlord', 'Tenant', 'Employer', 'Employee', 'Court', 'Observer')"
    )
    proposition: str = Field(description="The actual claim/belief in natural language")
    belief: BeliefStrength = Field(description="How confident in this claim's truth")
    value: ValueAttitude = Field(
        description="Whether this is viewed positively or negatively"
    )
    claim_type: ClaimType = Field(
        description="Type of claim (fact, value, policy, preference)"
    )
    evidence: List[EvidenceCitation] = Field(
        default_factory=list, description="Evidence supporting this claim"
    )

    def to_notation(self) -> str:
        """Render as compact notation string."""
        # Base claim: [ID] [Agent] [Belief][Value] [Type] "Proposition"
        parts = [
            self.claim_id,
            f"«{self.agent}»",
            f"{self.belief.to_symbol()}{self.value.to_symbol()}",
            self.claim_type.to_symbol(),
            f'"{self.proposition}"',
        ]

        # Add evidence if present
        if self.evidence:
            ev_notation = " ⋀ ".join(e.to_notation() for e in self.evidence)
            parts.append(f"⊢ {ev_notation}")

        return " ".join(parts)


class ArgumentLink(BaseModel):
    """Relationship between two claims."""

    from_claim: str = Field(description="Source claim ID")
    to_claim: str = Field(description="Target claim ID")
    relation: RelationType = Field(description="How from_claim relates to to_claim")
    explanation: Optional[str] = Field(
        default=None, description="Brief explanation of this relationship"
    )

    def to_notation(self) -> str:
        """Render as compact notation."""
        base = f"{self.from_claim} {self.relation.to_symbol()} {self.to_claim}"
        if self.explanation:
            base += f"  // {self.explanation}"
        return base


class ReasoningChain(BaseModel):
    """
    Complete reasoning chain with claims and their relationships.

    This captures the full argument structure in a queryable format
    and can render both as compact notation and prose.
    """

    claims: List[StrategicClaim] = Field(
        description="Individual claims in the reasoning (2-7 claims recommended)",
        min_length=1,
        max_length=10,
    )
    links: List[ArgumentLink] = Field(
        default_factory=list, description="How claims relate to each other"
    )
    prose_summary: str = Field(
        description="Natural language synthesis of the reasoning"
    )

    def to_notation(self) -> str:
        """Render complete chain as compact notation."""
        lines = []

        # Render all claims
        for claim in self.claims:
            lines.append(claim.to_notation())

        # Render links if present
        if self.links:
            lines.append("")
            lines.append("Links:")
            for link in self.links:
                lines.append(link.to_notation())

        return "\n".join(lines)

    def get_claim_by_id(self, claim_id: str) -> Optional[StrategicClaim]:
        """Retrieve a claim by its ID."""
        for claim in self.claims:
            if claim.claim_id == claim_id:
                return claim
        return None

    def get_supporting_claims(self, claim_id: str) -> List[StrategicClaim]:
        """Get all claims that support the given claim."""
        supporting_ids = [
            link.from_claim
            for link in self.links
            if link.to_claim == claim_id and link.relation == RelationType.SUPPORTS
        ]
        return [c for c in self.claims if c.claim_id in supporting_ids]

    def get_attacking_claims(self, claim_id: str) -> List[StrategicClaim]:
        """Get all claims that attack/challenge the given claim."""
        attacking_ids = [
            link.from_claim
            for link in self.links
            if link.to_claim == claim_id and link.relation == RelationType.ATTACKS
        ]
        return [c for c in self.claims if c.claim_id in attacking_ids]


# ============================================================================
# Negotiation-Specific Models
# ============================================================================


class ClauseVariationReasoning(BaseModel):
    """
    Enhanced reasoning model for clause variation analysis.

    Combines structured reasoning chain with prose explanation.
    """

    # Structured reasoning with notation support
    reasoning_chain: ReasoningChain = Field(
        description="Structured claims, evidence, and argument relationships explaining this variation"
    )

    # Quick summary fields for filtering/sorting
    key_advantages: List[str] = Field(
        description="2-4 key advantages of this variation from observer's perspective",
        min_length=0,
        max_length=5,
    )
    key_disadvantages: List[str] = Field(
        description="2-4 key disadvantages of this variation from observer's perspective",
        min_length=0,
        max_length=5,
    )

    # Risk assessment
    enforceability_confidence: BeliefStrength = Field(
        description="Confidence that this variation would be enforced by courts"
    )
    business_risk_level: Literal["very_low", "low", "moderate", "high", "very_high"] = (
        Field(description="Business risk level associated with this variation")
    )


class ComparativeAnalysis(BaseModel):
    """
    Cross-variation comparative reasoning.

    Explains why variations are ranked relative to each other.
    """

    reasoning_chain: ReasoningChain = Field(
        description="Claims comparing the variations and explaining relative rankings"
    )

    strategic_recommendations: List[str] = Field(
        description="2-4 strategic recommendations based on the analysis",
        min_length=2,
        max_length=5,
    )


# ============================================================================
# Utility Functions
# ============================================================================


def render_reasoning_compact(reasoning: ClauseVariationReasoning) -> str:
    """
    Render reasoning as compact notation for inspection.

    Args:
        reasoning: The reasoning to render

    Returns:
        Multi-line string with notation
    """
    lines = [
        "=== Structured Reasoning ===",
        "",
        reasoning.reasoning_chain.to_notation(),
        "",
        "=== Prose Summary ===",
        reasoning.reasoning_chain.prose_summary,
        "",
        f"Enforceability: {reasoning.enforceability_confidence.to_symbol()}",
        f"Business Risk: {reasoning.business_risk_level}",
    ]

    if reasoning.key_advantages:
        lines.extend(
            ["", "Key Advantages:", *[f"  + {adv}" for adv in reasoning.key_advantages]]
        )

    if reasoning.key_disadvantages:
        lines.extend(
            [
                "",
                "Key Disadvantages:",
                *[f"  - {dis}" for dis in reasoning.key_disadvantages],
            ]
        )

    return "\n".join(lines)
