#!/usr/bin/env python3
"""Generate README.md from scored AI Kit eval data."""

from __future__ import annotations

import json
from collections import defaultdict
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


def bar(value: float | int | None, width: int = 20) -> str:
    if value is None:
        return ""
    filled = round(float(value) / 100 * width)
    return "█" * filled + "░" * (width - filled)


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
        "docs": "Official docs",
        "no_context": "No context",
    }
    for variant in ["ai_kit", "docs", "no_context"]:
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
        "| Skill | AI Kit | Official Docs | Winner | No Context | AI Kit Safety | Docs Safety | Notes |",
        "|---|---:|---:|---|---:|---:|---:|---|",
    ]
    for skill in data["summary"]["skills"]:
        ai = get_row(rows, skill, "ai_kit")
        docs = get_row(rows, skill, "docs")
        no_context = get_row(rows, skill, "no_context")
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
            "| {skill} | {ai_rate} `{ai_dist}` | {docs_rate} `{docs_dist}` | {winner} | {no_rate} `{no_dist}` | {ai_safety} | {docs_safety} | {notes} |".format(
                skill=skill,
                ai_rate=pct(ai["success_rate_pct"]),
                ai_dist="".join(map(str, ai["success_distribution"])),
                docs_rate=pct(docs["success_rate_pct"]),
                docs_dist="".join(map(str, docs["success_distribution"])),
                winner=winner(ai, docs),
                no_rate=pct(no_context["success_rate_pct"]),
                no_dist="".join(map(str, no_context["success_distribution"])),
                ai_safety=ai["safety_errors"],
                docs_safety=docs["safety_errors"],
                notes=", ".join(notes) if notes else "-",
            )
        )
    return "\n".join(lines)


def render_bar_chart(data: dict, *, variants: list[str], title: str) -> str:
    rows = data["leaderboard"]
    labels = {
        "ai_kit": "AI Kit",
        "docs": "Docs",
        "no_context": "No context",
    }
    lines = [f"### {title}", ""]
    for skill in data["summary"]["skills"]:
        lines.append(f"**{skill}**")
        for variant in variants:
            row = get_row(rows, skill, variant)
            lines.append(f"- {labels[variant]:11} {bar(row['success_rate_pct'])} {pct(row['success_rate_pct'])}")
        lines.append("")
    return "\n".join(lines).strip()


def render_no_context(data: dict) -> str:
    rows = data["leaderboard"]
    lines = [
        "| Skill | No-Context Success | Distribution | Confidence | Safety | Contract |",
        "|---|---:|---|---:|---:|---:|",
    ]
    for skill in data["summary"]["skills"]:
        row = get_row(rows, skill, "no_context")
        lines.append(
            "| {skill} | {rate} | `{dist}` | {confidence} | {safety} | {contract} |".format(
                skill=skill,
                rate=pct(row["success_rate_pct"]),
                dist="".join(map(str, row["success_distribution"])),
                confidence=pct(row["validated_confidence_mean"]),
                safety=row["safety_errors"],
                contract=row["contract_errors"],
            )
        )
    return "\n".join(lines)


def render_readme(data: dict) -> str:
    rows = data["leaderboard"]
    ai = variant_totals(rows, "ai_kit")
    docs = variant_totals(rows, "docs")
    no_context = variant_totals(rows, "no_context")
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    return f"""# Xsolla AI Kit Skill Evaluation

## TL;DR

We evaluated 6 `xsolla-ai-kit` skills using the current harness algorithm:

- **AI Kit**: task prompt + `SKILL.md` + skill references.
- **Official docs**: task prompt + curated `developers.xsolla.com` corpus.
- **No context**: task prompt only.

Each skill was run `k=3` times per variant and judged by an Anthropic LLM judge against the same rubric.

Main result:

- **AI Kit**: `{ai['successes']}/{ai['runs']}` pass = **{pct(ai['success_rate'])}**
- **Official docs**: `{docs['successes']}/{docs['runs']}` pass = **{pct(docs['success_rate'])}**
- **No context control**: `{no_context['successes']}/{no_context['runs']}` pass = **{pct(no_context['success_rate'])}**

Interpretation: AI Kit outperforms official docs overall, but quality is uneven. Strong skills are `catalog-design`, `login-setup`, and `shop-setup`. Weak skills are `merchant-setup`, `payments-config`, and `webhooks-impl`.

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
| No context | User task only | Control group; does not change AI Kit vs docs result |

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

## Skill Comparison

This table keeps the main benchmark as **AI Kit vs Official docs**. The no-context result is included as a separate control column and does not change the AI Kit/docs winner.

{render_skill_table(data)}

## Graphs

{render_bar_chart(data, variants=['ai_kit', 'docs'], title='AI Kit vs Official Docs Success Rate')}

{render_bar_chart(data, variants=['no_context'], title='No-Context Control Success Rate')}

## No-Context Control Results

The no-context control shows what the same model does with only the task prompt and no skill/docs context.

{render_no_context(data)}

## Key Findings

1. `catalog-design`, `login-setup`, and `shop-setup` passed all AI Kit runs (`3/3`) and beat the official docs baseline.
2. `merchant-setup` performed better with official docs (`3/3`) than with AI Kit (`1/3`), indicating the skill needs tightening around credential safety and setup flow.
3. `payments-config` failed across all variants. This is expected risk because the skill is still placeholder/planned.
4. `webhooks-impl` failed across all variants. The AI Kit skill has useful content but did not reach the strict rubric threshold, so it needs rubric-aligned rewrite or deeper handler examples.
5. No-context failed every run (`0/18`), proving that some context is required for safe Xsolla integration work.

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
