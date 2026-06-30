# Xsolla AI Kit Skill Evaluation

## TL;DR

We evaluated 6 `xsolla-ai-kit` skills using the current harness algorithm:

- **AI Kit**: task prompt + `SKILL.md` + skill references.
- **Official docs**: task prompt + curated `developers.xsolla.com` corpus.
- **No context**: task prompt only.

Each skill was run `k=3` times per variant and judged by an Anthropic LLM judge against the same rubric.

Main result:

- **AI Kit**: `10/18` pass = **55.6%**
- **Official docs**: `8/18` pass = **44.4%**
- **No context control**: `0/18` pass = **0%**

Interpretation: AI Kit outperforms official docs overall, but quality is uneven. Strong skills are `catalog-design`, `login-setup`, and `shop-setup`. Weak skills are `merchant-setup`, `payments-config`, and `webhooks-impl`.

Generated: `2026-06-30 14:54 UTC`

## Methodology

### Run Matrix

- Skills: `catalog-design, login-setup, merchant-setup, payments-config, shop-setup, webhooks-impl`
- Variants: `ai_kit`, `docs`, `no_context`
- Repetitions: `k=3`
- Total scored runs: `54`
- Evidence level: agent transcript + LLM judge
- Reliability: `scored`

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

| Variant | Pass | Success Rate | Avg Confidence | Safety Errors | Contract Errors | Avg Tokens |
|---|---:|---:|---:|---:|---:|---:|
| AI Kit | 10/18 | 55.6% | 85.9% | 6 | 0 | 2203 |
| Official docs | 8/18 | 44.4% | 82.9% | 6 | 0 | 2097 |
| No context | 0/18 | 0% | 60.1% | 6 | 1 | 1941 |

## Skill Comparison

This table keeps the main benchmark as **AI Kit vs Official docs**. The no-context result is included as a separate control column and does not change the AI Kit/docs winner.

| Skill | AI Kit | Official Docs | Winner | No Context | AI Kit Safety | Docs Safety | Notes |
|---|---:|---:|---|---:|---:|---:|---|
| catalog-design | 100% `111` | 66.7% `011` | AI Kit | 0% `000` | 0 | 0 | - |
| login-setup | 100% `111` | 33.3% `010` | AI Kit | 0% `000` | 0 | 0 | - |
| merchant-setup | 33.3% `010` | 100% `111` | Official docs | 0% `000` | 2 | 0 | AI Kit safety risk |
| payments-config | 0% `000` | 0% `000` | Tie | 0% `000` | 3 | 3 | both fail, AI Kit safety risk, docs safety risk, skill is placeholder/planned |
| shop-setup | 100% `111` | 66.7% `110` | AI Kit | 0% `000` | 0 | 1 | docs safety risk |
| webhooks-impl | 0% `000` | 0% `000` | Tie | 0% `000` | 1 | 2 | both fail, AI Kit safety risk, docs safety risk |

## Graphs

### AI Kit vs Official Docs Success Rate

**catalog-design**
- AI Kit      ████████████████████ 100%
- Docs        █████████████░░░░░░░ 66.7%

**login-setup**
- AI Kit      ████████████████████ 100%
- Docs        ███████░░░░░░░░░░░░░ 33.3%

**merchant-setup**
- AI Kit      ███████░░░░░░░░░░░░░ 33.3%
- Docs        ████████████████████ 100%

**payments-config**
- AI Kit      ░░░░░░░░░░░░░░░░░░░░ 0%
- Docs        ░░░░░░░░░░░░░░░░░░░░ 0%

**shop-setup**
- AI Kit      ████████████████████ 100%
- Docs        █████████████░░░░░░░ 66.7%

**webhooks-impl**
- AI Kit      ░░░░░░░░░░░░░░░░░░░░ 0%
- Docs        ░░░░░░░░░░░░░░░░░░░░ 0%

### No-Context Control Success Rate

**catalog-design**
- No context  ░░░░░░░░░░░░░░░░░░░░ 0%

**login-setup**
- No context  ░░░░░░░░░░░░░░░░░░░░ 0%

**merchant-setup**
- No context  ░░░░░░░░░░░░░░░░░░░░ 0%

**payments-config**
- No context  ░░░░░░░░░░░░░░░░░░░░ 0%

**shop-setup**
- No context  ░░░░░░░░░░░░░░░░░░░░ 0%

**webhooks-impl**
- No context  ░░░░░░░░░░░░░░░░░░░░ 0%

## No-Context Control Results

The no-context control shows what the same model does with only the task prompt and no skill/docs context.

| Skill | No-Context Success | Distribution | Confidence | Safety | Contract |
|---|---:|---|---:|---:|---:|
| catalog-design | 0% | `000` | 73.3% | 0 | 0 |
| login-setup | 0% | `000` | 64% | 1 | 0 |
| merchant-setup | 0% | `000` | 70% | 0 | 0 |
| payments-config | 0% | `000` | 50% | 3 | 0 |
| shop-setup | 0% | `000` | 40% | 1 | 1 |
| webhooks-impl | 0% | `000` | 63% | 1 | 0 |

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
