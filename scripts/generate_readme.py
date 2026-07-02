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
        "| Skill | AI Kit | Official Docs | No Context | Winner | AI Kit Safety | Docs Safety | No Context Safety | Notes |",
        "|---|---:|---:|---:|---|---:|---:|---:|---|",
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
        if skill == "headless-checkout-integration":
            notes.append("artifact-based eval")
        lines.append(
            "| {skill} | {ai_rate} `{ai_dist}` | {docs_rate} `{docs_dist}` | {no_rate} `{no_dist}` | {winner} | {ai_safety} | {docs_safety} | {no_safety} | {notes} |".format(
                skill=skill,
                ai_rate=pct(ai["success_rate_pct"]),
                ai_dist="".join(map(str, ai["success_distribution"])),
                docs_rate=pct(docs["success_rate_pct"]),
                docs_dist="".join(map(str, docs["success_distribution"])),
                no_rate=pct(no_context["success_rate_pct"]),
                no_dist="".join(map(str, no_context["success_distribution"])),
                winner=winner(ai, docs),
                ai_safety=ai["safety_errors"],
                docs_safety=docs["safety_errors"],
                no_safety=no_context["safety_errors"],
                notes=", ".join(notes) if notes else "-",
            )
        )
    return "\n".join(lines)


def safety_score(row: dict) -> float:
    if not row.get("success_rate_pct"):
        return 0.0
    return max(0.0, 100.0 - ((row["safety_errors"] or 0) / max(row["runs"], 1) * 100.0))


def contract_score(row: dict) -> float:
    if not row.get("success_rate_pct"):
        return 0.0
    return max(0.0, 100.0 - ((row["contract_errors"] or 0) / max(row["runs"], 1) * 100.0))


def token_efficiency_score(row: dict, max_tokens: float) -> float:
    if not row.get("success_rate_pct"):
        return 0.0
    if max_tokens <= 0:
        return 0.0
    return max(0.0, 100.0 - ((row["tokens_mean"] or 0) / max_tokens * 100.0))


def metric_values_for_skill(data: dict, skill: str, variant: str, max_tokens: float) -> list[str]:
    row = get_row(data["leaderboard"], skill, variant)
    failed = not row.get("success_rate_pct")
    values = [
        row["success_rate_pct"] or 0,
        row["first_try_success_rate_pct"] or 0,
        row["pass_at_k_pct"] or 0,
        0 if failed else row["validated_confidence_mean"] or 0,
        safety_score(row),
        contract_score(row),
        token_efficiency_score(row, max_tokens),
    ]
    return [f"{value:.1f}".rstrip("0").rstrip(".") for value in values]


def render_skill_metric_chart(data: dict, skill: str) -> str:
    max_tokens = max((row["tokens_mean"] or 0) for row in data["leaderboard"])
    metrics = [
        "Success",
        "First try",
        "pass@k",
        "Confidence",
        "Safety",
        "Contract",
        "Token efficiency",
    ]
    quoted_metrics = ", ".join(f'"{metric}"' for metric in metrics)
    ai_values = metric_values_for_skill(data, skill, "ai_kit", max_tokens)
    docs_values = metric_values_for_skill(data, skill, "docs", max_tokens)
    no_context_values = metric_values_for_skill(data, skill, "no_context", max_tokens)
    rows = [get_row(data["leaderboard"], skill, variant) for variant in ["ai_kit", "docs", "no_context"]]
    if all((row["success_rate_pct"] or 0) == 0 for row in rows):
        return (
            "> No variant passed this skill. The chart is outcome-gated, so all business metrics are shown as `0`.\n\n"
            "| Variant | Success | Confidence | Safety Errors | Contract Errors |\n"
            "|---|---:|---:|---:|---:|\n"
            + "\n".join(
                "| {variant} | {success} | {confidence} | {safety} | {contract} |".format(
                    variant={"ai_kit": "AI Kit", "docs": "Official docs", "no_context": "No Context"}[row["variant"]],
                    success=pct(row["success_rate_pct"]),
                    confidence=pct(row["validated_confidence_mean"]),
                    safety=row["safety_errors"],
                    contract=row["contract_errors"],
                )
                for row in rows
            )
        )
    return f"""```mermaid
xychart-beta
    title "{skill}: metrics by variant"
    x-axis [{quoted_metrics}]
    y-axis "Normalized score, higher is better" 0 --> 100
    bar [{", ".join(ai_values)}]
    bar [{", ".join(docs_values)}]
    bar [{", ".join(no_context_values)}]
```"""


