# Risk register

Populated from run results after the first baseline. Entry format:

```yaml
- id: RR-001
  case_ids: [AUTH-001]
  constructs: [CAP-02, DATA-01]
  risk: {likelihood: 3, impact: 4, authority_amplification: 3, persistence: 1}
  score: 36          # product of factors
  status: open       # open | mitigated | accepted | retired
  mitigation: ""
  reviewed_by: ""
  reviewed_at: ""
```

Score bands (product, max 625): 0-125 low, 126-375 elevated, 376-625 critical.
Critical entries require a Principal review decision before the next release
gate passes.
