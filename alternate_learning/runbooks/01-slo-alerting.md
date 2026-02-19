# Runbook — 01 SLO & Alerting

## Dashboards you must have
- End-to-end latency p50/p95/p99
- Triton queue vs compute time
- GPU utilization + memory headroom
- Error rates/timeouts
- Request mix (context length distribution)

## Pager rules (examples)
- Sustained p99 breach for 10m + rising errors
- 5xx above threshold for 5m
- SLO burn rate fast

## Post-incident
- RCA with timeline
- Action items: prevent recurrence, add tests/gates
