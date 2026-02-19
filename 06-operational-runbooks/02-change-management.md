# Change Management for Mission-Critical AI Systems

## 1. Overview

**Change management** ensures controlled, tracked, and reversible updates to AI inference systems.

---

## 2. Change Types

| Type | Risk | Approval | Example |
|------|------|----------|---------|
| **Standard** | Low | Pre-approved | Config tweak, non-critical |
| **Normal** | Medium | Change advisory | New model version, scaling change |
| **Emergency** | High | Expedited | Hotfix, security patch |

---

## 3. Change Lifecycle

```mermaid
flowchart TD
    A[1. Request] --> B[2. Assess]
    B --> C[3. Approve]
    C --> D[4. Schedule]
    D --> E[5. Execute]
    E --> F[6. Verify]
    F --> G{Success?}
    G -->|Yes| H[7. Close]
    G -->|No| I[8. Rollback]
    I --> F
```

---

## 4. Model Deployment Change

```mermaid
flowchart LR
    A[New Model Ready] --> B[Create Change Request]
    B --> C[Schedule Maintenance Window]
    C --> D[Deploy to Staging]
    D --> E[Validate]
    E --> F{OK?}
    F -->|Yes| G[Deploy to Production]
    F -->|No| H[Abort / Fix]
    G --> I[Smoke Test]
    I --> J[Monitor]
    J --> K[Close Change]
```

---

## 5. Pre-Change Checklist

- [ ] Change request documented
- [ ] Rollback plan defined
- [ ] Backup / previous version available
- [ ] Maintenance window communicated
- [ ] On-call notified
- [ ] Monitoring dashboards ready

---

## 6. Rollback Procedure

| Scenario | Rollback Action |
|----------|-----------------|
| **Bad model version** | Load previous version: `POST /v2/repository/models/{model}/load` with prior version |
| **Config change** | Revert config.pbtxt, reload model |
| **Triton upgrade** | Rollback deployment to previous image |
| **K8s deployment** | `kubectl rollout undo deployment/triton` |

---

## 7. Zero-Downtime Deployments

```mermaid
flowchart LR
    subgraph BlueGreen["Blue-Green"]
        Blue[Blue - v1]
        Green[Green - v2]
        LB[Load Balancer]
        LB --> Blue
        LB -.->|Switch| Green
    end
```

**Strategy:**

1. Deploy new version (Green) alongside current (Blue)
2. Validate Green
3. Shift traffic to Green
4. Retire Blue

---

## 8. Change Windows

| Window | Use Case |
|--------|----------|
| **Business hours** | Low-risk, need validation during day |
| **Off-hours** | Higher risk, minimize user impact |
| **Planned maintenance** | Major upgrades, communicate in advance |

---

## 9. Documentation

**Change record:**

- Change ID
- Description
- Risk level
- Approval
- Execution steps
- Verification steps
- Rollback steps
- Outcome

---

## Next Steps

- [Event Management](./03-event-management.md)
- [Incident Management](./01-incident-management.md)
