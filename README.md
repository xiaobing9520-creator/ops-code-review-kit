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

## Detailed Scanning Flow (What Happens Internally)

Below is the complete end-to-end flow. When you run `@codebase-reverse-engineering`
followed by `@batch-scan`, the system executes all of these steps automatically.

### Phase 1: Reverse Engineering + File Manifest

**Trigger**: `@codebase-reverse-engineering`

**Step 1.1 — Scale Assessment**:
```bash
find . -type f -name "*.js" -o -name "*.vue" -o -name "*.ts" ... | sort | wc -l
```
Counts source files, classifies project scale (Small/Medium/Large).

**Step 1.2 — Module Discovery**:
Detects modules from build system (package.json workspaces, pom.xml modules, etc.).
Produces a FIXED sorted module list for the entire scan.

**Step 1.3 — Full Code Reading**:
Reads ALL source files in alphabetical order. No sampling, no selection.

**Step 1.4 — Architecture Documentation**:
Generates structured artifacts:
- `business-overview.md` — System purpose, modules, business transactions
- `tech-stack.md` — Languages, frameworks, versions, dependencies
- `architecture.md` — Component topology, data flow diagrams
- `data-flow.md` — Trust boundaries, API surfaces, integrations
- `architecture-preview.html` — Visual diagram for browser viewing

**Step 1.5 — File Manifest Generation** (NEW in v1.10):
For each source file, generates an entry in `file-manifest.json`:

```json
[
  {
    "path": "src/api/index.js",
    "module": "lab-admin-web",
    "description": "Axios HTTP client with request/response interceptors for auth token injection",
    "tokens": 1200,
    "imports": ["src/utils/auth.js", "src/config/env.js"],
    "imported_by": ["src/views/Login.vue", "src/views/Dashboard.vue"],
    "security_signals": ["hardcoded-secret", "localStorage", "console-log"],
    "quality_signals": ["var-declaration"]
  },
  {
    "path": "src/views/Login.vue",
    "module": "lab-admin-web",
    "description": "Admin login page with password MD5 hashing and MFA redirect",
    "tokens": 3400,
    "imports": ["src/api/index.js", "src/utils/md5.js"],
    "imported_by": [],
    "security_signals": ["md5-usage", "localStorage"],
    "quality_signals": []
  }
]
```

Signal detection uses deterministic grep patterns:
- `v-html` → grep for `v-html` in .vue files
- `hardcoded-secret` → grep for `password\s*=\s*['"]`, `secret\s*=\s*['"]`
- `md5-usage` → grep for `md5(`, `MD5(`
- `localStorage` → grep for `localStorage.setItem`, `localStorage.getItem`
- `console-log` → grep for `console.log(` in non-test files
- `empty-catch` → grep for `catch.*{[\s]*}` (empty catch blocks)
- etc.

**Phase 1 Output**:
```
code-review-artifacts/reverse-engineering/
├── business-overview.md
├── tech-stack.md
├── architecture.md
├── data-flow.md
├── architecture-preview.html
└── file-manifest.json          ← Critical for Phases 2-4
```

---

### Phase 2: Context Window Planning

**Trigger**: Automatically by `@batch-scan`

**Step 2.1 — Run scan-planner.py**:
```bash
python3 .kiro/scripts/scan-planner.py \
  --manifest code-review-artifacts/reverse-engineering/file-manifest.json \
  --output code-review-artifacts/scan-plan.json
```

**Algorithm**:
1. Read file-manifest.json → extract all files with their token counts
2. Build dependency graph from `imports`/`imported_by` edges
3. Find connected components (BFS) — files that reference each other
4. Sort components alphabetically by first file path (determinism)
5. Greedy bin-packing: assign components to batches, each ≤ 800K tokens
6. If a single component exceeds 800K → it gets its own dedicated batch

**Key constraint**: Connected components NEVER split across batches. If file A
imports file B, they are always in the same context window — ensuring the LLM
sees the full dependency chain.

