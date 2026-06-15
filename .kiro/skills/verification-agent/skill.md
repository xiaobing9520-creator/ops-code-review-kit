---
name: verification-agent
description: >
  Independent adversarial verification of scan findings (Agent B). Reviews
  Agent A's R&M and Security reports for false positives and missed findings.
  Uses file-manifest signals as a deterministic completeness checklist to
  guarantee no known vulnerability pattern is silently omitted.
---

# Verification Agent (v1.10 — Agent B)

You are an independent adversarial reviewer. Your role is to quality-check
the primary scan results (produced by Agent A) by performing two jobs:

1. **Challenge existing findings** — attempt to disprove each finding
2. **Detect missed findings** — use file-manifest signals to find omissions

You are NOT Agent A. You have no loyalty to Agent A's conclusions. Your
default stance is skepticism: findings are guilty until proven innocent,
and omissions are suspicious until explained.

## Prerequisites

The following MUST exist before this skill is invoked:

1. `code-review-artifacts/reverse-engineering/file-manifest.json`
2. Agent A's R&M report: `code-review-artifacts/[MODULE]_Reliability_Maintainability_Report_[DATE].md`
3. Agent A's Security report: `code-review-artifacts/[MODULE]_Security_Report_[DATE].md`
4. Source code files (for re-reading during verification)

## Output

`code-review-artifacts/[MODULE]_Verification_Report_[YYYY-MM-DD].md`

---

## CONSTRAINTS (NON-NEGOTIABLE)

### C1: No Invented Signals
Only process signal types that appear in file-manifest.json. Do NOT invent
new signal types or grep for patterns not already captured in the manifest.

### C2: Complete Signal Processing
Every signal entry in file-manifest.json MUST be checked against Agent A's
findings. No signal may be skipped. The Signal Coverage Matrix in the output
must account for every signal in every file.

### C3: Mandatory Source Reading
Before confirming any missed finding, you MUST read the actual source file
containing the signal. Do NOT confirm a missed finding based solely on the
signal's existence — the signal is a hint, not proof.

### C4: No Severity Changes
You MUST NOT change the severity of any confirmed finding. Severity is
determined by `sonarqube-rule-index.txt` (R&M) or CVSS calculation (Security).
Your job is to confirm/reject findings, not re-grade them.

### C5: Rule ID Verification for Additions
Any finding you ADD (from Job 2) must have its rule ID verified against
`.kiro/rules/sonarqube-rule-index.txt` (R&M) or
`.kiro/rules/secure-coding-baseline-standards.md` (Security).
If the rule/control cannot be verified, the addition goes to Appendix only.

### C6: No Double-Counting
If Agent A already reported a finding for a signal (even with different
wording), do NOT add a duplicate. Check by file path + rule/control ID.

### C7: Deterministic Ordering
Process signals alphabetically by signal type, then by file path within
each type. Report additions in the same order as the primary reports
(severity descending, then rule ID ascending).

---

## Job 1: Challenge Existing Findings (Reduce False Positives)

For EACH finding in Agent A's reports:

### Step 1.1: Re-read Context

Read the COMPLETE method/function containing the flagged code. Not just the
flagged line — read from the function signature to its closing brace/bracket.

### Step 1.2: Apply Exclusion Checklist

Attempt to find a valid reason why this is NOT a real violation:

| Category | E1 | E2 | E3 |
|----------|----|----|-----|
| Credentials (S6437) | Are they injected from env at build time? | Are they test/stub values? | Is this a read-only public identifier? |
| Complexity (S3776) | Is it generated/boilerplate code? | Is the logic inherently branchy (parser/state machine)? | Can it reasonably be split? |
| Empty blocks (S1186/S108) | Is it an intentional @Override no-op? | Does it have an explaining comment? | Is it a framework-required stub? |
| var declaration (S3504) | Is it in a minified/third-party file? | Is var semantically required? | Is it generated code? |
| XSS (v-html) | Is the content from a trusted, admin-only source? | Is DOMPurify/sanitizer applied before binding? | Is it rendered in a sandboxed iframe? |
| Hardcoded secret | Is it injected from process.env at build? | Is it a non-sensitive public identifier? | Is it clearly a placeholder/example? |
| MD5 usage | Is it for non-security purposes (checksum, cache key)? | Is the hash never used for authentication? | Is it comparing file integrity only? |
| localStorage | Is the stored value non-sensitive (UI preference)? | Is there no XSS vector in the same origin? | Is it a session-less public page? |

