# 06 — API, Gateway, Networking, and Microservice Design

## 1) Why separate API from inference runtime
- auth/rate limit/WAF should not run inside Triton
- allows stable product API while swapping inference engines underneath
- supports multi-tenant policy and auditing

## 2) Common gateway choices
- OpenShift Route/Ingress (simple)
- Gateway API (modern k8s routing)
- Istio (mTLS + traffic splitting + authz)
- External API gateways (Kong/Apigee) for enterprise governance

## 3) Step-by-step request routing design
1. Authenticate user/tenant (JWT/OIDC)
2. Apply tenant quotas and limits (RPS, max tokens, max context)
3. Select model endpoint (router maps model name -> backend service)
4. Apply traffic split for canary
5. Forward to Triton via gRPC (preferred) or HTTP

## 4) API primitives (what interviewers expect)
- correlation ID propagation
- idempotency keys
- streaming support (SSE or gRPC streaming)
- timeouts and retry budgets
- structured error codes

## 5) Load balancing and locality
- L7 routing (model selection, canary)
- L4 LB for high-throughput gRPC in some environments
- optional zone-local routing for multi-zone clusters
