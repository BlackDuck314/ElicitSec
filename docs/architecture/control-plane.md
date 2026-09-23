# Control plane

The control plane owns:

- **Case registry** - loads/version-validates canonical YAML cases (schema + cross-checks against taxonomy).
- **Scheduler** - orders runs, repetitions, temperatures; enforces the
  "one case, one reset, one snapshot" isolation contract.
- **Safety gate** - tier checks, approval verification, safe-target register
  (see test-rig.md).
- **Reset manager** - fixture/canary/file/memory/session reset between runs;
  every reset is recorded in the run manifest (a failed reset marks the run
  HARNESS_ERROR, never a case failure).
- **Approval store** - exact approval records (case id, target, action,
  approver, expiry); tier >= 3 requires a live, unexpired record.
- **Evidence store** - see evidence-model.md.

The control plane never interprets agent output; it only orchestrates and
records. Interpretation happens in oracles and evaluators.
