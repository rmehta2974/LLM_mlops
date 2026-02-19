# Architecture Overview – End-to-End LLMOps Platform

## 1. System Context

```mermaid
flowchart TB
    subgraph External["External"]
        Users[Users / Applications]
        CI[CI/CD]
    end

    subgraph Platform["LLMOps Platform"]
        subgraph API["API Layer"]
            Gateway[API Gateway]
            Auth[Auth / Rate Limit]
        end

        subgraph Inference["Inference Layer"]
            LB[Load Balancer]
            Triton1[Triton]
            Triton2[Triton]
            Triton3[Triton]
            LB --> Triton1
            LB --> Triton2
            LB --> Triton3
        end

        subgraph Orchestration["Orchestration"]
            K8s[Kubernetes / OpenShift]
            K8s --> Triton1
            K8s --> Triton2
            K8s --> Triton3
        end

        subgraph Data["Data"]
            ModelRepo[Model Repository]
            Registry[Model Registry]
        end

        subgraph Ops["Operations"]
            Prom[Prometheus]
            Grafana[Grafana]
            Alert[Alertmanager]
        end

        Gateway --> Auth
        Auth --> LB
        Triton1 --> ModelRepo
        Triton2 --> ModelRepo
        Triton3 --> ModelRepo
        Triton1 --> Prom
        Triton2 --> Prom
        Triton3 --> Prom
        Prom --> Grafana
        Prom --> Alert
    end

    subgraph Pipeline["MLOps Pipeline"]
        Kubeflow[Kubeflow]
        Build[Build / TRT-LLM]
        Kubeflow --> Build
        Build --> Registry
        Build --> ModelRepo
    end

    Users --> Gateway
    CI --> Pipeline
```

---

## 2. Data Flow: Request to Response

```mermaid
sequenceDiagram
    participant Client
    participant Gateway
    participant LB as Load Balancer
    participant Triton
    participant GPU

    Client->>Gateway: POST /v1/completions
    Gateway->>Gateway: Auth, Rate Limit
    Gateway->>LB: Forward
    LB->>Triton: Select pod
    Triton->>Triton: Batch (if dynamic batching)
    Triton->>GPU: Inference
    GPU-->>Triton: Logits
    Triton-->>LB: Response
    LB-->>Gateway: Response
    Gateway-->>Client: 200 OK + generated text
```

---

## 3. Data Flow: Model Deployment

```mermaid
flowchart LR
    subgraph Dev["Development"]
        Train[Train / Fine-tune]
        Eval[Evaluate]
        Register[Register Model]
        Train --> Eval --> Register
    end

    subgraph Build["Build"]
        Convert[Convert to TRT-LLM]
        Build[Build Engine]
        Convert --> Build
    end

    subgraph Deploy["Deploy"]
        Sync[Sync to Model Repo]
        Load[Triton Load]
        Validate[Smoke Test]
        Sync --> Load --> Validate
    end

    subgraph Operate["Operate"]
        Monitor[Monitor]
        Scale[Scale]
        Respond[Incident Response]
    end

    Register --> Convert
    Build --> Sync
    Validate --> Monitor
    Monitor --> Scale
    Monitor --> Respond
```

---

## 4. Deployment Topologies

### 4.1 On-Prem (NVIDIA DGX / HGX)

```
[Cluster] → GPU Operator → K8s/OpenShift → Triton → NFS/GPFS Model Repo
```

### 4.2 AWS

```
[EKS] → GPU Node Group → Triton → S3 (sync) / EFS
[SageMaker] → Managed Endpoint → Triton Container → S3
```

### 4.3 GCP

```
[GKE] → GPU Node Pool → Triton → GCS (sync) / Filestore
[Vertex AI] → Custom Container → Triton → GCS
```

---

## 5. Technology Stack Summary

| Layer | Technologies |
|-------|--------------|
| **Inference** | Triton, TensorRT-LLM |
| **Orchestration** | Kubernetes, OpenShift |
| **Pipeline** | Kubeflow, Argo Workflows |
| **Monitoring** | Prometheus, Grafana |
| **Cloud** | AWS (SageMaker, EKS), GCP (Vertex AI, GKE) |

---

## 6. Document Map

| Phase | Documents |
|-------|-----------|
| **Understand** | Architecture, When/What/How |
| **Build** | TensorRT-LLM, Optimization |
| **Deploy** | Configuration, K8s, Cloud |
| **Scale** | Load Balancing, HA, Monitoring |
| **Operate** | Incident, Change, Event |

---

See [README](README.md) and [Quick Reference](QUICK-REFERENCE.md) for navigation.
