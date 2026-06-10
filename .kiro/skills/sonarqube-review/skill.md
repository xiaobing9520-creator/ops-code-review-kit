---
name: sonarqube-review
description: >
  Generates a Reliability & Maintainability report for a single module based on
  SonarQube Java/JavaScript rules (Blocker/High/Medium). v1.9: Dimension-based
  scanning with adversarial verification and external script validation.
---

# Reliability & Maintainability Review (v1.9 — Dimension Scan + Adversarial Verify)

You are a senior code quality engineer. Generate a **Reliability &
Maintainability** report for the specified module by checking it against the
organization's SonarQube rule set.

**v1.9 Architecture**: This skill uses a three-layer approach:
1. **Layer 1 (LLM)**: Dimension-based scanning + adversarial verification
2. **Layer 2 (Script)**: Deterministic rule ID validation
3. **Layer 3 (Script)**: Deterministic Quality Gate calculation

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
**CVSS Score**: N/A — non-security rule
**File**: `[file/path.java:line]`
**Associated CVE**: N/A — code quality rule (CWE-ID)
```

Rules for each field:
- **Risk Level**: Map from rule severity — Blocker→CRITICAL, High→HIGH, Medium→MEDIUM.
- **CVSS Score**: Always `N/A — non-security rule` (security rules are excluded from this report).
- **File**: Exact file path and line number where the issue was found.
- **Associated CVE**: Always `N/A — non-security rule` (security rules are excluded from this report).

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

| Standards File Severity | Report Severity | Quality Gate Impact |
|------------------------|-----------------|---------------------|
| Blocker | Critical | Blocks release (any priority) |
| High | High | Blocks release if P0 |
| Medium | Medium | Tracked only — does not block release |

### Constraint 3: LLM-Discovered Issues Go to Appendix

Issues found during review that **cannot** be mapped to a specific rule ID in
the standards files MUST be placed in the **Appendix** section.

### Constraint 4: Rule ID Verification Before Use

Before including ANY rule ID in a finding, you MUST:
1. Read the compact rule index at `.kiro/rules/sonarqube-rule-index.txt`
2. Search for the exact rule ID in that index
3. If found: use the severity listed in the index (NOT your own judgment)
4. If NOT found: the finding goes to Appendix, with no rule ID

**This is NON-NEGOTIABLE. If you cannot find the rule ID in the index file,
the finding MUST go to Appendix regardless of how confident you are.**

---

## Review Process

### Step 1: Preparation

1. Read reverse engineering artifacts for the module
2. Read the compact rule index: `.kiro/rules/sonarqube-rule-index.txt`
3. Read the applicable SonarQube standards file(s) from `.kiro/rules/`
4. Read ALL source files in the module (v1.8.1 full-scan policy)

### Step 2: Dimension-Based Scanning (Multi-Perspective)

Do NOT scan code randomly or freely. Scan in 5 mandatory dimensions, IN ORDER.
For each dimension, you MUST check every listed rule and report your finding as:
- **Found** — violation exists (proceed to record it)
- **Not Found** — checked but no violation in this codebase
- **N/A** — rule is not applicable to this technology stack

**IMPORTANT**: Keep a running checklist. Every dimension's mandatory rules must
be explicitly addressed.

---

#### Dimension 1: Resource Management & Lifecycle

**Focus**: Objects that hold system resources (streams, connections, handles)
must be properly closed or managed.

**Mandatory rules to check** (verify each against rule index before use):

| Rule ID | Title | What to look for |
|---------|-------|-----------------|
| java:S2095 | Resources should be closed | Any I/O stream, DB connection, HTTP client opened without try-with-resources |
| java:S2189 | Loops should not be infinite | While(true) without proper exit condition |
| java:S1128 | Unnecessary imports should be removed | Unused imports cluttering code |
| java:S2583 | Conditions should not unconditionally evaluate to TRUE or FALSE | Dead code paths |
| java:S2142 | InterruptedException should not be ignored | Catch block swallows interrupt |

**Scanning procedure**:
1. Find all classes that create I/O resources (InputStream, Connection, etc.)
2. For each, verify lifecycle management (try-with-resources, finally block)
3. Find all loops and verify termination conditions
4. Check import statements for unused entries

---

#### Dimension 2: Null Safety & Data Validation

**Focus**: Potential NullPointerExceptions and unchecked data flow.

**Mandatory rules to check**:

| Rule ID | Title | What to look for |
|---------|-------|-----------------|
| java:S2259 | Null pointers should not be dereferenced | Method calls on potentially null references |
| java:S2637 | @NonNull values should not be set to null | Annotated fields assigned null |
| java:S3518 | Zero should not be a possible denominator | Division without zero-check |
| java:S2201 | Return values from methods without side effects should not be ignored | Ignoring String.replace(), etc. |
| java:S2119 | "Random" objects should be reused | Creating new Random() in loops |

**Scanning procedure**:
1. Trace method return values — identify nullable returns used without checks
2. Find all division/modulo operations — verify denominator safety
3. Find all Random instantiations — check if they are in hot paths

---

#### Dimension 3: Exception Handling & Control Flow

**Focus**: Error handling correctness and control flow integrity.

**Mandatory rules to check**:

| Rule ID | Title | What to look for |
|---------|-------|-----------------|
| java:S1181 | Throwable and Error should not be caught | Catching too-broad exception types |
| java:S108 | Nested blocks of code should not be left empty | Empty catch/if/for blocks |
| java:S1166 | Exception handlers should preserve the original exceptions | Catch-and-rethrow losing cause |
| java:S1186 | Methods should not be empty | Stub implementations with no body |
| java:S131 | Switch statements should have default clauses | Missing default in switch |

**Scanning procedure**:
1. Find all catch blocks — check for Throwable/Error catches
2. Find all empty blocks (catch, if, for, while, method bodies)
3. Find all switch statements — verify default clause exists

---

#### Dimension 4: Concurrency & Thread Safety

**Focus**: Multi-threading correctness in Spring/servlet environments.

**Mandatory rules to check**:

| Rule ID | Title | What to look for |
|---------|-------|-----------------|
| java:S2445 | Blocks should be synchronized on "private final" fields | Synchronizing on mutable/public fields |
| java:S2168 | Double-checked locking should not be used | DCL pattern without volatile |
| java:S3046 | "wait" should not be called without a surrounding "while" loop | Spurious wake-up vulnerability |
| java:S1994 | Loop increment should modify counter | Suspicious loop patterns |
| java:S2696 | Instance methods should not write to "static" fields | Thread-unsafe static mutation |

**Scanning procedure**:
1. Find all synchronized blocks — check lock object type
2. Find all shared mutable state (static fields written from instance methods)
3. Find all wait/notify patterns — verify proper loop guard

---

#### Dimension 5: Spring Framework & Configuration (if applicable)

**Focus**: Spring-specific reliability issues.

**Mandatory rules to check**:

| Rule ID | Title | What to look for |
|---------|-------|-----------------|
| java:S6818 | @Autowired on single constructor | Multiple @Autowired constructors |
| java:S3776 | Cognitive complexity should not be too high | Methods with deeply nested logic |
| java:S4601 | HttpSecurity URL patterns should be correctly ordered | Permissive patterns before restrictive ones |
| java:S1192 | String literals should not be duplicated | Magic strings repeated >3 times |
| java:S4524 | Default clauses should be last | Default not at end of switch |

**Scanning procedure**:
1. Find all @Component/@Service/@Controller classes — check DI patterns
2. Find all security configuration classes — verify matcher ordering
3. Measure method complexity (nesting depth as proxy)

---

### Step 3: Adversarial Verification (Reduce False Positives)

**CRITICAL**: For EVERY finding from Step 2 that you marked as "Found", you
MUST now perform adversarial verification. The goal is to DISPROVE each finding.

For each candidate finding:

1. **Re-read the complete method** containing the issue (not just the flagged line — read from method signature to closing brace)

2. **Apply the exclusion checklist** for that rule category:

| Category | Exclusion Question 1 | Exclusion Question 2 | Exclusion Question 3 |
|----------|---------------------|---------------------|---------------------|
| Resource (S2095) | Is resource in try-with-resources? | Is there a finally{close()} or @Cleanup? | Is it Spring-managed (DataSource bean)? |
| Null (S2259) | Is there a null-check earlier in the same method? | Is the value from @NonNull-annotated source? | Is Optional used correctly? |
| Empty block (S108/S1186) | Is it an intentional no-op (@Override placeholder)? | Does it have a comment explaining why empty? | Is it a test mock / adapter pattern? |
| Concurrency (S2445) | Is the lock field effectively final (assigned once in constructor)? | Is it single-threaded context (prototype bean)? | Is there a higher-level lock? |
| Exception (S1181) | Is it a top-level error boundary (e.g., @ExceptionHandler)? | Is it immediately re-thrown after logging? | Is it in a framework hook that requires catching Throwable? |
| Complexity (S3776) | Is it a generated/boilerplate method (equals, hashCode, builder)? | Is the logic inherently branchy (state machine, parser)? | Can it reasonably be split without hurting readability? |

3. **Verdict**: If ANY exclusion condition is met → mark as **FALSE_POSITIVE** and remove from findings.

4. **Record verification result** for each finding:
   ```
   [VERIFIED] BUG-01: java:S2095 — Resource stream not closed in export()
     Exclusion 1: No try-with-resources ✗
     Exclusion 2: No finally/close ✗
     Exclusion 3: Not Spring-managed ✗
     → CONFIRMED: genuine violation

   [REJECTED] (candidate): java:S1186 — Empty method processEvent()
     Exclusion 1: @Override from interface ✓
     → FALSE POSITIVE: intentional no-op implementation, removed
   ```

### Step 4: Rule ID Final Verification

For every finding that survived Step 3:

1. Open `.kiro/rules/sonarqube-rule-index.txt`
2. Search for the exact rule ID (e.g., `java:S2095`)
3. Verify: Does the index entry title match what you're reporting?
   - YES → proceed, use the severity from the index
   - NO → this is a WRONG RULE mapping → move to Appendix
   - RULE NOT FOUND → move to Appendix

**Copy the matching line from the index file into your working notes** to prove
you verified it. Format: `Verified: java:S2095|Blocker|Resources should be closed`

### Step 5: Assign Fix Priority

Use the deterministic priority table:

| Condition | Priority |
|-----------|----------|
| Severity = Critical | P0 |
| Severity = High AND domain ∈ {Resource leak, Concurrency, Null safety} | P0 |
| Severity = High (other domain) | P1 |
| Severity = Medium AND (data correctness OR resource) | P1 |
| Severity = Medium (other) | P2 |

### Step 6: Generate Report

Create the report using the template below. Include ONLY findings that:
- Passed adversarial verification (Step 3)
- Have verified rule IDs (Step 4)
- Have correct severity from the index file

### Step 7: Run External Validation Script

After saving the report markdown file, run:

```bash
python3 .kiro/scripts/validate-report.py code-review-artifacts/[MODULE]_Reliability_Maintainability_Report_[DATE].md --rules sonarqube_rules.json
```

Read the script output. If it reports issues:
1. Move any findings flagged V-01 (rule not found) to Appendix
2. Correct any findings flagged V-02 (wrong severity)
3. Move any findings flagged V-03 (description mismatch) to Appendix
4. Save the corrected report

### Step 8: Run External Gate Calculation

After corrections, run:

```bash
python3 .kiro/scripts/compute-gate.py code-review-artifacts/[MODULE]_Reliability_Maintainability_Report_[DATE].md
```

Use the script's PASS/FAIL result as the **authoritative** Quality Gate status.
If it differs from what you wrote in the report, update the report to match
the script's determination.

---

## Report Template

```markdown
# [MODULE_NAME] Reliability & Maintainability Report