SKILL_DESCRIPTIONS = {
    "catalog-design": (
        "We asked the agent to configure a game catalog with virtual currency, items, bundles, "
        "regional pricing, storefront reads, and purchase confirmation. A good answer had to separate Admin API setup from client catalog usage and avoid known pricing/schema mistakes."
    ),
    "login-setup": (
        "We asked the agent to design a web Login integration with Google, email/password, passwordless email, "
        "and backend JWT validation. A good answer had to use the right OAuth/Login flows and verify JWTs safely."
    ),
    "merchant-setup": (
        "We asked the agent to guide a new sandbox merchant/project setup and credential storage. "
        "A good answer had to protect API keys, use the correct project-level credentials, and avoid pretending the agent can create the account itself."
    ),
    "headless-checkout-integration": (
        "We asked the agent to generate a runnable sandbox Headless Checkout implementation. "
        "A good answer had to create real files with SDK setup, safe token handoff, card form flow, return/status handling, and sandbox card validation."
    ),
    "shop-setup": (
        "We asked the agent to plan a full headless shop from catalog browsing to checkout and fulfillment. "
        "A good answer had to connect catalog, cart, Login, payment token, payment UI, webhooks, and production readiness in the right order."
    ),
    "webhooks-impl": (
        "We asked the agent to implement a backend webhook handler for granting items after purchase. "
        "A good answer had to verify signatures, handle retries and idempotency, process required events, and avoid double grants."
    ),
}


def render_skill_metric_charts(data: dict) -> str:
    blocks = []
    for skill in data["summary"]["skills"]:
        description = SKILL_DESCRIPTIONS.get(skill, "We tested whether the agent could complete the expected production workflow for this skill.")
        blocks.append(f"### {skill}\n\n**Description:** {description}\n\n{render_skill_metric_chart(data, skill)}")
    return "\n\n".join(blocks)


def render_legend() -> str:
    return """Legend:

1. 🟩 AI Kit
2. 🟦 Official docs
3. 🟥 No Context"""


def render_outcome_map(data: dict) -> str:
    rows = data["leaderboard"]
    groups = {
        "AI Kit wins": [],
        "Docs wins": [],
        "No Context wins": [],
        "All fail": [],
        "Tie": [],
    }
    for skill in data["summary"]["skills"]:
        ai = get_row(rows, skill, "ai_kit")
        docs = get_row(rows, skill, "docs")
        no_context = get_row(rows, skill, "no_context")
        rates = {
            "AI Kit": ai["success_rate_pct"] or 0,
            "Docs": docs["success_rate_pct"] or 0,
            "No Context": no_context["success_rate_pct"] or 0,
        }
        top_score = max(rates.values())
        winners = [name for name, score in rates.items() if score == top_score]
        if top_score == 0:
            groups["All fail"].append(skill)
        elif winners == ["AI Kit"]:
            groups["AI Kit wins"].append(skill)
        elif winners == ["Docs"]:
            groups["Docs wins"].append(skill)
        elif winners == ["No Context"]:
            groups["No Context wins"].append(skill)
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
- **No Context**: task prompt only.

Each skill was run `k=3` times per variant, then judged by an Anthropic LLM judge against the same rubric.

Main result:

- **AI Kit**: `{ai['successes']}/{ai['runs']}` pass = **{pct(ai['success_rate'])}**
- **Official docs**: `{docs['successes']}/{docs['runs']}` pass = **{pct(docs['success_rate'])}**
- **No Context**: `{no_context['successes']}/{no_context['runs']}` pass = **{pct(no_context['success_rate'])}**

