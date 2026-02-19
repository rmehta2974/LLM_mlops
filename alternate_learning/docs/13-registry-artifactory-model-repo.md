# 13 — Registry/Artifactory-backed Model Distribution (Enterprise Pattern)

Generated: 2026-02-19T16:08:24.382791Z

This document implements the **recommended enterprise pattern**:

- **Artifact source-of-truth** = **Artifactory** (generic binaries) and/or **Container Registry** (OCI images)
- **Runtime access** = **pod-local model cache** mounted at `/models`
- **Triton** always reads a *local* repository; the backing system is abstracted by the pipeline.

This solves: immutable promotion, rollback, security scanning, DR portability, multi-cluster rollout.

---

## 1) Why not PVC-as-model-repo in enterprise?

PVC/ODF works, but enterprise platforms usually prefer **immutable + signed + scanned** delivery:
- strict versioning and promotion
- SBOM + vulnerability scans
- approvals and audit trails
- multi-cluster and multi-region portability

---

## 2) Reference architecture

```mermaid
flowchart TB
  DEV[Model Dev / Training] --> REG1[MLflow Registry]
  REG1 --> BUILD[Engine Build: TRT-LLM]
  BUILD --> ART[Publish artifacts: Artifactory (tar.gz)]
  BUILD --> OCI[Build OCI Model Image]
  ART --> GIT[Update GitOps version pointer]
  OCI --> GIT
  GIT --> ARGO[ArgoCD Sync]
  ARGO --> OCP[OpenShift / Kubernetes]
  OCP --> INIT[InitContainer pulls model to /models]
  INIT --> TRITON[Triton reads /models]
  TRITON --> GPU[GPU Nodes]
```

---

## 3) Two production-grade distribution methods

### Method A (Best): “Model Image” (OCI image contains /models)
**What happens**
- CI builds an image that contains:
  - TRT-LLM engine(s)
  - tokenizer/config
  - Triton `config.pbtxt`
- Triton container image can be:
  - a base Triton image + model layer
  - or a multi-container pod (sidecar image provides /models)

**Pros**
- fastest startup
- simplest runtime
- registry policies/scanning/signing apply

**Cons**
- image can be large (use registry caching and layer reuse)

### Method B: Artifactory binary + initContainer download
**What happens**
- CI publishes `model-v123.tar.gz` to Artifactory
- initContainer downloads and extracts to an `emptyDir` (pod-local cache)
- Triton reads `/models` from that cache

**Pros**
- artifact systems handle large binaries well
- easy multi-region replication
- runtime decoupled from container image

**Cons**
- cold start depends on artifact download time

---

## 4) “Version pointer” promotion model (GitOps-friendly)

**Never overwrite artifacts.**
- create immutable versions: `model:v1`, `model:v2`, `model:v3`
- promote by changing a pointer in Git (ConfigMap/values)

Rollback = revert pointer + ArgoCD sync.

---

## 5) Security controls (what enterprises expect)
- sign OCI images and verify on admission
- scan images and artifacts
- least-privilege credentials for artifact pulls
- network policies: isolate inference namespaces
- audit logs: GitOps + registry events + MLflow lineage

---

## 6) Where this is implemented in the repo
- Docs: `docs/14-build-release-pipeline.md`
- Diagrams: `diagrams/04-registry-artifactory-pattern.md`, `diagrams/05-release-strategies.md`
- Manifests:
  - `manifests/30-triton-with-model-image.yaml`
  - `manifests/31-triton-with-artifactory-initcontainer.yaml`
  - `manifests/40-istio-canary.yaml`
- Runbooks: `runbooks/06-canary-parallel-shadow.md`
