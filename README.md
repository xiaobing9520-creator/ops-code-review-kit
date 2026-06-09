# Ops Code Review Kit (v1.8.1)

## What Is This

A code review toolkit built on Kiro (AI IDE). Operations teams use this toolkit
to perform standardized reviews of application code delivered by development
teams, ensuring the system is secure, stable, and maintainable before acceptance.

**This toolkit does NOT require the development team to use Kiro or any specific tool.**
All review work is performed by the operations team in their own environment.

## Key Capabilities

- **One-click batch scan**: A single `@batch-scan` command triggers a full scan of all modules
- **Auto module discovery**: Automatically detects project modules from build system (Maven, Gradle, npm, etc.)
- **2 reports per module**: Reliability & Maintainability + Security
- **Global summary report**: Merges all module scan results with overall Pass/Fail determination
- **Full code scanning**: Every source file is read — no sampling, no skipping, 100% coverage
- **Strict rule mapping**: Every issue must map to a specific Rule ID — no ad-hoc adjustments
- **Quality gate**: Automatic Pass/Fail based on severity thresholds
- **Fix priorities**: P0-P3 classification with defined remediation timelines
- **AI-suggested fix code**: Each finding includes AI-generated corrective code where applicable
- **Word output**: Reports generated in both Markdown and Word (.docx) format

## Report Types

| Report | Review Standards | Coverage |
|--------|-----------------|----------|
| Reliability & Maintainability | SonarQube Java/JavaScript rules (Bug category only; excludes Security & Code Smell) | Blocker / High / Medium |
| Security | Philips Secure Coding Baseline (BSL 11.1.1.d, 230 controls) | 17 security domains |
| Summary | Aggregates all modules | Global Pass/Fail |

An N-module project produces **(2N + 1) reports** in one scan (e.g. 4 modules = 9 reports).
Modules are auto-detected from the project's build system or can be fixed via
an optional `module-manifest.md` file.

## Prerequisites

### Required

1. **Kiro IDE** — Download: https://kiro.dev

### Optional

2. **pandoc** — for Word (.docx) output generation

## Usage

### Step 1: Clone the Target Code

```bash
git clone <repository-url> /path/to/target-project
```

### Step 2: Inject the Review Toolkit

```bash
cp -r ops-code-review-kit-1.8.1/.kiro /path/to/target-project/
```

### Step 3: Run the Review in Kiro

1. Open the target project in Kiro IDE
2. In the AI chat panel, run:

```
@codebase-reverse-engineering
```

Once complete, run the one-click batch scan:

```
@batch-scan
```

**This single command will automatically:**
- Auto-detect all modules from the project structure
- Generate a Reliability & Maintainability report for each module
- Generate a Security report for each module
- Generate a global Summary report

### Step 4: Review the Results

After scanning, all reports are available in the `code-review-artifacts/` directory:

```
code-review-artifacts/
├── reverse-engineering/                              <- Codebase analysis docs
├── [Module1]_Reliability_Maintainability_Report_[date].md
├── [Module1]_Security_Report_[date].md
├── [Module2]_Reliability_Maintainability_Report_[date].md
├── [Module2]_Security_Report_[date].md
├── ...                                               <- 2 reports per module
└── Summary_Report_[date].md                          <- Summary report
```

### Step 5: Post-Fix Rescan

After the development team fixes issues from the initial scan, use `@rescan`
for verification:

**1. Preparation (in the new code version directory):**

```bash
# Copy previous reverse-engineering artifacts (no need to re-run)
cp -r /path/to/previous-version/code-review-artifacts/reverse-engineering/ \
      /path/to/new-version/code-review-artifacts/reverse-engineering/

# Copy previous scan reports as comparison baseline
cp /path/to/previous-version/code-review-artifacts/*_Report_*.md \
   /path/to/new-version/code-review-artifacts/previous-scan/
```

**2. Run the rescan:**

```
@rescan
```

**The rescan will automatically:**
- Verify each previously reported issue for fix completeness
- Assess fix correctness (root cause addressed, not just symptoms)
- Check for regressions introduced by the fixes
- Generate a delta report (FIXED / PARTIALLY FIXED / NOT FIXED / REGRESSED)
- Re-evaluate quality gate status

**Note**: Rescan does NOT require re-running `@codebase-reverse-engineering`,
as architecture and technology stack information typically does not change
during a fix cycle. Re-run it only if the new version includes significant
architectural changes beyond bug fixes.

## Module Discovery

### Auto-Detection (Default)

When no `module-manifest.md` exists, modules are discovered automatically using
the project's build system metadata:

| Priority | Build System | Detection Method |
|----------|-------------|------------------|
| 1 | Maven | `<modules>` in root `pom.xml` |
| 2 | Gradle | `include` in `settings.gradle(.kts)` |
| 3 | npm/pnpm/yarn | `workspaces` in root `package.json` |
| 4 | Nx/Turborepo/Lerna | Workspace config |
| 5 | Go | `go.work` |
| 6 | Directory heuristic | Subdirectories with their own build file |

