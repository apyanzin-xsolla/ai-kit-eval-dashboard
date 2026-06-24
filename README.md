# AI Kit Eval Dashboard

Read-only mini-site for Xsolla AI Kit skill evals.

It visualizes:

- success distribution over `k` runs;
- first-try success and `pass@k`;
- token usage;
- validated confidence;
- contract and safety errors.

## Data

The app reads static eval output from:

```text
src/data/dashboard-data.json
```

Generate fresh data from the AI Kit eval package, then copy it into this app:

```bash
PYTHONPATH=evals python3 -m ai_kit_evals.harness \
  --repo-root . \
  --k 3 \
  --runner fixture \
  --out-dir eval-output

cp eval-output/dashboard-data.json ../mini-apps/apps/ai-kit-eval-dashboard/src/data/dashboard-data.json
```

## Local Dev

```bash
pnpm install
pnpm run dev
```

## Build

```bash
npx tsc --noEmit
pnpm run build
```

## Deploy

PR this app into `xsolla/mini-apps` under:

```text
apps/ai-kit-eval-dashboard
```

Use branch naming:

```text
mini-apps/ai-kit-eval-dashboard-v1.0.0
```

After CI/CD merges it to `main`, the app will be available at:

```text
https://prototype.xsolla.dev/mini-apps/ai-kit-eval-dashboard
```
