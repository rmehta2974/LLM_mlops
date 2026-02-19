# 05 — Scaling and Availability (Step-by-step)

## 1) Scaling strategies

### A) Scale out (more Triton replicas)
Use when:
- model fits on a single GPU per pod
- you want HA and higher throughput

Mechanics:
- add replicas
- service load balances across them
- use topology spread across zones

### B) Scale up (bigger GPUs)
Use when:
- current GPU memory is limiting
- batching efficiency improves with bigger GPU

### C) Multi-GPU sharding (tensor parallel)
Use when:
- model does not fit on one GPU
- you need multi-GPU execution

## 2) Availability patterns

### Pattern 1: N+1 within a zone
- multiple replicas
- protects from node/pod failures

### Pattern 2: Multi-zone active/active
- spread replicas across zones
- storage must support zone behavior (or use object store + cache)

### Pattern 3: Multi-region DR
- replicate artifacts (S3/GCS)
- warm standby cluster and tested failover

## 3) Autoscaling options

### HPA
- scales on CPU or custom metrics
- good for predictable workloads

### KEDA
- scales on queue depth / RPS / custom triggers
- best for bursty workloads

## 4) Readiness + graceful termination
- readiness gates on model-loaded state
- preStop drains connections
- keep old pods until new ones ready
