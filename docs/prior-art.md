# Prior art

Initial prior-art map. Verify latest versions and citation details before
publication.

## Frameworks and cheat sheets
- OWASP AI Agent Security Cheat Sheet
- OWASP LLM Prompt Injection Prevention Cheat Sheet
- NIST AI RMF and NIST AI 600-1 Generative AI Profile
- MITRE ATLAS

## Agentic AI failure taxonomy
- Microsoft AI Red Team: *Taxonomy of Failure Modes in Agentic AI Systems*

## Evaluation environments
- InjecAgent: indirect prompt injection in tool-integrated agents
- AgentDojo: dynamic prompt-injection evaluation environment
- Agent Security Bench (ASB)
- ToolEmu: risk evaluation for tool-using language agents
- AgentHarm: harmful multi-step agent tasks
- R-Judge: agent safety-risk awareness evaluation

## Foundations
- Formal work on task alignment, action alignment, source authorization, and
  data isolation for LLM agents.

## Enterprise identity plumbing (target profile)
- Microsoft Teams bot SSO, Teams app permissions, Resource-Specific Consent
- Entra delegated / on-behalf-of / application / managed-identity permission
  models

## Relationship to ElicitSec

ElicitSec differs from jailbreak benchmarks by evaluating the full trajectory
(instructions -> data -> actions -> privileges -> state) with deterministic
environmental evidence, caller-bound authorization, and paired utility
controls, rather than scoring model text alone.
