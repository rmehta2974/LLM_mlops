# LLMOps / MLOps Platform Documentation

> **Comprehensive guide for deploying, operating, and scaling LLM inference at enterprise scale**  
> Covers Triton Inference Server, TensorRT-LLM, Kubeflow, NVIDIA on-prem, cloud (AWS/GCP), and production best practices.

---

## Table of Contents

| Section | Description |
|--------|-------------|
| [01. Triton Inference Server](01-triton-inference-server/) | Architecture, when/what/how, configuration, deployment |
| [02. TensorRT-LLM](02-tensorrt-llm/) | Integration, optimization, TRT-LLM with Triton |
| [03. MLOps Pipelines](03-mlops-pipelines/) | Kubeflow, NVIDIA on-prem, end-to-end workflows |
| [04. Scaling & Availability](04-scaling-availability/) | Load balancing, HA, autoscaling, monitoring |
| [05. Cloud Deployment](05-cloud-deployment/) | AWS, GCP, APIs, managed services |
| [06. Operational Runbooks](06-operational-runbooks/) | Incident, change, event management |

**Quick navigation:**
- [Quick Reference](QUICK-REFERENCE.md) – When to use what, config snippets, checklists
- [Architecture Overview](ARCHITECTURE-OVERVIEW.md) – End-to-end system context and data flows

---

## Quick Navigation

```
llmops-platform-docs/
├── README.md
├── 01-triton-inference-server/
│   ├── 01-architecture.md
│   ├── 02-when-what-how.md
│   ├── 03-configuration-deployment.md
│   └── 04-troubleshooting.md
├── 02-tensorrt-llm/
│   ├── 01-overview-integration.md
│   ├── 02-optimization-techniques.md
│   └── 03-triton-trtllm-workflow.md
├── 03-mlops-pipelines/
│   ├── 01-kubeflow-pipelines.md
│   ├── 02-nvidia-onprem.md
│   └── 03-end-to-end-workflow.md
├── 04-scaling-availability/
│   ├── 01-load-balancing.md
│   ├── 02-high-availability.md
│   └── 03-monitoring-observability.md
├── 05-cloud-deployment/
│   ├── 01-aws-sagemaker-neurons.md
│   ├── 02-gcp-vertex-ai.md
│   └── 03-api-design-patterns.md
└── 06-operational-runbooks/
    ├── 01-incident-management.md
    ├── 02-change-management.md
    └── 03-event-management.md
```

---

## Audience

- **AI/ML Platform Engineers** deploying LLMs in production
- **MLOps/LLMOps Practitioners** managing inference pipelines
- **Infrastructure Engineers** running Kubernetes/OpenShift at scale
- **Solutions Architects** designing GPU-accelerated AI platforms

---

## Prerequisites

- Basic knowledge of Kubernetes, containers, and microservices
- Familiarity with LLM concepts (embeddings, completion, inference)
- Understanding of GPU computing (NVIDIA CUDA, TensorRT)

---

## License & Contributions

Documentation for internal reference and skill development. Diagrams use Mermaid (renders on GitHub).
