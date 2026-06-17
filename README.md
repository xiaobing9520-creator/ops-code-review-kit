# Ops Code Review Kit (v1.10.1)

A Kiro IDE toolkit that lets operations teams perform standardized code reviews
on any project. You get security + reliability reports with specific rule
violations, CVSS scores, and fix recommendations — not vague suggestions.

**The development team does NOT need Kiro.** You copy this toolkit into their
code, run the scan in your own Kiro session, and deliver the reports.

---

## Quick Start (3 Steps)

```bash
# 1. Copy the toolkit into the target project
cp -r ops-code-review-kit/.kiro /path/to/target-project/

# 2. Generate the file manifest (run once, in terminal)
cd /path/to/target-project
python3 .kiro/scripts/generate-manifest.py --root .

# 3. Open in Kiro and scan
#    → In Kiro AI chat:
#    @codebase-reverse-engineering
#    @batch-scan
```

That's it. Reports appear in `code-review-artifacts/`.

---

## Scanning Flow — Full Panorama

Below is the complete end-to-end flow. Each box shows WHO does the work
(Script or LLM), WHAT it produces, and WHERE the output goes.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        COMPLETE SCANNING PIPELINE                            │
│                                                                             │
│  YOU (terminal)          KIRO (LLM)              SCRIPTS (deterministic)    │
│  ─────────────           ──────────              ─────────────────────────  │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ PREPARATION (one-time, before opening Kiro)                         │    │
│  │                                                                     │    │
│  │  $ cp -r ops-code-review-kit/.kiro /target-project/                 │    │
│  │  $ cd /target-project                                               │    │
│  │  $ python3 .kiro/scripts/generate-manifest.py --root .              │    │
│  │                                                                     │    │
│  │  Output: code-review-artifacts/reverse-engineering/file-manifest.json│    │
│  │          (ALL source files indexed — 100% coverage guaranteed)       │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                              │                                               │
│                              ▼                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ PHASE 1: Reverse Engineering           Trigger: @codebase-reverse-  │    │
│  │                                                 engineering          │    │
│  │  WHO: LLM (reads files, understands architecture)                   │    │
│  │                                                                     │    │
│  │  DOES:                                                              │    │
│  │   • Reads source files to understand business logic                 │    │
│  │   • Identifies system architecture, tech stack, data flows          │    │
│  │   • Detects modules from build system (Maven/Gradle/npm/Go)         │    │
│  │   • Generates architecture documentation                           │    │
│  │                                                                     │    │
│  │  PRODUCES:                                                          │    │
│  │   code-review-artifacts/reverse-engineering/                        │    │
│  │   ├── business-overview.md      ← System purpose & modules          │    │
│  │   ├── tech-stack.md             ← Languages, frameworks, deps       │    │
│  │   ├── architecture.md           ← Component topology                │    │
│  │   ├── data-flow.md              ← Trust boundaries, APIs            │    │
│  │   ├── analysis-summary.md       ← Scale assessment                  │    │
│  │   └── architecture-preview.html ← Visual diagrams (open in browser) │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                              │                                               │
│                              ▼                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ PHASE 2: Context Window Planning       Trigger: @batch-scan (auto)  │    │
│  │                                                                     │    │
│  │  WHO: Script (scan-planner.py) — NO LLM involved                   │    │
│  │                                                                     │    │
│  │  DOES:                                                              │    │
│  │   • Reads file-manifest.json                                        │    │
│  │   • Builds dependency graph (which files import each other)         │    │
│  │   • Groups connected files into batches (≤800K tokens each)         │    │
│  │   • Ensures related files stay in same batch                        │    │
│  │                                                                     │    │
│  │  PRODUCES:                                                          │    │
│  │   code-review-artifacts/scan-plan.json                              │    │
│  │   (e.g., "Batch 1: 1284 files, 798K tokens, modules A-I")          │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                              │                                               │
│                              ▼                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ PHASE 3: Primary Scan (Agent A)        Trigger: @batch-scan (auto)  │    │
│  │                                                                     │    │
│  │  WHO: LLM (reads code, identifies violations)                       │    │
│  │                                                                     │    │
│  │  DOES (for each batch):                                             │    │
│  │   • Reads ALL files assigned to this batch (no self-selection)      │    │
│  │   • Writes a one-line description for each file → updates manifest  │    │
│  │   • Scans for R&M issues (SonarQube rules — 5 dimensions)          │    │
│  │   • Scans for Security issues (BSL 230 controls — 17 domains)      │    │
│  │   • Uses grep signals as a checklist (must address every signal)    │    │
│  │                                                                     │    │
│  │  PRODUCES (per module):                                             │    │
│  │   code-review-artifacts/                                            │    │
│  │   ├── [Module]_Reliability_Maintainability_Report_[date].md         │    │
│  │   └── [Module]_Security_Report_[date].md                            │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                              │                                               │
│                              ▼                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ PHASE 4: Verification (Agent B)        Trigger: @batch-scan (auto)  │    │
│  │                                                                     │    │
│  │  WHO: LLM (independent adversarial reviewer)                        │    │
│  │                                                                     │    │
│  │  DOES:                                                              │    │
│  │   • Job 1: Challenges each finding — checks exclusion conditions    │    │
│  │     → removes false positives                                       │    │
│  │   • Job 2: Compares signals vs findings — finds missed patterns     │    │
│  │     → adds omitted issues                                           │    │
│  │   • Job 3: Cross-file attack chain analysis                         │    │
│  │                                                                     │    │
│  │  PRODUCES (per module):                                             │    │
│  │   code-review-artifacts/                                            │    │
│  │   └── [Module]_Verification_Report_[date].md                        │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                              │                                               │
│                              ▼                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ PHASE 5: Report Assembly               Trigger: @batch-scan (auto)  │    │
│  │                                                                     │    │
│  │  WHO: Script (compute-gate.py) + LLM (summary writing)             │    │
│  │                                                                     │    │
│  │  DOES:                                                              │    │
│  │   • Computes quality gate (PASS/FAIL) from post-verification counts │    │
│  │   • Aggregates all module results into summary                      │    │
│  │   • Converts to Word (.docx) via pandoc                             │    │
│  │                                                                     │    │
│  │  PRODUCES:                                                          │    │
│  │   code-review-artifacts/                                            │    │
│  │   └── Summary_Report_[date].md   ← Final deliverable               │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Script Invocation Timeline

