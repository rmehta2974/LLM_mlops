# Triton Inference Server – Architecture

## 1. Overview

**NVIDIA Triton Inference Server** is an open-source inference serving software that enables deployment of ML/DL models at scale. It supports multiple frameworks (TensorFlow, PyTorch, ONNX, TensorRT) and is designed for **low latency**, **high throughput**, and **flexible model deployment** in production.

---

## 2. High-Level Architecture Diagram

```mermaid
flowchart TB
    subgraph Clients["Client Layer"]
        REST[REST/gRPC Clients]
        Python[Python SDK]
        C[ C++ Client]
    end

    subgraph Triton["Triton Inference Server"]
        direction TB
        API[HTTP/gRPC API]
        Sched[Request Scheduler]
        
        subgraph ModelRepo["Model Repository"]
            M1[Model A - TensorRT]
            M2[Model B - ONNX]
            M3[Model C - PyTorch]
        end

        subgraph Backend["Backend Engines"]
            TRT[TensorRT Backend]
            ONNX[ONNX Backend]
            PT[PyTorch Backend]
        end

        API --> Sched
        Sched --> ModelRepo
        Sched --> TRT
        Sched --> ONNX
        Sched --> PT
        TRT --> M1
        ONNX --> M2
        PT --> M3
    end

    subgraph GPU["GPU Layer"]
        GPU1[GPU 0]
        GPU2[GPU 1]
    end

    Clients --> API
    TRT --> GPU1
    ONNX --> GPU1
    PT --> GPU2
```

---

## 3. Core Components

| Component | Role |
|-----------|------|
| **HTTP/gRPC API** | Entry point for inference requests; supports REST and gRPC |
| **Request Scheduler** | Queues, batches, and schedules requests across models/GPUs |
| **Model Repository** | File-based store (local path or cloud) where models are loaded from |
| **Backend Engines** | Framework-specific runtimes (TensorRT, ONNX, PyTorch, etc.) |
| **Dynamic Batching** | Combines multiple requests into batches for higher throughput |

---

## 4. Request Flow (Step-by-Step)

```mermaid
sequenceDiagram
    participant Client
    participant API as Triton API
    participant Scheduler as Request Scheduler
    participant Batcher as Dynamic Batcher
    participant Backend as Model Backend
    participant GPU

    Client->>API: POST /v2/models/{model}/infer
    API->>Scheduler: Enqueue request
    Scheduler->>Batcher: Add to batch queue
    Batcher->>Batcher: Wait for batch (or timeout)
    Batcher->>Backend: Batch of N requests
    Backend->>GPU: Inference (batched)
    GPU-->>Backend: Results
    Backend-->>Scheduler: Response
    Scheduler-->>API: Individual responses
    API-->>Client: 200 OK + inference result
```

---

## 5. Model Repository Layout

```
model_repository/
├── model_name/
│   ├── config.pbtxt          # Model configuration
│   ├── 1/                     # Version directory (version 1)
│   │   └── model.plan         # TensorRT engine / .onnx / .pt
│   └── 2/                     # Version directory (version 2)
│       └── model.plan
└── ensemble_model/            # Model ensembles
    ├── config.pbtxt
    └── 1/
        └── (no files - references other models)
```

---

## 6. Dynamic Batching Architecture

```mermaid
flowchart LR
    subgraph Incoming["Incoming Requests"]
        R1[Req 1]
        R2[Req 2]
        R3[Req 3]
        R4[Req 4]
    end

    subgraph Batcher["Dynamic Batcher"]
        Q[Batch Queue]
        B[Batch of 4]
    end

    subgraph Inference["Inference"]
        GPU[GPU]
    end

    R1 --> Q
    R2 --> Q
    R3 --> Q
    R4 --> Q
    Q --> B
    B --> GPU
```

**Key settings in `config.pbtxt`:**

- `dynamic_batching { max_queue_delay_microseconds: N }` – Max wait before sending batch
- `max_batch_size` – Maximum requests per batch
- Trade-off: **latency vs throughput**

---

## 7. Multi-GPU / Multi-Instance Architecture

```mermaid
flowchart TB
    subgraph Triton["Triton Server"]
        subgraph Instances["Model Instances"]
            I1[Instance 0 - GPU 0]
            I2[Instance 1 - GPU 1]
            I3[Instance 2 - GPU 0]
        end
        LB[Instance Load Balancer]
    end

    subgraph GPUs["GPU Pool"]
        G0[GPU 0]
        G1[GPU 1]
    end

    LB --> I1
    LB --> I2
    LB --> I3
    I1 --> G0
    I2 --> G1
    I3 --> G0
```

**Configuration** (`config.pbtxt`):

```
instance_group [
  {
    count: 2
    kind: KIND_GPU
    gpus: [0]
  },
  {
    count: 1
    kind: KIND_GPU
    gpus: [1]
  }
]
```

---

## 8. Model Ensemble Architecture

Enables multi-stage pipelines (e.g., preprocessing → embedding → LLM → post-processing).

```mermaid
flowchart LR
    subgraph Ensemble["Model Ensemble"]
        P[Preprocess]
        E[Embedding Model]
        L[LLM]
        Post[Postprocess]
    end

    Input[Input] --> P
    P --> E
    E --> L
    L --> Post
    Post --> Output[Output]
```

**Use case:** Chained inference without client-side orchestration.

---

## 9. Triton + Kubernetes Deployment Architecture

```mermaid
flowchart TB
    subgraph K8s["Kubernetes Cluster"]
        subgraph Ingress["Ingress / Load Balancer"]
            LB[Service]
        end

        subgraph Deployment["Triton Deployment"]
            T1[Triton Pod 1]
            T2[Triton Pod 2]
            T3[Triton Pod 3]
        end

        subgraph Storage["Persistent Storage"]
            PVC[PVC - Model Repo]
        end
    end

    Client[Client Apps] --> LB
    LB --> T1
    LB --> T2
    LB --> T3
    T1 --> PVC
    T2 --> PVC
    T3 --> PVC
```

---

## 10. Why This Architecture Matters

| Aspect | Benefit |
|--------|---------|
| **Dynamic batching** | Higher GPU utilization, better throughput |
| **Multi-instance** | Parallel execution, horizontal scale per model |
| **Model ensembles** | Complex pipelines without extra client logic |
| **Framework agnostic** | Mix TensorRT, ONNX, PyTorch in one server |
| **Versioning** | A/B testing, gradual rollouts via model versions |

---

## Next Steps

- [When/What/How to Use Triton](./02-when-what-how.md) – Decision guide
- [Configuration & Deployment](./03-configuration-deployment.md) – Step-by-step setup
- [Troubleshooting](./04-troubleshooting.md) – Common issues and fixes
