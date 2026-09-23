# Contributing

## Adding a canonical test case

1. Pick the suite prefix and next case ID (see `docs/methodology/aasm-ea.md`,
   section 7 for the suite map).
2. Copy a case from `suites/` as a template; every field in the
   `elicitation-case` schema is mandatory.
3. Every adversarial case must have a paired **utility control**
   (mandatory paired controls, methodology section 4.5).
4. Every case names its **protected invariants** and at least one
   **deterministic oracle** (`oracles/` type + fail condition).
5. Validate: `make validate` (schema) and `elicitsec run --case <id> --adapter mock`.
6. Open a PR. Tier 0-1 cases merge on review; Tier 3+ require the approval
   documented in `GOVERNANCE.md`.

## Development setup

```sh
uv venv
uv pip install -e ".[dev]"
make test
```

## Case review checklist

- [ ] Versioned (case version + methodology version)
- [ ] Constructs referenced exist in `taxonomy/constructs.yaml`
- [ ] Consequence tier matches the operations the case performs
- [ ] Utility control present and executable
- [ ] Oracles are deterministic (no model-in-the-loop for REALIZED_HARM)
- [ ] Fixtures referenced exist in `fixtures/` and are synthetic
- [ ] Cleanup/reset requirements stated in `run_policy`
- [ ] No real identifiers, secrets, or production paths
