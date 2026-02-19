# RPS and Pushing Models to PVC

## What is RPS?

**RPS = Requests Per Second**

Number of inference requests a system handles in one second.

| Term | Meaning |
|------|---------|
| **RPS** | Requests per second |
| **QPS** | Queries per second (often same as RPS) |
| **Throughput** | Requests or tokens per second |

**Example:** 100 RPS = 100 inference calls per second.

**Relation to latency:** Higher RPS → more load → potentially higher latency. Triton's dynamic batching increases RPS by grouping requests.

---

## How to Push Models to PVC

Triton only reads from a filesystem path. You don't "push" to Triton – you **populate the PVC** with model files.

### Option A: Job that Writes to PVC

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: push-model-to-pvc
spec:
  template:
    spec:
      restartPolicy: Never
      containers:
        - name: model-loader
          image: amazon/aws-cli
          command:
            - /bin/sh
            - -c
            - |
              aws s3 sync s3://my-bucket/model-repo/ /models/
          volumeMounts:
            - name: model-repo
              mountPath: /models
      volumes:
        - name: model-repo
          persistentVolumeClaim:
            claimName: triton-model-repo
```

### Option B: Job that Builds and Copies

```yaml
# Job runs trtllm-build, then copies to PVC
containers:
  - name: builder
    command:
      - /bin/sh
      - -c
      - |
        trtllm-build --checkpoint_dir /input --output_dir /tmp/engine
        cp -r /tmp/engine/* /models/llama2_7b/1/
    volumeMounts:
      - name: model-repo
        mountPath: /models
```

### Option C: Init Container (Sync Every Pod Start)

```yaml
initContainers:
  - name: sync-models
    image: amazon/aws-cli
    command: ["aws", "s3", "sync", "s3://bucket/model-repo/", "/models"]
    volumeMounts:
      - name: models
        mountPath: /models
containers:
  - name: triton
    volumeMounts:
      - name: models
        mountPath: /models
volumes:
  - name: models
    emptyDir: {}
```

**Note:** Init container + emptyDir = each pod syncs independently. For PVC, use Job to populate once.

### Manual Copy via Temporary Pod

```bash
kubectl run model-copy --rm -it --restart=Never \
  --image=busybox \
  --overrides='{"spec":{"containers":[{"name":"copy","image":"busybox","command":["sleep","3600"],"volumeMounts":[{"name":"models","mountPath":"/models"}]}],"volumes":[{"name":"models","persistentVolumeClaim":{"claimName":"triton-model-repo"}}]}}'

kubectl cp ./model_repository/llama2_7b model-copy:/models/llama2_7b
```

---

## End-to-End Flow

```
Build Engine (CI/Kubeflow) → Push Job copies to PVC → Triton Pods mount PVC
```

Optional: After push, call `POST /v2/repository/models/{model}/load` to reload Triton.
