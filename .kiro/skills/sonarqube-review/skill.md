---
name: sonarqube-review
description: >
  Generates a Reliability & Maintainability report for a single module based on
  SonarQube Java/JavaScript rules (Blocker/High/Medium). Excludes security rules
  and code smell rules. Strict rule-to-ID mapping, quality gate, fix priorities
  (P0–P3), and LLM-discovered issues isolated in appendix.
---

# Reliability & Maintainability Review (SonarQube Rules)

You are a senior code quality engineer. Generate a **Reliability &
Maintainability** report for the specified module by checking it against the
organization's SonarQube rule set.

**Scope**: This report covers reliability (Bug) rules only. Security rules and
Code Smell rules are excluded — security is handled by the separate Security
report (`@secure-coding-baseline-review`).

## Prerequisites

- `code-review-artifacts/reverse-engineering/` artifacts must exist.
  If not, instruct the user to run `@codebase-reverse-engineering` first.
- The module path must be specified by the user or the batch-scan orchestrator.

## Output

`code-review-artifacts/[MODULE_NAME]_Reliability_Maintainability_Report_[YYYY-MM-DD].md`

## Applicable Languages

- **Java** → `.kiro/rules/sonarqube-java-standards.md`
- **JavaScript/TypeScript** → `.kiro/rules/sonarqube-javascript-standards.md`

If the module contains neither, output a short "Not applicable" report.

---

## CRITICAL CONSTRAINTS

### Constraint 0: Unified Finding Header

Every finding in this report MUST begin with the following 4-line header block,
placed immediately after the finding title, before any other fields:

```
**Risk Level**: CRITICAL / HIGH / MEDIUM
**CVSS Score**: [score] ([severity]) / N/A — non-security rule
**File**: `[file/path.java:line]`
**Associated CVE**: [CVE-ID pattern] / N/A — code quality rule (CWE-ID)
```

Rules for each field:
- **Risk Level**: Map from rule severity — Blocker→CRITICAL, High→HIGH, Medium→MEDIUM.
- **CVSS Score**: Always `N/A — non-security rule` (security rules are excluded from this report).
- **File**: Exact file path and line number where the issue was found.
- **Associated CVE**: Always `N/A — non-security rule` (security rules are excluded from this report).

This header format is shared across ALL report types (R&M, Security, Security Review)
to ensure consistent presentation when reports are compared side-by-side.

### Constraint 1: Strict Rule-to-ID Mapping

Every issue in the main report body MUST map to a specific rule in the
standards files. For each issue you MUST provide:
- The **exact SonarQube Rule ID** (e.g., `java:S2095`)
- The **exact rule description** from the standards file
- The **exact severity** as defined in the standards file

**Prohibitions:**
- Do NOT report issues with rule IDs not found in the standards files
- Do NOT invent or recall rule IDs from training data
- Do NOT adjust rule severity — use exactly what the standards file states

### Constraint 2: Severity Follows SonarQube Definition

Map SonarQube severity to report severity as follows:

| Standards File Severity | Report Severity | Quality Gate Impact |
|------------------------|-----------------|---------------------|
| Blocker | Critical | Blocks release |
| High | High | Blocks release |
| Medium | Medium | Blocks release only if P0 |

- Use **Critical**, **High**, **Medium** as severity labels in the report.
- Do NOT use other labels (Major, Minor, Info, etc.)

### Constraint 3: LLM-Discovered Issues Go to Appendix

Issues found during review that **cannot** be mapped to a specific rule ID in
the standards files MUST be placed in the **Appendix** section, clearly labeled
as "general best practices". They do NOT count toward the quality gate.

---

## Review Process

### Step 1: Preparation

1. Read reverse engineering artifacts for the module
2. Read the applicable SonarQube standards file(s) from `.kiro/rules/`
3. Build a rule checklist — every rule gets checked (Pass / Fail / N/A)

### Step 2: Rule-by-Rule Scanning

For each rule in the standards file:

1. Read the rule definition, noncompliant/compliant examples
2. Search the module's source code for noncompliant patterns
3. If violation found:
   - Record: rule key, severity, file path, code snippet, root cause, impact
   - Assign fix priority (P0/P1/P2/P3) using the criteria below
4. If no violation: mark as Pass or N/A

Process rules by category in this order:
1. Reliability rules (resource leaks, concurrency, null safety)
2. Spring Framework rules (if applicable)
3. Testing quality rules

**EXCLUSION**: Do NOT scan security-category rules (`javasecurity:*`,
`jssecurity:*`, and rules in the "Security Rules" sections of the standards
files). Security scanning is performed separately via `@secure-coding-baseline-review`.

### Step 3: Assign Fix Priority

For every issue, assign a priority:

| Priority | Meaning | Typical Scenarios |
|----------|---------|-------------------|
| **P0** | Must fix before release | Affects correctness or security; includes some Medium issues |
| **P1** | Short-term fix (1–2 weeks) | High risk but not blocking current release |
| **P2** | Medium-term fix (1 month) | Code quality issues with some risk |
| **P3** | Long-term optimization | Low risk, technical debt |

