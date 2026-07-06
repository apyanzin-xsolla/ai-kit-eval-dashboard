# Xsolla AI Kit Skill Eval Report

- Total runs: `54`
- Scored runs: `54`
- Not scored runs: `0`
- Reliability: `scored`
- Skills: `catalog-design, login-setup, merchant-setup, headless-checkout-integration, shop-setup, webhooks-impl`
- Variants: `ai_kit, docs, no_context`
- Contract errors: `1`
- Safety errors: `21`

## Leaderboard

| Skill | Variant | Runs | Scored | Status | Evidence | Success distribution | Success rate | First try | pass@k | Tokens | Confidence | Contract errors | Safety errors | Last live contract check |
|---|---|---:|---:|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| catalog-design | ai_kit | 3 | 3 | scored | agent_transcript+llm_judge | `000` | 0% +/- 0.0% | 0% | 0% | 2323.7 | 80.0% | 0 | 0 | - |
| catalog-design | docs | 3 | 3 | scored | agent_transcript+llm_judge | `000` | 0% +/- 0.0% | 0% | 0% | 2136.3 | 62.7% | 0 | 0 | - |
| catalog-design | no_context | 3 | 3 | scored | agent_transcript+llm_judge | `000` | 0% +/- 0.0% | 0% | 0% | 2210.7 | 44.7% | 0 | 0 | - |
| login-setup | ai_kit | 3 | 3 | scored | agent_transcript+llm_judge | `011` | 66.7% +/- 47.1% | 0% | 100% | 2409.3 | 86.7% | 0 | 1 | - |
| login-setup | docs | 3 | 3 | scored | agent_transcript+llm_judge | `000` | 0% +/- 0.0% | 0% | 0% | 2400.3 | 67.6% | 0 | 0 | - |
| login-setup | no_context | 3 | 3 | scored | agent_transcript+llm_judge | `000` | 0% +/- 0.0% | 0% | 0% | 2140.7 | 38.3% | 0 | 1 | - |
| merchant-setup | ai_kit | 3 | 3 | scored | agent_transcript+llm_judge | `101` | 66.7% +/- 47.1% | 100% | 100% | 866.3 | 94.3% | 0 | 1 | - |
| merchant-setup | docs | 3 | 3 | scored | agent_transcript+llm_judge | `000` | 0% +/- 0.0% | 0% | 0% | 1247 | 80.4% | 0 | 0 | - |
| merchant-setup | no_context | 3 | 3 | scored | agent_transcript+llm_judge | `000` | 0% +/- 0.0% | 0% | 0% | 1118.3 | 30.4% | 0 | 0 | - |
| headless-checkout-integration | ai_kit | 3 | 3 | scored | agent_transcript+llm_judge | `111` | 100% +/- 0.0% | 100% | 100% | 9010 | 100.0% | 0 | 0 | - |
| headless-checkout-integration | docs | 3 | 3 | scored | agent_transcript+llm_judge | `111` | 100% +/- 0.0% | 100% | 100% | 8224 | 97.0% | 0 | 0 | - |
| headless-checkout-integration | no_context | 3 | 3 | scored | agent_transcript+llm_judge | `000` | 0% +/- 0.0% | 0% | 0% | 5533 | 15.2% | 1 | 3 | - |
| shop-setup | ai_kit | 3 | 3 | scored | agent_transcript+llm_judge | `000` | 0% +/- 0.0% | 0% | 0% | 2534.3 | 46.7% | 0 | 2 | - |
| shop-setup | docs | 3 | 3 | scored | agent_transcript+llm_judge | `000` | 0% +/- 0.0% | 0% | 0% | 2361.7 | 47.7% | 0 | 3 | - |
| shop-setup | no_context | 3 | 3 | scored | agent_transcript+llm_judge | `000` | 0% +/- 0.0% | 0% | 0% | 2119 | 25.5% | 0 | 3 | - |
| webhooks-impl | ai_kit | 3 | 3 | scored | agent_transcript+llm_judge | `000` | 0% +/- 0.0% | 0% | 0% | 2494 | 41.7% | 0 | 2 | - |
| webhooks-impl | docs | 3 | 3 | scored | agent_transcript+llm_judge | `000` | 0% +/- 0.0% | 0% | 0% | 2454.7 | 45.8% | 0 | 2 | - |
| webhooks-impl | no_context | 3 | 3 | scored | agent_transcript+llm_judge | `000` | 0% +/- 0.0% | 0% | 0% | 2336 | 34.5% | 0 | 3 | - |

## Artifact Contract

Every run directory contains `prompt.md`, `context.json`, `transcript.*`, `judge-payload.json`, and `teardown.json`.
CI should upload the whole output directory as the eval artifact.
