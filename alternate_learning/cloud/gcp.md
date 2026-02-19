# GCP (GKE) — Scalable LLM Inference Platform

## Components
- GKE (regional preferred)
- GPU node pool + NVIDIA drivers/plugin
- Cloud Load Balancing / Gateway
- GCS (versioned artifacts), optional Filestore cache
- Monitoring: Managed Service for Prometheus + Cloud Logging

## Diagram
```mermaid
flowchart TB
  U[Clients] --> GLB[Cloud Load Balancer]
  GLB --> SVC[K8s Service]
  SVC --> TR[Triton Pods on GPU nodes]
  TR --> GCS[GCS Artifacts]
  TR --> MSP[Managed Prometheus]
  MSP --> GRA[Grafana]
```