**Important**: Medium-severity issues MUST have an explicit P0–P3 assignment.
A Medium issue rated P0 will cause the quality gate to **Fail**.

### Step 4: Self-Validation

Before generating the report:

1. **Rule ID check**: Every issue's rule key exists in the standards file
2. **Severity check**: Every issue's severity matches the standards file
3. **Priority check**: Every Medium issue has an explicit P0–P3 label
4. **Appendix check**: Any issue without a valid rule ID is in the Appendix
5. **Completeness**: All rules in the standards have been evaluated

### Step 5: Quality Gate Evaluation

```
Pass conditions (ALL must be true):
  - 0 Critical issues
  - 0 High issues
  - 0 Medium issues with priority P0
Otherwise: Fail
```

### Step 6: Collect LLM-Discovered Issues

During scanning, if you find genuine code problems that do NOT map to any
rule in the standards files, collect them separately for the Appendix.
These are informational only and do not affect the quality gate.

### Step 7: Generate Report

Create the report using the template below.

---

## Report Template

```markdown
# [MODULE_NAME] Reliability & Maintainability Report

**Repository / Module**: [name]
**Scan Date**: [YYYY-MM-DD]
**Review Standards**: SonarQube Java/JavaScript Rules (Organization Quality Profile)
**Rule ID Format**: `java:Sxxxx` / `javabugs:Sxxxx` / `javaarchitecture:Sxxxx` / `javascript:Sxxxx` / `jsarchitecture:Sxxxx`

---

## 1. Review Summary

### 1.1 Issue Statistics by Category

| Category | Bug | Total |
|----------|-----|-------|
| Critical | [n] | [n] |
| High | [n] | [n] |
| Medium | [n] | [n] |
| **Total** | **[n]** | **[n]** |

### 1.2 Quality Gate

**Status: [PASS / FAIL]**

| Criteria | Threshold | Actual | Result |
|----------|-----------|--------|--------|
| Critical issues | 0 | [n] | Pass/Fail |
| High issues | 0 | [n] | Pass/Fail |
| Medium issues with P0 priority | 0 | [n] | Pass/Fail |

---

## 2. Issue Details

### BUG-01: [Brief title]

**Risk Level**: [CRITICAL / HIGH / MEDIUM]
**CVSS Score**: [score] ([severity]) / N/A — non-security rule
**File**: `[file/path.java:line]`
**Associated CVE**: [CVE-ID / CVE-ID pattern / N/A — code logic defect (CWE-ID) / N/A — non-security rule]

- **Rule**: `[java:Sxxxx]` — [Rule description from standards]
- **Fix Priority**: [P0 / P1 / P2 / P3]

**Code**:
```java
// Noncompliant code snippet
```

**Root Cause & Business Impact**:
[Explain why this is a problem and what business risk it poses]

**Fix Recommendation**:
[Specific, actionable fix for THIS code — not generic advice]

**Suggested Fix Code (AI-generated)**:
```java
// AI-suggested corrected code (if applicable)
```
> If no code-level fix can be demonstrated, state: "N/A — requires architectural or configuration change."

**Impact of Not Fixing**:
[What happens if this issue is left unresolved]

---

[Repeat for each issue: BUG-02, BUG-03, etc.]

---

## 3. Fix Priority Summary

| Priority | Count | Description |
|----------|-------|-------------|
| P0 | [n] | Must fix before release |
| P1 | [n] | Fix within 1–2 weeks |
| P2 | [n] | Fix within 1 month |
| P3 | [n] | Long-term optimization |

### P0 Issues (Release Blockers)

| Issue ID | Rule | Severity | Location | Description |
|----------|------|----------|----------|-------------|
| [BUG-01] | [java:Sxxxx] | [Critical] | [file:line] | [brief] |

---

## 4. Rule Coverage

| Metric | Value |
|--------|-------|
| Total rules in standards | [n] |
| Rules checked | [n] |
| Rules with findings (Fail) | [n] |
| Rules passed (Pass) | [n] |
| Rules not applicable (N/A) | [n] |

---

## 5. Appendix: Additional Findings (General Best Practices)

> The following issues were identified during review but do NOT map to any
> rule in the specified SonarQube rule set. They are based on general coding
> best practices and are provided for reference only. They do NOT affect the
> quality gate determination.

### APP-01: [Title]
- **Source**: General best practices (not in SonarQube rule set)
- **Location**: `[file:line]`
- **Description**: [issue description]
- **Recommendation**: [fix suggestion]

[If no additional findings: "No additional findings outside the rule set."]
```

## Completion Message

```
Reliability & Maintainability report generated.
Output: code-review-artifacts/[MODULE]_Reliability_Maintainability_Report_[DATE].md

Quality Gate: [PASS / FAIL]
Issues: Critical=[n], High=[n], Medium=[n] (P0=[n])
Rules checked: [n], Findings: [n]
```
