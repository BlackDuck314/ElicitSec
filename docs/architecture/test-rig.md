# Test rig architecture

```
                    +-----------------------------+
  canonical cases  |        CONTROL PLANE        |
  (suites/*.yaml)  |  loader -> validator ->     |
        |          |  safety gate -> scheduler   |
        v          +-------------+---------------+
  +-----+------------------+     |
  |  RUNNER / ORCHESTRATOR |     v
  |  (runners/)            |  adapter selection
  +-----+------------------+
        |  session / message / reset / snapshot
        v
  +-------------------+    +---------------------+
  |  TARGET ADAPTER   |--->|  target agent under  |
  |  (adapters/*)     |    |  test (OpenClaw/...) |
  +-------------------+    +----------+----------+
        |  transcript, tool calls, auth events, traces
        v
  +-------------------+    +---------------------+
  |  ORACLES          |--->|  evidence store     |
  |  deterministic +  |    |  (DuckDB/Parquet,   |
  |  semantic judge   |    |   redacted)         |
  +-------------------+    +----------+----------+
        |                              |
        v                              v
  classification / metrics ----->  reports (MD/HTML/JSON)
```

Execution flow per run (methodology section 14):

```
load case -> validate -> safety gate -> provision/reset fixtures
-> snapshot state -> create actor/session -> run utility control (baseline)
-> run adversarial scenario -> collect evidence -> run oracles
-> classify -> metrics/risk -> cleanup/reset -> persist -> report
```

Safety gate pseudocode:

```python
if case.consequence_tier > environment.max_allowed_tier:
    raise SafetyGateError("case exceeds environment safety policy")
if case.consequence_tier >= 3 and not approvals.verify(case.id, exact_target, exact_action):
    raise SafetyGateError("missing exact approval for consequential test")
if not safe_target_register.contains_all(case.referenced_targets):
    raise SafetyGateError("case references a non-approved target")
```
