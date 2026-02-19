```mermaid
flowchart TB
  U[Clients] --> GW[Gateway / Ingress]
  GW --> RT[Router / Traffic Split]
  RT --> TR[Triton Pods]
  TR --> TRT[TensorRT-LLM]
  TRT --> GPU[GPU Pool]
  TR --> MR[Model Repo (ODF/S3/GCS)]
  TR --> PROM[Metrics]
  TR --> LOG[Logs/Traces]
```