**Example scan-plan.json output**:
```json
{
  "version": "1.10",
  "total_files": 1344,
  "total_tokens": 2100000,
  "budget_per_batch": 800000,
  "batches": [
    {
      "id": 1,
      "files": ["src/api/index.js", "src/api/baseUrl.js", ...],
      "tokens": 780000,
      "modules": ["lab-admin-web"],
      "signal_summary": {"localStorage": 5, "console-log": 120, "md5-usage": 3}
    },
    {
      "id": 2,
      "files": ["src/views/Login.vue", "src/views/MFALogin.vue", ...],
      "tokens": 750000,
      "modules": ["lab-admin-web"],
      "signal_summary": {"v-html": 15, "hardcoded-secret": 2}
    }
  ],
  "single_batch": false
}
```

**Fallback**: If python3 is unavailable → single-batch mode (read all files directly).

---

### Phase 3: Primary Scan — Agent A

**Trigger**: Automatically by `@batch-scan`

For each batch in scan-plan.json, Agent A:

1. **Loads all files** in the batch into context (no file-selection decision)
2. **Loads the rule standards** (sonarqube-rule-index.txt + BSL standards)
3. **Loads manifest signals** for files in this batch as a completeness checklist

**3A: Reliability & Maintainability Report** (`@sonarqube-review` logic):

Agent A scans in 5 mandatory dimensions, IN ORDER:

| # | Dimension | Focus | Key Rules Checked |
|---|-----------|-------|-------------------|
| 1 | Resource Management | Streams, connections, lifecycle | S2095, S2189, S2142 |
| 2 | Null Safety | NullPointerException risks | S2259, S2637, S3518 |
| 3 | Exception Handling | Error handling correctness | S1181, S108, S1186 |
| 4 | Concurrency | Thread safety issues | S2445, S2168, S2696 |
| 5 | Spring/Config | Framework-specific issues | S6818, S4601, S3776 |

For each dimension, every mandatory rule is explicitly checked and reported as
Found / Not Found / N/A. This prevents random coverage gaps.

After dimension scanning, Agent A performs **self-adversarial verification**:
- Re-reads the full method containing each finding
- Applies exclusion checklist (e.g., "Is this resource Spring-managed?")
- Removes findings where any exclusion condition is met

**3B: Security Report** (`@secure-coding-baseline-review` logic):

Agent A scans across 17 BSL security domains:
1. Authentication & Password Management (11.1.1_1–31)
2. Communications Security (11.1.1_32–39)
3. Cryptography (11.1.1_40–46)
4. Data Protection (11.1.1_47–59)
5. Database Security (11.1.1_60–73)
6. Error Handling & Logging (11.1.1_74–98)
7. File Management (11.1.1_99–112)
8. General Coding Practices (11.1.1_113–124)
9. Input Validation (11.1.1_125–139)
10. Logical Access Control (11.1.1_140–162)
11. Memory Management (11.1.1_163–172)
12. Output Encoding (11.1.1_173–178)
13. Secure Design (11.1.1_179–187)
14. Security Configuration (11.1.1_188–193)
15. Security Logging (11.1.1_194–201)
16. Session Management (11.1.1_202–216)
17. System Configuration (11.1.1_217–228)

Each finding includes CVSS v3.1 scoring with full vector string.

**Phase 3 validation** (after report generation):
```bash
# Verify rule IDs exist in standards
python3 .kiro/scripts/validate-report.py [report].md --rules sonarqube_rules.json

# Compute quality gate deterministically
python3 .kiro/scripts/compute-gate.py [report].md
```

---

### Phase 4: Verification — Agent B

**Trigger**: Automatically by `@batch-scan` (after all Agent A reports complete)

Agent B is an INDEPENDENT adversarial reviewer. It has two jobs:

**Job 1 — Challenge Findings (Reduce False Positives)**:

