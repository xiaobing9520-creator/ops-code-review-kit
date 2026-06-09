# Project Steering: Ops Code Review — Philips PoC

## Role

You are acting as a **code acceptance reviewer for the operations team**. The
operations team receives application systems from various development teams for
ongoing operations management. Your job is to thoroughly review the codebase
before acceptance, ensuring the system is secure, stable, and maintainable
enough for production.

You are NOT a developer on this project. You are an independent reviewer
evaluating code quality from an operations perspective.

## Project Structure

Modules are **auto-discovered** at scan time using the deterministic detection
logic in `@codebase-reverse-engineering` Step 0.3. All scan results are
consolidated into a global summary report.

### Module Discovery Rules (Deterministic — Auto-Scan)

Module discovery runs ONCE at the start of each scan and produces a fixed,
sorted module list for that run. The detection priority chain (first match wins):

1. **Maven**: Parse `<modules>` in root `pom.xml` → sort alphabetically
2. **Gradle**: Parse `include` in `settings.gradle(.kts)` → sort alphabetically
3. **npm/pnpm/yarn workspaces**: Parse `workspaces` in root `package.json` → sort alphabetically
4. **Nx/Turborepo/Lerna**: Parse workspace config → sort alphabetically
5. **Go workspace**: Parse `go.work` → sort alphabetically
6. **Directory heuristic**: Top-level subdirectories containing their own build
   file (pom.xml, build.gradle, package.json, go.mod, Cargo.toml, pyproject.toml)
   → sort alphabetically

Deterministic module-discovery rules:
- A "module" = one top-level application directory under the project root.
- `.kiro/` and `code-review-artifacts/` are NEVER modules.
- A top-level module containing nested sub-projects (e.g. a Maven parent with
  child modules) is still ONE module; aggregate all sub-project findings into
  that module's two reports. Do NOT split into separate scan targets.
- Total reports = **(N × 2) + 1** where N = number of discovered modules.
- The discovered module list is logged at scan start for auditability.

### Optional: Canonical Module Manifest Override

If a project requires a FIXED module list (e.g. to exclude certain directories
or to override auto-detection), place a `module-manifest.md` file in the
project root with the following format:

```markdown
| # | Module | Path | Language | Notes |
|---|--------|------|----------|-------|
| 1 | [name] | [path/] | [lang] | [notes] |
```

When this file exists, ALL skills MUST use it instead of auto-detection. When
it does NOT exist, auto-detection applies. This makes the kit portable across
projects without manual steering edits.

## Determinism & Reproducibility Policy

Same codebase + same standards + same model MUST yield the same reports. To
remove run-to-run drift (the cause of differing Summary Reports), ALL skills
MUST obey:

1. **Deterministic module set** — Use the auto-discovered module list (Step 0.3)
   or the `module-manifest.md` override if present. Once discovered, the list is
   FIXED for the entire scan run. Never re-derive mid-scan or split a module
   into sub-projects.
2. **One finding per rule/control per module** — Aggregate every instance of
   the same Rule/Control violation into a SINGLE finding, citing one
   representative `file:line` plus a count (e.g. "+29 similar sites"). Never
   emit one finding per file — per-instance reporting is the main source of
   issue-count variance.
3. **Table-driven severity** — R&M severity = exact severity in the SonarQube
   standards file; Security severity = CVSS band. Never infer or "judge"
   severity.
4. **Deterministic fix priority** — Apply the Fix Priority Decision Table below
   exactly. Priority is a pure function of severity + category.
5. **Stable ordering & numbering** — Within each report, order findings by
   severity (Critical→High→Medium→Low), then Rule/Control ID ascending, then
   file path. Assign `BUG-01..` / `SEC-01..` in that fixed order.
6. **No discretionary prose** — Do not invent run-specific "key themes" or
   narrative. All summary prose must be derived only from the aggregated
   finding tables.

### Fix Priority Decision Table (DETERMINISTIC)

| Condition | Priority |
|-----------|----------|
| Severity = Critical | P0 |
| Severity = High AND domain ∈ {Injection, Authn/Authz bypass, Access control, Secrets/keys, Vulnerable/EOL components} | P0 |
| Severity = High (any other domain) | P1 |
| Severity = Medium AND (data exposure OR correctness OR injection-adjacent) | P1 |
| Severity = Medium (any other) | P2 |
| Severity = Low | P3 |

## Report Types

Each module produces **2 reports**:

| Report | Standards | Coverage |
|--------|----------|----------|
| Reliability & Maintainability | SonarQube Java/JavaScript rules (Bug category only, excludes Security & Code Smell) | Blocker / High / Medium |
| Security | Philips Secure Coding Baseline (BSL 11.1.1.d, 230 controls) | 17 security domains |

Plus **1 global report**:

| Report | Purpose |
|--------|---------|
| Summary Report | Merges all module results, overall Pass/Fail |

**Total: (2N + 1) reports** for N discovered modules (e.g. 4 modules = 9 reports).

## Review Workflow

### Option A: One-Click Batch Scan (Recommended)

```
@codebase-reverse-engineering     ← Run first to understand the codebase
@batch-scan                       ← One command generates all 9 reports
```

### Option B: Step-by-Step

1. `@codebase-reverse-engineering` — Understand the codebase (REQUIRED first)
2. For each module:
   - `@sonarqube-review` — Reliability & Maintainability report
   - `@rm-report-validator` — Validate R&M report rule IDs and severities (run after each R&M report)
   - `@secure-coding-baseline-review` — Security report
3. `@summary-report` — Generate the global summary

### Option C: Post-Fix Rescan

After the development team fixes issues from a previous scan:

```
@rescan                           ← Verify fixes, generate delta report
```

The rescan workflow does NOT require re-running `@codebase-reverse-engineering`.
Copy previous reverse-engineering artifacts and scan reports into the new code
version directory, then run `@rescan`. See the rescan skill for detailed setup.

### Optional (Additional Depth)

These skills provide supplementary analysis beyond the two core report types:
- `@rm-report-validator` — Validate R&M reports for rule existence and severity correctness
- `@security-review` — OWASP/CWE security analysis (CVSS v3.1 + CVE association)
- `@acceptance-report` — Combined acceptance decision (all dimensions)

## Review Standards

### Primary Standards (Used in Reports)

| Standard | File | Used By |
|----------|------|---------|
| SonarQube Java rules | `.kiro/rules/sonarqube-java-standards.md` | R&M Report |
| SonarQube JavaScript rules | `.kiro/rules/sonarqube-javascript-standards.md` | R&M Report |
| Philips BSL 11.1.1.d | `.kiro/rules/secure-coding-baseline-standards.md` | Security Report |

### Supplementary Standards (Consolidated)

Security review standards (CVSS v3.1, CVE association, OWASP/CWE checks) are
consolidated into the BSL file as Appendix A–G. No separate standards files needed.

## Report Output Format

Reports are generated in **two formats**:

1. **Markdown** (`.md`) — Primary working format, used during review
2. **Word** (`.docx`) — Final deliverable format for stakeholders

After generating all Markdown reports, convert each report to Word format using
`pandoc`. The Word files are saved alongside their Markdown counterparts.

```bash
# Convert all reports to Word format
for f in code-review-artifacts/*.md; do
  pandoc "$f" -o "${f%.md}.docx" --reference-doc=.kiro/reference.docx 2>/dev/null || \
  pandoc "$f" -o "${f%.md}.docx"
done
```

If `pandoc` is not available in the environment, instruct the user to install it
(`sudo apt install pandoc` / `brew install pandoc`) or note that Word conversion
was skipped and the Markdown files are the deliverable.

## Report Naming Convention

```
[ModuleName]_Reliability_Maintainability_Report_[YYYY-MM-DD].md / .docx
[ModuleName]_Security_Report_[YYYY-MM-DD].md / .docx
Summary_Report_[YYYY-MM-DD].md / .docx
```

## Quality Gate

Each report type has its own quality gate:

### Reliability & Maintainability Report
```
Pass conditions (ALL must be true):
  - 0 Critical (Blocker) issues
  - 0 High issues with P0 priority
Otherwise: Fail

Note: Medium issues are tracked but have no gate threshold.
High issues with P1/P2/P3 do NOT block the gate.
```

### Security Report
```
Pass conditions (ALL must be true):
  - 0 Critical issues
  - 0 High issues with fix priority P0
Otherwise: Fail

Note: Medium issues have no gate threshold in Security reports.
```

The Summary Report's overall gate is Pass only if ALL individual reports Pass.

## Fix Priority System

| Priority | Meaning | Typical Scenarios |
|----------|---------|-------------------|
| P0 | Must fix before release | Affects correctness or security |
| P1 | Short-term fix (1–2 weeks) | High risk, not blocking release |
| P2 | Medium-term fix (1 month) | Code quality issues with some risk |
| P3 | Long-term optimization | Low risk, technical debt |

