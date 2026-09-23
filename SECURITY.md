# Security

## Scope

ElicitSec is a security-evaluation framework. Reporting a security issue about
the framework itself (runner, oracles, harness) is welcome.

## Reporting

1. Do not post reproduction payloads that produce real harm to public issues.
2. Open a private report to the repository owner (CentaurMews) describing:
   - the affected component,
   - the consequence tier of the failure,
   - minimal reproduction (synthetic fixtures only),
   - observed vs expected behavior.
3. Synthetic canary values used in fixtures are non-operational by design;
   they exist to be matched, not used.

## Evidence handling

All test evidence is sensitive by default. See
`docs/methodology/responsible-testing.md` for redaction, retention, and
publication rules. Never commit real tenant IDs, user identifiers, secrets,
raw traces, or production paths to this repository.
