"""
Utility to inspect and render structured reasoning from negotiation variations.

Usage:
    python inspect_reasoning.py <jsonl_file> [--sample N]
"""

import json
import sys
from pathlib import Path


def render_full_analysis(record: dict, show_original: bool = True) -> str:
    """Render a complete negotiation analysis with notation."""
    lines = []

    lines.append("=" * 80)
    lines.append("NEGOTIATION VARIATION ANALYSIS")
    lines.append("=" * 80)
    lines.append("")

    # Original clause
    if show_original:
        original = record["original_clause_data"]
        lines.append("ORIGINAL CLAUSE:")
        lines.append(f"  Type: {original['clause_type']}")
        lines.append(f"  Area: {original['area_of_law']}")
        lines.append(f"  Location: {original['location']}")
        lines.append(f"  Industry: {original['industry']}")
        lines.append("")
        lines.append(f"  Text: {original['clause'][:200]}...")
        lines.append("")

    analysis = record["negotiation_analysis"]

    # Observer context
    context = analysis["context"]
    lines.append(f"OBSERVER: «{context['observer_role']}»")
    lines.append(f"Interests: {context['observer_interests']}")
    lines.append("")
    lines.append("-" * 80)

    # Variations with structured reasoning
    for var in analysis["variations"]:
        lines.append("")
        lines.append(
            f"VARIATION {var['variation_id']} (Rank #{var['rank']}, Score: {var['value_score']:.1f})"
        )
        lines.append("=" * 80)
        lines.append("")

        # Show variation text
        lines.append("Text:")
        lines.append(f"  {var['variation_text'][:300]}...")
        lines.append("")

        # Show structured reasoning if present
        if "reasoning" in var:
            reasoning_data = var["reasoning"]

            # Reconstruct the reasoning model
            if "reasoning_chain" in reasoning_data:
                chain_data = reasoning_data["reasoning_chain"]

                lines.append("STRUCTURED REASONING:")
                lines.append("")

                # Show claims in notation
                if "claims" in chain_data:
                    for claim in chain_data["claims"]:
                        # Manually render claim notation
                        belief_map = {
                            "certain_true": "⬤",
                            "strong_true": "●",
                            "lean_true": "◐",
                            "undecided": "◌",
                            "lean_false": "◑",
                            "certain_false": "○",
                        }
                        value_map = {
                            "approve": "⬆",
                            "disapprove": "⬇",
                            "mixed": "⇆",
                            "neutral": "⟂",
                        }
                        type_map = {
                            "fact": "⧈",
                            "value": "⚖",
                            "policy": "⏵",
                            "preference": "✦",
                        }

                        belief_sym = belief_map.get(claim["belief"], "?")
                        value_sym = value_map.get(claim["value"], "?")
                        type_sym = type_map.get(claim["claim_type"], "?")

                        line_parts = [
                            claim["claim_id"],
                            f"«{claim['agent']}»",
                            f"{belief_sym}{value_sym}",
                            type_sym,
                            f'"{claim["proposition"]}"',
                        ]

                        # Add evidence
                        if claim.get("evidence"):
                            ev_parts = []
                            source_map = {
                                "legal_precedent": "⚖️",
                                "statute": "📜",
                                "data": "📊",
                                "theory": "📚",
                                "observation": "👁",
                                "testimony": "🗣",
                                "industry_practice": "🏢",
                                "economic": "💰",
                                "risk": "⚠",
                            }
                            strength_map = {
                                "very_strong": "★★★",
                                "strong": "★★",
                                "weak": "★",
                                "very_weak": "☆",
                            }

                            for ev in claim["evidence"]:
                                src = source_map.get(ev["source"], "?")
                                str_sym = strength_map.get(ev["strength"], "?")
                                ev_parts.append(f"{src}{str_sym}")

                            line_parts.append(f"⊢ {' ⋀ '.join(ev_parts)}")

                        lines.append("  " + " ".join(line_parts))

                        # Show evidence descriptions
                        if claim.get("evidence"):
                            for ev in claim["evidence"]:
                                lines.append(f"    → {ev['description']}")

                # Show links
                if "links" in chain_data and chain_data["links"]:
                    lines.append("")
                    lines.append("  Links:")
                    relation_map = {
                        "supports": "⟶",
                        "attacks": "⟞",
                        "explains": "⇢",
                        "equivalent": "⟺",
                    }
                    for link in chain_data["links"]:
                        rel_sym = relation_map.get(link["relation"], "?")
                        link_str = (
                            f"  {link['from_claim']} {rel_sym} {link['to_claim']}"
                        )
                        if link.get("explanation"):
                            link_str += f"  // {link['explanation']}"
                        lines.append(link_str)

                # Show prose summary
                lines.append("")
                lines.append("PROSE SUMMARY:")
                lines.append(f"  {chain_data.get('prose_summary', 'N/A')}")

            # Show quick summary fields
            if reasoning_data.get("key_advantages"):
                lines.append("")
                lines.append("Key Advantages:")
                for adv in reasoning_data["key_advantages"]:
                    lines.append(f"  + {adv}")

            if reasoning_data.get("key_disadvantages"):
                lines.append("")
                lines.append("Key Disadvantages:")
                for dis in reasoning_data["key_disadvantages"]:
                    lines.append(f"  - {dis}")

            if "enforceability_confidence" in reasoning_data:
                belief_map = {
                    "certain_true": "⬤",
                    "strong_true": "●",
                    "lean_true": "◐",
                    "undecided": "◌",
                    "lean_false": "◑",
                    "certain_false": "○",
                }
                enf_sym = belief_map.get(
                    reasoning_data["enforceability_confidence"], "?"
                )
                lines.append("")
                lines.append(
                    f"Enforceability Confidence: {enf_sym} ({reasoning_data['enforceability_confidence']})"
                )
                lines.append(
                    f"Business Risk: {reasoning_data.get('business_risk_level', 'N/A')}"
                )

        lines.append("")
        lines.append("-" * 80)

    # Comparative analysis
    if "comparative_analysis" in analysis:
        comp = analysis["comparative_analysis"]
        lines.append("")
        lines.append("COMPARATIVE ANALYSIS")
        lines.append("=" * 80)
        lines.append("")

        if "reasoning_chain" in comp:
            chain_data = comp["reasoning_chain"]

            # Render claims
            if "claims" in chain_data:
                for claim in chain_data["claims"]:
                    belief_map = {
                        "certain_true": "⬤",
                        "strong_true": "●",
                        "lean_true": "◐",
                        "undecided": "◌",
                        "lean_false": "◑",
                        "certain_false": "○",
                    }
                    value_map = {
                        "approve": "⬆",
                        "disapprove": "⬇",
                        "mixed": "⇆",
                        "neutral": "⟂",
                    }
                    type_map = {
                        "fact": "⧈",
                        "value": "⚖",
                        "policy": "⏵",
                        "preference": "✦",
                    }

                    belief_sym = belief_map.get(claim["belief"], "?")
                    value_sym = value_map.get(claim["value"], "?")
                    type_sym = type_map.get(claim["claim_type"], "?")

                    line_parts = [
                        claim["claim_id"],
                        f"«{claim['agent']}»",
                        f"{belief_sym}{value_sym}",
                        type_sym,
                        f'"{claim["proposition"]}"',
                    ]
                    lines.append("  " + " ".join(line_parts))

            # Show links
            if "links" in chain_data and chain_data["links"]:
                lines.append("")
                lines.append("  Links:")
                relation_map = {
                    "supports": "⟶",
                    "attacks": "⟞",
                    "explains": "⇢",
                    "equivalent": "⟺",
                }
                for link in chain_data["links"]:
                    rel_sym = relation_map.get(link["relation"], "?")
                    lines.append(f"  {link['from_claim']} {rel_sym} {link['to_claim']}")

            lines.append("")
            lines.append("PROSE SUMMARY:")
            lines.append(f"  {chain_data.get('prose_summary', 'N/A')}")

        if comp.get("strategic_recommendations"):
            lines.append("")
            lines.append("Strategic Recommendations:")
            for i, rec in enumerate(comp["strategic_recommendations"], 1):
                lines.append(f"  {i}. {rec}")

    lines.append("")
    lines.append("=" * 80)

    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python inspect_reasoning.py <jsonl_file> [--sample N]")
        sys.exit(1)

    file_path = Path(sys.argv[1])
    sample_n = None

    if "--sample" in sys.argv:
        idx = sys.argv.index("--sample")
        if idx + 1 < len(sys.argv):
            sample_n = int(sys.argv[idx + 1])

    # Load and render
    with open(file_path) as f:
        records = [json.loads(line) for line in f]

    if sample_n is not None:
        if sample_n >= len(records):
            print(f"Error: Sample {sample_n} not found (only {len(records)} records)")
            sys.exit(1)
        records = [records[sample_n]]

    for i, record in enumerate(records):
        if i > 0:
            print("\n\n")
        print(render_full_analysis(record, show_original=(i == 0)))


if __name__ == "__main__":
    main()
