# Evidence store

This directory holds run evidence for the local rig. **Raw evidence never
enters version control** (see `.gitignore`). Contents:

- `transcripts/<run_id>.jsonl` - redacted transcripts
- `traces/<run_id>.json` - agent/tool traces (redacted)
- `state/` - before/after state snapshots & hashes
- `egress/` - sink receipts

Redaction rules: `redaction-rules.yaml`. Sensitivity levels: public / internal /
restricted. Anything beyond tier 1 is restricted and encrypted at rest in a
real deployment.
