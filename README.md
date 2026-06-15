# Ops Code Review Kit (v1.10)

## What Is This

A code review toolkit built on Kiro (AI IDE). Operations teams use this toolkit
to perform standardized reviews of application code delivered by development
teams, ensuring the system is secure, stable, and maintainable before acceptance.

**This toolkit does NOT require the development team to use Kiro or any specific tool.**
All review work is performed by the operations team in their own environment.

## Key Capabilities

- **One-click batch scan**: A single `@batch-scan` command triggers a full 5-phase scan
- **5-Phase Architecture**: RE + File Manifest → Context Planning → Agent A Scan → Agent B Verify → Report Assembly
- **Structural determinism**: Files are assigned to context windows algorithmically — the LLM never decides which files to read
- **File Manifest with grep signals**: Per-file descriptions + security/quality signals enable completeness verification
- **Agent A/B pattern**: Primary scanner + independent adversarial verifier eliminates false positives and catches omissions
- **Auto module discovery**: Automatically detects project modules from build system (Maven, Gradle, npm, etc.)
- **3 reports per module**: Reliability & Maintainability + Security + Verification
- **Global summary report**: Merges all module results with overall Pass/Fail
- **Context window planning**: Deterministic batch assignment respecting dependency graphs and token budgets
- **Signal-driven completeness**: grep-generated signals guarantee known vulnerability patterns are never missed
- **External validation scripts**: Python scripts verify rule IDs and compute Quality Gate deterministically
- **Strict rule mapping**: Every issue must map to a specific Rule ID — no ad-hoc adjustments
- **Quality gate**: Automatic Pass/Fail computed by external script (not LLM judgment)
- **Fix priorities**: P0-P3 classification with defined remediation timelines
- **AI-suggested fix code**: Each finding includes AI-generated corrective code
- **Word output**: Reports generated in both Markdown and Word (.docx) format

## Architecture (v1.10)

```
Phase 1: Reverse Engineering + File Manifest
           ├── Architecture docs (business-overview, tech-stack, data-flow, etc.)
           └── file-manifest.json (per-file descriptions + grep signals)

Phase 2: Context Window Planning (scan-planner.py)
           └── scan-plan.json (deterministic batch assignment)

Phase 3: Primary Scan — Agent A
           ├── Files PRE-LOADED per scan-plan.json (LLM doesn't choose)
           ├── Manifest signals as completeness checklist
           ├── R&M Report (SonarQube dimension scan)
           └── Security Report (BSL domain scan)

Phase 4: Verification — Agent B (independent adversarial reviewer)
           ├── Job 1: Challenge findings (false positive detection)
           ├── Job 2: Detect omissions (signal coverage matrix)
           └── Verification Report

Phase 5: Report Assembly + Gate Calculation
           ├── compute-gate.py (authoritative PASS/FAIL)
           ├── Summary Report (post-verification adjusted counts)
           └── Word (.docx) conversion
```

### Why 5 Phases?

v1.9 used text instructions ("Read ALL files") to ensure complete scanning.
Testing showed this was unreliable — the same codebase scanned twice produced
different results (18 vs 11 issues) because the LLM non-deterministically
selected which files to read.

v1.10 solves this structurally:
- **Phase 2** assigns files to batches algorithmically (no LLM choice)
- **Phase 3** receives files as input (not self-selected)
- **Phase 4** uses grep signals to detect any patterns Agent A missed

## Report Types

| Report | Review Standards | Coverage |
|--------|-----------------|----------|
| Reliability & Maintainability | SonarQube Java/JavaScript rules (Bug category only) | Blocker / High / Medium |
| Security | Philips Secure Coding Baseline (BSL 11.1.1.d, 230 controls) | 17 security domains |
| Verification | Agent B adversarial review | False positives + missed findings |
| Summary | Aggregates all modules | Global Pass/Fail |

An N-module project produces **(3N + 1) reports** in one scan.

## Prerequisites

### Required

