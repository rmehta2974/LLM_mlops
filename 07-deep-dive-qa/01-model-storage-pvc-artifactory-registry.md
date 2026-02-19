# Model Storage: PVC vs Artifactory vs Registry

## Overview

| Approach | How Triton Uses It | Best For |
|----------|-------------------|----------|
| **PVC** | Direct mount at `/models` | On-prem, single cluster, shared storage |
| **Artifactory / S3 / GCS** | Sync to local at startup | Multi-cluster, versioning, governance |
| **Container Registry (baked image)** | Model files inside Triton image | Simple, immutable, single model per image |
| **NGC / Model Registry** | Download at startup | NVIDIA ecosystem, pre-built models |

---

## Architecture Diagrams

### PVC-Based Model Repository

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         KUBERNETES / OPENSHIFT CLUSTER                           │
│                                                                                  │
│  ┌──────────────────────────────────────────────────────────────────────────┐   │
│  │                    CI/CD Pipeline (Kubeflow / Jenkins)                     │   │
│  │  [Build Engine] → [Validate] → [Copy to PVC]                              │   │
│  └──────────────────────────────────────────────────────────────────────────┘   │
│                                        │                                         │
│                                        ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │              PersistentVolumeClaim (ReadOnlyMany)                        │    │
│  │              Storage: NFS / Ceph / EBS / NetApp                          │    │
│  │  model_repository/                                                       │    │
│  │  ├── llama2_7b/                                                           │    │
│  │  └── mistral_7b/...                                                      │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│           │                    │                    │                              │
│           ▼                    ▼                    ▼                              │
│  ┌─────────────┐      ┌─────────────┐      ┌─────────────┐                        │
│  │ Triton Pod 1│      │ Triton Pod 2│      │ Triton Pod 3│                        │
│  │ mount:/models│     │ mount:/models│     │ mount:/models│                        │
│  └─────────────┘      └─────────────┘      └─────────────┘                        │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Artifactory / S3 + Init Sync

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    ARTIFACTORY / S3 / GCS (Source of Truth)                      │
└─────────────────────────────────────────────────────────────────────────────────┘
                                         │
                                         │  aws s3 sync (Init Container)
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│  Triton Pod                                                                     │
│  Init Container → emptyDir → Triton Container                                   │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Hybrid: Artifactory + PVC (Production Pattern)

```
CI/CD → Artifactory/S3 (Source of Truth)
              │
              │  Sync Job or ArgoCD
              ▼
        PVC (in cluster)
              │
              ├── Triton Pod 1
              ├── Triton Pod 2
              └── Triton Pod 3
```

---

## Recommendation by Scenario

| Scenario | Preferred Approach |
|----------|---------------------|
| Single cluster, on-prem | **PVC** – direct mount, simple, fast |
| Multi-cluster, cloud | **S3/GCS** (or Artifactory) – central store, sync at startup |
| Strong governance / audit | **Artifactory** – versioning, access control, retention |
| Simple, immutable deploys | **Baked image** – one image per model version |
| NVIDIA-centric | **NGC** – download at startup |

---

## Hybrid Pattern (Best of Both)

- **Artifactory/S3** = source of truth, versioning, governance
- **PVC** = what Triton reads from (fast, shared)
- **Sync** = Job/CronJob/Pipeline copies Artifactory → PVC
