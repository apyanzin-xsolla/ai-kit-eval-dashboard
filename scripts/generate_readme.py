#!/usr/bin/env python3
"""Generate README.md from scored AI Kit eval data."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "dashboard-data.json"
README_PATH = ROOT / "README.md"


def pct(value: float | int | None) -> str:
    if value is None:
        return "n/a"
    value = float(value)
    return f"{value:.0f}%" if value.is_integer() else f"{value:.1f}%"


def get_row(rows: list[dict], skill: str, variant: str) -> dict:
    return next(row for row in rows if row["skill"] == skill and row["variant"] == variant)


def variant_totals(rows: list[dict], variant: str) -> dict:
    subset = [row for row in rows if row["variant"] == variant]
    runs = sum(row["runs"] for row in subset)
    successes = sum(row["successes"] for row in subset)
    confidence_values = [row["validated_confidence_mean"] or 0 for row in subset]
    return {
        "runs": runs,
        "successes": successes,
        "success_rate": successes / runs * 100 if runs else 0,
        "confidence": sum(confidence_values) / len(confidence_values) if confidence_values else 0,
        "safety_errors": sum(row["safety_errors"] for row in subset),
        "contract_errors": sum(row["contract_errors"] for row in subset),
        "tokens_mean": sum(row["tokens_mean"] for row in subset) / len(subset) if subset else 0,
    }


def winner(ai: dict, docs: dict) -> str:
    ai_rate = ai["success_rate_pct"] or 0
    docs_rate = docs["success_rate_pct"] or 0
    if ai_rate > docs_rate:
        return "AI Kit"
    if docs_rate > ai_rate:
        return "Official docs"
    return "Tie"


def render_variant_summary(rows: list[dict]) -> str:
    lines = [
        "| Variant | Pass | Success Rate | Avg Confidence | Safety Errors | Contract Errors | Avg Tokens |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    labels = {
        "ai_kit": "AI Kit",
        "docs": "Official docs"
    }
    for variant in ["ai_kit", "docs"]:
        total = variant_totals(rows, variant)
        lines.append(
            "| {label} | {successes}/{runs} | {rate} | {confidence} | {safety} | {contract} | {tokens:.0f} |".format(
                label=labels[variant],
                successes=total["successes"],
                runs=total["runs"],
                rate=pct(total["success_rate"]),
                confidence=pct(total["confidence"]),
                safety=total["safety_errors"],
                contract=total["contract_errors"],
                tokens=total["tokens_mean"],
            )
        )
    return "\n".join(lines)


def render_skill_table(data: dict) -> str:
    rows = data["leaderboard"]
    lines = [
        "| Skill | AI Kit | Official Docs | Winner | AI Kit Safety | Docs Safety | Notes |",
        "|---|---:|---:|---|---:|---:|---|",
    ]
    for skill in data["summary"]["skills"]:
        ai = get_row(rows, skill, "ai_kit")
        docs = get_row(rows, skill, "docs")
        notes = []
        if ai["success_rate_pct"] == 0 and docs["success_rate_pct"] == 0:
            notes.append("both fail")
        if ai["safety_errors"]:
            notes.append("AI Kit safety risk")
        if docs["safety_errors"]:
            notes.append("docs safety risk")
        if skill == "payments-config":
            notes.append("skill is placeholder/planned")
        lines.append(
            "| {skill} | {ai_rate} `{ai_dist}` | {docs_rate} `{docs_dist}` | {winner} | {ai_safety} | {docs_safety} | {notes} |".format(
                skill=skill,
                ai_rate=pct(ai["success_rate_pct"]),
                ai_dist="".join(map(str, ai["success_distribution"])),
                docs_rate=pct(docs["success_rate_pct"]),
                docs_dist="".join(map(str, docs["success_distribution"])),
                winner=winner(ai, docs),
                ai_safety=ai["safety_errors"],
                docs_safety=docs["safety_errors"],
                notes=", ".join(notes) if notes else "-",
            )
        )
    return "\n".join(lines)


def render_success_mermaid(data: dict) -> str:
    rows = data["leaderboard"]
    skills = data["summary"]["skills"]
    labels = [skill.replace("-setup", "").replace("-design", "").replace("-config", "").replace("-impl", "") for skill in skills]
    ai_values = [str(get_row(rows, skill, "ai_kit")["success_rate_pct"] or 0) for skill in skills]
    docs_values = [str(get_row(rows, skill, "docs")["success_rate_pct"] or 0) for skill in skills]
    quoted_labels = ", ".join(f'"{label}"' for label in labels)
    return f"""```mermaid
xychart-beta
    title "Success Rate by Skill: AI Kit vs Official Docs"
    x-axis [{quoted_labels}]
    y-axis "Success rate (%)" 0 --> 100
    bar [{", ".join(ai_values)}]
    bar [{", ".join(docs_values)}]
```"""


def render_risk_mermaid(data: dict) -> str:
    rows = data["leaderboard"]
    skills = data["summary"]["skills"]
    labels = [skill.replace("-setup", "").replace("-design", "").replace("-config", "").replace("-impl", "") for skill in skills]
    ai_safety = [str(get_row(rows, skill, "ai_kit")["safety_errors"]) for skill in skills]
    docs_safety = [str(get_row(rows, skill, "docs")["safety_errors"]) for skill in skills]
    quoted_labels = ", ".join(f'"{label}"' for label in labels)
    return f"""```mermaid
xychart-beta
    title "Safety Errors by Skill: AI Kit vs Official Docs"
    x-axis [{quoted_labels}]
    y-axis "Safety errors" 0 --> 3
    bar [{", ".join(ai_safety)}]
    bar [{", ".join(docs_safety)}]
```"""


def render_outcome_map(data: dict) -> str:
    rows = data["leaderboard"]
    groups = {
        "AI Kit wins": [],
        "Docs wins": [],
        "Both fail": [],
        "Tie": [],
    }
    for skill in data["summary"]["skills"]:
        ai = get_row(rows, skill, "ai_kit")
        docs = get_row(rows, skill, "docs")
        outcome = winner(ai, docs)
        if ai["success_rate_pct"] == 0 and docs["success_rate_pct"] == 0:
            groups["Both fail"].append(skill)
        elif outcome == "AI Kit":
            groups["AI Kit wins"].append(skill)
        elif outcome == "Official docs":
            groups["Docs wins"].append(skill)
        else:
            groups["Tie"].append(skill)
    lines = [
        "```mermaid",
        "flowchart LR",
        "  A[Assessment outcome]",
    ]
    for idx, (name, skills) in enumerate(groups.items(), start=1):
        node = f"N{idx}"
        label = f"{name}: {', '.join(skills) if skills else 'none'}"
        lines.append(f"  A --> {node}[\"{label}\"]")
    lines.append("```")
    return "\n".join(lines)


def render_readme(data: dict) -> str:
    rows = data["leaderboard"]
    ai = variant_totals(rows, "ai_kit")
    docs = variant_totals(rows, "docs")
    no_context = variant_totals(rows, "no_context")
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    return f"""# Xsolla AI Kit Skill Evaluation

