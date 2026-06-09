# Release Notes

## v1.77

**Focus**: Make the deterministic reverse-engineering skill capture
security-critical authentication *internals* (password-hashing scheme and
token/session issuance) reproducibly, closing a depth gap observed between the
v1.65 and v1.7/v1.76 outputs.

### Background

v1.76 fixed architecture *topology* (separate admin plane vs consumer gateway).
A follow-up comparison of two runs over the same codebase (v1.65 vs
v1.7/v1.76) surfaced a remaining **depth** gap — not a contradiction, but
missing verifiable facts:

- The admin credential-hashing algorithm (**BCrypt**, in
  `SecurityUtil.matchesPassword → BCryptPasswordEncoder`) was omitted; the run
  stopped at the Shiro realm / `MyCredentialsMatcher` and never followed the
  delegation into the encoder.
- The consumer login/token-minting flow (token created in
  `TokenService.createToken`, `login_tokens:` Redis key, **TTL 10 min**) was
  omitted; only the steady-state token *validation* path was documented.

Root cause: Step 1.7 mandated reading the auth framework config, realm, login
filter, CSRF interceptor, and internal-feign filter — but it did **not** require
following those references one hop further into the concrete class that hashes
the password or mints the token. The v1.7 determinism rules govern layout and
sorting, not call-chain depth, so two runs could legitimately differ in how deep
they traced auth internals.

### Changed files

| File | Change |
|------|--------|
| `.kiro/skills/codebase-reverse-engineering/skill.md` | Added a leaf-implementation requirement for authentication internals (Step 1.7, pre-diagram investigation, Diagram 4 rules, Step 8 checklist). |

No other skills, rules, or steering files were modified.

### What changed in the reverse-engineering skill

1. **Step 1.7 — Trust Boundary & Routing Discovery: new "follow to leaf" rule**
   Added item 6 requiring each authentication mechanism to be traced to its
   **leaf implementation**, with file-path evidence, overriding Large-codebase
   sampling:
   - **Password storage** — the concrete hashing scheme (BCrypt / Argon2 /
     PBKDF2 / scrypt / plain / MD5 / SHA). Naming the realm/matcher class is not
     sufficient; follow the `CredentialsMatcher`/`PasswordEncoder`/login-service
     chain into the method that hashes or verifies the credential.
   - **Token / session issuance** — the minting method, store and key prefix,
     TTL/expiry, and token composition (opaque UUID, JWT, `md5(openId)+uuid`).
     Follow the service that CREATES the token, not only the validating filter.
   - **MFA / second factor** — the algorithm (TOTP/HOTP/SMS-OTP) and secret
     storage location.

2. **MANDATORY pre-diagram investigation — added auth leaf item**
   Mirrored the above at diagram time: the concrete password-hashing class and
   the token/session issuance service must be read before drawing, and the facts
   must appear in Diagram 4 and the Component Catalog.

3. **Diagram 4 — Authentication Flows: issuance + algorithm now required**
   - Token/session **issuance is mandatory when present** (endpoint, store, key,
     TTL, token composition) — a diagram showing only validation is incomplete.
   - The credential-hashing algorithm must be **labelled on the login step**.

4. **Step 8 self-validation checklist — extended**
   Added three authentication-depth checks:
   - Password storage mechanism named with file-path evidence (the
     `PasswordEncoder`/`CredentialsMatcher` implementation), or `Not Found`.
   - For every token/session type: issuance step, store key, and TTL recorded
     with evidence (the creating service, not only the validating filter), or
     `Not Found`.
   - Diagram 4 includes the issuance step and labels the hashing algorithm.

### Compatibility

- Determinism rules D1–D7 are unchanged; tabular artifacts remain deterministic.
- Diagram layout, colour palette, arrow styles, and the four-diagram order from
  v1.76 are unchanged.
- Output artifact filenames and directory layout are unchanged.
- More accurate quantitative facts (e.g. exact controller counts, gateway route
  tables) are still preferred over approximations.

### Action required

Re-run `@codebase-reverse-engineering` to regenerate `architecture.md` and
`architecture-preview.html` so that the admin password-hashing scheme (e.g.
BCrypt) and the consumer token/session issuance flow (key + TTL) are captured.
Existing generated artifacts under `code-review-artifacts/reverse-engineering/`
are not updated automatically.

### Note for kit maintainers

These edits were applied to the skill copy in this project's `.kiro/`. If the
master kit (`ops-code-review-kit`) is maintained separately, port the same four
edits there so future projects inherit the behaviour.
