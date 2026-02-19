# Canary rollout runbook

1. Deploy v3 alongside v2
2. Shift 1% traffic
3. Monitor p99 latency, GPU utilization
4. Increase to 10%, 50%, 100%
5. Rollback by shifting traffic back