1. **Kiro IDE** — Download: https://kiro.dev
2. **Claude Opus 4.6 / Sonnet 4.6** — 1M context window model (configured in Kiro)

### Optional

3. **Python 3.6+** — for scan-planner.py, validate-report.py, compute-gate.py
4. **pandoc** — for Word (.docx) output generation

## Usage

### Step 1: Clone the Target Code

```bash
git clone <repository-url> /path/to/target-project
```

### Step 2: Inject the Review Toolkit

```bash
cp -r ops-code-review-kit/.kiro /path/to/target-project/
```

### Step 3: Run the Review in Kiro

1. Open the target project in Kiro IDE
2. In the AI chat panel, run:

```
@codebase-reverse-engineering
```

This generates architecture docs AND `file-manifest.json` (Phase 1).

Once complete, run the batch scan (Phases 2-5):

```
@batch-scan
```

**This single command will automatically:**
- Run scan-planner.py to assign files to context window batches
- Generate R&M + Security reports for each module (Agent A)
- Run adversarial verification for each module (Agent B)
- Compute the quality gate and generate the Summary Report

### Step 4: Review the Results

```
code-review-artifacts/
├── reverse-engineering/
│   ├── architecture-preview.html
│   ├── *.md
│   └── file-manifest.json                 ← Per-file descriptions + signals
├── scan-plan.json                          ← Batch assignment plan
├── [Module1]_Reliability_Maintainability_Report_[date].md
├── [Module1]_Security_Report_[date].md
├── [Module1]_Verification_Report_[date].md ← Agent B results
├── ...
└── Summary_Report_[date].md
```

### Step 5: Post-Fix Rescan

After the development team fixes issues:

```bash
# Copy previous artifacts as baseline
cp -r /path/to/previous/code-review-artifacts/reverse-engineering/ \
      /path/to/new-version/code-review-artifacts/reverse-engineering/
cp /path/to/previous/code-review-artifacts/*_Report_*.md \
   /path/to/new-version/code-review-artifacts/previous-scan/
```

Then run:
```
@rescan
```

## Module Discovery

### Auto-Detection (Default)

| Priority | Build System | Detection Method |
|----------|-------------|------------------|
| 1 | Maven | `<modules>` in root `pom.xml` |
| 2 | Gradle | `include` in `settings.gradle(.kts)` |
| 3 | npm/pnpm/yarn | `workspaces` in root `package.json` |
| 4 | Nx/Turborepo/Lerna | Workspace config |
| 5 | Go | `go.work` |
| 6 | Directory heuristic | Subdirectories with their own build file |

### Manual Override

Create `module-manifest.md` in the project root:

```markdown
| # | Module | Path | Language | Notes |
|---|--------|------|----------|-------|
| 1 | my-backend | my-backend/ | Java | Maven multi-module |
| 2 | my-frontend | my-frontend/ | JS/Vue | SPA frontend |
```

## Context Window Strategy

Target model: Claude Opus 4.6 / Sonnet 4.6 (1M context window).

| Project Size | Total Tokens | Strategy |
|-------------|-------------|----------|
| Small (< 300K tokens) | Fits in single batch | All files + rules in one context window |
| Medium (300K–800K) | 2–3 batches | Group by dependency graph |
| Large (> 800K) | 4+ batches | Module-level batches |

The `scan-planner.py` script implements this deterministically:
- Connected components (files that import each other) stay in the same batch
- Token budget: 800K per batch (leaves ~200K for rules, prompt, output)
- Alphabetical tie-breaking ensures identical plans on every run

## Signal-Driven Completeness (v1.10)

file-manifest.json includes grep-detected signals per file:

| Signal | Category | Maps To |
|--------|----------|---------|
| v-html | security | BSL 11.1.1_174 |
| innerHTML | security | BSL 11.1.1_174 |
| hardcoded-secret | security | BSL 11.1.1_41, javascript:S6437 |
| md5-usage | security | BSL 11.1.1_8 |
| localStorage | security | BSL 11.1.1_51 |
| console-log | security | BSL 11.1.1_86, BSL 11.1.1_98 |
| eval-usage | security | BSL 11.1.1_113 |
| http-url | security | BSL 11.1.1_32 |
| empty-catch | quality | javascript:S1186, java:S108 |
| var-declaration | quality | javascript:S3504 |

