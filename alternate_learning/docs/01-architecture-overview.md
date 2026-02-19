# 01 — Architecture Overview (Why/Where/How)

This doc describes a production-grade LLM inference platform and *why* each component exists.

## 1) Goals and constraints

**Enterprise goals**
- Low and predictable latency (p95/p99)
- High throughput (tokens/sec) at lowest cost/token
- Safe rollouts (no downtime, quick rollback)
- Multi-tenant isolation (RBAC, network isolation, GPU quotas)
- Observability-first operations (SLOs, traces, GPU telemetry)
- DR-ready (zones/regions)

**Constraints**
- GPU capacity is limited; maximize utilization
- Models are huge; cold-start/model-load can be minutes
- Long prompts can cause OOM or tail latency spikes
- Pre/post-processing (tokenization, guardrails) can bottleneck

## 2) Reference service layers

### A) North/South API layer
- API Gateway / Ingress: auth, rate limiting, WAF, routing, TLS
- Router: traffic shaping, canary splits, model selection

Why:
- Keeps Triton pods focused on inference
- Enforces enterprise API policies outside the model runtime

### B) Inference runtime layer
- Triton Inference Server: standardized serving, model lifecycle, batching/concurrency, metrics
- TensorRT-LLM: optimized LLM execution engines and runtime

Why:
- Triton provides operational controls; TRT-LLM provides GPU efficiency

### C) Platform layer (OpenShift/Kubernetes)
- GPU Operator + device plugin
- Scheduling: node selectors, taints/tolerations, topology spread
- Autoscaling: HPA/KEDA
- Security: RBAC, SCC/PSA, network policies, mTLS (optional)

Why:
- Repeatable HA and safe operations at scale

### D) Artifact layer (model repo)
- ODF PVC or S3/GCS as source-of-truth
- Optional node-local/pod-local cache for fast startup

Why:
- Inference pods are stateless compute; model artifacts are stateful

### E) Observability + SRE
- Prometheus/Grafana, Alertmanager
- Logs (Loki/Elastic), Traces (Tempo/Jaeger)
- GPU telemetry (DCGM exporter)

## 3) Data paths

### Request data path
1. Client sends request (prompt + generation parameters)
2. Gateway authenticates, rate-limits, selects model/tenant routing
3. Router applies traffic split (canary/blue-green) if enabled
4. Triton receives request (gRPC preferred for high throughput)
5. Triton schedules (batching/concurrency) then dispatches backend call
6. TensorRT-LLM runs on GPU; returns token stream/result
7. Response returned via gateway to client

### Control/ops path
- CI builds TRT-LLM engines and container images
- GitOps deploys new versions (staging -> canary -> prod)
- Rollback is a Git revert or traffic split back to v1

## 4) Minimum viable production checklist
- [ ] API gateway separate from inference
- [ ] Dedicated GPU node pool + taints/tolerations
- [ ] Versioned model repo (ODF/S3/GCS) with rollback plan
- [ ] Readiness probes verify model loaded
- [ ] Autoscaling policy (RPS/queue length)
- [ ] SLO dashboards and alerts (latency, errors, GPU util, OOM)
- [ ] Runbooks for p99 spikes, OOM, model load failures
