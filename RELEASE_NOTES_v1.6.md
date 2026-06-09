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

## Appendix: Severity & Priority Classification Logic

### Two Orthogonal Dimensions

| Dimension | Source | Question It Answers |
|-----------|--------|---------------------|
| **Severity** (Risk Level) | CVSS v3.1 Base Score (8 metrics) | "If exploited, how bad is the impact?" |
| **Priority** (Fix Priority) | Business context judgment | "How urgently must this be fixed?" |

These dimensions are independent. A finding can be High severity but P2 priority
(serious but not urgent), or Medium severity but P0 priority (limited blast
radius but on a critical business path).

### Severity Classification

Derived from CVSS v3.1 score calculation (Attack Vector, Attack Complexity,
Privileges Required, User Interaction, Scope, Confidentiality/Integrity/Availability):

| Severity | CVSS Range | Meaning |
|----------|-----------|---------|
| **Critical** | 9.0 – 10.0 | Trivially exploitable, catastrophic impact |
| **High** | 7.0 – 8.9 | Exploitable with some conditions, serious impact |
| **Medium** | 4.0 – 6.9 | Exploitation requires specific preconditions (local access, user interaction, etc.) |
| **Low** | 0.1 – 3.9 | Limited impact even if exploited |

For R&M reports (non-security), severity maps from SonarQube rule definition:
Blocker → Critical, High → High, Medium → Medium.

### Priority Classification

Assigned based on business context, deployment environment, and fix cost:

| Priority | Meaning | Typical Scenarios |
|----------|---------|-------------------|
| **P0** | Must fix before release | On critical path (auth/payment), compliance-mandated, trivial to fix |
| **P1** | Fix within 1–2 weeks | High risk but mitigated by other controls, not blocking release |
| **P2** | Fix within 1 month | Some risk, acceptable short-term given other safeguards |
| **P3** | Long-term optimization | Minimal practical risk, technical debt |

### Why Medium + P0 Exists

A CVSS Medium (4.0–6.9) means exploitation requires preconditions — the
vulnerability is not trivially exploitable. But P0 can still apply when:

- The vulnerable code sits on a critical business path (e.g., payment, admin)
- Compliance explicitly requires the control regardless of CVSS
- The fix is trivial (no reason to carry the risk into production)
- Deployment context amplifies the real-world risk beyond what base CVSS reflects

### Quality Gate Logic by Report Type

| Report | Gate Criteria | Rationale |
|--------|--------------|-----------|
| **R&M** | Critical=0, High=0, Medium(P0)=0 | Bugs are deterministic — a resource leak or null pointer WILL fire in production, no "exploitation conditions" buffer |
| **Security** | Critical=0, High(P0)=0 | Security Medium has inherent exploitation preconditions (CVSS guarantees this); even P0 Medium is trackable post-release. High without P0 means serious but mitigated/deferrable. |

**In short**: R&M defects are certainties (will happen), security defects are
probabilities (may happen given conditions). The gate reflects this difference.

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