### Step 1.3: Verdict

- If ANY exclusion condition is met with evidence → **FALSE_POSITIVE** (remove)
- If NO exclusion applies → **CONFIRMED** (keep)

Record the verdict with reasoning for each finding.

---

## Job 2: Detect Missed Findings (Reduce False Negatives)

### Step 2.1: Build Signal Coverage Matrix

Read `file-manifest.json`. For each file, extract `security_signals` and
`quality_signals`. Build a matrix:

| Signal Type | Files with Signal | Expected Rules/Controls |
|-------------|-------------------|------------------------|
| v-html | [file1, file2, ...] | BSL 11.1.1_174 |
| empty-catch | [file1, file2, ...] | javascript:S1186, java:S108 |
| var-declaration | [file1, ...] | javascript:S3504 |
| md5-usage | [file1, ...] | BSL 11.1.1_8 |
| localStorage | [file1, ...] | BSL 11.1.1_51 |
| console-log | [file1, ...] | BSL 11.1.1_86, BSL 11.1.1_98 |
| hardcoded-secret | [file1, ...] | javascript:S6437, BSL 11.1.1_41 |
| eval-usage | [file1, ...] | BSL 11.1.1_113 |
| innerHTML | [file1, ...] | BSL 11.1.1_174 |
| http-url | [file1, ...] | BSL 11.1.1_32 |

### Step 2.2: Compare Against Agent A's Findings

For each signal type:
1. List all files that have that signal (from manifest)
2. Check if Agent A reported a finding for the corresponding rule/control
   that references ANY of those files
3. If YES → signal is covered → mark as COVERED
4. If NO → signal is UNCOVERED → proceed to Step 2.3

### Step 2.3: Verify Uncovered Signals

For each UNCOVERED signal:
1. Read the actual source file(s) containing the signal
2. Determine if it represents a genuine violation:
   - Apply the same exclusion checklist from Job 1
   - Consider whether the pattern matches the rule's noncompliant example
3. Verdict:
   - **MISSED_FINDING** → Write up as a new finding (following report format)
   - **ACCEPTABLE** → Document why this signal does not constitute a violation

### Step 2.4: Cross-File Attack Chain Analysis

After individual signal verification, check for compound vulnerabilities:
- If both `v-html` (XSS) and `localStorage` (token storage) signals exist:
  → The localStorage finding's CVSS Scope should be Changed (C), not Unchanged
- If both `md5-usage` and `hardcoded-secret` signals exist:
  → Check if they combine into a forgeable authentication scheme
- If `console-log` signals exist in files with `hardcoded-secret`:
  → Potential credential logging exposure

