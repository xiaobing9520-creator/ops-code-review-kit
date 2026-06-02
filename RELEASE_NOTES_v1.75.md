# Release Notes — v1.75

**Release Date**: 2026-06-02

## Summary

v1.75 merges client-side improvements from v1.65 into the v1.7 deterministic
baseline. It combines the v1.7 deterministic reverse engineering + HTML diagram
generation with v1.65's quality gate recalibration, R&M report validator,
rule set refinement, and deterministic module/priority policies.

**Lineage**: v1.6 → v1.65 (client) + v1.7 (ops team) → **v1.75** (merged)

---

## What's New (from v1.65 merge)

### 1. New Skill: @rm-report-validator

A dedicated validation skill that checks R&M reports against SonarQube rule
definitions. 5 validation checks:

| Check | Purpose |
|-------|---------|
| V-01 | Rule Existence — every rule ID must exist in standards file |
| V-02 | Severity Mapping — must match standards file exactly |
| V-03 | Rule Description — must match actual rule title |
| V-04 | Quality Gate Recalculation — recompute after corrections |
| V-05 | Appendix Labeling — invalid findings properly labeled |

Includes a **Known Rule Pitfalls** table documenting 7 historically misused
rule IDs (e.g., `javascript:S106` does not exist, `java:S2115` is Blocker not High).

### 2. Quality Gate Recalibrated (R&M Reports)

| Criteria | v1.6 / v1.7 | v1.75 |
|----------|-------------|-------|
| Critical issues | Blocks (any priority) | Blocks (any priority) |
| High issues | **All block** | **Only P0 blocks** |
| Medium issues with P0 | **Blocks** | **No longer blocks** |

**Rationale**: Not all High-severity bugs are release-blocking. The gate now
mirrors the Security report logic — only P0-priority issues at Critical/High
block the release. Medium issues are tracked for remediation planning only.

### 3. Canonical Module Manifest (in steering.md)

A fixed, authoritative module list that eliminates module-discovery drift:

```
| 1 | lab-backend        | lab-backend/        | Java   |
| 2 | lab-manage-backend | lab-manage-backend/ | Java   |
| 3 | lab-admin-web      | lab-admin-web/      | JS/Vue |
| 4 | lab-wxapp          | lab-wxapp/          | JS     |
```

Rules:
- Never re-derive modules from build files at scan time
- Sub-projects are aggregated into their parent module (not split)
- Guarantees 4 modules → 9 reports on every run

### 4. Deterministic Fix Priority Decision Table

Priority is now a pure function (no human judgment):

| Condition | Priority |
|-----------|----------|
| Severity = Critical | P0 |
| Severity = High AND domain ∈ {Injection, Authn/Authz, Access control, Secrets, Vulnerable components} | P0 |
| Severity = High (other) | P1 |
| Severity = Medium AND (data exposure OR correctness OR injection-adjacent) | P1 |
| Severity = Medium (other) | P2 |
| Severity = Low | P3 |

### 5. Rule Set Recalibration

| Standards File | v1.6 / v1.7 | v1.75 | Change |
|----------------|-------------|-------|--------|
| Java (SonarQube) | 394 rules | 343 rules | -51 (security-only rules removed from R&M scope) |
| JavaScript (SonarQube) | 261 rules | 232 rules | -29 (security-only removed; High severity tier added) |
| BSL 11.1.1.d | 230 controls | 230 controls | No change |

### 6. Finding Header Enforcement Strengthened

The 4-line unified finding header is now marked **NON-NEGOTIABLE** with:
- Explicit formatting rule: standalone lines, NOT list items (no `- ` prefix)
- SELF-CHECK instruction: verify all 4 lines before writing each finding
- CVSS Score is MANDATORY in Security reports (never omit)

### 7. Determinism & Reproducibility Policy (in steering.md)

Six determinism rules added at the steering level (complementing v1.7's D1-D7
in the reverse engineering skill):

1. Fixed module set (Canonical Manifest)
2. One finding per rule/control per module (aggregate instances)
3. Table-driven severity (no judgment)
4. Deterministic fix priority (Decision Table)
5. Stable ordering & numbering (severity → Rule ID → file path)
6. No discretionary prose

### 8. Enhanced Self-Validation in @sonarqube-review

Step 4 (Self-Validation) now embeds full V-01 through V-05 logic inline,
including specific error patterns to watch for. Runs before report generation,
not after.

### 9. Summary Report Determinism Guard

Before aggregating, `@summary-report` now checks that the module report set
matches the Canonical Manifest exactly. Mismatches are reported instead of
silently summarized.

---

## What's Retained (from v1.7)

All v1.7 features remain unchanged:

| Feature | Status |
|---------|--------|
| Determinism Rules D1-D7 in @codebase-reverse-engineering | Retained |
| architecture-preview.html generation (Mermaid → browser) | Retained |
| Deterministic file manifest + sorted tables | Retained |
| Factual-only output (no subjective assessments) | Retained |
| Scale-based scope rules (Small/Medium/Large) | Retained |
| Self-validation checklist (Step 8) | Retained |
| solution-architecture.drawio | Retained |

---

## Files Changed (vs v1.7)

| File | Action |
|------|--------|
| `.kiro/steering.md` | Merged (v1.65 base + v1.7 HTML artifact line) |
| `.kiro/skills/rm-report-validator/skill.md` | **New** (from v1.65) |
| `.kiro/skills/sonarqube-review/skill.md` | Replaced (v1.65 — new QG + validator) |
| `.kiro/skills/secure-coding-baseline-review/skill.md` | Replaced (v1.65 — header enforcement) |
| `.kiro/skills/batch-scan/skill.md` | Replaced (v1.65 — manifest + validator) |
| `.kiro/skills/summary-report/skill.md` | Replaced (v1.65 — determinism guard) |
| `.kiro/skills/rescan/skill.md` | Replaced (v1.65 — new QG + validator) |
| `.kiro/skills/security-review/skill.md` | Replaced (v1.65 — header enforcement) |
| `.kiro/rules/sonarqube-java-standards.md` | Replaced (v1.65 — 343 rules) |
| `.kiro/rules/sonarqube-javascript-standards.md` | Replaced (v1.65 — 232 rules) |
| `.kiro/skills/codebase-reverse-engineering/skill.md` | **Unchanged** (v1.7) |
| `architecture-preview.html` | **Unchanged** (v1.7) |
| `solution-architecture.drawio` | **Unchanged** (v1.7) |
| `RELEASE_NOTES_v1.75.md` | **New** |

---

## Migration from v1.7

Replace the entire `.kiro/` directory plus rule files:

```bash
rm -rf /path/to/target-project/.kiro
cp -r ops-code-review-kit/.kiro /path/to/target-project/
```

After upgrading, re-run `@codebase-reverse-engineering` then `@batch-scan`
to regenerate all artifacts under the new quality gate and rule set.

---

## Compatibility

- Kiro IDE: All versions
- pandoc: 2.x or 3.x (for Word output)
- Previous scan reports: Compatible with `@rescan` workflow
- Browser: Any modern browser for architecture-preview.html (Edge, Chrome, Firefox)
