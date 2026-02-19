# Shared patterns (AWS/GCP)

## Object store as source of truth
- immutable versioning
- promotion by pointer/tag, not overwrite

## Cold start strategy
- init container downloads model version to emptyDir cache
- consider node-local cache for huge models

## Autoscaling
- prefer scaling on queue depth/RPS over CPU
- keep warm baseline for burst
