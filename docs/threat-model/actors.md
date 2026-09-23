# Actors

Test identities are defined in `data/test-identities/` and the methodology
(section 9.1). Roles in the enterprise profile:

- **user_a_authorized** - has access to a defined test document/resource.
- **user_b_unauthorized** - explicitly denied access to the same resource.
- **guest_or_low_trust_user** - optional, where tenant policy allows.
- **test_operator** - runs the test and observes audit evidence.
- **agent_identity** - the agent's application/managed/runtime identity with
  intentionally minimal test permissions.

Adversarial actors are not a separate identity class: the attacker is always
an existing principal (user B, a group member, a sender of retrieved content)
whose *content* is attacker-controlled. This keeps identity semantics real.
