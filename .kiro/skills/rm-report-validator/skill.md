---
name: rm-report-validator
description: >
  Validates Reliability & Maintainability reports against the SonarQube rule
  definitions. Enforces rule existence and strict severity mapping. Detects and
  corrects: undefined rule IDs, wrong severity labels, and findings that belong
  in the Appendix. Prevents future inconsistencies by embedding validation logic
  directly into the review workflow.
---

# R&M Report Validator

You are a code review quality auditor. Your job is to validate one or more
Reliability & Maintainability (R&M) reports against the organization's
SonarQube rule definitions and correct any inconsistencies found.

## When to Use This Skill

- After generating a new R&M report (run as a post-generation check)
- When a report is flagged for rule inconsistencies
- Before finalizing any R&M report for delivery

---

## Rule Definition Sources

| Language | Standards File |
|----------|---------------|
| Java | `.kiro/rules/sonarqube-java-standards.md` |
| JavaScript / TypeScript | `.kiro/rules/sonarqube-javascript-standards.md` |

Always load the correct standards file for the module's language before
performing any validation.

---

## Validation Rules

### V-01: Rule Existence Check

**Every rule ID cited in the main findings (not Appendix) MUST exist in the
standards file for the module's language.**

Procedure:
1. Extract every rule ID from the Findings Summary table (e.g., `javascript:S1854`)
2. Search the standards file for `### <ruleId> —`
3. If NOT found → the finding MUST be moved to the Appendix

**Examples of rules that do NOT exist in the JavaScript standards and must
never appear in the main findings of a JavaScript R&M report:**
- `javascript:S106` (no such rule — console.log issues are LLM-discovered)
- `javascript:S1066` (no such rule in JS — exists only in Java standards)

**Examples of rules that do NOT exist in the Java standards and must never
appear in the main findings of a Java R&M report:**
- Any rule ID not found by searching `### java:Sxxxx —` or `### javasecurity:Sxxxx —`

---

### V-02: Strict Severity Mapping

**Every finding's severity label MUST exactly match the severity defined in
the standards file. No overrides, upgrades, downgrades, or inferences.**

Severity mapping (from standards file to report label):

| Standards File Severity | Report Severity Label |
|-------------------------|-----------------------|
| Blocker | Critical |
| High | High |
| Medium | Medium |

Procedure:
1. For each finding in the main body, look up its rule ID in the standards file
2. Read the `**Severity**: <value>` line for that rule
3. Map: Blocker → Critical, High → High, Medium → Medium
4. If the report uses a different label → correct it

**Common errors to detect:**
- Rule defined as `Blocker` but report says `High` (e.g., `java:S2755`, `java:S2115`, `javascript:S2189`)
- Rule defined as `Medium` but report says `High` (e.g., `javascript:S1854`, `java:S1854`)
- Rule defined as `High` but report says `Critical`

---

### V-03: Rule Description Accuracy

**The rule description used in a finding MUST match the actual rule title in
the standards file.**

Procedure:
1. For each finding, check the rule description against the standards file
2. If the description does not match the rule's actual title → the finding is
   using the wrong rule ID
3. Wrong-rule findings MUST be moved to the Appendix (they are LLM-discovered)

**Common error pattern**: Using `java:S3305` (Factory method injection in
@Configuration classes) to report outdated dependencies — these are different
concerns. Outdated dependency findings have no matching SonarQube rule and
belong in the Appendix.

---

### V-04: Quality Gate Recalculation

After correcting findings (moving invalid ones to Appendix, fixing severities),
recalculate the Quality Gate:

```
Critical count = number of findings with severity Critical remaining in main body
High count     = number of findings with severity High remaining in main body
Medium P0 count = number of Medium findings with Fix Priority P0

Quality Gate PASS if: Critical == 0 AND High == 0 AND Medium P0 == 0
Otherwise: FAIL
```

Update the Quality Gate table and Findings Summary table to reflect corrected counts.

---

### V-05: Appendix Labeling

All findings moved to the Appendix MUST be labeled:

```
- **Source**: General best practices (not in SonarQube [Java/JavaScript] rule set)
```