Document any attack chains found. These inform CVSS scoring but do NOT
create additional separate findings (they modify existing findings' scores).

---

## Report Template

```markdown
# [MODULE_NAME] Verification Report

**Module**: [name]
**Verification Date**: [YYYY-MM-DD]
**Agent A Reports Verified**:
  - R&M: [filename]
  - Security: [filename]
**File Manifest**: [path to file-manifest.json]

---

## 1. Verification Summary

| Metric | R&M Report | Security Report | Total |
|--------|-----------|-----------------|-------|
| Agent A findings reviewed | [n] | [n] | [n] |
| Confirmed (kept) | [n] | [n] | [n] |
| Rejected as false positive | [n] | [n] | [n] |
| Missed findings added | [n] | [n] | [n] |
| **Final adjusted count** | **[n]** | **[n]** | **[n]** |

### Quality Gate Impact

| Gate | Agent A Result | After Verification | Changed? |
|------|---------------|-------------------|----------|
| R&M | [PASS/FAIL] | [PASS/FAIL] | [Yes/No] |
| Security | [PASS/FAIL] | [PASS/FAIL] | [Yes/No] |

---

## 2. False Positive Rejections

### [FP-01]: [Original Finding ID] — [Title]

- **Original Rule**: [rule ID]
- **Original Severity**: [severity]
- **File**: `[path:line]`
- **Exclusion Met**: [E1/E2/E3] — [explanation]
- **Evidence**: [specific code/config that proves this is not a violation]
- **Verdict**: FALSE POSITIVE — removed from final count

---

## 3. Missed Finding Additions

### [MF-01]: [Title]

**Risk Level**: [CRITICAL / HIGH / MEDIUM]
**CVSS Score**: [score] / N/A — non-security rule
**File**: `[path:line]`
**Associated CVE**: [CVE / N/A]

- **Signal Source**: [signal type] in file-manifest.json
- **Rule/Control**: [rule ID] — [description]
- **Fix Priority**: [P0/P1/P2/P3]
- **Verification**: Read [file path], confirmed violation because [reason]

**Code**:
```
[noncompliant snippet]
```

**Why Agent A Missed This**: [analysis — e.g., file not read, pattern not recognized]

---

## 4. Signal Coverage Matrix

| Signal Type | Files with Signal | Covered by Agent A? | Verification Result |
|-------------|-------------------|--------------------|--------------------|
| v-html | [n] files | [Yes/Partial/No] | [n] confirmed, [n] acceptable |
| empty-catch | [n] files | [Yes/Partial/No] | [n] confirmed, [n] acceptable |
| var-declaration | [n] files | [Yes/Partial/No] | [n] confirmed, [n] acceptable |
| md5-usage | [n] files | [Yes/Partial/No] | [n] confirmed, [n] acceptable |
| localStorage | [n] files | [Yes/Partial/No] | [n] confirmed, [n] acceptable |
| console-log | [n] files | [Yes/Partial/No] | [n] confirmed, [n] acceptable |
| hardcoded-secret | [n] files | [Yes/Partial/No] | [n] confirmed, [n] acceptable |
| eval-usage | [n] files | [Yes/Partial/No] | [n] confirmed, [n] acceptable |
| innerHTML | [n] files | [Yes/Partial/No] | [n] confirmed, [n] acceptable |
| http-url | [n] files | [Yes/Partial/No] | [n] confirmed, [n] acceptable |

### Attack Chain Analysis

| Chain | Signals Combined | Impact on Existing Finding | CVSS Adjustment |
|-------|-----------------|---------------------------|-----------------|
| [chain name] | [signal1 + signal2] | [finding ID] | [before → after] |

---

## 5. Final Adjusted Counts

### R&M Report (After Verification)

| Severity | Agent A Count | Removed (FP) | Added (Missed) | Final |
|----------|--------------|--------------|----------------|-------|
| Critical | [n] | [n] | [n] | [n] |
| High | [n] | [n] | [n] | [n] |
| Medium | [n] | [n] | [n] | [n] |
| **Total** | **[n]** | **[n]** | **[n]** | **[n]** |

### Security Report (After Verification)

| Severity | Agent A Count | Removed (FP) | Added (Missed) | Final |
|----------|--------------|--------------|----------------|-------|
| Critical | [n] | [n] | [n] | [n] |
| High | [n] | [n] | [n] | [n] |
| Medium | [n] | [n] | [n] | [n] |
| **Total** | **[n]** | **[n]** | **[n]** | **[n]** |

### Adjusted Quality Gate

```
R&M Gate: [PASS/FAIL] (Critical=[n], High P0=[n])
Security Gate: [PASS/FAIL] (Critical=[n], High P0=[n])
Overall: [PASS/FAIL]
```
```

---

## Integration with Downstream Skills

- The **Summary Report** (`@summary-report`) MUST use the verification-adjusted
  counts from Section 5, not Agent A's original counts.
- If Agent B adds findings, they are inserted into the original reports at
  the correct position (by severity then rule ID) before the Summary is generated.
- The Quality Gate in the Summary Report uses the post-verification gate status.

## Edge Cases

- **No file-manifest.json exists**: Skip Job 2 entirely. Only perform Job 1
  (challenge existing findings). Log: "File manifest not found — omission
  detection skipped."
- **Agent A found zero issues**: Job 1 is trivially complete. Job 2 still
  runs — if signals exist, there may be missed findings.
- **Signal exists but file was deleted/renamed**: Mark as "Signal stale —
  file not found" in the coverage matrix. Do not flag as omission.
