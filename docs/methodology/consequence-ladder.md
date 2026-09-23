# Consequence ladder

Progressive validation, never destructive testing by default (methodology
section 4.3, [aasm-ea.md](aasm-ea.md)).

| Tier | Operation class | Examples | Approval |
|---|---|---|---|
| 0 | No side effect | explain, classify, summarize public fixture | standard RoE |
| 1 | Low-impact controlled read | read sandbox file, public canary document | standard RoE |
| 2 | Sensitive synthetic read | user-A-only document, synthetic mailbox token, test Key Vault canary | explicit per-suite approval |
| 3 | Reversible controlled write | create draft, modify dedicated test file, post to internal test channel | exact target/action approval |
| 4 | Persistent/configuration test | test-only state marker, memory fixture, approved isolated config | separate approval + rollback plan |
| 5 | High-impact/irreversible | RBAC changes, credential creation, external egress, deletion, deployment | avoid by default; isolated environment + executive approval |

The runner's safety gate enforces: `case.consequence_tier <= environment.max_allowed_tier`,
exact approval for tier >= 3, and safe-target registration for every referenced target.
CI may only run tiers 0-1 (see [operations/ci-regression.md](../operations/ci-regression.md)).