For each finding in Agent A's reports:
1. Re-read the COMPLETE method/function (not just the flagged line)
2. Apply exclusion checklist:

| Category | Exclusion 1 | Exclusion 2 | Exclusion 3 |
|----------|------------|------------|------------|
| Hardcoded secret (S6437) | Injected from env at build? | Test/stub value? | Public identifier? |
| XSS (v-html) | Trusted admin-only source? | DOMPurify applied? | Sandboxed iframe? |
| MD5 usage (BSL 8) | Non-security purpose? | Never for auth? | File integrity only? |
| localStorage (BSL 51) | Non-sensitive value stored? | No XSS vector? | Public page? |
| Empty catch (S1186) | Intentional @Override no-op? | Comment explains why? | Framework stub? |

3. If ANY exclusion is met with evidence → **FALSE POSITIVE** → removed

**Job 2 — Detect Omissions (Reduce False Negatives)**:

1. Build **Signal Coverage Matrix** from file-manifest.json:

| Signal Type | Files with Signal | Expected Rule | Covered by Agent A? |
|-------------|-------------------|---------------|---------------------|
| v-html | 52 files | BSL 11.1.1_174 | Yes/No/Partial |
| md5-usage | 8 files | BSL 11.1.1_8 | Yes/No/Partial |
| localStorage | 22 files | BSL 11.1.1_51 | Yes/No/Partial |
| console-log | 648 files | BSL 11.1.1_98 | Yes/No/Partial |

2. For each UNCOVERED signal:
   - Read the actual source file
   - Determine if it's a genuine violation (apply same exclusion checklist)
   - If genuine → add as **MISSED FINDING** with full documentation
   - If acceptable → document why (e.g., "content from trusted CMS, admin-only")

3. **Cross-file attack chain analysis**:
   - v-html + localStorage in same app → token theft via XSS (CVSS Scope = Changed)
   - md5-usage + hardcoded-secret → forgeable auth scheme
   - console-log + hardcoded-secret → credential logging exposure

**Phase 4 Output**: Verification Report per module with:
- False positive rejections (with evidence)
- Missed finding additions (with signal source)
- Signal Coverage Matrix (every signal accounted for)
- Final adjusted counts (authoritative for Summary Report)

---

### Phase 5: Report Assembly + Gate Calculation

**Trigger**: Automatically by `@batch-scan`

1. **Compute overall gate**:
```bash
python3 .kiro/scripts/compute-gate.py --summary code-review-artifacts/*_Report_*.md
```

