# Assessment modes

Black-box, grey-box, and white-box modes are defined in the methodology
(section 4.4, [aasm-ea.md](aasm-ea.md)). Summary:

| Mode | Inputs | Use | Limitation |
|---|---|---|---|
| Black box | user/channel access + controlled test resources | external behavior, injection, cross-user, egress | limited identity/tool/policy visibility |
| Grey box | + app manifest, config, permission inventory, logs/traces | **recommended enterprise mode** | may not expose implementation bugs |
| White box | + source, prompts, tool router, memory/retrieval code, IaC | static/dynamic review, taint paths, CI, instrumentation | requires owner collaboration |

A case declares the modes it is valid under in `assessment_modes`; the runner
refuses to run a case in a mode the case does not support.
