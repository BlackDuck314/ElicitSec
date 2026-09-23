# Cleanup and recovery

- Every case declares `run_policy.cleanup` (what it touched and how to undo).
- The reset manager runs after every case (success or failure) and records
  the result; a failed reset flags the run HARNESS_ERROR.
- Persistent-state tests (tier 4) require a pre-run snapshot and an automatic
  restore; restore failure aborts the suite and pages the operator.
- Stop condition: if a run touches any target not in the safe-target
  register, the suite aborts, state is restored from the last snapshot, and
  the incident is recorded in `results/local/incidents/`.
