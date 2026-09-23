# Security properties

| ID | Property | Requirement |
|---|---|---|
| P1 | Instruction integrity | Untrusted input cannot alter governing policy, tool permissions, approval status, or identity context |
| P2 | Provenance integrity | User requests, retrieved text, tool results, memory, policy, and verified approval remain distinguishable |
| P3 | Caller-bound authorization | Agent actions are constrained by the verified requesting principal's rights |
| P4 | Data isolation | Unauthorized users cannot obtain content, metadata, existence, citations, snippets, or derived facts |
| P5 | Action integrity | Tool calls are evaluated outside the model against caller, target, operation, parameters, purpose, and approval |
| P6 | Least privilege | Agent/tool/runtime identities have minimal scoped permissions |
| P7 | State integrity | Untrusted content cannot modify durable policy, config, tools, memory, or deployment state |
| P8 | Approval integrity | Approval is external to the model and bound to exact operation, parameters, target, user, and expiry |
| P9 | Egress integrity | Outbound destinations and data classes are policy controlled |
| P10 | Auditability and recovery | The system produces evidence for input, context, action, identity, result, persistence, and cleanup |

Every security property has at least one canonical case in `suites/` that
tests it, and at least one oracle that can verify its violation.
