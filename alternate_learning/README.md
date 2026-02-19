# LLMOps on Kubernetes/OpenShift: Triton + TensorRT-LLM (Enterprise Runbook)

Generated: 2026-02-19T15:09:39.905715Z

This repository is a **deep, step-by-step** GitHub documentation pack for designing and operating a **production LLM inference platform** using:

- **Triton Inference Server** (serving/runtime control plane)
- **TensorRT-LLM** (LLM optimization + execution engines)
- **OpenShift / Kubernetes** (multi-tenant, HA, scaling, policy)
- **Kubeflow / MLflow** (MLOps/LLMOps pipelines, registry, promotion)
- **Observability + SRE** (SLOs, dashboards, incident playbooks)
- **OpenShift Data Foundation (ODF)** (artifact storage + HA model repo)
- **AWS and GCP reference architectures** (cloud-native variants)

> This is written for interviews and real implementations: **why / where / how**, scaling, availability, and troubleshooting.

---

## Repo map

- `docs/` — architecture and design docs
- `diagrams/` — Mermaid diagrams (render in GitHub)
- `manifests/` — Kubernetes/OpenShift YAML examples (Triton, autoscaling, GPU scheduling, configmaps)
- `runbooks/` — operational playbooks (deploy, scale, debug, incident response)
- `cloud/` — AWS & GCP implementation notes + patterns
- `examples/` — sample config snippets (Triton model config, request profiles)

---

## Quick start index

1. Architecture overview: `docs/01-architecture-overview.md`
2. Triton deep dive: `docs/02-triton-architecture.md`
3. TensorRT-LLM deep dive: `docs/03-tensorrt-llm.md`
4. LLMOps pipeline: `docs/04-llmops-pipeline.md`
5. Scaling & HA: `docs/05-scaling-availability.md`
6. Networking & API design: `docs/06-api-gateway-networking.md`
7. Observability & SRE: `docs/07-observability-sre.md`
8. ODF storage patterns: `docs/08-odf-storage.md`
9. Troubleshooting: `runbooks/05-troubleshooting.md`
10. Cloud reference (AWS/GCP): `cloud/README.md`

## Added deep-dive docs

- `docs/09-model-optimization.md`
- `docs/10-mission-critical-ops.md`
- `docs/11-load-balancing-ha-routing.md`
- `docs/12-kubeflow-mlflow-implementation.md`
