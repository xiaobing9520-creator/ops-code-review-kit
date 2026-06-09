# Release Notes

## v1.8

**Release Date**: 2026-06-09

**Focus**: Replace alphabetical file sampling with Architecture-Role Pattern
Matching for better accuracy in reverse engineering, make module discovery
fully automatic (open-structure), and fix accumulated bugs from v1.75-v1.77.

### Background

v1.77 closed a depth gap in authentication tracing. However, two structural
problems and several accumulated bugs remained:

1. **File sampling accuracy** — Medium/Large codebases used alphabetical
   sampling ("first N files per package"), which misses architecturally critical
   files whose names sort later (e.g. `UserService.java` skipped in favour of
   `AbstractBaseConfig.java`). This caused the reverse-engineering output to
   omit key components, leading to downstream scan coverage gaps.

2. **Single-project lock-in** — The `steering.md` hardcoded a Canonical Module
   Manifest for one specific project (4 fixed modules). Using the kit on a
   different project required manually editing steering.md. This blocked
   portability and made the kit unsuitable for teams reviewing multiple
   codebases.

3. **Accumulated bugs** — README Quality Gate was out of sync with actual
   implementation; acceptance-report referenced non-existent file paths; auth
   tracing had no defined stopping condition.

### Changed files

| File | Change |
|------|--------|
| `.kiro/skills/codebase-reverse-engineering/skill.md` | New Step 0.4 (Architecture-Role Pattern Matching); updated D2.6, Scale table; 3-hop auth tracing limit; version bumped to v1.8 |
| `.kiro/steering.md` | Removed hardcoded module manifest; added auto-discovery rules + optional `module-manifest.md` override |
| `.kiro/skills/batch-scan/skill.md` | Module discovery uses auto-detection with manifest override fallback |
| `.kiro/skills/summary-report/skill.md` | Determinism guard updated for dynamic module count |
| `.kiro/skills/acceptance-report/skill.md` | Fixed prerequisites (now references Summary_Report); fixed appendix report paths |
| `README.md` | Complete rewrite — new sections for module discovery, scanning strategy, version history; fixed Quality Gate; removed hardcoded examples |
| `RELEASE_NOTES_1.8.md` | New |

---

### New Feature 1: Architecture-Role Pattern Matching

**Problem**: Alphabetical sampling selects files by name position, not by
architectural significance. A file named `AaaHelper.java` gets read while
`PaymentService.java` is skipped.

**Solution**: Two-tier pattern-based file selection:

**Tier 1 — Architecture-Role Files (always read):**

| Category | Patterns |
|----------|----------|
| API Layer | `*Controller`, `*Resource`, `*Handler`, `*Router`, `*Endpoint`, `*Resolver` |
| Business Logic | `*Service`, `*ServiceImpl`, `*UseCase`, `*Interactor`, `*Orchestrator`, `*Saga`, `*Workflow` |
| Data Access | `*Repository`, `*Mapper`, `*DAO`, `*Store`, `*DataSource` |
| Configuration | `*Config`, `*Configuration`, `*Properties`, `*Module`, `*Provider`, `*Registry` |
| Domain Model | `*Entity`, `*Model`, `*Aggregate`, `*ValueObject`, `*DTO`, `*VO` |
| Integration | `*Client`, `*Feign*`, `*Gateway`, `*Adapter`, `*Proxy`, `*Connector` |
| Security | `*Filter`, `*Interceptor`, `*Security*`, `*Auth*`, `*Guard`, `*Middleware` |
| Design Patterns | `*Factory`, `*Builder`, `*Strategy`, `*Listener`, `*Subscriber`, `*Observer`, `*Publisher` |

**Tier 2 — Alphabetical fill** (Medium codebases only): remaining budget
filled from non-matching files, sorted alphabetically.

**Budget rules:**

| Scale | Tier-1 | Tier-2 | Cap |
|-------|--------|--------|-----|
| Small (<50) | N/A — all files | N/A | No cap |
| Medium (50-500) | ALL matches | Fill to budget | 5/package |
| Large (>500) | ALL matches | None | 3/package (Tier-1 exceeding cap still read) |