| When | Script | Input | Output | Purpose |
|------|--------|-------|--------|---------|
| Before Kiro | `generate-manifest.py` | Filesystem | `file-manifest.json` | Index ALL source files + extract grep signals |
| Phase 2 (auto) | `scan-planner.py` | `file-manifest.json` | `scan-plan.json` | Split files into context-window batches |
| Phase 3 (auto) | `validate-report.py` | Each report `.md` | Pass/Fail | Verify rule IDs exist in standards |
| Phase 5 (auto) | `compute-gate.py` | All reports | PASS/FAIL | Compute quality gate deterministically |

### What is "Reverse Engineering"?

When you run `@codebase-reverse-engineering`, the LLM reads the project's source
code and produces documentation that describes:

- **What the system does** (business overview, user-facing features)
- **How it's built** (tech stack, frameworks, dependencies)
- **How it's structured** (modules, layers, component relationships)
- **How data flows** (APIs, databases, trust boundaries)

This documentation helps the scanning phases (3-4) understand the business
context of the code — e.g., knowing that a module handles payment processing
makes a hardcoded secret finding more critical than in a demo app.

### What is `file-manifest.json`?

A JSON file with one entry per source file in the project. Generated by script
(not the LLM) to guarantee 100% coverage. Example:

```json
{
  "path": "ph-lab-user/src/main/java/com/itnode/user/service/WxLoginService.java",
  "module": "ph-lab-user",
  "description": "",
  "tokens": 2400,
  "imports": ["ph-lab-common/src/.../TokenService.java"],
  "imported_by": ["ph-lab-user/src/.../WxLoginController.java"],
  "security_signals": ["hardcoded-secret", "md5-usage"],
  "quality_signals": ["empty-catch"]
}
```