Agent B uses these signals as a completeness checklist. If a signal exists but
Agent A didn't report a corresponding finding, Agent B investigates and either
adds the missed finding or documents why it's acceptable.

## Quality Gate

```
FAIL if ANY of the following is true:
  - severity = Critical  (any priority)
  - severity = High  AND  priority = P0

PASS if none of the above conditions are met.
```

Quality gate uses **post-verification** counts (after Agent B adjustments).
The Summary Report's overall gate is PASS only if ALL individual reports PASS.

## Fix Priority Definitions

| Priority | Meaning | Typical Scenarios |
|----------|---------|-------------------|
| **P0** | Must fix before release | Affects correctness or security |
| **P1** | Short-term fix (1-2 weeks) | High risk but not blocking current release |
| **P2** | Medium-term fix (1 month) | Code quality issues with some risk |
| **P3** | Long-term optimization | Low risk, technical debt |

## Step-by-Step Execution

If you prefer not to use the one-click batch scan:

```
@codebase-reverse-engineering     ← Phase 1: Analyze + generate file-manifest.json
@sonarqube-review                 ← Phase 3: R&M report for a specific module
@secure-coding-baseline-review    ← Phase 3: Security report for a specific module
@verification-agent               ← Phase 4: Adversarial verification
@summary-report                   ← Phase 5: Generate summary
@rescan                           ← Post-fix verification (optional)
```

## FAQ

**Q: What if the development team doesn't use Kiro?**
A: The development team does not need Kiro. The `.kiro/` directory is the
operations team's review toolkit and is not committed to their repository.

**Q: What changed from v1.9 to v1.10?**
A: v1.10 structurally eliminates non-determinism. v1.9 told the LLM "read all
files" (unreliable). v1.10 assigns files to context windows algorithmically and
uses grep signals + an independent verification agent to guarantee completeness.

**Q: Do I need Python installed?**
A: Python 3.6+ is recommended for scan-planner.py and validation scripts. If
unavailable, the system falls back to single-batch mode and inline validation.

**Q: What if my project exceeds the 1M token context window?**
A: scan-planner.py automatically splits into multiple batches (800K per batch).
Connected components in the dependency graph stay together. Very large projects
may need 4+ batches, processed sequentially.

**Q: How does Agent B verification work?**
A: Agent B is an independent adversarial reviewer that: (1) challenges every
Agent A finding using an exclusion checklist to detect false positives, and
(2) uses file-manifest signals to find patterns Agent A missed. The final
report counts come from Agent B's verification.

**Q: Can I skip verification (Agent B)?**
A: You can run `@sonarqube-review` and `@secure-coding-baseline-review` without
`@verification-agent`, but this reverts to v1.9 behavior without completeness
guarantees. Not recommended.

## Version History

| Version | Key Changes |
|---------|-------------|
| v1.10 | 5-phase architecture; file-manifest.json with grep signals; scan-planner.py for deterministic batch assignment; Agent B verification; structural non-determinism elimination |
| v1.9 | Three-layer architecture: dimension scanning + adversarial verification + external script validation |
| v1.8.1 | Full-scan mode — read ALL source files, no sampling regardless of codebase size |
| v1.8 | Architecture-Role Pattern Matching; open module discovery; bug fixes |
| v1.77 | Auth leaf-implementation tracing (password hashing, token issuance) |
| v1.76 | Two-plane architecture topology fix; 4-diagram specification |
| v1.75 | Merged v1.65 + v1.7; quality gate recalibration; R&M validator |
| v1.7 | Determinism rules D1-D7; HTML diagram preview |
| v1.6 | Initial release with BSL + SonarQube dual-standard review |