Discovered modules are sorted alphabetically for determinism.

### Manual Override (Optional)

To fix the module list (e.g. to exclude directories or handle special cases),
create `module-manifest.md` in the project root:

```markdown
| # | Module | Path | Language | Notes |
|---|--------|------|----------|-------|
| 1 | my-backend | my-backend/ | Java | Maven multi-module — scan as ONE |
| 2 | my-frontend | my-frontend/ | JS/Vue | SPA frontend |
```

When this file exists, all skills use it instead of auto-detection.

## Code Scanning Strategy

### Full-Scan (v1.8.1)

v1.8.1 reads **ALL source files** regardless of codebase size. There is no
sampling, no per-package budget, and no tiered selection.

| Scale | File Count | Strategy |
|-------|-----------|----------|
| **Any** | All sizes | Read ALL source files — full scan |

**Why full scan**: The Quality Gate inconsistency analysis (see
`QUALITY_GATE_INCONSISTENCY_ANALYSIS.md`) showed that any form of sampling —
alphabetical or pattern-based — introduces non-determinism when the LLM's file
selection varies between runs. Full scan eliminates this risk entirely: same
codebase = same files read = same findings = same Quality Gate result.

Codebase scale (Small < 50, Medium 50-500, Large > 500) is still recorded in
the output for informational purposes but does not affect scan behavior.

## Report Structure

### Unified Finding Header

Every finding across all report types (R&M / Security / Security Review / Rescan)
begins with the same 4-line header block, ensuring consistent formatting for
cross-report comparison:

```
**Risk Level**: CRITICAL / HIGH / MEDIUM
**CVSS Score**: 9.8 (Critical) / N/A — non-security rule
**File**: `src/main/java/com/example/Config.java:42`
**Associated CVE**: CVE-2016-4437 pattern / N/A — code logic defect (CWE-xxx)
```

### Category Reports (R&M / Security)

Each category report contains:

1. **Report header** — Repository/module name, scan date, review standards, rule ID format
2. **Review summary** — Statistics by category + severity distribution + quality gate status
3. **Issue details** — Each issue includes:
   - Unified header (Risk Level / CVSS Score / File / Associated CVE)
   - Issue ID (e.g., BUG-01, SEC-01)
   - Rule ID + rule description (strictly mapped to SonarQube / BSL rules)
   - File path + code snippet
   - Root cause & business impact
   - Detailed fix recommendation (code-specific)
   - AI-suggested fix code (corrected code snippet, where applicable)
   - Fix priority (P0/P1/P2/P3)
   - Impact of not fixing
4. **Fix priority summary**
5. **Appendix** — LLM-discovered issues that cannot map to the rule set (excluded from quality gate)

### Rescan Reports

Each rescan report contains:

1. **Fix verification results** — Statistics by FIXED / PARTIALLY FIXED / NOT FIXED / REGRESSED
2. **Fix rate** — Total issues, fixed count, fix percentage
3. **Per-issue verification details** — Fix status and assessment for each previous finding
4. **Regressions** — New issues introduced during the fix process
5. **Remaining open issues list**

### Summary Report

- Per-module x per-report-type Pass/Fail summary
- All module issues merged into a single detail table
- Global fix priority distribution

## Quality Gate

### Shared Quality Gate (applies to both R&M and Security Reports)
```
FAIL if ANY of the following is true:
  - severity = Critical  (any priority)
  - severity = High  AND  priority = P0

PASS if none of the above conditions are met.

Note: Medium issues are tracked but never block the gate.
High issues with P1/P2/P3 do NOT block the gate.
```

The Summary Report's overall gate is PASS only if ALL individual reports PASS.

## Fix Priority Definitions

| Priority | Meaning | Typical Scenarios |
|----------|---------|-------------------|
| **P0** | Must fix before release | Affects correctness or security |
| **P1** | Short-term fix (1-2 weeks) | High risk but not blocking current release |
| **P2** | Medium-term fix (1 month) | Code quality issues with some risk |
| **P3** | Long-term optimization | Low risk, technical debt |

Medium-severity issues must have an explicit P0-P3 label. Medium issues do
NOT affect the quality gate regardless of priority.

## Rule Sources

### SonarQube Rules (Reliability & Maintainability Report)

- Standards files: `.kiro/rules/sonarqube-java-standards.md` (341 rules) / `.kiro/rules/sonarqube-javascript-standards.md`
- **Scope**: Bug category only — Security rules and Code Smell rules are excluded
- Covers Blocker, High, and Medium severity levels
- Every issue's rule ID, name, and severity strictly follows the rule definition
- Issues that cannot map to a specific Rule ID are excluded from the main report

### Philips Secure Coding Baseline (Security Report)

- BSL 11.1.1.d Version 3 (October 2025)
- 230 security controls across 17 security domains
- Every issue maps to a specific BSL Control ID (e.g., `11.1.1_41`)

