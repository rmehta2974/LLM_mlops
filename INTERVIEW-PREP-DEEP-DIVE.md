# Interview Prep – Deep Dive: Kubeflow, Triton, TensorRT-LLM, K8s/OpenShift

> **Use this as your 2-hour prep guide.** Covers Kubeflow pipelines, model lifecycle, Triton config, API, scheduling, and K8s/OpenShift deployment.

---

# PART 1: KUBEFLOW PIPELINES (DETAILED)

## 1.1 What is Kubeflow Pipelines?

- **Orchestration layer** for ML workflows on Kubernetes
- Built on **Argo Workflows** (DAG-based)
- Each step = **container** running a task
- Artifacts passed between steps via **minio/S3** or **PVC**
- UI for runs, experiments, and artifact lineage

## 1.2 Kubeflow Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Kubeflow Central Dashboard                                              │
│  • Experiments, Runs, Pipelines, Artifacts                               │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  Pipeline Controller (KFP API Server)                                     │
│  • Submits workflows to Argo                                             │
│  • Tracks run status, artifacts                                         │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  Argo Workflows                                                          │
│  • DAG execution                                                         │
│  • Creates K8s Pods for each step                                       │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  Kubernetes Pods (GPU nodes for training/build)                         │
│  • Step 1: Data prep pod                                                │
│  • Step 2: Training pod (PyTorch/NeMo)                                  │
│  • Step 3: Convert + Build pod (trtllm-build)                          │
│  • Step 4: Deploy pod (copy to model repo, trigger Triton load)        │
└─────────────────────────────────────────────────────────────────────────┘
```

## 1.3 LLMOps Pipeline – Step-by-Step

| Step | Component | Input | Output | K8s Resource |
|------|-----------|-------|--------|--------------|
| 1 | Data prep | Raw data (S3/GCS) | Tokenized dataset | Job/Pod |
| 2 | Training | Base model + data | Checkpoint (S3) | Job with GPU |
| 3 | Convert | Checkpoint | TRT-LLM checkpoint | Job with GPU |
| 4 | Build | TRT-LLM checkpoint | Engine files | Job with GPU |
| 5 | Validate | Engine | Pass/fail | Job |
| 6 | Deploy | Engine | Model in Triton repo | Job + Triton reload |
| 7 | Smoke test | Triton URL | Latency/accuracy | Job |

## 1.4 Kubeflow Pipeline DSL Example (Python)

```python
from kfp import dsl
from kfp.dsl import component, pipeline, OutputPath, InputPath

@component
def train_model(
    data_path: InputPath(str),
    output_checkpoint: OutputPath(str),
    epochs: int = 3
):
    """Runs PyTorch/NeMo fine-tuning. Outputs checkpoint path."""
    # Container runs: python train.py --data @data_path --output @output_checkpoint
    pass

@component
def convert_to_trtllm(
    checkpoint_path: InputPath(str),
    output_ckpt: OutputPath(str)
):
    """Runs convert_checkpoint.py. Outputs TRT-LLM checkpoint path."""
    pass

@component
def build_engine(
    ckpt_path: InputPath(str),
    engine_path: OutputPath(str),
    max_batch_size: int = 64
):
    """Runs trtllm-build. Outputs engine directory path."""
    pass

@component
def deploy_to_triton(
    engine_path: InputPath(str),
    model_repo: str,  # S3 or NFS path
    model_name: str,
    version: int
):
    """Copies engine to model repo, calls Triton load API."""
    pass

@pipeline(name="llm-training-deploy")
def llm_pipeline(
    data_path: str,
    model_repo: str,
    model_name: str = "llama2_7b"
):
    train_task = train_model(data_path=data_path)
    convert_task = convert_to_trtllm(checkpoint_path=train_task.outputs["output_checkpoint"])
    build_task = build_engine(ckpt_path=convert_task.outputs["output_ckpt"])
    deploy_task = deploy_to_triton(
        engine_path=build_task.outputs["engine_path"],
        model_repo=model_repo,
        model_name=model_name
    )