2. **Generate Summary Report** using post-verification counts (Agent B's adjusted numbers)

3. **Convert to Word**:
```bash
for f in code-review-artifacts/*.md; do
  pandoc "$f" -o "${f%.md}.docx"
done
```

---

### Data Flow Between Phases

```
Phase 1 ──produces──→ file-manifest.json ──consumed by──→ Phase 2, Phase 4
Phase 2 ──produces──→ scan-plan.json     ──consumed by──→ Phase 3
Phase 3 ──produces──→ R&M + Security Reports ──consumed by──→ Phase 4, Phase 5
Phase 4 ──produces──→ Verification Report ──consumed by──→ Phase 5
Phase 5 ──produces──→ Summary Report + Word files (FINAL deliverables)
```

Each phase's output is a deterministic function of its inputs. Same code +
same rules + same model = same reports.

---

## Step-by-Step Execution (Manual Mode)

If you prefer not to use the one-click batch scan:

```
@codebase-reverse-engineering     ← Phase 1: Analyze + generate file-manifest.json
@sonarqube-review                 ← Phase 3: R&M report for a specific module
@secure-coding-baseline-review    ← Phase 3: Security report for a specific module
@verification-agent               ← Phase 4: Adversarial verification
@summary-report                   ← Phase 5: Generate summary
@rescan                           ← Post-fix verification (optional)
```

## Report Finding Format (Example)

Every finding across all report types uses a unified header format:

### R&M Report Finding Example

```markdown
### BUG-01: Hardcoded APP_ID and APP_SECRET in shop Axios client

**Risk Level**: CRITICAL
**CVSS Score**: N/A — non-security rule
**File**: `src/api/indexShop.js:12`
**Associated CVE**: N/A — code quality rule (CWE-798)

- **Rule**: `javascript:S6437` — Credentials should not be hard-coded
- **Verified**: javascript:S6437|Critical|Credentials should not be hard-coded
- **Fix Priority**: P0
- **Dimension**: Resource Management

**Code**:
  const APP_ID = 'wx1234567890abcdef'
  const APP_SECRET = 'abc123def456...'

**Root Cause & Business Impact**:
Signing secret is embedded in the browser bundle. Any user can extract it
from DevTools and forge authenticated shop API requests.

**Adversarial Verification**:
- Exclusion 1: Injected from env at build time? → NOT MET (hardcoded literal)
- Exclusion 2: Test/stub value? → NOT MET (matches production pattern)
- Exclusion 3: Public identifier? → NOT MET (marked as SECRET)
- **Verdict**: CONFIRMED

**Fix Recommendation**:
Move to environment variables via .env files.

**Suggested Fix Code (AI-generated)**:
  const APP_ID = process.env.VUE_APP_SHOP_APP_ID || ''
  const APP_SECRET = process.env.VUE_APP_SHOP_APP_SECRET || ''
```

### Security Report Finding Example

```markdown
### SEC-01: Client-side MD5 password hashing before transmission

**Risk Level**: HIGH
**CVSS Score**: 7.4 (High)
**File**: `src/views/Login.vue:89`
**Associated CVE**: N/A — code logic defect (CWE-328)

- **BSL Control**: `11.1.1_8` — Do not use MD5 for password hashing
- **Security Domain**: Cryptography
- **CVSS Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N`
- **Fix Priority**: P0

**Code**:
  form.password = md5(form.password)

**Root Cause & Business Impact**:
MD5 hashes are trivially reversible via rainbow tables. Combined with
base64 encoding for new passwords, credentials are near-plaintext.

**Fix Recommendation**:
Remove client-side hashing entirely. Rely on TLS for transport security.
Implement bcrypt/Argon2 server-side.

**Impact of Not Fixing**:
Attacker intercepting traffic or accessing logs can recover passwords
in seconds using precomputed MD5 tables.
```

---

## Toolkit File Structure

```
.kiro/
├── steering.md                              ← Master configuration (architecture, rules, policies)
├── rules/
│   ├── sonarqube-java-standards.md          ← 341 Java rules (Blocker/High/Medium)
│   ├── sonarqube-javascript-standards.md    ← JavaScript rules
│   ├── sonarqube-rule-index.txt             ← Compact rule ID → severity lookup
│   ├── sonarqube_rules.json                 ← Machine-readable rule database
│   └── secure-coding-baseline-standards.md  ← BSL 11.1.1.d (230 controls, 17 domains)
├── scripts/
│   ├── scan-planner.py                      ← Phase 2: Deterministic batch assignment
│   ├── validate-report.py                   ← Phase 3: Rule ID + severity validation
│   └── compute-gate.py                      ← Phase 5: Quality Gate calculation
└── skills/
    ├── codebase-reverse-engineering/skill.md ← Phase 1: Full RE + file-manifest.json
    ├── batch-scan/skill.md                  ← Orchestrator: runs Phases 2-5
    ├── sonarqube-review/skill.md            ← Agent A: R&M dimension scan
    ├── secure-coding-baseline-review/skill.md ← Agent A: BSL domain scan
    ├── verification-agent/skill.md          ← Agent B: Adversarial verification
    ├── summary-report/skill.md              ← Phase 5: Summary generation
    └── rescan/skill.md                      ← Post-fix delta verification
```

---

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