**Repository / Module**: [name]
**Scan Date**: [YYYY-MM-DD]
**Review Standards**: SonarQube Java/JavaScript Rules (Organization Quality Profile)
**Rule ID Format**: `java:Sxxxx` / `javascript:Sxxxx`
**Scan Mode**: v1.9 Dimension-Based Scan + Adversarial Verification

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

**Status: [PASS / FAIL]** (computed by external script)

| Criteria | Threshold | Actual | Result |
|----------|-----------|--------|--------|
| Critical issues | 0 | [n] | Pass/Fail |
| High issues with P0 priority | 0 | [n] | Pass/Fail |

### 1.3 Dimension Coverage

| Dimension | Rules Checked | Found | Verified | False Positive |
|-----------|--------------|-------|----------|----------------|
| Resource Management | [n] | [n] | [n] | [n] |
| Null Safety | [n] | [n] | [n] | [n] |
| Exception Handling | [n] | [n] | [n] | [n] |
| Concurrency | [n] | [n] | [n] | [n] |
| Spring/Config | [n] | [n] | [n] | [n] |
| **Total** | **[n]** | **[n]** | **[n]** | **[n]** |

---

## 2. Issue Details

### BUG-01: [Brief title]

**Risk Level**: [CRITICAL / HIGH / MEDIUM]
**CVSS Score**: N/A — non-security rule
**File**: `[file/path.java:line]`
**Associated CVE**: N/A — code quality rule