**Why pattern matching over weighted scoring (fan-in)**: Scoring produces
continuous values with boundary-flip risk — a file at score 49.9 vs 50.1 can
swap between runs if one import line changes. Pattern matching is discrete
(match/no-match): same filenames = same selection = same output. No threshold
sensitivity.

---

### New Feature 2: Open Module Discovery

**Problem**: Kit was locked to one project's 4-module structure.

**Solution**:
- Auto-detect modules using build system metadata (Maven, Gradle, npm, Go,
  directory heuristic) — same logic previously in Step 0.3
- Sort alphabetically for determinism
- Optional `module-manifest.md` in project root overrides auto-detection
- When no manifest exists, the kit works on ANY project out of the box
- Reports formula: **(N x 2) + 1** where N = discovered modules

---

### Bug Fix 1: README Quality Gate Out of Sync

**Problem**: README stated "0 High issues" blocks release, but the actual gate
(since v1.75) only blocks on Critical or High+P0.

**Fix**: README now shows the shared Quality Gate matching steering.md and all
skill definitions.

---

### Bug Fix 2: Acceptance Report Path References

**Problem**: `acceptance-report/skill.md` referenced paths that don't exist:
- `code-review-artifacts/sonarqube-review/sonarqube-report.md`
- `code-review-artifacts/secure-coding-baseline-review/bsl-report.md`

Actual reports are at `code-review-artifacts/[Module]_*_Report_[date].md`.

**Fix**: Prerequisites now reference `Summary_Report_[date].md` (which
aggregates all per-module findings). Appendix links updated to match actual
output paths.

---

### Bug Fix 3: Auth Tracing Without Stopping Condition

**Problem**: v1.77 added "follow to leaf implementation" for auth tracing but
defined no hop limit. Deep call chains could produce non-deterministic results
depending on how far the model traces.

**Fix**: Added explicit **3-hop limit** — trace from entry point (filter/realm)
through at most 3 delegation levels. If the concrete implementation is not
found within 3 hops, record the deepest class reached and mark as
`Not Found — exceeded 3-hop trace limit`.

---

### Bug Fix 4: Skill Version Number Stale

**Problem**: `codebase-reverse-engineering/skill.md` title and all generated
artifact headers still showed "v1.7".

**Fix**: Updated to "v1.8" throughout — title, `**Generated by**` lines, and
completion message.

---

### Compatibility

- Determinism rules: **D2.6 updated** (pattern matching replaces alphabetical);
  D1-D5, D7 unchanged.
- Diagram rules, colour palette, arrow styles: unchanged from v1.76/v1.77.
- Output artifact filenames and directory layout: unchanged.
- All scan/review skills (sonarqube-review, secure-coding-baseline-review,
  security-review, rescan, rm-report-validator): unchanged in logic.
- Projects with an existing `module-manifest.md`: behaviour identical to old
  hardcoded manifest.
- Projects WITHOUT a manifest: now auto-detected (previously required manual
  steering edits).

### Migration from v1.77

1. Replace the `.kiro/` directory:
   ```bash
   rm -rf /path/to/target-project/.kiro
   cp -r ops-code-review-kit-1.8/.kiro /path/to/target-project/
   ```

2. (Optional) If your project previously relied on the hardcoded manifest and
   you want to keep a fixed module list, create `module-manifest.md` in the
   project root:
   ```markdown
   | # | Module | Path | Language | Notes |
   |---|--------|------|----------|-------|
   | 1 | my-backend | my-backend/ | Java | ... |
   | 2 | my-frontend | my-frontend/ | JS | ... |
   ```

3. Re-run `@codebase-reverse-engineering` then `@batch-scan` to regenerate
   all artifacts with the improved file selection strategy.

### Action required

Re-run `@codebase-reverse-engineering` to regenerate architecture artifacts.
The pattern-matching strategy will read different (more relevant) files than
the previous alphabetical approach, producing more accurate architecture
documentation on the first run.
