# Tekton Pipeline (OpenShift) — Engine Build + Artifact Publish + GitOps Update (Stub)

## Typical tasks
1. checkout
2. fetch weights
3. build TRT-LLM engine
4. golden prompt tests
5. perf smoke
6. publish to Artifactory + Registry
7. bump GitOps pointer (PR)
8. notify / create change record (optional)

## Notes
- pin CUDA/TRT/TRT-LLM images for deterministic builds
- deploy by image digest for immutability
