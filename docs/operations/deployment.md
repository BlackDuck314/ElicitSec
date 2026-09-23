# Deployment

## Local deterministic rig (default)

```sh
uv venv && uv pip install -e ".[dev]"
cp .env.example .env
make test
elicitsec run --suite suites --adapter mock --out results/local
elicitsec report --from results/local --out results/local/report.md
```

No external credentials are needed for the mock adapter. All fixtures are
synthetic files in `fixtures/`.

## Docker/compose rig (integration)

`docker-compose.yml` defines the egress sink, a mock OpenClaw endpoint, and
the runner; `compose.test.yml` is the CI profile (tier 0-1 only).
(Files to be completed with the Milestone 1 integration work.)

## Enterprise test environment (Milestones 2+)

Requires the dedicated test tenant/subscription decisions listed in
`README.md` open questions. IaC (Terraform/Bicep) lands with those milestones.
