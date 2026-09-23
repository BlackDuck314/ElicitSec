# Terminology

| Term | Definition |
|---|---|
| Elicitation case | A versioned experiment: target behavior, authorized context, attacker perturbation, protected invariants, evidence plan, paired utility control, safety constraints. |
| Construct | A named threat construct (OBJ/CTX/CAP/STATE/CHAIN/DATA-*), see `taxonomy/constructs.yaml`. |
| Consequence tier | Ordered scale (0-5) of the most consequential operation a case may perform; drives approval gates. |
| Utility control | The legitimate equivalent of an adversarial case; measures overrefusal and utility under attack. |
| Canary | A synthetic asset with a unique marker used as a deterministic proof target. |
| Oracle | A deterministic checker over environmental evidence. Never the model. |
| Semantic judge | A model-based rubric evaluator. May label SEMANTIC_FAILURE, never REALIZED_HARM. |
| IDAPS | Instructions, Data, Actions, Privileges, State - the core failure model. |
| AASM-EA | Agentic Application Security Methodology: Enterprise Agent profile. |
| RoE | Rules of engagement: scope, identities, stop conditions, safe-target register. |
| Safe-target register | Allowlist of synthetic targets a case may touch. |
| Run manifest | Structured per-run record (classification, evidence refs, versions). |
