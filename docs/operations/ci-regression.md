# CI regression

Pipeline tiers (methodology section 15):

| Pipeline tier | Cases | Environment |
|---|---|---|
| PR / unit | schema validation, adapter contract tests, oracle tests, fixture checks | local/container |
| Safe regression | tier 0-1 canonical cases | isolated staging / direct API mock |
| Integration regression | tier 1-2 Teams/Work IQ/Graph cases | dedicated test tenant |
| Scheduled full run | tier 0-4, controlled state/egress | dedicated isolated rig |
| Manual high-consequence | tier 4-5 only if approved | separate isolated environment |

Change-triggered suites: see methodology section 15.2 (model/prompt changes
trigger direct-injection + utility; retrieval changes trigger RAG/provenance;
tool changes trigger tool-policy; Teams/Entra changes trigger identity suites;
memory changes trigger persistence; runtime/IaC changes trigger
filesystem/state/egress).
