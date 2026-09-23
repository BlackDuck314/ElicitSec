# Reproducibility

A run is reproducible when, given the same inputs, it produces the same
classification. Inputs are pinned in the run manifest:

- case id + case version + methodology version
- target: agent build/commit, container digest, model id, system policy hash,
  tool policy hash, app manifest version
- execution: attacker identity, channel context, repetition index, temperature,
  seed (where the model supports it)
- fixture manifest hash (all fixtures the case touches)
- oracle versions and evidence store version

Non-determinism sources and their controls:

| Source | Control |
|---|---|
| LLM sampling | temperature pinning per `run_policy.temperatures`; repetitions per case |
| Time-dependent prompts | fixture content is static; no clock-dependent text |
| Shared state | reset manager restores snapshots between runs; non-isolated runs are flagged |
| Retrieval ordering | fixture manifests pin document set and order |
| External services | adapters record every external decision (authorization, audit event) as evidence |

Results store: DuckDB + Parquet (initial), see `architecture/evidence-model.md`.
