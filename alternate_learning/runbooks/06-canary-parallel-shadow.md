# Runbook — 06 Canary, Parallel (Blue/Green), and Shadow Releases

Generated: 2026-02-19T16:08:24.382791Z

---

## Canary (preferred)
1. Deploy v3 with 0% traffic
2. Warm up v3 (synthetic probes)
3. Shift 1% -> observe
4. Shift 10% -> observe
5. Shift 50% -> observe
6. Shift 100%
7. Keep v2 hot for rollback window

Rollback triggers:
- sustained p99 regression
- error rate increase
- OOM or restart spike
- GPU headroom collapse

Rollback action:
- set weight back to v2 immediately

---

## Parallel / Blue-Green
1. Deploy v3 alongside v2
2. Warm and validate v3
3. Flip traffic 100% to v3 in change window
4. Keep v2 for rollback window
5. Decommission v2 after stability window

---

## Shadow
1. Mirror a sample of traffic to v3
2. Compare outputs/latency offline
3. Promote to canary

---

## Dashboards to open during release
- p95/p99 latency by version
- errors by version
- Triton queue/compute
- GPU util and memory headroom
- restarts/OOM
