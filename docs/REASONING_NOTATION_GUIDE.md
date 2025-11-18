# Reasoning Notation System for Legal Analysis

This guide explains the compact notation system used to represent structured reasoning in the negotiation variation dataset.

## Overview

The notation provides a visual shorthand for argument structure, combining:
- **Epistemic markers** (how confident in a claim's truth)
- **Normative markers** (whether something is good/bad)
- **Claim types** (fact, value, policy, preference)
- **Evidence citations** (sources and strength)
- **Argument relationships** (how claims support/attack each other)

## Quick Reference

### Example Notation

```
① «Employer» ●⬆ ⧈ "12-month restriction is industry standard" ⊢ 🏢★★ ⋀ 📊★
② «Employee» ●⬇ ⚖ "12 months excessively limits career mobility" ⊢ ⚖️★★★
③ «Mediator» ◐⟂ ⏵ "6-month compromise balances interests" ⊢ ① ⋀ ②

Links:
① ⟶ ③  // Industry practice supports compromise
② ⟶ ③  // Employee concerns support shorter duration
```

Reads as:
- Claim ①: Employer strongly believes (●) and approves (⬆) of the factual (⧈) claim that "12-month restriction is industry standard", supported by strong industry practice evidence (🏢★★) and weak data (📊★)
- Claim ②: Employee strongly believes (●) but disapproves (⬇) of the value judgment (⚖) that "12 months excessively limits mobility", with very strong legal precedent (⚖️★★★)
- Claim ③: Mediator moderately believes (◐) with neutral stance (⟂) that the policy (⏵) of "6-month compromise" works, based on claims ① and ②

## Notation Elements

### 1. Belief Strength (Epistemic Confidence)

How confident in a claim's **truth**:

| Symbol | Meaning | JSON Value |
|--------|---------|-----------|
| ⬤ | Certain true | `certain` |
| ● | Strongly believe true | `high` |
| ◐ | Leaning toward true | `moderate` |
| ◌ | Unsure / undecided | `low` |
| ◑ | Leaning toward false | `very_low` |
| ○ | Certain false | `very_low` |

**Example:**
- `●⧈ "Non-competes reduce employee mobility"` → Strongly believe this is factually true
- `◌⧈ "AI will replace most lawyers by 2030"` → Unsure if this will happen

### 2. Value Attitude (Normative Stance)

How one **feels** about a state of affairs:

| Symbol | Meaning | JSON Value |
|--------|---------|-----------|
| ⬆ | Approve / good / want more | `approve` |
| ⬇ | Disapprove / bad / want less | `disapprove` |
| ⇆ | Mixed / depends on context | `mixed` |
| ⟂ | No value judgment / neutral | `neutral` |

**Example:**
- `●⬆⚖ "Fair dealing principles protect weaker parties"` → Believe it's true AND approve
- `●⬇⚖ "Unlimited liquidated damages clauses are unjust"` → Believe it's true AND disapprove

### 3. Claim Types

What kind of claim is being made:

| Symbol | Type | JSON Value | Description |
|--------|------|-----------|-------------|
| ⧈ | Fact | `fact` | Empirical, descriptive, verifiable |
| ⚖ | Value | `value` | Ethical, normative, good/bad |
| ⏵ | Policy | `policy` | Recommendation, should/shouldn't |
| ✦ | Preference | `preference` | Personal taste, subjective |

**Example:**
- `⧈ "Italian courts scrutinize non-compete duration"` → Factual claim
- `⚖ "Overly broad non-competes are unfair"` → Value judgment
- `⏵ "We should negotiate for 12 months instead of 24"` → Policy recommendation

### 4. Evidence Sources

Types of evidence supporting claims:

| Symbol | Source | JSON Value | Typical Use |
|--------|--------|-----------|-------------|
| ⚖️ | Legal precedent | `legal_precedent` | Case law, court decisions |
| 📜 | Statute | `statute` | Legislation, regulations |
| 📊 | Data/Statistics | `data` | Empirical studies, surveys |
| 🏢 | Industry practice | `industry_practice` | Standard practices, norms |
| 💰 | Economic analysis | `economic` | Cost-benefit, market impact |
| ⚠ | Risk assessment | `risk` | Legal/business risk analysis |
| 📚 | Theory/Literature | `theory` | Academic work, doctrine |
| 👁 | Observation | `observation` | Direct experience |
| 🗣 | Testimony | `testimony` | Expert opinion, authority |

### 5. Evidence Strength

How strong the evidence is:

| Symbol | Strength | JSON Value |
|--------|----------|-----------|
| ★★★ | Very strong | `very_strong` |
| ★★ | Strong | `strong` |
| ★ | Weak | `weak` |
| ☆ | Very weak | `very_weak` |

**Combining source + strength:**
```
⊢ ⚖️★★★           // Very strong legal precedent
⊢ 📊★ ⋀ 🏢★★      // Weak data AND strong industry practice
⊢ 💰★★ ⋀ ⚠★★★    // Strong economic analysis AND very strong risk assessment
```

### 6. Argument Relationships

How claims relate to each other:

| Symbol | Relation | JSON Value | Meaning |
|--------|----------|-----------|---------|
| ⟶ | Supports | `supports` | Claim A strengthens claim B |
| ⟞ | Attacks | `attacks` | Claim A undermines claim B |
| ⇢ | Explains | `explains` | Claim A explains why claim B |
| ⟺ | Equivalent | `equivalent` | Claims mutually reinforce |

**Example:**
```
① ●⧈ "Shorter restrictions are more enforceable"
② ●⚖ "We want enforceable protection"
③ ●⏵ "Propose 12 months instead of 24"

Links:
① ⟶ ③  // Enforceability supports the shorter duration
② ⟶ ③  // Desire for enforceability supports the policy
```

## Complete Examples

### Example 1: Employment Non-Solicitation (Employee Perspective)

```
① «Employee» ●⬇ ⧈ "24-month restriction limits job mobility" ⊢ ⚖️★★★
② «Employee» ●⬇ ⚖ "Excessive restraints harm career development" ⊢ 💰★★ ⋀ 📚★★
③ «Employee» ●⬆ ⏵ "Negotiate down to 12 months with carve-outs" ⊢ ① ⋀ ②

Prose: "A 24-month restriction significantly impairs an employee's ability to pursue
opportunities in their field. Case law shows courts scrutinize lengthy restraints.
Economic analysis indicates career mobility is essential for information workers.
Strategic recommendation: Push for 12 months with exceptions for general hiring."
```

### Example 2: Landlord-Tenant Lease Term (Landlord Perspective)

```
① «Landlord» ●⬆ ⧈ "Long-term leases reduce vacancy risk" ⊢ 📊★★ ⋀ 💰★★★
② «Landlord» ◐⬇ ⧈ "5-year terms may deter quality tenants" ⊢ 🏢★ ⋀ 👁★★
③ «Landlord» ●⬆ ⏵ "Propose 3-year initial term with renewal option" ⊢ ① ⋀ ②

Links:
① ⟶ ③  // Stability goal supports multi-year term
② ⟞ ①  // Tenant deterrence challenges pure stability argument
```

### Example 3: Comparative Analysis Across Variations

```
Variation A (6 months):
Ⓐ₁ «Party B» ●⬆ ⏵ "Maximizes hiring flexibility" ⊢ 💰★★★
Ⓐ₂ «Party B» ●⬆ ⧈ "Lower enforceability risk" ⊢ ⚖️★★★

Variation B (12 months):
Ⓑ₁ «Party B» ◐⬆ ⏵ "Reasonable compromise" ⊢ 🏢★★
Ⓑ₂ «Party B» ●⟂ ⧈ "Industry standard duration" ⊢ 📊★★

Variation C (24 months):
Ⓒ₁ «Party B» ●⬇ ⏵ "Excessive restriction" ⊢ ⚖️★★ ⋀ 💰★★★
Ⓒ₂ «Party B» ◐⬇ ⧈ "High litigation risk" ⊢ ⚠★★★

Comparative:
Ⓐ₁ ⟶ "Choose A as primary position"
Ⓑ₁ ⟶ "Accept B as fallback"
Ⓒ₁ ⟞ "Resist C strongly"
```

## Usage in Dataset

The negotiation variations dataset includes:

1. **JSON fields** with structured values:
   ```json
   {
     "claim_text": "12-month restriction is industry standard",
     "confidence": "high",
     "attitude": "approve",
     "claim_type": "fact",
     "evidence_summary": "industry practice + data"
   }
   ```

2. **Notation rendering** (can be generated from JSON):
   ```
   ● ⬆ ⧈ "12-month restriction is industry standard" ⊢ 🏢★★ ⋀ 📊★
   ```

3. **Prose synthesis**:
   ```
   "Industry benchmarks and HR data show 12-month post-term restrictions
   are standard practice in the information sector. This duration balances
   employer protection with employee mobility..."
   ```

## Benefits

1. **Queryable**: Can filter by confidence, attitude, claim type, etc.
2. **Visual**: Compact notation for quick scanning
3. **Structured**: Enables programmatic analysis of reasoning patterns
4. **Educational**: Makes argument structure explicit
5. **Multi-perspective**: Clearly shows different stakeholder viewpoints

## Tools

### Rendering Functions

See `reasoning_models.py` for:
- `to_symbol()` methods on enum classes
- `to_notation()` methods on claim/evidence classes
- `render_reasoning_compact()` for full formatting

### Inspection Utility

```bash
python inspect_reasoning.py <jsonl_file> --sample N
```

Displays both structured notation and prose for a given sample.

---

**Reference:** This notation system was designed for the ALEA Legal Benchmark negotiation variations dataset, combining structured representation with human readability for legal reasoning analysis.
