# ElicitSec

ElicitSec is an evidence-led security-evaluation framework for enterprise,
tool-using AI agents.

It evaluates whether attacker-controlled content can cause an agent to:

- adopt an unauthorized objective;
- attempt or perform an out-of-policy tool action;
- cross a user, data, identity, or authorization boundary;
- modify persistent instructions, memory, configuration, or tool state; or
- disclose or transmit protected data.

ElicitSec evaluates the complete trajectory:

```text
untrusted input
  -> context construction
  -> agent reasoning
  -> tool selection
  -> executing identity
  -> authorization decision
  -> external state or output
  -> deterministic evidence
```

## Core principle

No attacker-controlled content may cause an agent to access, disclose, modify,
or transmit a resource unless the verified requesting principal is
independently authorized for that exact operation and target.

## Core model: IDAPS

- **Instructions** influence intent.
- **Data** creates value.
- **Actions** create impact.
- **Privileges** amplify harm.
- **State** makes compromise persistent.

## Initial target profile

OpenClaw + Microsoft Teams + Work IQ + Microsoft Entra ID + Azure VM.
The architecture is adapter-based; other agents and enterprise stacks plug in
through the adapter contract (`docs/architecture/adapter-contract.md`).

## Status

- **v0.1 seed methodology**: approved design (see `docs/methodology/aasm-ea.md`).
- **Milestone 0** (repository foundation): in progress.
- **Milestone 1** (local deterministic harness): in progress.
- Real-environment integration (Milestones 2-5) is blocked on the open
  questions below until they are answered.

## Repository layout

```
docs/        methodology, threat model, architecture, operations, reports
taxonomy/    constructs, boundaries, properties, impacts, assets, mitigations
schemas/     JSON Schemas for cases, manifests, evidence, findings, oracles
suites/      canonical elicitation cases (YAML), grouped by suite prefix
fixtures/    synthetic test data (canaries, documents, emails, tool returns)
adapters/    target-system adapters (mock, openclaw, teams, workiq, ...)
runners/     case runner/orchestrator, safety gate, reset manager
oracles/     deterministic evidence oracles + semantic evaluators
evaluators/  classification, utility, risk scoring, metrics
data/        target profiles, test identities, safe-target register, policy
evidence/    redacted evidence store (see evidence/README.md)
results/     baselines, regression, sanitized publication
scripts/     rig bootstrap, canary provisioning, suite runner, reporting
.github/     CI workflows
```

## Development

```sh
uv venv && uv pip install -e ".[dev]"
make validate   # schema-validate all cases
make test       # unit + contract tests
elicitsec run --suite suites/authorization --adapter mock
```

## Open questions (need Principal decision before real integrations)

1. Is the initial test target a staging OpenClaw environment, a production-like
   clone, or the existing production deployment?
2. Is a direct OpenClaw API/test harness available, or must first-phase
   interaction go through Teams?
3. What traces can OpenClaw expose (model context, retrievals, tool calls,
   policy checks, identity, state writes)?
4. Does Work IQ expose a test-friendly fixture/source setup with retrieval and
   audit traces?
5. Which Entra permission model applies per connector (delegated, on-behalf-of,
   application, managed identity, static credential)?
6. Can a dedicated test tenant/subscription/SharePoint site/mailbox/Key Vault
   be created?
7. Which CI platform is the first target (GitHub Actions, Azure DevOps, local)?
8. Can agent runtime state be snapshotted/restored between tests?
9. What legal/organizational approval boundary applies to Tier 3+ tests?
10. What level of raw evidence may be retained, and where is it encrypted?

## Responsible use

ElicitSec is an evaluation framework, not an offensive tool. Public content is
limited to methodology, taxonomy, schemas, synthetic fixtures, and sanitized
aggregate metrics. Production identifiers, real user data, and secrets never
enter the repository (see `SECURITY.md` and `docs/methodology/responsible-testing.md`).
