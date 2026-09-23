# IDAPS in depth

Each dimension maps to constructs in `taxonomy/constructs.yaml`:

| Dimension | Question | Construct families |
|---|---|---|
| Instructions | What can influence objective/plan? | OBJ-* (override, displacement, authority displacement, approval substitution) |
| Data | What can be retrieved/inferred/disclosed? | DATA-* (disclosure, metadata, transformation, exfiltration), CTX-* (injection paths) |
| Actions | What external operations? | CAP-* (authorization confusion, confused deputy, cross-principal, scope escalation, tool overreach, token misbinding), CHAIN-* |
| Privileges | Whose authority executes? | CAP-01/02, STATE-03/04, P6 least privilege |
| State | What persists? | STATE-* (instruction, memory, tool/policy, config integrity) |

Injection contexts (CTX-*) are the delivery paths; constructs combine: a
threat scenario is a construct chain (e.g. CTX-04 -> OBJ-02 -> DATA-04).
