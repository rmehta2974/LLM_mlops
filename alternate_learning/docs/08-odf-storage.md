# 08 — OpenShift Data Foundation (ODF) Storage for LLM Inference

## 1) What requires persistence
- model weights, TRT engines, tokenizers
- evaluation artifacts and reports
- deployment metadata

Inference pods are ephemeral; artifacts must not be.

## 2) ODF patterns

### Pattern A: PVC-mounted model repo
- Triton mounts PVC at /models
- Use versioned directories
- Rollback by switching pointer to previous version

### Pattern B: Object store (NooBaa S3) + pod cache
- S3 is source-of-truth
- init container downloads required version to emptyDir
- reduces dependency on shared FS semantics

## 3) Snapshots and rollback
- keep immutable versions
- use VolumeSnapshots for fast rollback when supported
- never overwrite current artifacts; promote by pointer changes

## 4) DR
- replicate object storage across regions
- rebuild caches in DR cluster
- test failover runbooks periodically