- **description**: Empty when script generates it; LLM fills it during Phase 3
- **security_signals / quality_signals**: Detected by grep patterns, used by
  Agent B as a "must-check" completeness list
- **imports / imported_by**: Used by scan-planner.py to keep related files together

---

## Multi-Session Scanning (Large Projects)

Projects with many modules (e.g., 21 Maven modules, 3600 files) cannot fit in
a single Kiro context window. The toolkit handles this automatically:

```
Session 1:  @batch-scan  → scans Batch 1 (modules A-I)
Session 2:  @batch-scan  → detects Batch 1 done, scans Batch 2 (modules J-T)
Session 3:  @batch-scan  → detects Batches 1-2 done, scans Batch 3 + Summary
```

**You just type `@batch-scan` each time.** The Resume Protocol auto-detects
progress by checking which report files already exist:
- `scan-plan.json` exists → skip Phase 1-2
- Module reports exist → skip those modules
- All modules done → generate Summary Report

No manual instructions needed between sessions.

---

## What the Reports Look Like

### Report Types

| Report | Per Module | Standards | What it catches |
|--------|-----------|-----------|-----------------|
| R&M | Yes | SonarQube 575 rules | Resource leaks, NPE, concurrency bugs, exception handling |
| Security | Yes | BSL 230 controls | Injection, auth bypass, crypto weakness, secrets exposure |
| Verification | Yes | Agent B adversarial | False positives removed, missed findings added |
| Summary | 1 total | All combined | Global PASS/FAIL, priority roadmap |

Formula: **N modules → (3N + 1) reports**

### Example Finding

```markdown
### SEC-01: HSDP RSA private key in source-controlled YAML

**Risk Level**: CRITICAL
**CVSS Score**: 9.1 (Critical)
**File**: `ph-lab-user/src/main/resources/application-prod.yml:45`
**Associated CVE**: N/A — code logic defect (CWE-798)

- **BSL Control**: `11.1.1_41` — Do not store secrets in source code
- **Security Domain**: Data Protection
- **CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N`
- **Fix Priority**: P0

**Code**:
  hsdp:
    private-key: |
      -----BEGIN RSA PRIVATE KEY-----
      MIIEpAIBAAKCAQEA...

**Root Cause & Business Impact**:
RSA private key committed in YAML config. Anyone with repo access can
impersonate the service to HSDP identity provider.

**Fix Recommendation**:
Move to AWS Secrets Manager or environment variable injection at deploy time.
```

---

## Quality Gate

```
FAIL if ANY of:
  • severity = Critical (any priority)
  • severity = High AND priority = P0

PASS otherwise.
```

Computed by `compute-gate.py` (script, not LLM judgment). Uses post-verification
counts (after Agent B adjusts for false positives/missed findings).

---

## Module Discovery

The toolkit auto-detects project modules from the build system:

| Priority | Build System | What it reads |
|----------|-------------|---------------|
| 1 | Maven | `<module>` entries in root `pom.xml` |
| 2 | Gradle | `include` in `settings.gradle(.kts)` |
| 3 | npm/pnpm/yarn | `workspaces` in `package.json` |
| 4 | Go | `use()` blocks in `go.work` |
| 5 | Heuristic | Subdirs with their own build file |

Override: create `module-manifest.md` in project root with a module table.

---

## Prerequisites

| Requirement | Required? | Purpose |
|-------------|-----------|---------|
| Kiro IDE | Yes | Runs the LLM scanning sessions |
| Python 3.6+ | Recommended | Scripts: generate-manifest, scan-planner, compute-gate |
| pandoc | Optional | Converts reports to Word (.docx) |

If Python is unavailable, the system falls back to single-batch mode (all files
in one context window — works for small projects).

---

## Toolkit File Structure

```
.kiro/
├── steering.md                              ← Master config (architecture, rules, policies)
├── scripts/
│   ├── generate-manifest.py                 ← Indexes ALL files + detects signals (run before Kiro)
│   ├── scan-planner.py                      ← Assigns files to batches (Phase 2)
│   ├── validate-report.py                   ← Validates rule IDs exist in standards (Phase 3)
│   └── compute-gate.py                      ← Computes PASS/FAIL gate (Phase 5)
├── rules/
│   ├── sonarqube-java-standards.md          ← 341 Java bug rules
│   ├── sonarqube-javascript-standards.md    ← 234 JavaScript bug rules
│   ├── sonarqube-rule-index.txt             ← Quick lookup: rule ID → severity
│   └── secure-coding-baseline-standards.md  ← BSL 11.1.1.d (230 controls)
└── skills/
    ├── codebase-reverse-engineering/skill.md ← Phase 1: understand the codebase
    ├── batch-scan/skill.md                  ← Orchestrator: Phases 2-5 + resume
    ├── sonarqube-review/skill.md            ← Agent A: R&M scanning
    ├── secure-coding-baseline-review/skill.md ← Agent A: Security scanning
    ├── verification-agent/skill.md          ← Agent B: adversarial verification
    ├── summary-report/skill.md              ← Phase 5: summary generation
    └── rescan/skill.md                      ← Post-fix delta verification
