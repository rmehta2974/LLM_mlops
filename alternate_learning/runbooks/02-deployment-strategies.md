# Runbook — 02 Deployment Strategies (Blue/Green, Canary, Shadow)

## Blue/Green
- Deploy v2 alongside v1
- Flip traffic to v2 after it is ready
- Keep v1 warm for rollback

## Canary (recommended)
1. Deploy v2 with 0% traffic
2. Warm up model + synthetic probes
3. Shift 1% traffic for 10–30 minutes
4. Gate on p99/errors/GPU/OOM
5. Increase to 10% -> 50% -> 100%

## Shadow
- Mirror traffic to v2 for validation without user impact