```

## 1.5 How Pipelines Run on K8s

- Each `@component` = **container image** + **command**
- KFP compiles to **Argo Workflow** YAML
- Argo creates **Pods**; each Pod runs one step
- **Artifacts**: Stored in object storage (MinIO/S3), paths passed as env vars or mounted
- **GPU**: Request `nvidia.com/gpu` in Pod spec for training/build steps

---

# PART 2: MODEL LOADING, VERSIONING, STORAGE

## 2.1 How Triton Loads Models

**Flow:**
1. Triton starts with `--model-repository=/models`
2. Scans `model_repository/` for directories
3. Each directory = one model (e.g. `llama2_7b`)
4. Reads `config.pbtxt` → determines backend (e.g. `tensorrt_llm`)
5. Loads backend, passes path to `1/` (version 1)
6. Backend loads `rank0.engine`, `model.py`, etc. into GPU memory
7. Model state = **READY**

**Load control:**
- **Explicit load**: `POST /v2/repository/models/{model}/load`
- **Explicit unload**: `POST /v2/repository/models/{model}/unload`
- **Polling**: Triton can poll repo for new versions (optional)

## 2.2 Model Versioning (Triton)

```
model_repository/
└── llama2_7b/
    ├── config.pbtxt          # Shared by all versions
    ├── 1/                     # Version 1
    │   ├── rank0.engine
    │   └── model.py
    ├── 2/                     # Version 2 (e.g. FP8 optimized)
    │   ├── rank0.engine
    │   └── model.py
    └── 3/                     # Version 3 (e.g. fine-tuned)
        └── rank0.engine
```

**Request specific version:**
```
POST /v2/models/llama2_7b/versions/2/infer
```

**Default version:** If no version in URL, Triton uses the latest numeric version.

**Version policy (config.pbtxt):**
```protobuf
version_policy {
  specific { versions: [1, 2] }   # Load only v1 and v2
}
# OR
version_policy {
  latest { num_versions: 2 }     # Load latest 2 versions
}
```

## 2.3 Where Models Are Stored

| Stage | Location | Format |
|-------|----------|--------|
| **Training output** | S3/GCS/NFS | Checkpoint (safetensors, .bin) |
| **Model registry** | MLflow, NGC, custom | Metadata + artifact URI |
| **TRT-LLM engine** | S3/GCS/NFS, PVC | .engine files |
| **Triton model repo** | NFS, PVC, S3-synced local | config.pbtxt + version dirs |

**K8s/OpenShift:** Use **PVC** (ReadOnlyMany) for shared model repo, or **init container** to sync from S3/GCS to emptyDir.

---

# PART 3: HOW MODELS ARE BUILT

## 3.1 Build Pipeline (TensorRT-LLM)

```
Step 1: Obtain base model
        Hugging Face: git clone / download
        NGC: ngc registry download

Step 2: Convert to TRT-LLM format
        python convert_checkpoint.py \
          --model_dir ./Llama-2-7b-hf \
          --output_dir ./llama2_ckpt \
          --tp_size 1 --dtype float16

Step 3: Build TensorRT engine
        trtllm-build \
          --checkpoint_dir ./llama2_ckpt \
          --output_dir ./engine \
          --gemm_plugin float16 \
          --max_batch_size 64 \
          --max_input_len 2048 \
          --max_output_len 1024