They MUST NOT carry a SonarQube rule ID. They do NOT count toward the quality gate.

---

## Validation Workflow

### Step 1: Load Standards

Read the applicable standards file for the module's language. Build a lookup
map: `ruleId → severity`.

### Step 2: Extract Findings

From the report's Findings Summary table, extract all rows with:
- Finding ID (BUG-xx)
- Rule ID
- Severity label
- Fix Priority

### Step 3: Run V-01 (Existence Check)

For each rule ID:
- Search standards file for `### <ruleId> —`
- If not found: flag as UNDEFINED → queue for Appendix move

### Step 4: Run V-02 (Severity Check)

For each rule ID that passed V-01:
- Look up severity in standards file
- Map to report label (Blocker→Critical, High→High, Medium→Medium)
- If report label differs: flag as SEVERITY_MISMATCH → correct in place

### Step 5: Run V-03 (Description Check)

For each rule ID that passed V-01:
- Compare finding's rule description to standards file rule title
- If mismatch: flag as WRONG_RULE → queue for Appendix move

### Step 6: Apply Corrections

1. Move all UNDEFINED and WRONG_RULE findings to Appendix with proper labeling
2. Correct all SEVERITY_MISMATCH findings in place
3. Renumber remaining BUG-xx entries sequentially
4. Recalculate Quality Gate (V-04)
5. Update Findings Summary table

### Step 7: Output Validation Report

Print a concise validation summary:

```
## Validation Summary

Module: [module name]
Standards: [sonarqube-java-standards / sonarqube-javascript-standards]

| Check | Finding | Issue | Action Taken |
|-------|---------|-------|--------------|
| V-01  | BUG-xx  | Rule javascript:S106 not found in standards | Moved to Appendix |
| V-02  | BUG-xx  | javascript:S1854 severity was High, should be Medium | Corrected to Medium |
| V-03  | BUG-xx  | java:S3305 description mismatch (wrong rule for finding) | Moved to Appendix |

Quality Gate (before): Critical=[n], High=[n]
Quality Gate (after):  Critical=[n], High=[n]
```

---

## Integration with sonarqube-review Skill

When generating a new R&M report using `@sonarqube-review`, the following
self-validation steps from this skill MUST be embedded as **Step 4: Self-Validation**
(already referenced in the sonarqube-review skill):

1. **Rule ID check** (V-01): Every issue's rule key exists in the standards file
2. **Severity check** (V-02): Every issue's severity matches the standards file exactly
3. **Description check** (V-03): Rule description matches the actual rule title
4. **Priority check**: Every Medium issue has an explicit P0–P3 label
5. **Appendix check** (V-05): Any issue without a valid rule ID is in the Appendix with correct labeling

These checks MUST be performed before writing the final report. Do not skip
them even if the findings seem obvious.

---

## Known Rule Pitfalls

The following rules have been historically misused. Pay special attention:

### JavaScript

| Rule ID | Actual Definition | Common Misuse |
|---------|------------------|---------------|
| `javascript:S106` | Does NOT exist in JS standards | Incorrectly used for console.log findings |
| `javascript:S1066` | Does NOT exist in JS standards (exists only in Java) | Incorrectly used for dead code / config issues |
| `javascript:S1854` | Exists — severity **Medium** | Incorrectly reported as High |
| `javascript:S2189` | Exists — severity **Blocker** (→ Critical) | Incorrectly reported as High |

### Java

| Rule ID | Actual Definition | Common Misuse |
|---------|------------------|---------------|
| `java:S3305` | Factory method injection in @Configuration classes — severity **High** | Incorrectly used for "outdated dependencies" findings |
| `java:S2755` | XML parsers / XXE — severity **Blocker** (→ Critical) | Incorrectly reported as High |
| `java:S2115` | Database password security — severity **Blocker** (→ Critical) | Incorrectly used for framework EOL findings, and reported as High |
| `java:S1854` | Unused assignments — severity **Medium** | May be incorrectly reported as High |
| `java:S1066` | Mergeable if statements — severity **Medium** | May be incorrectly reported as High |