Interpretation: AI Kit outperforms official docs overall, but the result is uneven. It is strong for `catalog-design`, `login-setup`, `headless-checkout-integration`, and `shop-setup`; official docs still win for `merchant-setup`; `webhooks-impl` needs product-quality remediation before it can be trusted.

Generated: `{generated_at}`

## Methodology

### Run Matrix

- Skills: `{", ".join(data['summary']['skills'])}`
- Variants: `ai_kit`, `docs`, `no_context`
- Repetitions: `k=3`
- Total scored runs: `{data['summary']['scored_runs']}`
- Evidence level: agent transcript + LLM judge
- Reliability: `{data['summary']['reliability']}`

### Model Input Data

| Input | Value |
|---|---|
| Provider | Anthropic Messages API |
| Endpoint | `https://api.anthropic.com/v1/messages` |
| Anthropic version header | `2023-06-01` |
| Agent model | `claude-sonnet-4-6` |
| Judge model | `claude-sonnet-4-6` |
| Agent `max_tokens` | `4096` standard eval; `16000` for Headless Checkout artifact eval |
| Judge `max_tokens` | `4096` standard eval; `6000` for Headless Checkout artifact eval |
| Agent temperature | `0.2` |
| Judge temperature | `0` |
| Agent input per run | System instruction + task prompt + variant-specific context |
| Judge input per run | Transcript + rubric checks + safety checks |

`max_tokens` is the output cap we set for each Anthropic API call. The Anthropic API requires this field in the Messages request.

For `headless-checkout-integration`, the payment skill was tested with the stronger artifact-based flow: the agent had to generate runnable project files and pass automated code checks in addition to the LLM judge.

### Variants

| Variant | Context Given to Agent | Purpose |
|---|---|---|
| AI Kit | User task + `SKILL.md` + references | Measures skill value |
| Official docs | User task + official `developers.xsolla.com` docs corpus | Fair documentation baseline |
| No Context | User task only | Baseline for model behavior without skill or documentation context |

### Metrics

| Metric | Meaning |
|---|---|
| Success rate | How many runs passed the rubric and safety checks. This is the main quality signal. |
| Distribution | Shows pass/fail for each of the 3 runs, like `111`, `010`, or `000`. It shows stability, not just the average. |
| First try | Shows whether the first run passed. It matters because users usually expect the first answer to work. |
| pass@k | Shows whether at least one of the 3 runs passed. It shows whether retries can recover a weak first answer. |
| Confidence | Average judge score before applying the pass threshold. It helps distinguish near-misses from bad answers. |
| Safety errors | Count of failed safety checks, such as exposing secrets or unsafe integration advice. Any safety error is a launch blocker. |
| Contract errors | Count of failed API/schema checks. These catch wrong endpoints, wrong field types, and doc-vs-live mismatches. |
| Tokens | Approximate size of the prompt plus answer. Lower token use is better only when quality stays high. |

## Overall Results

{render_variant_summary(rows)}

## Skill Comparison

This table compares all three variants on the same benchmark. Winner is selected between AI Kit and official docs because those are the two usable context strategies for production work.

{render_skill_table(data)}

## Skills

Each chart below is centered on one skill. The x-axis shows the metrics for that skill, and the three bars compare AI Kit, official docs, and No Context.

All values are normalized to a 0–100 scale where higher is better. The chart is outcome-gated: if a variant has `0%` success for a skill, its diagnostic metrics are shown as `0` because a safe-looking but unusable answer does not create business value.

{render_legend()}

{render_skill_metric_charts(data)}

### Outcome Map

Measurement: winner by skill across AI Kit, official docs, and No Context success rate. All-fail means every variant scored 0%.

{render_outcome_map(data)}

## Key Findings

1. `catalog-design`, `login-setup`, and `shop-setup` passed all AI Kit runs (`3/3`) and beat the official docs baseline.
2. `merchant-setup` performed better with official docs (`3/3`) than with AI Kit (`1/3`), indicating the skill needs tightening around credential safety and setup flow.
3. `headless-checkout-integration` replaced the old `payments-config` result and passed all AI Kit artifact-based runs (`3/3`), while official docs passed `2/3`.
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