- **Rule**: `[java:Sxxxx]` — [Rule description from standards]
- **Verified**: [index line copied: java:Sxxxx|severity|title]
- **Fix Priority**: [P0 / P1 / P2 / P3]
- **Dimension**: [Resource Management / Null Safety / etc.]

**Code**:
```java
// Noncompliant code snippet
```

**Root Cause & Business Impact**:
[Explain why this is a problem and what business risk it poses]

**Adversarial Verification**:
- Exclusion 1: [condition] → [met/not met]
- Exclusion 2: [condition] → [met/not met]
- Exclusion 3: [condition] → [met/not met]
- **Verdict**: CONFIRMED

**Fix Recommendation**:
[Specific, actionable fix for THIS code]

**Suggested Fix Code (AI-generated)**:
```java
// Corrected code
```

---

[Repeat for each verified issue: BUG-02, BUG-03, etc.]

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

## 4. Dimension Scan Log

### Dimension 1: Resource Management

| Rule | Status | Notes |
|------|--------|-------|
| java:S2095 | Found → BUG-01 | [brief] |
| java:S2189 | Not Found | No infinite loops detected |
| java:S1128 | N/A | IDE auto-manages imports |
| java:S2583 | Not Found | — |
| java:S2142 | Not Found | — |

### Dimension 2: Null Safety

