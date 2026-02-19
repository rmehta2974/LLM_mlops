# Load Balancing for LLM Inference

## 1. Overview

Load balancing distributes inference requests across multiple Triton instances to:

- **Increase throughput** – More pods = more capacity
- **Reduce latency** – Avoid queue buildup on single pod
- **Improve availability** – Failover when a pod is unhealthy

---

## 2. Load Balancing Architecture

```mermaid
flowchart TB
    subgraph Clients["Clients"]
        C1[App 1]
        C2[App 2]
        C3[App 3]
    end

    subgraph LB["Load Balancer Layer"]
        direction TB
        Ingress[Ingress / API Gateway]
        Service[Kubernetes Service]
        Ingress --> Service
    end

    subgraph Triton["Triton Pods"]
        T1[Pod 1]
        T2[Pod 2]
        T3[Pod 3]
    end

    C1 --> Ingress
    C2 --> Ingress
    C3 --> Ingress
    Service --> T1
    Service --> T2
    Service --> T3
```

---

## 3. Kubernetes Service Types

| Type | Load Balancing | Use Case |
|------|----------------|----------|
| **ClusterIP** | Round-robin (internal) | Internal traffic |
| **NodePort** | Via kube-proxy | Development |
| **LoadBalancer** | Cloud LB (AWS ELB, GCP LB) | Production |
| **Ingress** | L7 routing, TLS | Production with paths/hosts |

---

## 4. Load Balancing Algorithms

```mermaid
flowchart TD
    subgraph Algorithms["Algorithms"]
        RR[Round Robin]
        LC[Least Connections]
        IPH[IP Hash]
        LBW[Load-based / Weighted]
    end

    subgraph When["When to Use"]
        RR --> W1[Default, stateless]
        LC --> W2[Long-lived connections, LLM streaming]
        IPH --> W3[Sticky sessions]
        LBW --> W4[Heterogeneous pods]
    end
```

| Algorithm | Pros | Cons |
|-----------|------|------|
| **Round Robin** | Simple, fair | Ignores pod load |
| **Least Connections** | Balances active requests | Needs connection tracking |
| **IP Hash** | Sticky sessions | May imbalance |
| **Weighted** | Handles different pod sizes | More configuration |

**For LLM streaming**: Prefer **least connections** – long requests shouldn’t overload one pod.

---

## 5. Nginx Ingress Example

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: triton-ingress
  annotations:
    nginx.ingress.kubernetes.io/upstream-hash-by: "$request_uri"  # Optional: sticky
    nginx.ingress.kubernetes.io/proxy-body-size: "100m"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "600"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "600"
spec:
  ingressClassName: nginx
  rules:
    - host: inference.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: triton-inference
                port:
                  number: 8000
```

---

## 6. API Gateway Patterns

```mermaid
flowchart TB
    subgraph Gateway["API Gateway"]
        Auth[Auth / API Key]
        RateLimit[Rate Limiting]
        Route[Routing]
        Metrics[Metrics]
    end

    subgraph Backend["Backend"]
        Triton1[Triton - Model A]
        Triton2[Triton - Model B]
    end

    Client[Client] --> Auth
    Auth --> RateLimit
    RateLimit --> Route
    Route --> Triton1
    Route --> Triton2
    Route --> Metrics
```

**Path-based routing:**

- `/v1/models/llama` → Triton model `llama`
- `/v1/models/mistral` → Triton model `mistral`

---

## 7. Autoscaling Integration

```mermaid
flowchart LR
    subgraph Metrics["Metrics"]
        CPU[CPU]
        GPU[GPU Utilization]
        QLen[Queue Length]
    end

    subgraph HPA["HPA"]
        ScaleUp[Scale Up]
        ScaleDown[Scale Down]
    end

    subgraph Pool["Pod Pool"]
        P1[Pod]
        P2[Pod]
        P3[Pod]
    end

    Metrics --> HPA
    HPA --> ScaleUp
    HPA --> ScaleDown
    ScaleUp --> Pool
    ScaleDown --> Pool
```

Load balancer automatically includes new pods and removes scaled-down ones via Kubernetes Service endpoints.

---

## 8. Multi-Region Load Balancing

```mermaid
flowchart TB
    subgraph Global["Global Load Balancer"]
        GCP[GCP Global LB]
        Route53[AWS Route 53]
    end

    subgraph Region1["Region US-East"]
        K8s1[Kubernetes]
        Triton1[Triton]
        K8s1 --> Triton1
    end

    subgraph Region2["Region EU-West"]
        K8s2[Kubernetes]
        Triton2[Triton]
        K8s2 --> Triton2
    end

    Client[Client] --> GCP
    GCP --> K8s1
    GCP --> K8s2
```

- Use **latency-based routing** or **geographic routing**
- Consider **model replication** across regions

---

## 9. Checklist

- [ ] Kubernetes Service with correct selector
- [ ] Readiness probes so unhealthy pods are excluded
- [ ] Timeouts tuned for long LLM requests
- [ ] Algorithm chosen (round-robin vs least connections)
- [ ] HPA so pool size adapts to load

---

## Next Steps

- [High Availability](./02-high-availability.md)
- [Monitoring & Observability](./03-monitoring-observability.md)
