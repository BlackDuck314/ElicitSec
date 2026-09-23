# Report template

```markdown
# ElicitSec assessment report - <target profile>

- Run: <run_id>
- Date: <timestamp>
- Methodology version: 0.1
- Assessment mode: <black|grey|white>_box
- Target: <agent id, build, model, policy hashes>

## Scope and RoE
<scope statement, identities, stop conditions, safe-target register ref>

## Summary metrics
| Metric | Value |
| BU | |
| UUA | |
| SFR | |
| UTAR | |
| ABVR | |
| OHR | |
| PSR | |
| CPLR | |
| ORR | |

## Findings
| ID | Case | Constructs | Class | Risk | Status |
| F-001 | AUTH-001 | CAP-02, DATA-01 | REALIZED_HARM | 480 | open |

## Per-case detail
### <case id> - <title>
- Classification: <...>
- Evidence: <refs>
- Oracle results: <...>
- Reproduction: <command>

## Recovery and cleanup
<...>

## Recommendations
<...>
```