### LLM-Discovered Issue Isolation

Issues found outside the SonarQube / BSL rule sets are not mixed into the main
report. They are collected in the Appendix section at the end of each report
and do not affect the quality gate.

## Step-by-Step Execution

If you prefer not to use the one-click batch scan, you can run each step manually:

```
@codebase-reverse-engineering     <- 1. Analyze the codebase (must run first)
@sonarqube-review                 <- 2. Generate R&M report for a specific module
@secure-coding-baseline-review    <- 3. Generate Security report for a specific module
@summary-report                   <- 4. Generate summary report
@rescan                           <- 5. Post-fix verification scan (optional, after fixes)
```

### Optional: Supplementary Review (Deep Analysis)

These skills provide analysis beyond the two core report types, using BSL
Appendix A-G as review standards:

```
@security-review          <- OWASP/CWE security analysis (CVSS v3.1 scoring + CVE association)
@acceptance-report        <- Combined acceptance decision (all dimensions)
```

## Output Format

Reports are generated in **both Markdown and Word (.docx)** format:

- Markdown: Primary working format, viewable in Kiro / GitHub / any editor
- Word (.docx): Final deliverable for stakeholders, generated via `pandoc`

**Prerequisite for Word output**: Install [pandoc](https://pandoc.org/installing.html):
```bash
# macOS
brew install pandoc

# Ubuntu / Debian
sudo apt install pandoc

# Amazon Linux
sudo yum install pandoc
```

If `pandoc` is not available, the scan completes normally but Word conversion is skipped.

## FAQ

**Q: What if the development team doesn't use Kiro?**
A: The development team does not need to use Kiro. The `.kiro/` directory is the
operations team's review toolkit and is not committed to the development team's repository.

**Q: Can I use this on any project?**
A: Yes. v1.8 auto-detects modules from the build system. Just copy the `.kiro/`
directory into any project and run. No configuration required for standard
Maven/Gradle/npm/Go projects.

**Q: Can I scan only specific modules?**
A: Yes. Use `@batch-scan module1 module2` to specify module names. You can also
use `@sonarqube-review` and `@secure-coding-baseline-review` to scan modules individually.

**Q: How do I fix the module list for a project?**
A: Create a `module-manifest.md` file in the project root with a table of
modules. When present, this overrides auto-detection. See the "Module Discovery"
section above.

**Q: How do I update the SonarQube rule set?**
A: Export the latest rule configuration (JSON format) from your organization's
SonarQube system, then update `.kiro/rules/sonarqube-java-standards.md`,
`.kiro/rules/sonarqube-javascript-standards.md`, and the corresponding JSON files.

**Q: How are severity levels defined in the reports?**
A: SonarQube: Blocker -> Critical, High -> High, Medium -> Medium.
BSL Security reports use CVSS v3.1 scoring: 8 metrics (AV/AC/PR/UI/S/C/I/A)
produce a vector score — 9.0-10.0 -> Critical, 7.0-8.9 -> High, 4.0-6.9 -> Medium,
0.1-3.9 -> Low. Every security issue includes the full CVSS vector string and
associated CVE identifier.

**Q: Should I fix issues in the Appendix?**
A: Appendix issues come from LLM general best practice analysis and are outside
the specified rule set. They do not affect the quality gate. Treat them as
advisory and address at your discretion.

**Q: What if the quality gate fails?**
A: Check the P0 issues list in the Summary Report — these must be fixed. After
fixes are applied, use `@rescan` for verification (no need to re-run
`@codebase-reverse-engineering`).

**Q: Does the post-fix rescan require re-running reverse engineering?**
A: No. Copy the previous `code-review-artifacts/reverse-engineering/` directory
into the new code version directory. `@rescan` will use these artifacts
automatically. Only re-run reverse engineering if the new version includes
significant architectural changes.

**Q: How does a rescan differ from an initial scan?**
A: `@rescan` focuses on fix verification, not a full re-scan. It checks each
previous finding for fix completeness, assesses fix correctness, and detects
regressions. It produces a delta report rather than a full report.

**Q: What changed in v1.8.1's code scanning approach?**
A: v1.8.1 eliminates all file sampling entirely. Every source file is read
regardless of codebase size. This guarantees 100% code coverage and fully
deterministic results — no file is ever skipped due to budget caps or
selection heuristics.

## Version History

| Version | Key Changes |
|---------|-------------|
| v1.8.1 | Full-scan mode — read ALL source files, no sampling regardless of codebase size |
| v1.8 | Architecture-Role Pattern Matching; open module discovery; bug fixes |
| v1.77 | Auth leaf-implementation tracing (password hashing, token issuance) |
| v1.76 | Two-plane architecture topology fix; 4-diagram specification |
| v1.75 | Merged v1.65 + v1.7; quality gate recalibration; R&M validator |
| v1.7 | Determinism rules D1-D7; HTML diagram preview |
| v1.6 | Initial release with BSL + SonarQube dual-standard review |
