---
name: batch-scan
description: >
  One-click batch scan: triggers full code review for all modules in the
  project. Generates 2 reports per module (Reliability & Maintainability +
  Security) plus 1 global Summary Report. 9 reports total for 4 modules.
---

# Batch Scan — One-Click Full Project Review

You are the operations team's automated scanning orchestrator. When invoked,
perform a complete code review of **all modules** in the project and generate
all reports automatically.

## What This Skill Does

For a project with N modules, this skill:
1. Identifies all modules in the project
2. For each module, generates:
   - **Reliability & Maintainability Report** (SonarQube rules)
   - **Security Report** (Philips BSL 11.1.1.d)
3. Generates a global **Summary Report** combining all modules
4. Total output: (N × 2) + 1 reports

For a typical 4-module project: **9 reports**, one command.

## Prerequisites

- The project must be open in Kiro
- `.kiro/` configuration must be present in the project root
- Codebase reverse engineering should be done first. If
  `code-review-artifacts/reverse-engineering/` does not exist, run
  `@codebase-reverse-engineering` first before proceeding.

## Output Directory

All reports go to `code-review-artifacts/` at the project root:

```
code-review-artifacts/
├── [Module1]_Reliability_Maintainability_Report_[date].md
├── [Module1]_Security_Report_[date].md
├── [Module2]_Reliability_Maintainability_Report_[date].md
├── [Module2]_Security_Report_[date].md
├── [Module3]_Reliability_Maintainability_Report_[date].md
├── [Module3]_Security_Report_[date].md
├── [Module4]_Reliability_Maintainability_Report_[date].md
├── [Module4]_Security_Report_[date].md
└── Summary_Report_[date].md
```

---

## Execution Process

### Step 1: Identify Modules

Module discovery is **deterministic** and driven by the Canonical Module
Manifest in `.kiro/steering.md`. Do NOT re-derive the module set from build
files, and do NOT split a module into its sub-projects.

Procedure:
1. Read the Canonical Module Manifest table in `.kiro/steering.md`.
2. Use exactly those modules, in that order, with those exact names and paths.
3. A top-level directory that contains nested sub-projects (e.g.
   `lab-manage-backend` → `lab-admin` + `lab-fss-admin`) is still ONE module.
   Aggregate all sub-project findings into that single module's two reports.
4. Never treat `.kiro/` or `code-review-artifacts/` as a module.

This guarantees the same module set (4 modules → 9 reports) on every run, which
is required for a reproducible Summary Report.

If — and only if — the manifest is absent (different project), fall back to:
top-level application directories under the project root, each scanned as one
module, never split into sub-projects. List them and proceed without splitting.

Output the modules being used:
```
Modules (from Canonical Module Manifest):
  1. lab-backend         — lab-backend/
  2. lab-manage-backend  — lab-manage-backend/  (incl. lab-admin + lab-fss-admin)
  3. lab-admin-web       — lab-admin-web/
  4. lab-wxapp           — lab-wxapp/

Proceeding with scan...
```

### Step 2: Process Each Module

For each module, IN SEQUENCE:

#### 2.1 Understand the Module
- Read the module's source structure
- Identify programming languages
- Identify frameworks (Spring, Express, etc.)
- Determine applicable rule sets

#### 2.2 Generate Reliability & Maintainability Report

Apply the `@sonarqube-review` skill logic for this module:
- Check against SonarQube rules from `.kiro/rules/sonarqube-*-standards.md`
- Strict rule-to-ID mapping
- Quality gate evaluation
- Fix priority assignment (P0–P3)
- LLM-discovered issues to appendix

After generating, run the `@rm-report-validator` validation checks inline:
- V-01: Confirm every rule ID exists in the standards file — move undefined rules to Appendix
- V-02: Confirm every severity label matches the standards file exactly — correct any mismatch
- V-03: Confirm every rule description matches the actual rule title — move wrong-rule findings to Appendix
- Recalculate Quality Gate if any corrections were made

Save as: `code-review-artifacts/[ModuleName]_Reliability_Maintainability_Report_[YYYY-MM-DD].md`

#### 2.3 Generate Security Report

Apply the `@secure-coding-baseline-review` skill logic for this module:
- Check against BSL 11.1.1.d controls from `.kiro/rules/secure-coding-baseline-standards.md`
- Strict control-to-ID mapping
- Quality gate evaluation
- Fix priority assignment (P0–P3)
- LLM-discovered issues to appendix

