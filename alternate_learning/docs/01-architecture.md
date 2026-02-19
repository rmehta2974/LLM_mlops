# 01 Architecture

## Overview

```mermaid
flowchart TB
  Client --> Gateway
  Gateway --> Service
  Service --> TritonV2
  Service --> TritonV3

  TritonV2 --> TRTLLM2
  TritonV3 --> TRTLLM3

  TRTLLM2 --> CUDA2
  TRTLLM3 --> CUDA3

  CUDA2 --> GPU2
  CUDA3 --> GPU3

  Artifactory --> InitContainer
  S3 --> InitContainer
  InitContainer --> TritonV2
  InitContainer --> TritonV3
```

## Components

- Kubernetes/OpenShift scheduler: schedules Triton pods onto GPU nodes
- Triton: schedules inference requests, batching, concurrency
- TensorRT-LLM: optimized inference runtime
- CUDA: GPU execution runtime
- Artifactory/S3: artifact distribution
