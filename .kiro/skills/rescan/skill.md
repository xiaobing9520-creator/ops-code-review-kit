---
name: rescan
description: >
  Post-fix rescan workflow: verifies that previously reported issues have been
  properly fixed in the new code version. Reuses existing reverse-engineering
  artifacts, focuses on fix completeness and correctness, and produces a
  delta report comparing before/after scan results.
---

# Rescan — Post-Fix Verification Scan

You are a senior code reviewer performing a **post-fix verification scan**.
The development team has submitted a new code version with fixes for issues
found in a previous scan. Your job is to verify that:

1. Each reported issue has been properly fixed
2. The fix is correct and complete (no partial fixes or regressions)
3. The fix does not introduce new issues in the same area

This is NOT a full initial scan — it is a targeted verification focused on
previously reported findings.

## When to Use This Skill

Use `@rescan` when:
- A previous scan (`@batch-scan` or individual module scans) has been completed
- The development team has fixed some or all reported issues
- A new code version has been delivered for verification

## Prerequisites

### Required: Previous Scan Reports

Previous scan reports MUST exist in `code-review-artifacts/`:
- `[Module]_Reliability_Maintainability_Report_[date].md`
- `[Module]_Security_Report_[date].md`
- `Summary_Report_[date].md`

If no previous reports exist, instruct the user to run `@batch-scan` first
instead of `@rescan`.

### Required: Reverse Engineering Artifacts

The `code-review-artifacts/reverse-engineering/` artifacts from the previous
scan are reusable:

**Users do NOT need to re-run `@codebase-reverse-engineering` for a rescan.**

Instead, copy the previous artifacts into the new code version's directory:

```bash
# Copy previous reverse-engineering artifacts to the new code version
cp -r /path/to/previous-version/code-review-artifacts/reverse-engineering/ \
      /path/to/new-version/code-review-artifacts/reverse-engineering/
```

**Why this is safe**: Reverse engineering artifacts capture the system's
architecture, technology stack, and API surface. For a fix-only code drop
(no new features), these remain valid. If the new version includes significant
architectural changes beyond bug fixes, the user should re-run
`@codebase-reverse-engineering` instead.

### Required: Previous Scan Reports in New Directory

Copy previous scan reports so the rescan can reference them:

```bash
# Copy previous reports to the new version's artifacts directory
cp /path/to/previous-version/code-review-artifacts/*_Report_*.md \
   /path/to/new-version/code-review-artifacts/previous-scan/
```

## Output

For each module:
- `code-review-artifacts/[MODULE]_Rescan_Report_[YYYY-MM-DD].md`

Plus a global:
- `code-review-artifacts/Rescan_Summary_Report_[YYYY-MM-DD].md`

---

## Rescan Process

### Step 1: Load Previous Findings

1. Read all previous scan reports from `code-review-artifacts/previous-scan/`
2. Build a checklist of ALL previously reported issues:
   - Issue ID (e.g., BUG-01, SEC-03)
   - Rule/Control ID
   - Severity
   - File and location
   - Description
3. Sort by severity (Critical → High → Medium) and fix priority (P0 → P3)

### Step 2: Verify Each Fix

For each previously reported issue, IN ORDER OF SEVERITY:

#### 2.1 Locate the Fix

1. Go to the file and location referenced in the previous finding
2. If the file has been renamed or moved, search for the equivalent code
3. Read the surrounding code context

#### 2.2 Evaluate Fix Status

Classify each issue into one of these statuses:

| Status | Meaning | Quality Gate Impact |
|--------|---------|---------------------|
| **FIXED** | Issue is properly resolved | No impact |
| **PARTIALLY FIXED** | Fix is incomplete or covers only some cases | Same as original severity |
| **INCORRECTLY FIXED** | Fix introduces new problems or doesn't address root cause | Same or higher severity |
| **NOT FIXED** | Issue remains unchanged | Same as original severity |
| **REGRESSED** | Fix attempt created a new, different issue | Assessed independently |

#### 2.3 Fix Completeness Check

For each issue marked as FIXED, verify:

1. **Root cause addressed**: Does the fix address the root cause identified in
   the previous report, not just the symptom?
2. **All instances covered**: If the same pattern existed in multiple locations,
   are ALL instances fixed?
3. **Edge cases handled**: Does the fix handle edge cases (null, empty, boundary
   values)?
4. **No regression**: Does the fix break any nearby functionality? Check for:
   - Changed method signatures that affect callers
   - Removed code that was used elsewhere
   - New dependencies that may have issues
5. **Consistent with codebase patterns**: Does the fix follow the project's
   existing coding patterns and conventions?

#### 2.4 Record Verification Result

For each issue, record:
- Previous Issue ID and severity
- Fix status (FIXED / PARTIALLY FIXED / INCORRECTLY FIXED / NOT FIXED / REGRESSED)
- Evidence (what code changed, is it correct)
- Notes (any concerns about the fix approach)

### Step 3: Scan for New Issues in Changed Files

For files that were modified as part of the fixes:

1. Run the applicable rule checks ONLY on the changed code areas
2. Check if the fix introduced any new violations
3. Any new issues are classified as REGRESSED and reported separately
4. For any new R&M findings, apply `@rm-report-validator` checks inline:
   - V-01: Rule ID must exist in the standards file
   - V-02: Severity must match the standards file exactly
   - V-03: Rule description must match the actual rule title
   Undefined or wrong-rule findings go to the Appendix only.

**Important**: This is NOT a full re-scan of the entire module. Only scan
code areas that were touched by the fixes.

### Step 4: Generate Rescan Report

For each module, create the rescan report using the template below.

### Step 5: Generate Rescan Summary

After all modules, create a global summary.

