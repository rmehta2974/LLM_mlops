# Quick Reference – LLMOps Platform

## 1. When to Use What

| Need | Use |
|------|-----|
| Production LLM serving | Triton + TensorRT-LLM |
| Multi-framework serving | Triton (TensorRT, ONNX, PyTorch) |
| Pipeline orchestration | Kubeflow Pipelines |
| On-prem GPU cluster | NVIDIA GPU Operator + Triton |
| Managed cloud | SageMaker (AWS), Vertex AI (GCP) |
| Full control on cloud | EKS/GKE + Triton |

---

## 2. Triton Config Quick Reference

```protobuf
# config.pbtxt essentials
name: "model_name"
platform: "tensorrt_llm"  # or tensorrt, onnx, pytorch
max_batch_size: 64

dynamic_batching {
  max_queue_delay_microseconds: 500
}

instance_group [
  {
    count: 2
    kind: KIND_GPU
    gpus: [ 0, 1 ]
  }
]
```

---

## 3. Key Commands

| Task | Command |
|------|---------|
| Triton health | `curl http://localhost:8000/v2/health/ready` |
| Model status | `curl http://localhost:8000/v2/models/<model>/ready` |
| Triton logs | `kubectl logs <pod> -c triton` |
| GPU status | `nvidia-smi` |
| Build TRT-LLM | `trtllm-build --checkpoint_dir X --output_dir Y` |

---

## 4. Metrics to Watch

| Metric | Alert If |
|--------|----------|
| `nv_inference_request_failure` | Rate > 1% |
| `nv_inference_queue_duration_us` | P99 > 5s |
| `nv_gpu_utilization` | Sustained > 95% |
| `nv_gpu_memory_used_bytes` | > 90% of total |

---

## 5. HA Checklist

- [ ] replicas >= 2
- [ ] PodDisruptionBudget
- [ ] Multi-AZ
- [ ] Readiness probe on `/v2/health/ready`
- [ ] Graceful shutdown (preStop sleep)

---

## 6. Optimization Decision Tree

```
Need lower latency? → FP16/FP8, reduce batch, reduce queue delay
Need more throughput? → Increase batch, add instances
Need to fit larger model? → Quantization, TP, PP
Long context? → Paged KV cache
```

---

## 7. Document Index

| Topic | Path |
|-------|------|
| Triton Architecture | `01-triton-inference-server/01-architecture.md` |
| When/What/How Triton | `01-triton-inference-server/02-when-what-how.md` |
| Triton K8s Deploy | `01-triton-inference-server/03-configuration-deployment.md` |
| Triton Troubleshooting | `01-triton-inference-server/04-troubleshooting.md` |
| TensorRT-LLM + Triton | `02-tensorrt-llm/01-overview-integration.md` |
| Optimization (Quant, etc.) | `02-tensorrt-llm/02-optimization-techniques.md` |
| Kubeflow Pipelines | `03-mlops-pipelines/01-kubeflow-pipelines.md` |
| NVIDIA On-Prem | `03-mlops-pipelines/02-nvidia-onprem.md` |
| Load Balancing | `04-scaling-availability/01-load-balancing.md` |
| High Availability | `04-scaling-availability/02-high-availability.md` |
| Monitoring | `04-scaling-availability/03-monitoring-observability.md` |
| AWS | `05-cloud-deployment/01-aws-sagemaker-neurons.md` |
| GCP | `05-cloud-deployment/02-gcp-vertex-ai.md` |
| API Design | `05-cloud-deployment/03-api-design-patterns.md` |
| Incident Mgmt | `06-operational-runbooks/01-incident-management.md` |
| Change Mgmt | `06-operational-runbooks/02-change-management.md` |
| Event Mgmt | `06-operational-runbooks/03-event-management.md` |