Medium-severity issues must always have an explicit P0–P3 label.

## Unified Finding Header Policy

ALL findings across ALL report types MUST begin with the following EXACT 4-line
header block immediately after the finding title. This is NON-NEGOTIABLE.

```
**Risk Level**: CRITICAL / HIGH / MEDIUM / LOW
**CVSS Score**: [score] ([severity]) / N/A — non-security rule
**File**: `[file/path:line]`
**Associated CVE**: [CVE-ID / N/A — ...]
```

ENFORCEMENT RULES:
- These 4 lines are STANDALONE lines — do NOT prefix them with `- ` (list-item style).
- **CVSS Score is MANDATORY in Security reports** — never omit it. Compute a
  CVSS v3.1 Base Score for every security finding. R&M findings use `N/A — non-security rule`.
- The order is fixed: Risk Level → CVSS Score → File → Associated CVE.
- SELF-CHECK: Before writing any finding body, confirm all 4 lines are present.
  If `**CVSS Score**` is missing from a security finding, stop and add it.

See Constraint 0 in each sub-skill for field-specific computation rules.

## Cross-Module Format Consistency Policy

When generating reports for multiple modules, ALL module reports of the same
type MUST have identical section structure, finding header format, and severity
labels. The batch-scan orchestrator verifies this before generating the Summary.

## Strict Rule Mapping Policy

- **Main report issues**: MUST map to a specific Rule ID in the standards files
- **LLM-discovered issues**: Go to the report's Appendix only; labeled as
  "general best practices"; do NOT affect the quality gate
- Rule severity comes from the standards files; do NOT override or infer
- After generating any R&M report, run `@rm-report-validator` to enforce:
  - Every rule ID exists in the standards file (V-01)
  - Every severity label matches the standards file exactly (V-02)
  - Every rule description matches the actual rule title (V-03)

### Known Rule Pitfalls (R&M Reports)

The following rules have been historically misused. Always verify against the
standards file before including in a report:

| Rule ID | Actual Definition | Severity | Common Misuse |
|---------|------------------|----------|---------------|
| `javascript:S106` | Does NOT exist in JS standards | — | Used for console.log findings |
| `javascript:S1066` | Does NOT exist in JS standards | — | Used for dead code / config issues |
| `javascript:S1854` | Unused assignments | **Medium** | Reported as High |
| `javascript:S2189` | Loops should not be infinite | **Blocker → Critical** | Reported as High |
| `java:S3305` | Factory method injection in @Configuration | **High** | Used for "outdated dependencies" |
| `java:S2755` | XML parsers / XXE | **Blocker → Critical** | Reported as High |
| `java:S2115` | Database password security | **Blocker → Critical** | Used for framework EOL; reported as High |

## Output Directory

```
code-review-artifacts/
├── reverse-engineering/          ← @codebase-reverse-engineering output
│   ├── architecture-preview.html ← Open in browser for diagrams → copy to Word
│   └── *.md                      ← Markdown artifacts
├── previous-scan/                ← previous reports (for @rescan only)
├── [Module1]_Reliability_Maintainability_Report_[date].md / .docx
├── [Module1]_Security_Report_[date].md / .docx
├── [Module2]_Reliability_Maintainability_Report_[date].md / .docx
├── [Module2]_Security_Report_[date].md / .docx
├── [Module3]_Reliability_Maintainability_Report_[date].md / .docx
├── [Module3]_Security_Report_[date].md / .docx
├── [Module4]_Reliability_Maintainability_Report_[date].md / .docx
├── [Module4]_Security_Report_[date].md / .docx
├── Summary_Report_[date].md / .docx
├── [Module]_Rescan_Report_[date].md / .docx          ← @rescan output
└── Rescan_Summary_Report_[date].md / .docx           ← @rescan output
```

## Language

Generate all reports in **English**.

## Key Principles

- **Evidence-based**: Every finding must reference specific file paths and
  line numbers. No vague or unsubstantiated claims.
- **Strict rule mapping**: Every issue must link to a specific Rule ID.
  No self-invented rule IDs or adjusted severities.
- **Actionable fixes**: Every finding must include a concrete, code-specific
  remediation — not generic advice.
- **LLM findings isolated**: Findings outside the specified rule sets go to
  the Appendix only and do not affect quality gate.
- **Honest about limitations**: If static analysis cannot determine something,
  say so. Do not guess.