```

---

## Post-Fix Rescan

After the development team fixes issues:

```bash
# Copy previous artifacts as baseline
cp -r /previous/code-review-artifacts/reverse-engineering/ \
      /new-version/code-review-artifacts/reverse-engineering/
```

Then in Kiro:
```
@rescan
```

This produces a delta report (FIXED / NOT FIXED / REGRESSED) without
re-scanning the entire codebase.

---

## FAQ

**Q: What if my project has 1000+ files?**
A: `generate-manifest.py` handles any size (tested on 3600 files). `scan-planner.py`
splits into multiple batches. Each batch runs in its own Kiro session.

**Q: Do I need to configure anything?**
A: No. Copy `.kiro/`, run `generate-manifest.py`, and go. Module detection,
batch planning, and report generation are all automatic.

**Q: What if Kiro's context runs out mid-scan?**
A: Open a new session and type `@batch-scan` again. The Resume Protocol
detects completed batches from existing report files and continues.

**Q: Can I scan just one module?**
A: Yes. Use `@sonarqube-review` and `@secure-coding-baseline-review` individually.

**Q: How is this different from running SonarQube directly?**
A: This toolkit adds: BSL security scanning (230 controls), CVSS scoring,
adversarial verification (Agent B), cross-file attack chain analysis,
AI-generated fix code, and Word report output. SonarQube only covers R&M.

**Q: What changed from earlier versions?**
A: See Version History below. The key evolution: v1.6-v1.8 relied on LLM file
selection (non-deterministic). v1.10+ assigns files algorithmically via scripts,
making results reproducible.

---

## Design Principles

| Principle | Implementation |
|-----------|---------------|
| Enumeration = Script | File listing, token counting, signal detection, batch planning |
| Judgment = LLM | Code understanding, violation detection, fix recommendations |
| Verification = Independent | Agent B (separate context, adversarial stance) |
| Determinism | Same code + same rules → same scan plan → same file assignments |
| Completeness | grep signals guarantee known patterns are never silently missed |

---

## Version History

| Version | Key Changes |
|---------|-------------|
| v1.10.1 | Multi-module detection (Maven/Gradle/Go/npm); Resume Protocol; file descriptions by LLM |
| v1.10 | 5-phase architecture; file-manifest.json; scan-planner.py; Agent B verification |
| v1.9 | Three-layer architecture: dimension scanning + adversarial verification |
| v1.8.1 | Full-scan mode — read ALL source files, no sampling |
| v1.8 | Architecture-Role Pattern Matching; open module discovery |
| v1.75 | Merged determinism rules + quality gate recalibration |
| v1.7 | Determinism rules D1-D7; HTML architecture diagrams |
| v1.6 | Initial release: BSL + SonarQube dual-standard review |
