---
name: acceptance-report
description: >
  Generates the final acceptance decision report by aggregating findings from
  all four dimension-specific reviews (security, reliability, performance,
  maintainability). Produces a Pass/Conditional/Reject decision with supporting
  evidence and remediation requirements.
---

# Acceptance Report

You are the operations team's chief reviewer making the final acceptance
decision. Your job is to aggregate all review findings into a single,
actionable report that clearly states whether this codebase is ready for
operations acceptance.

## Prerequisites

ALL of the following reports MUST exist before running this skill:
- `code-review-artifacts/reverse-engineering/analysis-summary.md`
- `code-review-artifacts/security-review/security-report.md`
- `code-review-artifacts/reliability-review/reliability-report.md`
- `code-review-artifacts/performance-review/performance-report.md`
- `code-review-artifacts/maintainability-review/maintainability-report.md`

If any file is missing, instruct the user to run the corresponding skill first.

## Output

`code-review-artifacts/acceptance-report.md`

## Report Generation Process

### Step 1: Collect All Findings

1. Read all four review reports
2. Read the reverse engineering analysis summary
3. Extract from each report:
   - Rating/score
   - Finding counts by severity
   - Critical and High findings list
   - Key metrics

### Step 2: Aggregate Metrics

Compile a unified metrics dashboard:

| Dimension | Score | Critical | High | Medium | Low |
|-----------|-------|----------|------|--------|-----|
| Security | [from security report] | | | | |
| Reliability | [from reliability report] | | | | |
| Performance | [from performance report] | | | | |
| Maintainability | [from maintainability report] | | | | |

### Step 3: Calculate Composite Score

Apply dimension weights to calculate an overall score:

| Dimension | Weight | Score | Weighted |
|-----------|--------|-------|----------|
| Security | 35% | [n] | [n] |
| Reliability | 30% | [n] | [n] |
| Performance | 15% | [n] | [n] |
| Maintainability | 20% | [n] | [n] |
| **Composite** | **100%** | | **[n]** |

### Step 4: Apply Acceptance Decision Rules

Apply the following rules IN ORDER (first matching rule determines decision):

**REJECT if any of these are true:**
- Any Critical security finding (CWE Top 5, hardcoded secrets, etc.)
- Total Critical findings across all dimensions > 0
- Total High findings across all dimensions > 10
- Any single dimension score < 40
- Security dimension score < 50

**CONDITIONAL ACCEPT if any of these are true:**
- High findings: 4-10 total
- Any single dimension score between 40-60
- Composite score between 50-70
- Missing external tool scan data (SCA/SAST)
- Test coverage assessed as "Insufficient" or "None"

**ACCEPT if all of these are true:**
- No Critical findings
- High findings <= 3
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
| Security | 35% | [n]/100 | [n] | [Excellent/Good/Fair/Poor] |
| Reliability | 30% | [n]/100 | [n] | [Excellent/Good/Fair/Poor] |
| Performance | 15% | [n]/100 | [n] | [Excellent/Good/Fair/Poor] |
| Maintainability | 20% | [n]/100 | [n] | [Excellent/Good/Fair/Poor] |
| **Composite** | **100%** | | **[n]/100** | **[rating]** |

## Findings Summary

| Severity | Security | Reliability | Performance | Maintainability | Total |
|----------|----------|-------------|-------------|-----------------|-------|
| Critical | [n] | [n] | [n] | [n] | [n] |
| High | [n] | [n] | [n] | [n] | [n] |
| Medium | [n] | [n] | [n] | [n] | [n] |
| Low | [n] | [n] | [n] | [n] | [n] |
| **Total** | **[n]** | **[n]** | **[n]** | **[n]** | **[n]** |

## Key Metrics

| Metric | Value | Standard | Status |
|--------|-------|----------|--------|
| Vulnerability Density | [n]/KLOC | < 0.5/KLOC | Pass/Fail |
| Defect Density | [n]/KLOC | < 1.0/KLOC | Pass/Fail |
| Technical Debt Ratio | [n]% | < 10% | Pass/Fail |
| Code Smell Density | [n]/KLOC | < 5/KLOC | Pass/Fail |
| 12-Factor Compliance | [n]/6 | >= 4/6 | Pass/Fail |
| Maintainability Index | [n]/100 | >= 65 | Pass/Fail |

## Data Completeness

| Data Source | Status | Impact on Decision |
|------------|--------|-------------------|
| Kiro AI Code Analysis | Completed | Primary data source |
| SCA Scan (Trivy) | Completed / Not Provided | [impact] |
| SAST Scan (Semgrep) | Completed / Not Provided | [impact] |
| IaC Scan (Checkov) | Completed / Not Provided | [impact] |
| Test Coverage Report | Completed / Not Provided | [impact] |

## Critical & High Findings Requiring Remediation

[List ALL Critical and High findings from all four reviews. For each:]

### [ID] [Finding Title] — [Dimension]
- **Severity**: Critical / High
- **Location**: `[file:line]`
- **Issue**: [Brief description]
- **Required Action**: [What must be done]
- **Deadline**: Before re-submission / Within 30 days

## Dimension Highlights

### Security
[2-3 sentence summary of security review findings and key concerns]

### Reliability
[2-3 sentence summary of reliability review findings and key concerns]

### Performance
[2-3 sentence summary of performance review findings and key concerns]

### Maintainability
[2-3 sentence summary of maintainability review findings and key concerns]

## Remediation Plan (if Conditional Accept or Reject)

### Required Before Acceptance
| # | Finding ID | Description | Dimension | Priority |
|---|-----------|-------------|-----------|----------|
| 1 | [id] | [desc] | [dim] | [1-Critical/2-High] |

### Required Within 30 Days (Conditional Accept only)
| # | Finding ID | Description | Dimension | Priority |
|---|-----------|-------------|-----------|----------|
| 1 | [id] | [desc] | [dim] | [priority] |

### Re-Review Scope
- **Re-review type**: Full / Targeted
- **Dimensions to re-review**: [list]
- **Estimated re-review effort**: [description]

## Standards Compliance Summary

| Standard | Compliance Status |
|----------|------------------|
| OWASP Top 10 (2021) | [n]/10 categories checked, [n] issues found |
| CWE Top 25 (2025) | Top 5 blocking checks performed |
| 12-Factor App | [n]/6 key factors compliant |
| NIST SSDF PW.7 | Code review performed (this report) |

## Appendix: Detailed Reports

For full findings and technical details, refer to:
- [Security Report](security-review/security-report.md)
- [Reliability Report](reliability-review/reliability-report.md)
- [Performance Report](performance-review/performance-report.md)
- [Maintainability Report](maintainability-review/maintainability-report.md)
- [Architecture Documentation](reverse-engineering/architecture.md)
```

## Completion Message

```
============================================
  Code Acceptance Review Complete
============================================

DECISION: [ACCEPT / CONDITIONAL ACCEPT / REJECT]

Composite Score: [n]/100
  - Security:        [n]/100 (weight 35%)
  - Reliability:     [n]/100 (weight 30%)
  - Performance:     [n]/100 (weight 15%)
  - Maintainability: [n]/100 (weight 20%)

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
