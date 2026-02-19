# 07 — Observability and SRE (Mission-Critical Operations)

## 1) The “four golden signals” (plus GPU)
- Latency (p50/p95/p99)
- Traffic (RPS, tokens/sec)
- Errors (5xx, timeouts, model errors)
- Saturation (queue depth, pending requests)
- GPU: utilization, memory, power/temp, throttling

## 2) Step-by-step: What to instrument
1. Gateway metrics (auth failures, rate-limits, latency)
2. Router metrics (traffic split, per-model RPS)
3. Triton metrics (queue time vs compute time)
4. GPU telemetry (DCGM exporter)
5. Node metrics (disk pressure, network errors)

## 3) SLO examples
- Availability 99.9%
- p99 latency target per request class (short/long prompts)
- error rate budgets

## 4) Alerting strategy
- Page only on user impact (SLO burn, sustained p99 breaches)
- Ticket on capacity (GPU util high, memory headroom low)
- Ticket on hygiene (node pressure, image pulls)

## 5) Incident workflow
- detect -> triage -> mitigate -> recover -> RCA
- keep runbooks and rollback procedures tested
