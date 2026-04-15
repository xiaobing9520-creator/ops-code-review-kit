---
name: summary-report
description: >
  Generates a global Summary Report that merges all module scan results
  (Reliability & Maintainability + Security) into a single consolidated view
  with overall Pass/Fail determination and combined issue tables.
---

# Summary Report

You are the operations team's chief reviewer. Generate a global **Summary
Report** that consolidates all module-level scan results into one actionable
document.

## Prerequisites

ALL module-level reports MUST already exist in `code-review-artifacts/`:
- `[Module]_Reliability_Maintainability_Report_[date].md` for each module
- `[Module]_Security_Report_[date].md` for each module

If any report is missing, instruct the user to run `@batch-scan` or the
individual module scans first.

## Output

`code-review-artifacts/Summary_Report_[YYYY-MM-DD].md`

## Generation Process

### Step 1: Collect All Reports

1. List all `*_Reliability_Maintainability_Report_*.md` files
2. List all `*_Security_Report_*.md` files
3. Read each report and extract:
   - Module name
   - Quality gate status (Pass / Fail)
   - Issue counts by severity (Critical / High / Medium)
   - All issue details
   - Fix priority distribution

### Step 2: Aggregate

1. Compute overall quality gate:
   - **Pass** only if ALL individual reports are Pass
   - **Fail** if ANY individual report is Fail
2. Sum issue counts across all modules and report types
3. Merge all issue detail tables

### Step 3: Generate Report

---

## Report Template

```markdown
# Summary Report

**Scan Date**: [YYYY-MM-DD]
**Review Standards**:
  - Reliability & Maintainability: SonarQube Java/JavaScript Rules
  - Security: Philips Secure Coding Baseline (BSL 11.1.1.d v3)
**Modules Scanned**: [n]

---

## 1. Overall Quality Gate

**Status: [PASS / FAIL]**

| Module | R&M Report | Security Report | Overall |
|--------|-----------|-----------------|---------|
| [Module 1] | Pass/Fail | Pass/Fail | Pass/Fail |
| [Module 2] | Pass/Fail | Pass/Fail | Pass/Fail |
| [Module 3] | Pass/Fail | Pass/Fail | Pass/Fail |
| [Module 4] | Pass/Fail | Pass/Fail | Pass/Fail |
| **Overall** | | | **[PASS/FAIL]** |

---

## 2. Issue Summary by Module

| Module | Critical | High | Medium | Total |
|--------|----------|------|--------|-------|
| [Module 1] — R&M | [n] | [n] | [n] | [n] |
| [Module 1] — Security | [n] | [n] | [n] | [n] |
| [Module 2] — R&M | [n] | [n] | [n] | [n] |
| [Module 2] — Security | [n] | [n] | [n] | [n] |
| [Module 3] — R&M | [n] | [n] | [n] | [n] |
| [Module 3] — Security | [n] | [n] | [n] | [n] |
| [Module 4] — R&M | [n] | [n] | [n] | [n] |
| [Module 4] — Security | [n] | [n] | [n] | [n] |
| **Total** | **[n]** | **[n]** | **[n]** | **[n]** |

---

## 3. All Issues

The table below merges issues from all modules and all report types
(SonarQube R&M + BSL Security).

| Issue ID | Module | Severity | Description | Standard | Fix Priority | Rule ID | Rule Description | Fix Recommendation | Impact of Not Fixing |
|----------|--------|----------|-------------|----------|-------------|---------|------------------|-------------------|---------------------|
| BUG-01 | [Module 1] | Critical | [brief] | SonarQube | P0 | java:S2095 | Resources should be closed | [specific fix] | [risk] |
| SEC-01 | [Module 1] | Critical | [brief] | Philips BSL | P0 | 11.1.1_41 | No crypto keys in source | [specific fix] | [risk] |
| ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |

---

## 4. Fix Priority Distribution

| Priority | Count | Description |
|----------|-------|-------------|
| P0 | [n] | Must fix before release |
| P1 | [n] | Fix within 1–2 weeks |
| P2 | [n] | Fix within 1 month |
| P3 | [n] | Long-term optimization |

### P0 Issues (Release Blockers) — All Modules

| Issue ID | Module | Severity | Rule ID | Description |
|----------|--------|----------|---------|-------------|
| [BUG-01] | [Module] | [Critical] | [Rule] | [brief] |

---

## 5. Appendix Items (Not in Quality Gate)

> Issues discovered via general best practices that do not map to the
> specified rule sets. For reference only.

| Issue ID | Module | Source | Description | Recommendation |
|----------|--------|--------|-------------|----------------|
| APP-01 | [Module] | General best practices | [brief] | [fix] |

[If none: "No additional findings outside the specified rule sets."]
```

## Completion Message

```
Summary report generated.
Output: code-review-artifacts/Summary_Report_[DATE].md

Modules scanned: [n]
Overall Quality Gate: [PASS / FAIL]

Total issues across all modules:
  Critical: [n]
  High:     [n]
  Medium:   [n]
  P0 (release blockers): [n]

Individual module results:
  [Module 1]: R&M=[Pass/Fail], Security=[Pass/Fail]
  [Module 2]: R&M=[Pass/Fail], Security=[Pass/Fail]
  [Module 3]: R&M=[Pass/Fail], Security=[Pass/Fail]
  [Module 4]: R&M=[Pass/Fail], Security=[Pass/Fail]

Reports generated (9 total):
  [list all 9 report files]
```
