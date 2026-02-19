# Model Push to PVC: Options and Triton Endpoint Discovery

## 1. Who Can Write to the PVC?

**Only a Pod.** The PVC is a Kubernetes volume; only Pods can mount it. So only a Pod can write to it.

The difference is **how** you run that Pod:

| Method | Trigger | What Runs |
|--------|---------|-----------|
| **Job** | CI / manual | One Pod, runs once |
| **CronJob** | Schedule | Pod every run |
| **Pipeline** | Pipeline run | Pipeline step runs as Pod |
| **GitOps** | Git change | Argo CD applies Job → Pod runs |

---

## 2. Option A: One-Off Job

**Trigger:** CI pipeline after build completes.

**Flow:**
```
CI builds engine → Uploads to S3
       │
       ▼
CI triggers K8s Job
       │
       ▼
Job Pod runs with PVC mounted
       │
       ▼
Pod runs: aws s3 sync s3://bucket/llama2_7b/2/ /models/llama2_7b/2/
       │
       ▼
Files copied to PVC. Job completes.
```

**Job YAML:**
```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: push-model-llama2-v2
spec:
  template:
    spec:
      restartPolicy: Never
      containers:
        - name: sync
          image: amazon/aws-cli
          command:
            - sh
            - -c
            - |
              aws s3 sync s3://my-bucket/models/llama2_7b/2/ /models/llama2_7b/2/
          volumeMounts:
            - name: models
              mountPath: /models
      volumes:
        - name: models
          persistentVolumeClaim:
            claimName: triton-model-repo
```

---

## 3. Option B: CronJob

**Trigger:** Time-based (e.g. every hour).

**Flow:**
```
CronJob runs every hour
       │
       ▼
Creates Job → Pod
       │
       ▼
Pod: aws s3 sync s3://bucket/models/ /models/
       │
       ▼
PVC updated with latest from S3
```

**CronJob YAML:**
```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: sync-models-to-pvc
spec:
  schedule: "0 * * * *"   # Every hour
  jobTemplate:
    spec:
      template:
        spec:
          restartPolicy: OnFailure
          containers:
            - name: sync
              image: amazon/aws-cli
              command:
                - sh
                - -c
                - |
                  aws s3 sync s3://my-bucket/model-repo/ /models/
              volumeMounts:
                - name: models
                  mountPath: /models
          volumes:
            - name: models
              persistentVolumeClaim:
                claimName: triton-model-repo
```

---

## 4. Option C: Pipeline

**Trigger:** Pipeline run (e.g. after build step).

**Flow:**
```
Pipeline Step 1: Build engine (trtllm-build)
       │
       ▼
Pipeline Step 2: Push to PVC
       │
       ▼
  This step runs as a Pod with PVC mounted
       │
       ▼
  Pod copies files to /models/
       │
       ▼
Pipeline Step 3: (Optional) Trigger Triton load
```

**Kubeflow component example:**
```python
@component
def push_to_pvc(
    engine_path: InputPath(str),
    model_name: str,
    version: int
):
    """Runs in a Pod. Kubeflow mounts PVC if configured."""
    import shutil
    import os
    dest = f"/models/{model_name}/{version}"
    os.makedirs(dest, exist_ok=True)
    shutil.copytree(engine_path, dest, dirs_exist_ok=True)
```

The pipeline step runs in a Pod. You must configure the pipeline to mount the PVC for that step.

---

## 5. Option D: GitOps (Argo CD)

**Trigger:** Git change detected.

**Flow:**
```
Git repo
  ├── k8s/
  │   └── sync-job.yaml
  └── (no large model files in Git)

Argo CD
       │
       ▼
Detects change
       │
       ▼
Applies sync-job.yaml
       │
       ▼
Job Pod runs with PVC mounted
       │
       ▼
Pod syncs from S3 (or copies from init container)
       │
       ▼
PVC updated
```

**Important:** Git typically doesn't store large model files. GitOps stores **Job manifests**; the Job pulls from S3/GCS/Artifactory.

**Example:**
```yaml
# k8s/model-sync-job.yaml (in Git)
apiVersion: batch/v1
kind: Job
metadata:
  name: sync-llama2-v2
  annotations:
    argocd.argoproj.io/hook: PreSync
spec:
  template:
    spec:
      containers:
        - name: sync
          image: amazon/aws-cli
          command: ["aws", "s3", "sync", "s3://bucket/models/llama2_7b/2/", "/models/llama2_7b/2/"]
          volumeMounts:
            - name: models
              mountPath: /models
      volumes:
        - name: models
          persistentVolumeClaim:
            claimName: triton-model-repo
```

---

## 6. Summary: Push to PVC

| Method | Trigger | Who Runs It | What It Does |
|--------|---------|-------------|--------------|
| **Job** | CI / manual | One Pod | One-time sync to PVC |
| **CronJob** | Schedule | Pod every run | Periodic sync to PVC |
| **Pipeline** | Pipeline run | Pipeline step Pod | Sync after build |
| **GitOps** | Git change | Argo CD applies Job | Job Pod syncs to PVC |

**Common point:** Every method uses a Pod that mounts the PVC and runs a command (e.g. `aws s3 sync`, `cp`) to copy files into the model repo path.

---

## 7. How Triton "Publishes" Endpoints

Triton does not "create" or "publish" endpoints. It exposes a **fixed API** and maps paths to models/versions based on the filesystem.

### The API is Fixed

```
Base path: /v2/models/{model_name}/versions/{version}/infer
```

Triton doesn't "register" endpoints. It just handles requests that match this pattern.

### How Triton Discovers Models

```
Triton startup
       │
       ▼
Scans /models (model repository root)
       │
       ▼
For each directory (e.g. llama2_7b):
  - Read config.pbtxt
  - List subdirs 1, 2, 3, ...
  - Each numeric dir = one version
       │
       ▼
Load models (per version_policy)
       │
       ▼
Ready to serve
```

### Directory Layout → Endpoints

```
model_repository/
├── llama2_7b/          ← model_name
│   ├── config.pbtxt
│   ├── 1/              ← version 1
│   └── 2/              ← version 2
└── mistral_7b/         ← model_name
    ├── config.pbtxt
    └── 1/              ← version 1
```

**Endpoints (automatically available):**
- `/v2/models/llama2_7b/versions/1/infer`
- `/v2/models/llama2_7b/versions/2/infer`
- `/v2/models/mistral_7b/versions/1/infer`

Triton doesn't "create" these – they exist by convention for any `{model_name}` and `{version}` that exist in the repo.

### Request Flow

```
1. Request: POST /v2/models/llama2_7b/versions/2/infer
2. Triton parses: model_name = llama2_7b, version = 2
3. Checks: is /models/llama2_7b/2/ loaded?
4. If yes: enqueue request
5. If no: 404 or load first
6. Run inference
7. Return response
```

---

## 8. End-to-End Picture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  SOURCE OF TRUTH (S3 / Artifactory)                                         │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        │  Sync (Job / CronJob / Pipeline)
                                        │  Must run in a Pod with PVC mounted
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  PVC (model_repository)                                                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        │  Triton reads at startup or explicit load
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  TRITON                                                                      │
│  Scans /models → discovers models and versions → loads them                  │
│  No separate "publish" step; endpoints are fixed by URL pattern              │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  ENDPOINTS (by convention)                                                   │
│  /v2/models/llama2_7b/versions/1/infer                                      │
│  /v2/models/llama2_7b/versions/2/infer                                      │
│  /v2/models/mistral_7b/versions/1/infer                                     │
└─────────────────────────────────────────────────────────────────────────────┘
```
