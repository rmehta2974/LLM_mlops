# Model Loading, Pipelines, and Canary

## 1. How Models Are Loaded in Triton

### Automatic Load at Startup

Default: Triton loads all models in the model repository when it starts.

```bash
tritonserver --model-repository=/models
```

### Explicit Load / Unload (Runtime Control)

| Action | Endpoint |
|--------|----------|
| **Load** | `POST /v2/repository/models/{model}/load` |
| **Unload** | `POST /v2/repository/models/{model}/unload` |

```bash
# Load model
curl -X POST http://localhost:8000/v2/repository/models/llama2_7b/load

# Load specific version
curl -X POST http://localhost:8000/v2/repository/models/llama2_7b/load \
  -d '{"parameters": {"version": "2"}}'

# Unload
curl -X POST http://localhost:8000/v2/repository/models/llama2_7b/unload
```

### Startup Config

```bash
# Load only via API (no auto-load at startup)
tritonserver --model-repository=/models --model-control-mode=explicit

# Load only specific models
tritonserver --model-repository=/models --load-model=llama2_7b --load-model=mistral_7b
```

---

## 2. Model Pipelines (Ensembles)

Chain multiple models: preprocess → embed → LLM → postprocess.

### Layout

```
model_repository/
├── preprocess/1/
├── embedding/1/
├── llm/1/
└── ensemble_pipeline/1/   ← config only, orchestrates
```

### Ensemble config.pbtxt

```protobuf
name: "ensemble_pipeline"
platform: "ensemble"
ensemble_scheduling {
  step [
    { model_name: "preprocess", input_map: {...}, output_map: {...} },
    { model_name: "embedding", input_map: {...}, output_map: {...} },
    { model_name: "llm", input_map: {...}, output_map: {...} }
  ]
}
```

Client calls `POST /v2/models/ensemble_pipeline/infer` – Triton runs the chain.

---

## 3. Canary / Gradual Rollout

### Version-Based (Single Triton)

Load v1 and v2. Route via API gateway:
- 90% → `/v2/models/llama2_7b/versions/1/infer`
- 10% → `/v2/models/llama2_7b/versions/2/infer`

### Deployment-Based (K8s)

- **Stable deployment:** 3 replicas, v1
- **Canary deployment:** 1 replica, v2
- Ingress: `canary-weight: 10` for canary

### Nginx Ingress Canary

```yaml
annotations:
  nginx.ingress.kubernetes.io/canary: "true"
  nginx.ingress.kubernetes.io/canary-weight: "10"
```

### Istio VirtualService

```yaml
http:
  - route:
      - destination: { host: triton-stable }
        weight: 90
      - destination: { host: triton-canary }
        weight: 10
```