MANDATORY CVSS CHECK: After generating each Security Report, verify that EVERY
finding contains `**CVSS Score**:` as a standalone line (not a list item). If
any finding is missing `**CVSS Score**`, add it before saving the report.

Save as: `code-review-artifacts/[ModuleName]_Security_Report_[YYYY-MM-DD].md`

#### 2.4 Progress Update

After each module, output progress:
```
[n/N] Module "[name]" complete.
  R&M: [PASS/FAIL] — Critical=[n], High=[n], Medium=[n]
  Security: [PASS/FAIL] — Critical=[n], High=[n], Medium=[n]
```

### Step 3: Generate Summary Report

After all modules are processed, apply the `@summary-report` skill logic:
- Read all module-level reports
- Aggregate into Summary_Report_[date].md
- Compute overall quality gate

### Step 4: Convert to Word Format

After all Markdown reports are generated, convert each to Word (`.docx`) format:

```bash
for f in code-review-artifacts/*.md; do
  pandoc "$f" -o "${f%.md}.docx" --reference-doc=.kiro/reference.docx 2>/dev/null || \
  pandoc "$f" -o "${f%.md}.docx"
done
```

If `pandoc` is not available, report that Word conversion was skipped and
instruct the user to install it.

### Step 5: Final Output

```
============================================
  Batch Scan Complete
============================================

Modules scanned: [n]
Reports generated: [2n + 1] (Markdown + Word)

Overall Quality Gate: [PASS / FAIL]

Module Results:
  [Module1]: R&M=[Pass/Fail], Security=[Pass/Fail]
  [Module2]: R&M=[Pass/Fail], Security=[Pass/Fail]
  [Module3]: R&M=[Pass/Fail], Security=[Pass/Fail]
  [Module4]: R&M=[Pass/Fail], Security=[Pass/Fail]

Total Issues: [n]
  Critical: [n]
  High:     [n]
  Medium:   [n]
  P0 (release blockers): [n]

Reports (Markdown + Word):
  code-review-artifacts/[Module1]_Reliability_Maintainability_Report_[date].md (.docx)
  code-review-artifacts/[Module1]_Security_Report_[date].md (.docx)
  code-review-artifacts/[Module2]_Reliability_Maintainability_Report_[date].md (.docx)
  code-review-artifacts/[Module2]_Security_Report_[date].md (.docx)
  code-review-artifacts/[Module3]_Reliability_Maintainability_Report_[date].md (.docx)
  code-review-artifacts/[Module3]_Security_Report_[date].md (.docx)
  code-review-artifacts/[Module4]_Reliability_Maintainability_Report_[date].md (.docx)
  code-review-artifacts/[Module4]_Security_Report_[date].md (.docx)
  code-review-artifacts/Summary_Report_[date].md (.docx)

Word conversion: [Completed / Skipped — pandoc not available]
============================================
```

---

## Cross-Module Format Consistency

All module reports MUST follow identical formatting to ensure side-by-side
comparability. Before generating reports, enforce:

1. **Unified Finding Header**: Every finding across ALL modules and report types
   MUST begin with the same 4-line header block (Risk Level / CVSS Score / File / Associated CVE).
   See Constraint 0 in each sub-skill for the exact template.

2. **Identical Section Structure**: Every R&M report has the same sections in the
   same order, and every Security report has the same sections in the same order,
   regardless of the module or its technology stack.

3. **Consistent Severity Labels**: Use only `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`.
   Never use alternative labels (Blocker, Major, Minor, etc.) in any report.

4. **Consistent Numbering**: Issue IDs within each report type use the same prefix
   pattern — `BUG-nn` for R&M, `SEC-nn` for Security.

5. **Self-Validation Step**: After generating all module reports and before
   generating the Summary Report, spot-check 2 modules to confirm their report
   structures are identical in section order and finding header format. Specifically
   verify that every finding contains all 4 mandatory header lines in this order:
   `**Risk Level**` → `**CVSS Score**` → `**File**` → `**Associated CVE**`.
   If `**CVSS Score**` is missing from any finding, add it before proceeding.

---

## Important Notes

- Each module is processed independently — issues in one module do not
  affect another module's quality gate
- The Summary Report's overall quality gate is the AND of all individual gates
- If context window is a concern for very large modules, focus scanning on
  core source code, entry points, and security-sensitive paths
- Report dates use the scan date, not the current date at report generation
