#!/usr/bin/env python3
"""Generate README.md for the Headless Checkout skill eval use case."""

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


def row(data: dict, variant: str) -> dict:
    return next(item for item in data["leaderboard"] if item["variant"] == variant)


def dist(item: dict) -> str:
    values = item.get("success_distribution") or []
    return "".join(str(value) for value in values) if values else "n/a"


def table(data: dict) -> str:
    labels = {
        "ai_kit": "AI Kit",
        "docs": "Official docs",
        "no_context": "No Context",
    }
    lines = [
        "| Variant | Pass | Success Rate | Distribution | Judge Confidence | Safety Errors | Contract Errors | Avg Tokens |",
        "|---|---:|---:|---|---:|---:|---:|---:|",
    ]
    for variant in ["ai_kit", "docs", "no_context"]:
        item = row(data, variant)
        lines.append(
            "| {label} | {successes}/{runs} | {success_rate} | `{distribution}` | {confidence} | {safety} | {contract} | {tokens} |".format(
                label=labels[variant],
                successes=item["successes"],
                runs=item["runs"],
                success_rate=pct(item["success_rate_pct"]),
                distribution=dist(item),
                confidence=pct(item["validated_confidence_mean"]),
                safety=item["safety_errors"],
                contract=item["contract_errors"],
                tokens=item["tokens_mean"],
            )
        )
    return "\n".join(lines)


def chart(data: dict, *, field: str, title: str, y_label: str, y_max: int) -> str:
    values = [str(row(data, variant).get(field) or 0) for variant in ["ai_kit", "docs", "no_context"]]
    return f"""```mermaid
xychart-beta
    title "{title}"
    x-axis ["AI Kit", "Official docs", "No Context"]
    y-axis "{y_label}" 0 --> {y_max}
    bar [{", ".join(values)}]
```"""


def render(data: dict) -> str:
    ai = row(data, "ai_kit")
    docs = row(data, "docs")
    no_context = row(data, "no_context")
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    return f"""# Headless Checkout Skill Evaluation

## TL;DR

We tested the current `headless-checkout-integration` skill from the latest `xsolla-ai-kit` repository.
The expected result was a runnable sandbox Headless Checkout implementation, not just a written explanation.

Main result:

- **AI Kit**: `{ai['successes']}/{ai['runs']}` pass = **{pct(ai['success_rate_pct'])}**
- **Official docs**: `{docs['successes']}/{docs['runs']}` pass = **{pct(docs['success_rate_pct'])}**
- **No Context**: `{no_context['successes']}/{no_context['runs']}` pass = **{pct(no_context['success_rate_pct'])}**

Conclusion: AI Kit produced the strongest result for this use case. It generated complete runnable artifacts more reliably than official docs or no-context prompting.

Generated: `{generated_at}`

## What We Tested

Use case: **integrate Xsolla Headless Checkout into a web app and complete a sandbox credit-card payment flow**.

Expected implementation:

- install and initialize `@xsolla/pay-station-sdk` with `sandbox: true`;
- safely get and hand off a short-lived payment token;
- render payment method selection;
- build the card form from server-driven `form.fields`;
- call `form.activate()` after secure fields are mounted;
- handle `onNextAction` branches: `show_fields`, `show_errors`, `redirect`, `3DS`, and `check_status`;
- implement a return/status page using `psdk-status` or `getStatus()`;
- include validation for three sandbox card paths:
  - `4111111111111111` — no 3DS;
  - `4111111111111152` — 3DS via acquirer redirect;
  - `4423610000000007` — 3DS via external MPI.

## How We Tested

We ran the same task in three variants:

| Variant | Input Context |
|---|---|
| AI Kit | Task prompt + `headless-checkout-integration/SKILL.md` + references |
| Official docs | Task prompt + official Xsolla Headless Checkout documentation |
| No Context | Task prompt only |

Each variant ran `k=3` times. Every run had to generate real project files, then pass both automated code checks and an LLM judge.

## Evaluation Algorithm

```mermaid
flowchart LR
  A[Test prompt] --> B[Run agent 3 times per variant]
  B --> C[Generated project files]
  C --> D[Programmatic code checks]
  C --> E[LLM judge rubric]
  D --> F[Pass/fail]
  E --> F
  F --> G[Aggregate success rate, confidence, errors, tokens]
```

## Metrics

| Metric | Meaning |
|---|---|
| Success rate | How many runs passed both the code checks and judge rubric. This is the main quality signal. |
| Distribution | Shows pass/fail for each of the 3 runs, like `111` or `110`. It shows stability, not just the average. |
| Judge confidence | Average judge score before thresholding. It shows how close failed runs were to passing. |
| Safety errors | Count of failed safety checks, such as exposing API keys. Any safety error is a launch risk. |
| Contract errors | Count of failed required artifact/code checks. These show missing implementation pieces. |
| Avg tokens | Approximate size of prompt plus answer. Lower is better only when quality remains high. |

## Results

{table(data)}

## Visual Summary

Legend:

1. 🟩 AI Kit
2. 🟦 Official docs
3. 🟥 No Context

### Success Rate

Measurement: percent of runs that passed the full artifact-based evaluation.

{chart(data, field="success_rate_pct", title="Headless Checkout Success Rate", y_label="Success rate (%)", y_max=100)}

### Judge Confidence

Measurement: average judge pass rate before thresholding.

{chart(data, field="validated_confidence_mean", title="Headless Checkout Judge Confidence", y_label="Confidence (%)", y_max=100)}

### Token Volume

Measurement: approximate mean tokens in prompt plus answer transcript.

{chart(data, field="tokens_mean", title="Headless Checkout Token Volume", y_label="Mean tokens", y_max=10000)}

## What We Got

AI Kit passed all three runs. The official docs baseline passed two out of three runs. The no-context baseline passed zero runs.

This means the new skill materially improves the agent's ability to produce a complete sandbox Headless Checkout implementation, especially when the eval checks generated files instead of only prose.

## Files

- `data/dashboard-data.json` — machine-readable scored result.
- `data/ai-kit-eval-report.md` — raw harness report.
- `scripts/generate_readme.py` — regenerates this README from `data/dashboard-data.json`.

## Regenerate

```bash
python3 scripts/generate_readme.py
```
"""


def main() -> None:
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    README_PATH.write_text(render(data), encoding="utf-8")
    print(f"Wrote {README_PATH}")


if __name__ == "__main__":
    main()
