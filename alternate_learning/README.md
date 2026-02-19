# Enterprise LLM Inference on OpenShift/Kubernetes with Triton + TensorRT-LLM

Generated: 2026-02-19T18:29:14.823192Z

This repository provides end-to-end, production-grade documentation and manifests for deploying and operating GPU-accelerated LLM inference using:

- NVIDIA GPU Operator
- Triton Inference Server
- TensorRT-LLM optimized engines
- Artifactory / S3 model distribution
- Canary and blue/green rollouts
- GitOps and CI/CD pipelines
- OpenShift or upstream Kubernetes
- Python inference clients

## Repo layout

- docs/ — architecture, scheduling, pipelines, versioning
- diagrams/ — Mermaid architecture and rollout diagrams
- manifests/ — GPU Operator, Triton deployments, services, canary routing
- pipelines/ — Tekton and GitHub Actions examples
- clients/python/ — Python inference examples
- runbooks/ — canary, rollback, troubleshooting
- build/ — TRT-LLM build and publish scripts

Start with:
- docs/01-architecture.md
- docs/02-scheduling-and-gpu-runtime.md
- manifests/gpu-operator/
- manifests/triton/

## Added in v5: sharding, metrics, endpoints, performance triage

- docs/03-gpu-sharding-multi-instance.md
- docs/04-prometheus-metrics-and-troubleshooting.md
- docs/05-triton-api-endpoints.md
- diagrams/06-gpu-sharding-patterns.md
- manifests/observability/01-servicemonitor-triton.yaml
- runbooks/07-performance-triage.md
