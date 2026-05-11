# Release Notes — v1.6

**Release Date**: 2026-05-11

## Summary

v1.6 refines the scanning scope, updates quality gates, improves report
formatting consistency, adds AI-generated fix code to findings, and introduces
Word (.docx) output format as the final deliverable.

---

## Changes

### 1. R&M Report: Security Rules Excluded

The Reliability & Maintainability report (`@sonarqube-review`) no longer scans
security-category rules (`javasecurity:*`, `jssecurity:*`). Security scanning is
performed exclusively by the dedicated Security report
(`@secure-coding-baseline-review`), avoiding duplication and scope overlap.

### 2. R&M Report: Code Smell Rules Excluded

Code Smell (maintainability smell) rules are no longer scanned. The R&M report
now focuses solely on **Bug** category rules — issues that affect program
correctness and reliability.

### 3. Security Report: Updated Quality Gate

The Security report quality gate has been revised:

| Criteria | v1.5 | v1.6 |
|----------|------|------|
| Critical issues | 0 | 0 |
| High issues | 0 | **Only P0-priority High issues block** |
| Medium issues with P0 | Blocks | **No threshold (tracked only)** |

This change acknowledges that not all High-severity security findings are
release-blocking — only those rated P0 (must-fix-before-release) trigger a Fail.

### 4. Security Report: Section 4 Format Aligned with R&M Report

The previous "BSL Compliance Summary" section (with "Compliance rate" metric)
has been replaced with "Rule Coverage" — the same format used in the R&M report:

```
| Metric | Value |
|--------|-------|
| Total BSL controls | 230 |
| Controls checked | [n] |
| Controls with findings (Fail) | [n] |
| Controls passed (Pass) | [n] |
| Controls not applicable (N/A) | [n] |
```

### 5. Summary Report: Removed Server-Side Security Caveat

The statement "本次审查未评估服务端安全控制" (or its English equivalent) is no
longer included in the Summary report. The BSL security scan covers all
applicable controls including server-side aspects — no additional disclaimer
is needed.

### 6. All Reports: AI-Suggested Fix Code

Every finding now includes a **"Suggested Fix Code (AI-generated)"** section
after the Fix Recommendation. This provides a concrete code-level correction
that development teams can reference directly.

Format:
```
**Suggested Fix Code (AI-generated)**:
```java
// Corrected code
```
> If no code-level fix can be demonstrated: "N/A — requires architectural or configuration change."
```

### 7. Word (.docx) Output Format

Reports are now generated in **both Markdown and Word format**. After all
Markdown reports are complete, `pandoc` is used to convert each `.md` file to
`.docx`. This provides a stakeholder-ready deliverable without requiring
recipients to use Markdown-aware tools.

**Prerequisite**: `pandoc` must be installed in the review environment.
If unavailable, the scan completes normally and Word conversion is skipped
with a notification.

---

## Migration from v1.5

No manual migration required. Simply replace the `.kiro/` directory in your
target project with the v1.6 version:

```bash
rm -rf /path/to/target-project/.kiro
cp -r ops-code-review-kit/.kiro /path/to/target-project/
```

## Compatibility

- Kiro IDE: All versions
- pandoc: 2.x or 3.x (for Word output)
- Previous scan reports: Compatible with `@rescan` workflow
