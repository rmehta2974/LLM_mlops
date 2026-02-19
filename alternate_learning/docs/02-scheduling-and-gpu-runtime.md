# 02 Scheduling and GPU Runtime

## Scheduling layers

1. Kubernetes scheduler → places Triton pods on nodes
2. Triton scheduler → batches inference requests
3. CUDA scheduler → executes kernels on GPU

## GPU assignment

Kubernetes uses extended resource:

```yaml
resources:
  limits:
    nvidia.com/gpu: 1
```

Device plugin exposes GPU to container.
CUDA_VISIBLE_DEVICES is set so Triton sees only assigned GPU.
