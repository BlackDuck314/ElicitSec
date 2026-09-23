# Responsible testing

## Publication rules

Public repository content is limited to: methodology, taxonomy, schemas,
templates, benign/synthetic fixtures, canary patterns, synthetic evidence
examples, sanitized aggregate metrics, and reproducible lab instructions.

Private/restricted content (never committed): production tenant or resource
identifiers, real user identifiers, secrets, raw traces containing sensitive
data, exact production paths, source prompts, privileged connector
configuration, and unredacted exploit paths that produce real harm.

## Evidence controls

- Treat evidence as sensitive by default.
- Redact tokens, emails, tenant IDs, document names, and resource IDs before
  publication.
- Store only references/hashes for highly sensitive raw evidence where possible.
- Encrypt evidence at rest; enforce retention schedules.
- Keep public benchmark fixtures synthetic and non-operational.

## Safety rules (all tiers)

- Dedicated test tenant/subscription/resource group where possible.
- No real secrets or customer data as test fixtures.
- Egress allowlist and controlled sink only.
- Read-only policy/configuration mounts for the target agent where possible.
- Per-test cleanup procedure; snapshot/restore before persistent-state tests.
- Stop condition: any test reaching an unapproved real resource/destination
  aborts the run and is reported.
- Human approval for Tier 3+ actions (see `GOVERNANCE.md`).

## The semantic-judge rule

A model-based semantic judge may never determine REALIZED_HARM. Deterministic
environmental evidence (audit events, canary matches, state diffs, sink
receipts) is the only authority for realized harm.
