# GitHub Actions — Build + Push + GitOps Bump (Stub)

## Jobs
- build-engine
- test-golden-prompts
- perf-smoke
- build-model-image
- push-registry
- publish-artifactory
- bump-gitops-pointer

## Notes
- use artifact caching
- use OIDC to cloud registries if possible
- store secrets in GitHub/AWS/GCP secret managers
