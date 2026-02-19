# Runbook — Performance Triage (Triton + GPU)

Generated: 2026-02-19T18:37:36.566358Z

## 1) Symptom → first checks

### Timeouts / latency spikes
- Check gateway timeouts and upstream resets
- Check Triton p99 latency and error rate
- Check GPU util + memory headroom

### Slow but GPU idle
- CPU bottleneck (tokenization/preprocess)
- network path bottleneck
- NUMA/topology issue
- batches too small (overhead dominates)

### Queue growing
- saturated Triton
- too few replicas/instances
- no load shedding

## 2) Split latency into queue vs compute
- queue >> compute → scale out + rate limit
- compute >> queue → tune batching/instances; consider quantization/sharding

## 3) Fix checklist
- Scale replicas
- Tune dynamic batching
- Tune instance_group cautiously
- Cap tokens/context
- Validate correct node placement and CPU headroom
- Verify GPU Operator/driver health
