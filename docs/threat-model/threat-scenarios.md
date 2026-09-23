# Threat scenarios

Canonical scenario chains (construct -> boundary -> property):

| Scenario | Chain | Boundary | Property at risk |
|---|---|---|---|
| Chat-override | OBJ-01 + CTX-01 | TB-01 | P1 |
| Retrieval poisoning | CTX-02 + OBJ-02 | TB-02 | P2, P1 |
| Provenance laundering | CTX-06 + DATA-02 | TB-02 | P2, P4 |
| Confused deputy | CAP-01/02 + DATA-01 | TB-03, TB-04 | P3, P4 |
| Approval forgery | OBJ-04 + CHAIN-02 | TB-07 | P8 |
| Memory poisoning | CTX-05 + STATE-02 | TB-05 | P7, P2 |
| Egress exfiltration | DATA-04 (+ CTX-*) | TB-06 | P9 |
| Persistent config tamper | STATE-03/04 | TB-05 | P7, P6 |
| Multi-turn shaping | CTX-07 + CHAIN-01 | TB-01/04 | P1, P5 |

Each row maps to one or more cases in `suites/`.
