# Governance

- **Owner:** Ferrini AI Staff (Dante Ferrini, Principal).
- **Repository:** `CentaurMews/ElicitSec` (working name: enterprise-agent-security-evals).
- **Methodology versioning:** the methodology (AASM-EA) is versioned in
  `docs/methodology/`; changes are semver-tagged. Case files carry their own
  version and reference the methodology version they were written against.

## Approval gates

| Change class | Required approval |
|---|---|
| Methodology / taxonomy / schema changes | Principal (Dante) |
| New canonical test case (any tier) | Principal review of case file |
| Tier 0-1 execution | standard rules of engagement |
| Tier 2 execution | explicit per-suite approval |
| Tier 3 execution | exact target/action approval |
| Tier 4+ execution | separate approval + rollback plan; isolated environment |
| Publication of results | sanitized only, per `docs/methodology/responsible-testing.md` |

## Decision log

- 2026-09-22: Repository created from the v0.1 seed design
  (`ElicitSec_Agentic_Security_Evaluation_Repository_Seed.md`, Prime Shared).
  Initial target profile: OpenClaw + Teams + Work IQ + Entra + Azure VM.
