# Xsolla AI Kit Skill Eval Report

- Total runs: `54`
- Scored runs: `54`
- Not scored runs: `0`
- Reliability: `scored`
- Skills: `catalog-design, login-setup, merchant-setup, payments-config, shop-setup, webhooks-impl`
- Variants: `ai_kit, docs, no_context`
- Contract errors: `1`
- Safety errors: `18`

## Leaderboard

| Skill | Variant | Runs | Scored | Status | Evidence | Success distribution | Success rate | First try | pass@k | Tokens | Confidence | Contract errors | Safety errors | Last live contract check |
|---|---|---:|---:|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| catalog-design | ai_kit | 3 | 3 | scored | agent_transcript+llm_judge | `111` | 100% +/- 0.0% | 100% | 100% | 2355 | 100.0% | 0 | 0 | - |
| catalog-design | docs | 3 | 3 | scored | agent_transcript+llm_judge | `011` | 66.7% +/- 47.1% | 0% | 100% | 2241.7 | 93.3% | 0 | 0 | - |
| catalog-design | no_context | 3 | 3 | scored | agent_transcript+llm_judge | `000` | 0% +/- 0.0% | 0% | 0% | 2247.3 | 73.3% | 0 | 0 | - |
| login-setup | ai_kit | 3 | 3 | scored | agent_transcript+llm_judge | `111` | 100% +/- 0.0% | 100% | 100% | 2461.7 | 100.0% | 0 | 0 | - |
| login-setup | docs | 3 | 3 | scored | agent_transcript+llm_judge | `010` | 33.3% +/- 47.1% | 0% | 100% | 2348.7 | 84.0% | 0 | 0 | - |
| login-setup | no_context | 3 | 3 | scored | agent_transcript+llm_judge | `000` | 0% +/- 0.0% | 0% | 0% | 2255.3 | 64.0% | 0 | 1 | - |
| merchant-setup | ai_kit | 3 | 3 | scored | agent_transcript+llm_judge | `010` | 33.3% +/- 47.1% | 0% | 100% | 819.7 | 83.3% | 0 | 2 | - |
| merchant-setup | docs | 3 | 3 | scored | agent_transcript+llm_judge | `111` | 100% +/- 0.0% | 100% | 100% | 1231.3 | 100.0% | 0 | 0 | - |
| merchant-setup | no_context | 3 | 3 | scored | agent_transcript+llm_judge | `000` | 0% +/- 0.0% | 0% | 0% | 1157.7 | 70.0% | 0 | 0 | - |
| payments-config | ai_kit | 3 | 3 | scored | agent_transcript+llm_judge | `000` | 0% +/- 0.0% | 0% | 0% | 2356 | 50.0% | 0 | 3 | - |
| payments-config | docs | 3 | 3 | scored | agent_transcript+llm_judge | `000` | 0% +/- 0.0% | 0% | 0% | 1917 | 58.3% | 0 | 3 | - |
| payments-config | no_context | 3 | 3 | scored | agent_transcript+llm_judge | `000` | 0% +/- 0.0% | 0% | 0% | 2106.3 | 50.0% | 0 | 3 | - |
| shop-setup | ai_kit | 3 | 3 | scored | agent_transcript+llm_judge | `111` | 100% +/- 0.0% | 100% | 100% | 2711.7 | 100.0% | 0 | 0 | - |
| shop-setup | docs | 3 | 3 | scored | agent_transcript+llm_judge | `110` | 66.7% +/- 47.1% | 100% | 100% | 2337.7 | 93.3% | 0 | 1 | - |
| shop-setup | no_context | 3 | 3 | scored | agent_transcript+llm_judge | `000` | 0% +/- 0.0% | 0% | 0% | 1573.3 | 40.0% | 1 | 1 | - |
| webhooks-impl | ai_kit | 3 | 3 | scored | agent_transcript+llm_judge | `000` | 0% +/- 0.0% | 0% | 0% | 2516 | 82.3% | 0 | 1 | - |
| webhooks-impl | docs | 3 | 3 | scored | agent_transcript+llm_judge | `000` | 0% +/- 0.0% | 0% | 0% | 2505.7 | 68.3% | 0 | 2 | - |
| webhooks-impl | no_context | 3 | 3 | scored | agent_transcript+llm_judge | `000` | 0% +/- 0.0% | 0% | 0% | 2304.7 | 63.0% | 0 | 1 | - |

## Artifact Contract

Every run directory contains `prompt.md`, `context.json`, `transcript.*`, `judge-payload.json`, and `teardown.json`.
CI should upload the whole output directory as the eval artifact.


---

## Replacement payment skill: headless-checkout-integration

# Xsolla AI Kit Skill Eval Report

- Total runs: `9`
- Scored runs: `9`
- Not scored runs: `0`
- Reliability: `scored`
- Skills: `headless-checkout-integration`
- Variants: `ai_kit, docs, no_context`
- Contract errors: `0`
- Safety errors: `0`

## Leaderboard

| Skill | Variant | Runs | Scored | Status | Evidence | Success distribution | Success rate | First try | pass@k | Tokens | Confidence | Contract errors | Safety errors |
|---|---|---:|---:|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| headless-checkout-integration | ai_kit | 3 | 3 | scored | agent_transcript+llm_judge | `111` | 100% | 100% | 100% | 8931.3 | 97.0% | 0 | 0 |
| headless-checkout-integration | docs | 3 | 3 | scored | agent_transcript+llm_judge | `110` | 66.7% | 100% | 100% | 8169.3 | 63.6% | 0 | 0 |
| headless-checkout-integration | no_context | 3 | 3 | scored | agent_transcript+llm_judge | `000` | 0% | 0% | 0% | 317 | 0% | 0 | 0 |