Step 4: Package for Triton
        Copy engine/* to model_repository/llama2_7b/1/
        Add config.pbtxt
        Add model.py (TensorRT-LLM backend entrypoint)
```

## 3.2 Build Parameters (trtllm-build)

| Param | Effect |
|-------|--------|
| `--max_batch_size` | Max requests per batch |
| `--max_input_len` | Max prompt tokens |
| `--max_output_len` | Max generated tokens |
| `--tp_size` | Tensor parallel GPUs |
| `--pp_size` | Pipeline parallel stages |
| `--use_fp8` | FP8 precision |
| `--use_int8` | INT8 (needs calibration) |
| `--gemm_plugin` | GEMM kernel (float16, float8) |
| `--gpt_attention_plugin` | Attention impl (float16, float8) |

---

# PART 4: TUNING (DETAILED)

## 4.1 Offline Tuning (Engine Build)

| Technique | Command/Config | Goal |
|----------|---------------|------|
| **FP16** | `--dtype float16` | Default, good quality |
| **FP8** | `--use_fp8 --fp8_kv_cache` | 2x faster, A100/H100 |
| **INT8** | `--use_int8` + calibration | Lower memory |
| **Batch size** | `--max_batch_size 64` | Throughput vs memory |
| **Seq length** | `--max_input_len 4096` | Long context vs memory |
| **Tensor parallel** | `--tp_size 2` | Split across 2 GPUs |
| **Pipeline parallel** | `--pp_size 2` | Split layers across GPUs |

## 4.2 Runtime Tuning (Triton config.pbtxt)

```protobuf
# Latency vs throughput
dynamic_batching {
  preferred_batch_size: [4, 8, 16]
  max_queue_delay_microseconds: 500   # Lower = lower latency, lower throughput
  preserve_ordering: false
}

# More instances = more parallelism
instance_group [
  {
    count: 2
    kind: KIND_GPU
    gpus: [0, 1]
  }
]

# Sequence batching for streaming
sequence_batching {
  max_sequence_idle_microseconds: 5000000
}
```

## 4.3 Tuning Decision Matrix

| Goal | Change |
|------|--------|
| Lower latency | ↓ max_queue_delay, ↓ batch size, add instances |
| Higher throughput | ↑ batch size, ↑ queue delay, add instances |
| Fit larger model | Quantization, TP, PP |
| Long context | Paged KV cache, ↑ max_input_len |

---

# PART 5: TRAINING (IN PIPELINE CONTEXT)

## 5.1 Training Options for LLMs

| Framework | Use Case |
|-----------|----------|
| **NeMo** | NVIDIA, best TRT-LLM integration |
| **Hugging Face** | Popular, many models |
| **PyTorch** | Custom training |
| **Megatron** | Large-scale |

## 5.2 Training Step in Kubeflow

- Runs as **K8s Job** with GPU
- Input: Base model path, dataset path (S3/NFS)
- Output: Checkpoint path (upload to S3 or write to shared PVC)
- Resource: `nvidia.com/gpu: 1` (or more for multi-GPU)

---

# PART 6: TRITON CONFIG (DETAILED)

## 6.1 config.pbtxt – Full Example

```protobuf
name: "llama2_7b"
platform: "tensorrt_llm"
max_batch_size: 0   # 0 = dynamic batching

input [
  {
    name: "input_ids"
    data_type: TYPE_INT32
    dims: [ -1 ]
  },
  {
    name: "input_lengths"
    data_type: TYPE_INT32
    dims: [ -1 ]
  }
]

output [
  {
    name: "output_ids"
    data_type: TYPE_INT32
    dims: [ -1 ]
  }
]

instance_group [
  {
    count: 2
    kind: KIND_GPU
    gpus: [ 0, 1 ]
  }
]

dynamic_batching {
  preferred_batch_size: [ 4, 8, 16, 32 ]
  max_queue_delay_microseconds: 500
}

parameters: {
  key: "tensor_parallel_size"
  value: { string_value: "1" }
}
```

## 6.2 Key Config Fields

| Field | Purpose |
|-------|---------|
| `name` | Model identifier |
| `platform` | Backend: tensorrt_llm, tensorrt, onnx, pytorch |
| `max_batch_size` | 0 = dynamic; N = max N |
| `input` / `output` | Tensor names, types, dims (-1 = dynamic) |
| `instance_group` | How many instances, which GPUs |
| `dynamic_batching` | Batching behavior |
| `parameters` | Backend-specific (e.g. tensor_parallel_size) |

---

# PART 7: TRITON API ENDPOINTS

## 7.1 HTTP API (Port 8000)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/v2/health/ready` | GET | Readiness – models loaded |
| `/v2/health/live` | GET | Liveness – server running |
| `/v2` | GET | Server metadata |
| `/v2/models` | GET | List models |
| `/v2/models/{model}` | GET | Model metadata |
| `/v2/models/{model}/ready` | GET | Is model ready? |
| `/v2/models/{model}/versions/{version}/infer` | POST | Inference |
| `/v2/repository/models/{model}/load` | POST | Load model |
| `/v2/repository/models/{model}/unload` | POST | Unload model |
| `/v2/repository/index` | GET | List repo contents |

## 7.2 Inference Request Format

```http
POST /v2/models/llama2_7b/infer
Content-Type: application/json

{
  "inputs": [
    {
      "name": "input_ids",
      "shape": [1, 128],
      "datatype": "INT32",
      "data": [1, 2, 3, ...]
    },
    {
      "name": "input_lengths",
      "shape": [1],
      "datatype": "INT32",
      "data": [128]
    }
  ],
  "outputs": [
    { "name": "output_ids" }
  ]
}
```

## 7.3 gRPC API (Port 8001)

- Same operations, binary protocol
- Lower overhead for high throughput
- Use `tritonclient.grpc` for Python

---

# PART 8: SCHEDULING (TRITON)

## 8.1 Request Flow Through Scheduler

```
Client Request
      │
      ▼
┌─────────────────┐
│  HTTP/gRPC API  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Request Queue  │  ← Requests wait here
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Dynamic Batcher │  ← Waits up to max_queue_delay_microseconds
│                 │    OR until preferred_batch_size reached
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Instance        │  ← Selects least-busy instance
│ Selector        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Model Backend   │  ← Runs inference on GPU
│ (TensorRT-LLM)  │
└────────┬────────┘
         │
         ▼
   Response to client
```

## 8.2 Dynamic Batching Explained

- **Problem**: GPU underutilized with batch size 1
- **Solution**: Queue requests, form batch of N, run once
- **Trade-off**: `max_queue_delay_microseconds` = max wait time
  - Low (e.g. 100µs) → lower latency, smaller batches, lower throughput
  - High (e.g. 1000µs) → higher latency, larger batches, higher throughput

## 8.3 Instance Scheduling

- **Round-robin** or **least-busy** across instances
- Multiple instances = parallel execution
- Each instance = separate GPU memory load of model

---

# PART 9: KUBERNETES DEPLOYMENT

## 9.1 Triton on K8s – Key Resources

```yaml
# Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: triton-inference
spec:
  replicas: 2
  template:
    spec:
      containers:
        - name: triton
          image: nvcr.io/nvidia/tritonserver:24.01-py3
          args: ["tritonserver", "--model-repository=/models"]
          resources:
            limits:
              nvidia.com/gpu: 1
          volumeMounts:
            - name: models
              mountPath: /models
              readOnly: true
          livenessProbe:
            httpGet:
              path: /v2/health/live
              port: 8000
          readinessProbe:
            httpGet:
              path: /v2/health/ready
              port: 8000
      volumes:
        - name: models
          persistentVolumeClaim:
            claimName: triton-model-repo
```

## 9.2 Model Repo on K8s

**Option A: PVC (ReadOnlyMany)**
- Create PVC, populate via Job or init container
- Mount in all Triton pods

**Option B: Init container sync from S3**
```yaml
initContainers:
  - name: sync-models
    image: amazon/aws-cli
    command: ["aws", "s3", "sync", "s3://bucket/models/", "/models"]
    volumeMounts:
      - name: models
        mountPath: /models
containers:
  - name: triton
    volumeMounts:
      - name: models
        mountPath: /models
volumes:
  - name: models
    emptyDir: {}
```

## 9.3 GPU Node Requirements

- **NVIDIA device plugin** (or GPU Operator) installed
- Nodes with `nvidia.com/gpu` allocatable
- CUDA compatibility between driver and container

---

# PART 10: OPENSHIFT

## 10.1 Triton on OpenShift

- OpenShift = **Kubernetes + Red Hat extras**
- Same Deployment, Service, Route concepts
- **Route** instead of Ingress for external access
- **SecurityContextConstraint** may need adjustment for Triton
- GPU: Use GPU Operator or device plugin compatible with OpenShift

## 10.2 OpenShift Route Example

```yaml
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  name: triton-route
spec:
  to:
    kind: Service
    name: triton-inference
  port:
    targetPort: 8000
```

## 10.3 Differences from Vanilla K8s

| K8s | OpenShift |
|-----|-----------|
| Ingress | Route |
| PodSecurityPolicy | SecurityContextConstraint |
| Default SA | Often more restricted |
| Same | Deployment, Service, PVC, GPU |

---

# PART 11: INTERVIEW Q&A – QUICK REFERENCE

**Q: What does Triton do?**  
A: Inference serving: loads models, batches requests, runs backends (TensorRT-LLM, etc.) on GPU, returns results.

**Q: How does model versioning work in Triton?**  
A: Numeric version dirs (1/, 2/, 3/). Request via `/v2/models/{model}/versions/{v}/infer`. Multiple versions can be loaded.

**Q: What is dynamic batching?**  
A: Queue requests, wait up to `max_queue_delay_microseconds`, form batch, run once on GPU. Trade-off: latency vs throughput.

**Q: How do you deploy Triton on K8s?**  
A: Deployment with GPU, PVC for model repo, Service, Ingress/Route. Readiness on `/v2/health/ready`.

**Q: What is Kubeflow Pipelines?**  
A: ML workflow orchestration on K8s. DAG of containerized steps (train → convert → build → deploy). Built on Argo.

**Q: Where are models stored?**  
A: Training → S3/GCS. Engine build → S3/GCS. Triton → NFS, PVC, or S3-synced local.

**Q: How does the API work?**  
A: HTTP/gRPC. POST to `/v2/models/{model}/infer` with inputs. Triton batches, runs backend, returns outputs.

**Q: What is TensorRT-LLM?**  
A: NVIDIA library for optimized LLM inference. Builds engines from checkpoints. Served via Triton tensorrt_llm backend.

**Q: How do you tune for latency vs throughput?**  
A: Latency: lower queue delay, smaller batch. Throughput: higher queue delay, larger batch, more instances.

---

# PART 12: COMMANDS CHEAT SHEET

```bash
# Triton
tritonserver --model-repository=/models
curl http://localhost:8000/v2/health/ready
curl http://localhost:8000/v2/models/llama2_7b/ready

# TRT-LLM build
trtllm-build --checkpoint_dir ./ckpt --output_dir ./engine --max_batch_size 64

# K8s
kubectl get pods -l app=triton
kubectl logs <pod> -c triton
kubectl exec -it <pod> -- nvidia-smi
```

---

Good luck with your interview.
