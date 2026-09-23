# Test data

Rules:

- All fixtures are synthetic; canary markers are registered in
  `fixtures/canary-data/` before use.
- Fixtures are content-hashed; the fixture manifest (hash per file) is part
  of the run manifest so results are reproducible.
- No real secrets, no real user data, no production identifiers.
- Email/document fixtures are generated, not captured, from real mail.
- `fixtures/manifests/*.yaml` declare what each suite provisions and how it
  is cleaned up.
