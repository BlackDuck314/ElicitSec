# Trust boundaries

From the OpenClaw enterprise profile (methodology section 5.3):

| Boundary | Flow | Primary threats | Required property |
|---|---|---|---|
| TB-01 | Teams sender -> agent | direct injection, authority spoofing, group-context confusion | instruction integrity |
| TB-02 | retrieved content -> context | indirect injection, knowledge-base poisoning, provenance loss | provenance integrity |
| TB-03 | agent -> data source | cross-user access, semantic leakage, broad retrieval | caller-bound authorization, data isolation |
| TB-04 | agent -> tool | tool abuse, parameter escalation, action chaining | action integrity |
| TB-05 | agent -> state | memory/soul/config/tool mutation | state integrity |
| TB-06 | agent -> egress | exfiltration, unauthorized communications | egress integrity |
| TB-07 | agent -> human approval | approval forgery/reuse/substitution | approval integrity |

System context diagram (target profile) is in the methodology, section 5.2.
