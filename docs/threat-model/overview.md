# Threat model overview

ElicitSec models enterprise agents as **delegated, identity-bearing systems**.
The central question: *can attacker-controlled content cause an agent to adopt
an unauthorized objective, attempt an out-of-policy tool call, cross a
caller/data/identity boundary, alter durable state, or cause observable
security harm?*

The model decomposes any agent interaction along IDAPS:

```
I  Instructions  what can influence the agent's objective or plan?
D  Data          what can the agent retrieve, infer, disclose, transform?
A  Actions       what external operations can it take?
P  Privileges    whose authority executes each operation?
S  State         what persists beyond the current interaction?
```

Threat proposition: instructions influence intent; data creates value;
actions create impact; privileges amplify harm; state makes compromise
persistent.

See: [idaps.md](idaps.md), [trust-boundaries.md](trust-boundaries.md),
[security-properties.md](security-properties.md), [threat-scenarios.md](threat-scenarios.md),
[assets.md](assets.md), [actors.md](actors.md), [risk-register.md](risk-register.md).