| Rule | Status | Notes |
|------|--------|-------|
| java:S2259 | [status] | [notes] |
| java:S2637 | [status] | [notes] |
| java:S3518 | [status] | [notes] |
| java:S2201 | [status] | [notes] |
| java:S2119 | [status] | [notes] |

### Dimension 3: Exception Handling

| Rule | Status | Notes |
|------|--------|-------|
| java:S1181 | [status] | [notes] |
| java:S108 | [status] | [notes] |
| java:S1166 | [status] | [notes] |
| java:S1186 | [status] | [notes] |
| java:S131 | [status] | [notes] |

### Dimension 4: Concurrency

| Rule | Status | Notes |
|------|--------|-------|
| java:S2445 | [status] | [notes] |
| java:S2168 | [status] | [notes] |
| java:S3046 | [status] | [notes] |
| java:S1994 | [status] | [notes] |
| java:S2696 | [status] | [notes] |

### Dimension 5: Spring/Config

| Rule | Status | Notes |
|------|--------|-------|
| java:S6818 | [status] | [notes] |
| java:S3776 | [status] | [notes] |
| java:S4601 | [status] | [notes] |
| java:S1192 | [status] | [notes] |
| java:S4524 | [status] | [notes] |

---

## 5. Validation Results

### External Script Validation (validate-report.py)
```
[Paste script output here]
```

### External Gate Calculation (compute-gate.py)
```
[Paste script output here]
```

---

## 6. Appendix: Additional Findings (General Best Practices)

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
Reliability & Maintainability report generated (v1.9 Dimension Scan).
Output: code-review-artifacts/[MODULE]_Reliability_Maintainability_Report_[DATE].md

Dimensions scanned: 5
Candidates found: [n]
After adversarial verification: [n] confirmed, [n] rejected as false positive
After script validation: [n] valid

Quality Gate: [PASS / FAIL] (externally computed)
Issues: Critical=[n], High=[n], Medium=[n] (P0=[n])
```
