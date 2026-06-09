# Release Notes

## v1.76

**Focus**: Fix incorrect architecture topology produced by the deterministic
reverse-engineering skill, while preserving v1.7's determinism guarantees.

### Background

v1.7 introduced strict determinism rules (D1–D7) and, in the process, replaced
the prescriptive architecture-diagram guidance that v1.65 had. On large
codebases this caused two problems:

- The architecture step no longer required investigating the admin/back-office
  security plane, so it was collapsed into the consumer gateway flow.
- The Large-scale "first 3 files alphabetically per package" sampling rule did
  not guarantee reading the files that prove request routing (frontend
  `.env*`/base-URL configs, gateway filters, Shiro/CSRF/MFA, internal-feign
  filter, reverse proxy, per-service Dockerfiles).

Net effect: a *consistently wrong* topology (admin SPA shown as routing through
the consumer gateway with gateway-token auth, instead of a separate Shiro-based
admin plane behind nginx).

### Changed files

| File | Change |
|------|--------|
| `.kiro/skills/codebase-reverse-engineering/skill.md` | Restored prescriptive architecture/diagram guidance and added mandatory trust-boundary investigation. Grew from 828 to 1311 lines. |

No other skills, rules, or steering files were modified.

### What changed in the reverse-engineering skill

1. **New Step 1.7 — Trust Boundary & Routing Discovery (REQUIRED, overrides
   sampling)**
   Even on Large codebases, the skill must now read, before drawing data flows:
   - frontend/client API base config (`.env*`, `baseUrl.*`, `request.*`,
     `api/index.*`)
   - API gateway routes and global filters (auth, CORS, referer, XSS)
   - admin security stack (Shiro/Spring Security, realm, login filter, session
     store, CSRF, MFA, login rate-limit/lockout, HMAC internal-feign filter +
     request interceptor)
   - reverse proxy / ingress prefix routing
   - per-service container base images (each `Dockerfile`)

2. **Architecture diagrams — restored four-diagram specification**
   Replaced the thin single `graph LR` guidance with the full prescriptive spec:
   - Global diagram rules + `classDef` colour palette + arrow-style legend
   - Diagram 1 — System Context (layered tiers)
   - Diagram 2 — Consumer-Plane Microservice Map
   - Diagram 3 — Admin-Plane Detail (conditional; separate security plane)
   - Diagram 4 — Authentication Flows (conditional)
   - Added a determinism note: diagram rules govern *layout*; *content* remains
     governed by D1–D7, derived only from facts in the code (no invented nodes).
   - Added a rule to route each client to the edge node it ACTUALLY calls,
     instead of assuming all traffic transits the gateway.

3. **Step 8 self-validation checklist — extended**
   Added topology/diagram checks: four diagrams in the prescribed order;
   `flowchart TB` layered layout; standard `classDef` palette; consistent arrow
   styles; and a mandatory check that an admin plane with its own auth stack
   appears as a SEPARATE plane (not routed through the consumer gateway).

### Compatibility

- Determinism rules D1–D7 are unchanged; tabular artifacts (counts, sorted
  tables) remain deterministic.
- Output artifact filenames and directory layout are unchanged.

### Action required

Re-run `@codebase-reverse-engineering` to regenerate `architecture.md` and
`architecture-preview.html` with the corrected two-plane topology. Existing
generated artifacts under `code-review-artifacts/reverse-engineering/` are not
updated automatically.
