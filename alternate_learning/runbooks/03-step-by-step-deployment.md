# Runbook — 03 Step-by-step Deployment

## 1) Create namespace and storage
```bash
oc apply -f manifests/00-namespace.yaml
oc apply -f manifests/01-model-repo-pvc.yaml
```

## 2) Deploy Triton + service
```bash
oc apply -f manifests/10-triton-deployment.yaml
oc apply -f manifests/11-triton-service.yaml
```

## 3) Validate health
```bash
oc -n llm-inference get pods -o wide
oc -n llm-inference port-forward deploy/triton-llm 8000:8000
curl -s localhost:8000/v2/health/ready
```

## 4) Autoscaling
```bash
oc apply -f manifests/20-hpa.yaml
# Or KEDA:
oc apply -f manifests/21-keda-scaledobject.yaml
```
