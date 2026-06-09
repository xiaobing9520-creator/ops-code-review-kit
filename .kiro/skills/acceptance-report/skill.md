---
name: acceptance-report
description: >
  Generates the final acceptance decision report by aggregating findings from
  security review and optional SonarQube/BSL reports. Produces a
  Pass/Conditional/Reject decision with supporting evidence and remediation
  requirements.
---

# Acceptance Report

You are the operations team's chief reviewer making the final acceptance
decision. Your job is to aggregate all review findings into a single,
actionable report that clearly states whether this codebase is ready for
operations acceptance.

## Prerequisites

ALL of the following reports MUST exist before running this skill:
- `code-review-artifacts/reverse-engineering/analysis-summary.md`
- `code-review-artifacts/Summary_Report_[date].md` (from `@batch-scan` or `@summary-report`)

The following reports are OPTIONAL but strongly recommended:
- `code-review-artifacts/security-review/security-report.md` (from `@security-review` — deep OWASP/CWE analysis)

If `Summary_Report` is missing, instruct the user to run `@batch-scan` first.
The Summary Report already aggregates all R&M and Security (BSL) findings per
module, so separate sonarqube-review or bsl-report files are NOT required as
prerequisites — their content is captured in the per-module reports that feed
the summary.

If the optional `@security-review` report exists, incorporate its deeper
OWASP/CWE findings into the acceptance decision alongside the BSL findings.

## Output

`code-review-artifacts/acceptance-report.md`

## Report Generation Process

### Step 1: Collect All Findings

1. Read the security review report
2. Read the SonarQube review report (if it exists)
3. Read the BSL compliance report (if it exists)
4. Read the reverse engineering analysis summary
5. Extract from each report:
   - Rating/score
   - Finding counts by severity
   - Critical and High findings list
   - Key metrics

### Step 2: Aggregate Metrics

Compile a unified metrics dashboard:

| Dimension | Score | Critical | High | Medium | Low |
|-----------|-------|----------|------|--------|-----|
| Security | [from security report] | | | | |
| SonarQube (if applicable) | [from sonarqube report] | | | | |
| BSL Compliance (if applicable) | [from bsl report] | | | | |

### Step 3: Calculate Composite Score

Apply dimension weights to calculate an overall score:

Apply dimension weights to calculate an overall score.

When SonarQube + BSL reports are **both available**:

| Dimension | Weight | Score | Weighted |
|-----------|--------|-------|----------|
| Security (OWASP/CWE) | 40% | [n] | [n] |
| SonarQube (R&M) | 30% | [n] | [n] |
| BSL Compliance | 30% | [n] | [n] |
| **Composite** | **100%** | | **[n]** |

When only Security report is **available**:

| Dimension | Weight | Score | Weighted |
|-----------|--------|-------|----------|
| Security (OWASP/CWE) | 100% | [n] | [n] |
| **Composite** | **100%** | | **[n]** |

When Security + SonarQube (no BSL):

| Dimension | Weight | Score | Weighted |
|-----------|--------|-------|----------|
| Security (OWASP/CWE) | 50% | [n] | [n] |
| SonarQube (R&M) | 50% | [n] | [n] |
| **Composite** | **100%** | | **[n]** |

When Security + BSL (no SonarQube):

| Dimension | Weight | Score | Weighted |
|-----------|--------|-------|----------|
| Security (OWASP/CWE) | 50% | [n] | [n] |
| BSL Compliance | 50% | [n] | [n] |
| **Composite** | **100%** | | **[n]** |

### Step 4: Apply Acceptance Decision Rules

Apply the following rules IN ORDER (first matching rule determines decision):

**REJECT if any of these are true:**
- Any Critical security finding (CWE Top 5, hardcoded secrets, etc.)
- Any Critical SonarQube Blocker finding in security category
- Total Critical findings across all reports > 0
- Total High findings across all reports > 10
- Any single dimension score < 40
- Security dimension score < 50

**CONDITIONAL ACCEPT if any of these are true:**
- High findings: 4-10 total
- Any single dimension score between 40-60
- Composite score between 50-70
- Missing external tool scan data (SCA/SAST)
- SonarQube review not performed for a Java/JS project
- Test coverage assessed as "Insufficient" or "None"

**ACCEPT if all of these are true:**
- No Critical findings across all reports
- High findings <= 3 total
- All dimension scores >= 70
- Composite score >= 70

### Step 5: Define Remediation Requirements

For Conditional Accept and Reject:

1. List all Critical and High findings that must be fixed
2. Group findings by responsible area (security, reliability, etc.)
3. Prioritize by severity and impact
4. Specify remediation deadline:
   - Critical: Must fix before re-submission
   - High: 30-day remediation window (for Conditional Accept)
5. Specify re-review scope:
   - Full re-review: if Reject
   - Targeted re-review: if Conditional Accept (only affected dimensions)

### Step 6: Generate Acceptance Report

Create `code-review-artifacts/acceptance-report.md`:

```markdown
# Code Acceptance Review Report

**Review Date**: [date]
**Project**: [project name from analysis-summary.md]
**Codebase Scale**: [from analysis-summary.md]
**Reviewer**: Kiro AI Code Review System

---

## ACCEPTANCE DECISION: [ACCEPT / CONDITIONAL ACCEPT / REJECT]

[One paragraph explaining the decision rationale]

---

## Composite Score

| Dimension | Weight | Score | Weighted | Rating |
|-----------|--------|-------|----------|--------|
| Security (OWASP/CWE) | [w]% | [n]/100 | [n] | [Excellent/Good/Fair/Poor] |
| SonarQube (R&M) | [w]% | [n]/100 | [n] | [Excellent/Good/Fair/Poor] / N/A |
| BSL Compliance | [w]% | [n]/100 | [n] | [Excellent/Good/Fair/Poor] / N/A |
| **Composite** | **100%** | | **[n]/100** | **[rating]** |

> Note: Weights adjust based on which reports are available. See Step 3 for weight tables.

## Findings Summary

| Severity | Security (OWASP/CWE) | SonarQube (R&M) | BSL Compliance | Total |
|----------|---------------------|-----------------|----------------|-------|
| Critical | [n] | [n] | [n] | [n] |
| High | [n] | [n] | [n] | [n] |
| Medium | [n] | — | [n] | [n] |
| Low | [n] | — | [n] | [n] |
| **Total** | **[n]** | **[n]** | **[n]** | **[n]** |

> Note: SonarQube findings only have Critical (Blocker) and High severity levels.
> Columns show "—" or N/A if that report was not applicable.

## Key Metrics

| Metric | Value | Standard | Status |
|--------|-------|----------|--------|
| Vulnerability Density | [n]/KLOC | < 0.5/KLOC | Pass/Fail |
| CVSS Max Score | [n] | < 7.0 (no Critical) | Pass/Fail |
| CVE Matches | [n] | 0 unmitigated | Pass/Fail |
| SonarQube Blocker Count | [n] | 0 | Pass/Fail / N/A |
| BSL Compliance Rate | [n]% | >= 90% | Pass/Fail / N/A |

## Data Completeness

| Data Source | Status | Impact on Decision |
|------------|--------|-------------------|
| Kiro AI Code Analysis | Completed | Primary data source |
| SonarQube Rule Review | Completed / Not Applicable / Not Provided | [impact] |
| BSL 11.1.1.d Compliance | Completed / Not Provided | [impact] |
| SCA Scan (Trivy) | Completed / Not Provided | [impact] |
| SAST Scan (Semgrep) | Completed / Not Provided | [impact] |
| IaC Scan (Checkov) | Completed / Not Provided | [impact] |
| Test Coverage Report | Completed / Not Provided | [impact] |

## Critical & High Findings Requiring Remediation

[List ALL Critical and High findings from all available reports. For each:]

### [ID] [Finding Title] — [Report Source]
- **Severity**: Critical / High
- **Location**: `[file:line]`
- **Issue**: [Brief description]
- **Required Action**: [What must be done]
- **Deadline**: Before re-submission / Within 30 days

## Report Highlights

### Security (OWASP/CWE)
[2-3 sentence summary of security review findings — CVSS scores, CVE matches, key concerns]

### SonarQube R&M (if applicable)
[2-3 sentence summary of SonarQube rule-based review findings. Note the
SonarQube compliance rate and any Blocker-level violations found.]

### BSL Compliance (if applicable)
[2-3 sentence summary of BSL 11.1.1.d Secure Coding Baseline compliance.
Note overall compliance rate, number of non-compliant controls, and top
security domains with gaps.]

## Remediation Plan (if Conditional Accept or Reject)

### Required Before Acceptance
| # | Finding ID | Description | Report Source | Priority |
|---|-----------|-------------|---------------|----------|
| 1 | [id] | [desc] | [source] | [1-Critical/2-High] |

### Required Within 30 Days (Conditional Accept only)
| # | Finding ID | Description | Report Source | Priority |
|---|-----------|-------------|---------------|----------|
| 1 | [id] | [desc] | [source] | [priority] |

### Re-Review Scope
- **Re-review type**: Full / Targeted
- **Dimensions to re-review**: [list]
- **Estimated re-review effort**: [description]

## Standards Compliance Summary

| Standard | Compliance Status |
|----------|------------------|
| OWASP Top 10 (2021) | [n]/10 categories checked, [n] issues found |
| CWE Top 25 (2025) | Top 5 blocking checks performed |
| CVSS v3.1 | All findings scored with vector strings |
| NIST SSDF PW.7 | Code review performed (this report) |
| SonarQube Rules | [n]% compliance ([n] violations / [n] applicable rules) or N/A |
| BSL 11.1.1.d | [n]% compliance ([n] non-compliant / [n] applicable controls) or N/A |

## Appendix: Detailed Reports

For full findings and technical details, refer to:
- [Summary Report](Summary_Report_[date].md) — all modules aggregated
- Per-module R&M reports: `[Module]_Reliability_Maintainability_Report_[date].md`
- Per-module Security reports: `[Module]_Security_Report_[date].md`
- [Security Review](security-review/security-report.md) (if `@security-review` was run)
- [Architecture Documentation](reverse-engineering/architecture.md)
```

## Completion Message

```
============================================
  Code Acceptance Review Complete
============================================

DECISION: [ACCEPT / CONDITIONAL ACCEPT / REJECT]

Composite Score: [n]/100
  - Security (OWASP/CWE): [n]/100 (weight [w]%)
  - SonarQube (R&M):      [n]/100 (weight [w]%) [or N/A]
  - BSL Compliance:        [n]/100 (weight [w]%) [or N/A]

Total Findings: [n]
  - Critical: [n]
  - High:     [n]
  - Medium:   [n]
  - Low:      [n]

Full report: code-review-artifacts/acceptance-report.md

[If ACCEPT]:
The codebase meets acceptance criteria. Proceed with operations onboarding.

[If CONDITIONAL ACCEPT]:
The codebase requires remediation of [n] issues before full acceptance.
Remediation deadline and re-review scope are detailed in the report.
Please share the report with the development team.

[If REJECT]:
The codebase does not meet acceptance criteria due to [n] critical issues.
Full remediation and re-submission is required.
Please share the report with the development team.
============================================
```