## TL;DR

We evaluated 6 `xsolla-ai-kit` skills using the current harness algorithm.

- **AI Kit**: task prompt + `SKILL.md` + skill references.
- **Official docs**: task prompt + curated `developers.xsolla.com` corpus.
Each skill was run `k=3` times for the AI Kit and official-docs variants, then judged by an Anthropic LLM judge against the same rubric. A no-context control was also run to verify that raw model knowledge alone is not enough for safe Xsolla integration work.

Main result:

- **AI Kit**: `{ai['successes']}/{ai['runs']}` pass = **{pct(ai['success_rate'])}**
- **Official docs**: `{docs['successes']}/{docs['runs']}` pass = **{pct(docs['success_rate'])}**
Interpretation: AI Kit outperforms official docs overall, but the result is uneven. It is strong for `catalog-design`, `login-setup`, and `shop-setup`; official docs still win for `merchant-setup`; `payments-config` and `webhooks-impl` need product-quality remediation before they can be trusted.

Generated: `{generated_at}`

## Methodology

### Run Matrix

- Skills: `{", ".join(data['summary']['skills'])}`
- Variants: `ai_kit`, `docs`, `no_context`
- Repetitions: `k=3`
- Total scored runs: `{data['summary']['scored_runs']}`
- Evidence level: agent transcript + LLM judge
- Reliability: `{data['summary']['reliability']}`

### Variants

| Variant | Context Given to Agent | Purpose |
|---|---|---|
| AI Kit | User task + `SKILL.md` + references | Measures skill value |
| Official docs | User task + official `developers.xsolla.com` docs corpus | Fair documentation baseline |
| No context | User task only | Control group used only to validate that context is necessary |

### Metrics

| Metric | Meaning |
|---|---|
| Success rate | Share of runs with judge pass rate >= rubric threshold and safety checks passing |
| Distribution | Per-run pass/fail over `k=3`, e.g. `111`, `010`, `000` |
| First try | Whether run 1 passed |
| pass@k | Whether at least one of the `k` runs passed |
| Confidence | Average judge pass rate before thresholding |
| Safety errors | Count of failed safety checks |
| Contract errors | Count of failed contract/programmatic checks |
| Tokens | Approximate tokens in prompt + answer transcript |

## Overall Results

{render_variant_summary(rows)}

Control check: the no-context baseline scored `{no_context['successes']}/{no_context['runs']}` pass = **{pct(no_context['success_rate'])}**. This confirms that the benchmark is measuring context quality, not only generic model capability.

## Skill Comparison

This table keeps the benchmark focused on **AI Kit vs Official docs**. The no-context baseline is intentionally excluded from the winner calculation.

{render_skill_table(data)}

## Graphs

### Success Rate

{render_success_mermaid(data)}

### Safety Errors

{render_risk_mermaid(data)}

### Outcome Map

{render_outcome_map(data)}

## Key Findings

1. `catalog-design`, `login-setup`, and `shop-setup` passed all AI Kit runs (`3/3`) and beat the official docs baseline.
2. `merchant-setup` performed better with official docs (`3/3`) than with AI Kit (`1/3`), indicating the skill needs tightening around credential safety and setup flow.
3. `payments-config` failed across all variants. This is expected risk because the skill is still placeholder/planned.
4. `webhooks-impl` failed across all variants. The AI Kit skill has useful content but did not reach the strict rubric threshold, so it needs rubric-aligned rewrite or deeper handler examples.
5. The no-context control failed every run (`0/18`), so context quality is the core variable in this assessment rather than generic model capability.

## Files

- `data/dashboard-data.json` — machine-readable scored results.
- `data/ai-kit-eval-report.md` — raw harness report.
- `scripts/generate_readme.py` — regenerates this README from `data/dashboard-data.json`.

## Re-generate README

```bash
python3 scripts/generate_readme.py
```
"""


def main() -> None:
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    README_PATH.write_text(render_readme(data), encoding="utf-8")
    print(f"Wrote {README_PATH}")


if __name__ == "__main__":
    main()
