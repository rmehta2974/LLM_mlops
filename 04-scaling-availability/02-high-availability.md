# High Availability for LLM Inference

## 1. Overview

**High Availability (HA)** aims for:

- **No single point of failure**
- **Automatic failover**
- **Target SLAs** (e.g. 99.9% uptime)

---

## 2. HA Architecture

```mermaid
flowchart TB
    subgraph Availability["HA Layers"]
        direction TB
        subgraph L1["Layer 1: Multi-Pod"]
            P1[Pod 1]
            P2[Pod 2]
            P3[Pod 3]
        end

        subgraph L2["Layer 2: Multi-Node"]
            N1[Node 1]
            N2[Node 2]
            N3[Node 3]
        end

        subgraph L3["Layer 3: Multi-AZ"]
            AZ1[AZ-a]
            AZ2[AZ-b]
        end

        L1 --> L2 --> L3
    end
```

---

## 3. Pod-Level HA

### 3.1 Minimum Replicas

```yaml
spec:
  replicas: 3  # Minimum for HA
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0  # Never go below desired
```

### 3.2 Pod Disruption Budget (PDB)

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: triton-pdb
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: triton
```

Ensures at least 2 Triton pods stay running during voluntary disruptions (e.g. node drain).

### 3.3 Anti-Affinity

```yaml
affinity:
  podAntiAffinity:
    preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 100
        podAffinityTerm:
          labelSelector:
            matchLabels:
              app: triton
          topologyKey: kubernetes.io/hostname
```

Prefers spreading Triton pods across different nodes.

---

## 4. Node-Level HA

```mermaid
flowchart LR
    subgraph Zone1["Zone A"]
        N1[Node 1]
        N2[Node 2]
    end

    subgraph Zone2["Zone B"]
        N3[Node 3]
        N4[Node 4]
    end

    T1[Triton] --> N1
    T2[Triton] --> N2
    T3[Triton] --> N3
```

**Topology spread:**

```yaml
topologySpreadConstraints:
  - maxSkew: 1
    topologyKey: topology.kubernetes.io/zone
    whenUnsatisfiable: ScheduleAnyway
    labelSelector:
      matchLabels:
        app: triton
```

---

## 5. Multi-AZ Deployment

```mermaid
flowchart TB
    subgraph AZ1["Availability Zone 1"]
        K8s1[K8s Node Pool]
        Triton1[Triton x2]
        K8s1 --> Triton1
    end

    subgraph AZ2["Availability Zone 2"]
        K8s2[K8s Node Pool]
        Triton2[Triton x2]
        K8s2 --> Triton2
    end

    subgraph LB["Regional Load Balancer"]
        ELB[ELB / GLB]
    end

    ELB --> AZ1
    ELB --> AZ2
```

- Deploy Triton in at least 2 AZs
- Use a regional load balancer to distribute traffic

---

## 6. Model Repository HA

| Storage | HA Strategy |
|---------|-------------|
| **NFS** | NFS cluster, failover |
| **PVC** | ReadOnlyMany, replicated storage (e.g. Ceph) |
| **Object (S3)** | Multi-AZ, versioning |
| **Init sync** | Sync from S3 to local; multiple pods can run sync |

---

## 7. Failure Detection & Recovery

```mermaid
flowchart TD
    A[Pod Unhealthy] --> B[Readiness fails]
    B --> C[Removed from Service]
    C --> D[No new traffic]
    D --> E[Kubelet restarts / Replacement]
    E --> F[New pod ready]
    F --> G[Re-added to Service]
```

**Probes:**

```yaml
livenessProbe:
  httpGet:
    path: /v2/health/live
    port: 8000
  initialDelaySeconds: 90
  periodSeconds: 10
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /v2/health/ready
    port: 8000
  initialDelaySeconds: 120
  periodSeconds: 10
  failureThreshold: 3
```

---

## 8. Graceful Shutdown

```yaml
lifecycle:
  preStop:
    exec:
      command: ["/bin/sh", "-c", "sleep 15"]
terminationGracePeriodSeconds: 60
```

- `preStop` sleep allows load balancer to stop sending traffic
- `terminationGracePeriodSeconds` allows in-flight requests to finish

---

## 9. HA Checklist

- [ ] `replicas >= 2`
- [ ] PodDisruptionBudget defined
- [ ] Anti-affinity / topology spread
- [ ] Multi-AZ deployment
- [ ] Liveness and readiness probes
- [ ] Graceful shutdown configured
- [ ] Model repo is highly available

---

## Next Steps

- [Monitoring & Observability](./03-monitoring-observability.md)
- [Cloud Deployment - AWS](../05-cloud-deployment/01-aws-sagemaker-neurons.md)
