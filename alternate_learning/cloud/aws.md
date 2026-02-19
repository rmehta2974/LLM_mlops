# AWS (EKS) — Scalable LLM Inference Platform

## Components
- EKS + OIDC
- GPU node group (g5/p4/p5) + NVIDIA plugin/operator
- ALB (API) + optionally NLB (high-throughput gRPC)
- S3 (versioned artifacts), optional EFS/EBS cache
- Observability: AMP/AMG or CloudWatch

## Diagram
```mermaid
flowchart TB
  U[Clients] --> ALB[ALB / API Gateway]
  ALB --> SVC[K8s Service]
  SVC --> TR[Triton Pods on GPU nodes]
  TR --> S3[S3 Artifacts]
  TR --> AMP[Managed Prometheus]
  AMP --> AMG[Managed Grafana]
```
