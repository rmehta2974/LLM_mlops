# Practical Scenarios

## Scenario 1: New Model Deploy Without Restart

**Context:** New fine-tuned model ready; Triton already serving traffic.

**Flow:**
1. CI builds engine → uploads to S3
2. Job syncs S3 → PVC (`model_repository/llama2_7b/2/`)
3. Call Triton load API:
   ```bash
   curl -X POST http://triton:8000/v2/repository/models/llama2_7b/load \
     -d '{"parameters": {"version": "2"}}'
   ```
4. v2 loaded; v1 stays loaded
5. Route 5% traffic to v2 for canary

---

## Scenario 2: Preprocess → Embed → LLM Pipeline

**Context:** RAG: user query → embedding → vector search → LLM with context.

**Flow:** Ensemble model runs tokenizer → embedding → llm. Client sends one request.

---

## Scenario 3: Canary Rollout of FP8 Model

**Context:** Current FP16; new FP8 build ready. Compare latency and quality.

**Flow:**
1. Deploy v2 (FP8) to same Triton repo as v1 (FP16)
2. Ingress: 90% → v1, 10% → v2
3. Monitor; if OK, increase to 50% then 100%
4. Unload v1 when done

---

## Scenario 4: Multi-Model Server (Shared GPU)

**Context:** One Triton serves embedding + small LLM.

**Flow:** Model repo has `embedding/` and `llm_7b/`. Clients call `/v2/models/embedding/infer` or `/v2/models/llm_7b/infer`.

---

## Scenario 5: Emergency Rollback

**Context:** v2 has high error rate; revert to v1.

**Flow:**
1. Route 100% traffic to v1 (Ingress/API gateway)
2. Optionally unload v2
3. Or: scale down canary deployment, scale up stable

---

## Scenario 6: A/B Test Two Fine-Tunes

**Context:** Compare fine-tune A vs B.

**Flow:** Load both as v1 and v2. Route by header `x-experiment: A` or `B`. Log and analyze.

---

## Scenario 7: Batch Inference at Night

**Context:** Batch jobs at night; real-time during day.

**Flow:** Option A: Same Triton, higher `max_queue_delay` at night. Option B: Separate batch deployment.

---

## Scenario 8: Model Repo Sync from Artifactory

**Context:** Models in Artifactory; Triton uses PVC.

**Flow:** CronJob runs hourly: sync Artifactory → PVC, call Triton load for changed models.

---

## Scenario 9: Blue-Green Deployment

**Context:** Zero-downtime deploy.

**Flow:** Deploy green (new Triton), validate, switch Ingress from blue → green.

---

## Scenario 10: Multi-Region with Same Model

**Context:** US and EU clusters; same model in both.

**Flow:** Build once, upload to S3. Each region syncs S3 → regional PVC. Triton in each region loads from local PVC.

---

## Scenario 11: Long-Context Model Upgrade

**Context:** 4K → 8K context; check memory.

**Flow:** Deploy v2 as canary, monitor GPU memory. If OOM, reduce batch size or use model parallelism.

---

## Scenario 12: Deprecate Old Model

**Context:** Retiring v1 after v2 is stable.

**Flow:**
1. Ensure no traffic to v1
2. Unload v1: `curl -X POST .../unload -d '{"parameters": {"version": "1"}}'`
3. Remove v1 dir from repo
