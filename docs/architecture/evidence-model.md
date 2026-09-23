# Evidence model

Every run produces:

- transcript (Teams/message content, conversation ids, sender identities)
- agent trace (model context where exposed)
- tool calls (name, parameters, result, authorization decision, executing identity)
- authorization events (policy decisions with subject/target/operation)
- audit events (Graph/Work IQ/Azure/Key Vault/filesystem/egress)
- state snapshots (before/after hashes or full snapshots)
- oracle results (deterministic checks + semantic labels)

Storage: DuckDB + Parquet initially (local, encrypted at rest for anything
beyond tier 1); JSONL run manifests alongside for portability.

Redaction: `evidence/redaction-rules.yaml` defines rules applied before any
persistence outside the raw store (tokens, emails, tenant ids, document
names, resource ids). Raw evidence stays local; only redacted copies and
references enter version control or reports.

Retention: configurable per environment; public/sanitized results carry no
raw content by construction.
