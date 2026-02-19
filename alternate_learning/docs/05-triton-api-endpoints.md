# 05 Triton API Endpoints (HTTP + gRPC) Cheat Sheet

Generated: 2026-02-19T18:37:36.566358Z

Ports (default):
- HTTP: 8000
- gRPC: 8001
- Metrics: 8002

---

## Health (HTTP)
- Live: `GET /v2/health/live`
- Ready: `GET /v2/health/ready`

## Server / model metadata (HTTP)
- `GET /v2`
- `GET /v2/models`
- `GET /v2/models/<model>`
- `GET /v2/models/<model>/versions/<ver>`

## Inference (HTTP)
- `POST /v2/models/<model>/infer`

## Repository control (optional; often disabled)
- Load: `POST /v2/repository/models/<model>/load`
- Unload: `POST /v2/repository/models/<model>/unload`
- Index: `POST /v2/repository/index`

## Metrics
- `GET :8002/metrics`

---

## Useful OpenShift commands

```bash
oc -n llm-inference get pods -o wide
oc -n llm-inference logs deploy/triton-llm-v2
oc -n llm-inference exec -it deploy/triton-llm-v2 -- curl -s localhost:8000/v2/health/ready
oc -n llm-inference exec -it deploy/triton-llm-v2 -- curl -s localhost:8002/metrics | head
```
