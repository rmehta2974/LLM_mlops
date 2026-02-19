# LLMOps Pipeline

```mermaid
flowchart TB
  A[Train/Fine-tune] --> B[Registry (MLflow)]
  B --> C[Engine Build (TRT-LLM)]
  C --> D[Container Build]
  D --> E[Deploy Staging (GitOps)]
  E --> F[Perf/Quality Gates]
  F --> G[Canary]
  G --> H[Prod]
  H --> I[Monitor + Feedback]
  I --> A
```