---

## Rescan Report Template

```markdown
# [MODULE_NAME] Rescan Report

**Repository / Module**: [name]
**Rescan Date**: [YYYY-MM-DD]
**Previous Scan Date**: [YYYY-MM-DD from previous report]
**Scan Type**: Post-Fix Verification (Rescan)

---

## 1. Rescan Summary

### 1.1 Fix Verification Results

| Status | Critical | High | Medium | Total |
|--------|----------|------|--------|-------|
| FIXED | [n] | [n] | [n] | [n] |
| PARTIALLY FIXED | [n] | [n] | [n] | [n] |
| INCORRECTLY FIXED | [n] | [n] | [n] | [n] |
| NOT FIXED | [n] | [n] | [n] | [n] |
| REGRESSED (new) | [n] | [n] | [n] | [n] |
| **Total** | **[n]** | **[n]** | **[n]** | **[n]** |

### 1.2 Fix Rate

| Metric | Value |
|--------|-------|
| Total issues from previous scan | [n] |
| Issues fully fixed | [n] |
| Fix rate | [n]% |
| Remaining open issues | [n] |
| New issues (regressions) | [n] |

### 1.3 Quality Gate (Rescan)

**Status: [PASS / FAIL]**

Apply the **Shared Quality Gate** to remaining issues:

```
FAIL if ANY of the following is true:
  - severity = Critical  AND  status ≠ FIXED
  - severity = High  AND  priority = P0  AND  status ≠ FIXED

PASS if none of the above conditions are met.
```

> "Remaining" means status is NOT FIXED / PARTIALLY FIXED / INCORRECTLY FIXED / REGRESSED.
> Medium issues and High issues with P1/P2/P3 do NOT block the gate.

---

## 2. Fix Verification Details

### [Previous Issue ID]: [Brief title]

**Risk Level**: [CRITICAL / HIGH / MEDIUM]
**CVSS Score**: [score] ([severity]) / N/A — non-security rule
**File**: `[original file/path.java:line]`
**Associated CVE**: [from previous report]

- **Rule/Control**: [Rule ID from previous report]
- **Previous Severity**: [severity from previous report]
- **Fix Status**: [FIXED / PARTIALLY FIXED / INCORRECTLY FIXED / NOT FIXED / REGRESSED]

**Previous Finding**:
[Brief summary of what was reported]

**Fix Verification**:
[What changed in the code — show before/after if helpful]

**Assessment**:
[Why the fix is/isn't complete. For PARTIALLY FIXED or INCORRECTLY FIXED,
explain what remains or what's wrong with the fix.]

**Remaining Action** (if not fully fixed):
[What still needs to be done]

---

[Repeat for each previously reported issue]

---

## 3. New Issues Found in Changed Code (Regressions)

> Issues discovered in code areas modified during the fix process.

### REG-01: [Brief title]

**Risk Level**: [CRITICAL / HIGH / MEDIUM]
**CVSS Score**: [score] ([severity]) / N/A — non-security rule
**File**: `[file/path.java:line]`
**Associated CVE**: [CVE-ID / N/A]

- **Rule/Control**: [Rule ID]
- **Introduced by**: Fix for [previous issue ID]
- **Description**: [What the new issue is]
- **Fix Recommendation**: [How to fix]

[If none: "No regressions found in modified code areas."]

---

## 4. Remaining Open Issues

| Issue ID | Rule/Control | Severity | Status | Remaining Action |
|----------|-------------|----------|--------|-----------------|
| [ID] | [Rule] | [Sev] | [Status] | [Action needed] |

---

## 5. Recommendations

### For Development Team
[Specific guidance on remaining fixes]

### For Operations Team
[Assessment of whether the code is approaching acceptance readiness]
```

---

## Rescan Summary Report Template

```markdown
# Rescan Summary Report

**Rescan Date**: [YYYY-MM-DD]
**Previous Scan Date**: [YYYY-MM-DD]
**Modules Rescanned**: [n]

---

## 1. Overall Rescan Quality Gate

**Status: [PASS / FAIL]**

| Module | R&M Rescan | Security Rescan | Overall |
|--------|-----------|-----------------|---------|
| [Module 1] | Pass/Fail | Pass/Fail | Pass/Fail |
| [Module 2] | Pass/Fail | Pass/Fail | Pass/Fail |
| **Overall** | | | **[PASS/FAIL]** |

## 2. Fix Progress Overview

| Module | Previous Issues | Fixed | Partial | Not Fixed | Regressed | Fix Rate |
|--------|----------------|-------|---------|-----------|-----------|----------|
| [Module 1] | [n] | [n] | [n] | [n] | [n] | [n]% |
| [Module 2] | [n] | [n] | [n] | [n] | [n] | [n]% |
| **Total** | **[n]** | **[n]** | **[n]** | **[n]** | **[n]** | **[n]%** |

## 3. Remaining Critical & High Issues

| Issue ID | Module | Severity | Status | Description |
|----------|--------|----------|--------|-------------|
| [ID] | [Module] | [Sev] | [Status] | [brief] |

## 4. Assessment

[Overall assessment: Is the codebase approaching acceptance readiness?
What are the key remaining gaps? Recommend next steps.]
```

## Completion Message

```
============================================
  Rescan Complete
============================================

Modules rescanned: [n]
Previous issues: [n]
Fixed: [n] ([n]%)
Remaining: [n]
Regressions: [n]

Rescan Quality Gate: [PASS / FAIL]

Reports:
  [list all rescan report files]

[If PASS]:
All previously reported issues have been resolved. The codebase is ready
for acceptance review.

[If FAIL]:
[n] issues remain unresolved. Share the rescan reports with the development
team for further remediation.
============================================
```
