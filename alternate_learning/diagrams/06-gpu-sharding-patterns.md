# GPU sharding and scaling patterns

```mermaid
flowchart TB
  subgraph P1[1 pod 1 GPU]
    LB1[LB] --> Pod1[Triton Pod]
    Pod1 --> GPU1[GPU]
  end

  subgraph P2[1 pod N GPUs (tensor parallel)]
    LB2[LB] --> Pod2[Triton Pod]
    Pod2 --> G0[GPU0]
    Pod2 --> G1[GPU1]
    Pod2 --> G2[GPU2]
    Pod2 --> G3[GPU3]
  end

  subgraph P3[MIG slices]
    LB3[LB] --> A[Triton A]
    LB3 --> B[Triton B]
    A --> M1[MIG 1]
    B --> M2[MIG 2]
  end
```
