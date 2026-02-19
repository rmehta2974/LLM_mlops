# 04 Observability: Prometheus Metrics, Bad Signals, and How to Fix Them (Triton + GPU)

Generated: 2026-02-19T18:37:36.566358Z

This document gives:
- key Triton Prometheus metrics and what they mean
- bad patterns and what to troubleshoot
- improvement levers (batching, instances, scaling, NUMA, model params)

---

## 1) Enabling metrics

Triton exposes Prometheus metrics on port **8002** by default.
- Endpoint: `http://<pod-ip>:8002/metrics`
- In-cluster: `http://triton.llm-inference.svc:8002/metrics` (if Service exposes it)

---

## 2) Triton metrics to track (most useful)

Metric names can vary slightly by Triton version/backend; these are the common families.

### Requests / errors
- `nv_inference_request_success` (counter)
- `nv_inference_request_failure` (counter)
- `nv_inference_request_duration_us` (histogram)

### Queue vs compute split
- `nv_inference_queue_duration_us` (histogram)
- `nv_inference_compute_duration_us` (histogram)

### Saturation / backlog
- “inflight/pending” gauges (commonly exposed by Triton builds/plugins)
- observe whether backlog grows over time

### Batch effectiveness
- batch size histograms/summaries (backend dependent)

---

## 3) GPU metrics (via GPU Operator + DCGM exporter)

Typical signals:
- GPU utilization (%)
- GPU memory used/total
- power draw, temperature
- throttling (thermal/power)

---

## 4) What bad looks like (and meaning)

### A) p99 increases but GPU util is low
Likely:
- CPU/tokenization bottleneck
- network/gateway bottleneck
- NUMA/topology issue
- batch too small (overhead dominates)

Fix:
- move tokenization off Triton critical path (or client-side)
- raise preferred batch size carefully
- increase pod CPU requests/limits
- improve topology alignment (CPU close to GPU)

### B) Queue time dominates compute time
Signal:
- queue >> compute

Meaning:
- not enough capacity

Fix:
- scale replicas (more pods/GPU nodes)
- add instances only if memory allows
- rate limit / shed load

### C) OOM / restarts or GPU memory near limit
Meaning:
- concurrency too high
- too many instances
- KV cache explosion (long context)

Fix:
- cap tokens/context
- reduce concurrency/instances
- consider quantization
- move to multi-GPU sharding or larger GPU

### D) GPU util pegged + p99 spikes
Meaning:
- saturation and tail latency

Fix:
- scale out
- reduce batch size for strict latency SLO
- use MIG for isolation if sharing

---

## 5) Fast troubleshooting workflow

1. Is it errors or latency?
2. Split latency: queue vs compute
3. Check GPU: util, memory, throttling
4. Check pod placement: correct nodes, enough CPU
5. Validate model config: instance_group + batching
6. Roll fixes with canary

---

## 6) Improvement levers (safe order)

- Scale replicas (cleanest)
- Tune batching (throughput vs latency)
- Tune instance_group (only with headroom)
- Cap context/tokens
- NUMA/topology alignment
- Quantization
