# Runbook — 05 Troubleshooting (Step-by-step)

## p99 latency spikes
1. Compare v1 vs v2 metrics immediately
2. Check queue time vs compute time
3. Check GPU memory/OOMs
4. Validate batching/instance-group changes
5. Roll back traffic if SLO impacted

## GPU underutilized but queue high
- concurrency too low
- batching misconfigured
- CPU preprocessing bottleneck
- network bottleneck

## Frequent OOM
- enforce max context length and max tokens
- reduce concurrent sequences
- increase headroom / bigger GPU / fewer instances per GPU
