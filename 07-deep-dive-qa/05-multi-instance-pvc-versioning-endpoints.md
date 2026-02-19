# Multi-Instance, Multi-Pod PVC, Versioning, and Endpoints

## 1. Multi-Instance vs Multi-Pod

### Multi-Instance (Inside One Triton Process)

Multiple copies of the same model in one Triton process, typically on different GPUs.

```
┌─────────────────────────────────────────────────────────────────┐
│  Single Triton Process (1 Pod)                                   │
│  Model: llama2_7b                                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │ Instance 0  │  │ Instance 1  │  │ Instance 2  │             │
│  │ GPU 0       │  │ GPU 1       │  │ GPU 2       │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│         ▲                ▲                ▲                      │
│         └────────────────┼────────────────┘                      │
│                    Scheduler (round-robin / least-busy)          │
└─────────────────────────────────────────────────────────────────┘
```

**Config:**
```protobuf
instance_group [
  { count: 1, kind: KIND_GPU, gpus: [0] },
  { count: 1, kind: KIND_GPU, gpus: [1] },
  { count: 1, kind: KIND_GPU, gpus: [2] }
]
```

### Multi-Pod (Multiple Triton Processes)

Multiple Triton pods, each with its own process. Each pod can mount the same PVC.

```
┌─────────────────────────────────────────────────────────────────┐
│                    PVC (ReadOnlyMany)                            │
│                    model_repository/                             │
└─────────────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ Triton Pod 1    │  │ Triton Pod 2    │  │ Triton Pod 3    │
│ mount: /models  │  │ mount: /models  │  │ mount: /models  │
│ GPU 0           │  │ GPU 1           │  │ GPU 2           │
└─────────────────┘  └─────────────────┘  └─────────────────┘
         │                    │                    │
         └────────────────────┼────────────────────┘
                              ▼
                    ┌─────────────────┐
                    │ Service (LB)     │
                    └─────────────────┘
```

---

## 2. Can Multiple Triton Pods Use the Same PVC?

**Yes.** Use `ReadOnlyMany` (or `ReadWriteMany`) storage class.

| Storage Class | Access Mode | Multiple Pods? |
|---------------|-------------|----------------|
| NFS | ReadOnlyMany | Yes |
| Ceph / Rook | ReadOnlyMany | Yes |
| EBS | ReadWriteOnce | No (one node) |
| EFS (AWS) | ReadWriteMany | Yes |

---

## 3. How the Pipeline Stores Models in PVC

The pipeline does not talk to Triton. It writes files into the PVC, then Triton (or you) loads them.

**Flow:**
1. Pipeline builds engine (trtllm-build)
2. Pipeline **Step 2** runs as a **Pod with PVC mounted**
3. Pod copies: `cp -r /tmp/engine/* /models/llama2_7b/2/`
4. (Optional) Pipeline Step 3: Call Triton load API

Triton never writes; it only reads. The pipeline writes via a Pod.

---

## 4. How Triton Picks Up Models

### At Startup

1. `--model-repository=/models`
2. Triton scans `/models` for subdirectories
3. For each subdir (e.g. `llama2_7b`): reads config, loads version dirs
4. Models become READY

### At Runtime (Explicit Load)

1. New files appear under `/models/llama2_7b/3/`
2. Call `POST /v2/repository/models/llama2_7b/load` with `version: "3"`
3. Triton loads from `/models/llama2_7b/3/`

### Polling (Optional)

```bash
tritonserver --model-repository=/models --repository-poll-secs=30
```

---

## 5. Versioning: Native and How It Works

Triton versions models by **directory layout** – no separate database.

### Layout = Versioning

```
model_repository/
└── llama2_7b/
    ├── config.pbtxt
    ├── 1/               ← Version 1
    ├── 2/               ← Version 2
    └── 3/               ← Version 3
```

### Version Policy

```protobuf
version_policy {
  specific { versions: [1, 2] }   # Load only v1 and v2
}
# OR
version_policy {
  latest { num_versions: 2 }      # Load latest 2 versions
}
```

---

## 6. How Triton Exposes Endpoints

Triton does not "create" endpoints. It exposes a **fixed API** and maps paths to models/versions.

### URL Structure

| URL | Purpose |
|-----|---------|
| `/v2/models/{model_name}/infer` | Infer with default version |
| `/v2/models/{model_name}/versions/{version}/infer` | Infer with specific version |

### Examples

```
Model: llama2_7b, versions: 1, 2
Model: mistral_7b, versions: 1

Endpoints:
  POST /v2/models/llama2_7b/infer                    → default version
  POST /v2/models/llama2_7b/versions/1/infer        → v1
  POST /v2/models/llama2_7b/versions/2/infer        → v2
  POST /v2/models/mistral_7b/infer                  → mistral
```

### How routing works

```
Request: POST /v2/models/llama2_7b/versions/2/infer
Triton: Parse model_name="llama2_7b", version="2"
        → Check if loaded
        → Enqueue to scheduler
        → Run inference
        → Return response
```

---

## 7. Processing Different Workloads

| Workload | Endpoint |
|----------|----------|
| Embedding | `/v2/models/embedding/infer` |
| LLM completion | `/v2/models/llama2_7b/infer` |
| Canary (new version) | `/v2/models/llama2_7b/versions/2/infer` |
| RAG pipeline | `/v2/models/ensemble_rag/infer` |

Client chooses model and version via the URL.
