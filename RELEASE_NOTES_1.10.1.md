# Release Notes — v1.10.1

**Release Date**: 2026-06-17

## What's New in v1.10.1 (vs v1.10)

### Multi-Module Project Detection

`generate-manifest.py` now correctly detects and assigns files to modules in
multi-module projects. Previously only npm workspaces were supported — Maven,
Gradle, and Go projects were treated as single-module, causing incomplete scans.

**Supported build systems** (in priority order):
1. **Maven** — parses `<module>` entries in root `pom.xml`
2. **Gradle** — parses `include` in `settings.gradle(.kts)`
3. **npm/pnpm/yarn** — resolves `workspaces` in `package.json`
4. **Go** — parses `use()` blocks in `go.work`
5. **Heuristic fallback** — subdirs containing their own build file

**Bug fixed**: lab-backend (21 Maven modules, 3605 files) was previously tagged
as a single module "lab-backend", causing Kiro to only scan 3/21 modules. Now
all 21 modules are correctly identified and independently scanned.

---

## Summary (inherited from v1.10)

v1.10.1 structurally eliminates the primary source of non-determinism in code
review scans: LLM file-reading decisions. Testing v1.9 on the same codebase
(lab-admin-web) produced inconsistent results across runs (18 vs 11 issues)
because the LLM non-deterministically selected which files to read, despite
explicit "Read ALL" instructions.

v1.10.1 solves this by removing LLM file-selection entirely. Files are assigned
to context windows algorithmically, grep-generated signals provide a
deterministic completeness checklist, and an independent verification agent
catches any remaining omissions.

## New Architecture: 5-Phase Pipeline

```
Phase 1: Reverse Engineering + File Manifest
Phase 2: Context Window Planning (scan-planner.py)
Phase 3: Primary Scan — Agent A (files pre-loaded, not self-selected)
Phase 4: Verification — Agent B (adversarial review with signal checklist)
Phase 5: Report Assembly + Gate Calculation
```

## New Features

### 1. generate-manifest.py (Phase 1) — CRITICAL

New Python script that generates `file-manifest.json` with **100% source file
coverage**, without requiring the LLM to read any files.

```bash
python3 .kiro/scripts/generate-manifest.py --root .
```

**Why this script exists**: The initial v1.10.1 design had a bootstrap paradox —
file-manifest.json needed to cover ALL files, but the LLM generating it could
only read ~20 files per session. First real-world test on lab-admin-web showed
20/1349 file coverage (1.5%). This script eliminates LLM involvement entirely
for the enumeration step.

**What it does** (pure Python, no LLM, fully deterministic):
- Scans filesystem for ALL source files (sorted alphabetically)
- Computes token estimates (file_size / 4)
- Extracts `import`/`require` statements via regex → builds dependency graph
- Runs grep patterns for security_signals and quality_signals
- Resolves `@/` path aliases to actual file paths
- Excludes node_modules, vendor, dist, test fixtures, third-party bundles

**Output per file**:
- **path**: Relative file path
- **module**: Auto-detected from package.json/workspaces
- **tokens**: Approximate token count for batch planning
- **imports / imported_by**: Dependency edges for graph construction
- **security_signals**: grep-detected patterns (v-html, hardcoded-secret, md5-usage, localStorage, console-log, eval-usage, innerHTML, http-url)
- **quality_signals**: grep-detected patterns (empty-catch, var-declaration)

Signals are deterministic (same file → same grep → same signals) and serve as
the completeness checklist for Phase 4.

**Tested**: lab-admin-web (1496 files, 3.2M tokens) → manifest generated in <5s.

### 2. scan-planner.py (Phase 2)

New Python script that reads file-manifest.json and produces scan-plan.json:
- Builds a dependency graph from import/imported_by relationships
- Finds connected components (files that MUST be in the same context window)
- Greedily assigns components to batches respecting a token budget (800K default)
- **Splits oversized components**: When a connected component exceeds the budget
  (common in large SPAs where most files are interconnected), it is split into
  sub-batches via greedy bin-packing by file size
- Alphabetical tie-breaking guarantees identical plans on every run
- Falls back to single-batch mode if python3 is unavailable

**Tested**: lab-admin-web had one component of 1315 files (2.35M tokens) —
correctly split into 3 sub-batches of ~800K each. Final plan: 5 batches total.

### 3. Verification Agent — Agent B (Phase 4)

New skill (`@verification-agent`) providing independent adversarial verification:

**Job 1 — Challenge findings (reduce false positives)**:
- Re-reads full method context for each finding
- Applies exclusion checklist per rule category
- Removes findings where any exclusion condition is met

**Job 2 — Detect omissions (reduce false negatives)**:
- Builds Signal Coverage Matrix from file-manifest.json
- Compares against Agent A's findings
- For uncovered signals: reads source, verifies whether genuine violation exists
- Adds missed findings with full documentation

**Job 3 — Cross-file attack chain analysis**:
- Detects compound vulnerabilities (e.g., XSS + localStorage = token theft)
- Adjusts CVSS scoring for combined impact

### 4. Context-Aware Scanning (Phase 3)

Agent A no longer decides which files to read. The batch-scan orchestrator:
1. Runs scan-planner.py to determine batches
2. Loads all files in each batch into context
3. Provides manifest signals as a checklist

This eliminates "selective reading" — the root cause of v1.9 non-determinism.

### 5. Signal-to-Rule Mapping

Deterministic mapping from grep signals to rules/controls:

| Signal | Rule/Control |
|--------|-------------|
| v-html | BSL 11.1.1_174 |
| innerHTML | BSL 11.1.1_174 |
| hardcoded-secret | javascript:S6437, BSL 11.1.1_41 |
| md5-usage | BSL 11.1.1_8 |
| localStorage | BSL 11.1.1_51 |
| console-log | BSL 11.1.1_86, BSL 11.1.1_98 |
| eval-usage | BSL 11.1.1_113 |
| http-url | BSL 11.1.1_32 |
| empty-catch | javascript:S1186, java:S108 |
| var-declaration | javascript:S3504 |

## Changes to Existing Skills

### @codebase-reverse-engineering
- Added **Step 0.5**: Run `generate-manifest.py` to produce file-manifest.json
  covering ALL source files (script-based, not LLM-based)
- Fallback instructions for when python3 is unavailable (grep + wc -c)
- Verification step: entry count must equal source file count or scan aborts
- Version header updated to v1.10.1

### @batch-scan
- Complete rewrite for 5-phase architecture
- Now orchestrates scan-planner.py, Agent A, Agent B, and report assembly
- Reports per module: 2 → 3 (added Verification Report)
- Total reports: (2N+1) → (3N+1)

### @sonarqube-review
- Now receives files pre-loaded in context (doesn't self-select)
- Uses quality_signals from file-manifest.json as completeness checklist
- Version header updated to v1.10.1

### @secure-coding-baseline-review
- Now receives files pre-loaded in context (doesn't self-select)
- Uses security_signals from file-manifest.json as completeness checklist
- Added signal-to-control mapping in Step 1

### steering.md
- Complete rewrite documenting 5-phase architecture
- Added Determinism Rule 10 (Signal coverage completeness)
- Added Context Window Strategy table
- Added Fallback Rules for when scripts are unavailable
- Added PROHIBITION against LLM overriding rule index severity
- Report count formula updated: (3N+1)

## New Files

| File | Purpose |
|------|---------|
| `.kiro/scripts/generate-manifest.py` | Deterministic file manifest generator (covers ALL source files without LLM) |
| `.kiro/scripts/scan-planner.py` | Deterministic context window batch planner (with oversized component splitting) |
| `.kiro/skills/verification-agent/skill.md` | Agent B adversarial verification skill |

## Breaking Changes

- Report count per module increased from 2 to 3 (Verification Report added)
- `scan-plan.json` is now a required intermediate artifact (auto-generated)
- `file-manifest.json` is now a required intermediate artifact (auto-generated)
- Batch-scan final output uses post-verification counts (not Agent A raw counts)

## Migration from v1.9

1. Replace the `.kiro/` directory with the v1.10.1 version
2. No changes needed to rule files (`.kiro/rules/` unchanged)
3. Python 3.6+ recommended (for scan-planner.py); falls back gracefully if unavailable
4. Existing `code-review-artifacts/` from v1.9 runs can remain; v1.10.1 will overwrite

## Lessons Learned (v1.9 → v1.10.1)

### The Problem

v1.9 on the same codebase (lab-admin-web, 1349 files) produced:
- Run 1: 18 issues (8 R&M + 10 Security)
- Run 2: 11 issues (1 R&M + 10 Security)

Root cause: the LLM non-deterministically selected which files to read, despite
explicit "Read ALL source files" instructions in the skill definition.

### Key Insights

| # | Insight | Implication |
|---|---------|-------------|
| 1 | **Text instructions ≠ behavior guarantees** | "Read ALL" doesn't mean the LLM will. Instructions are suggestions, not contracts. |
| 2 | **LLM unsuited for enumeration tasks** | Listing all files, counting tokens, building dependency graphs — these are O(N) operations that must be scripts. |
| 3 | **Self-validation is unreliable** | The same LLM that fabricates a rule ID also "validates" it as correct. Verification must be external. |
| 4 | **Don't relocate the problem** | Moving "read all files" from Phase 3 to Phase 1 doesn't help — the LLM has the same context limit in both phases. |
| 5 | **Algorithms need degradation strategies** | In a Vue SPA, nearly all files form one connected component. The planner must split, not give up. |

### Design Principle

```
Enumeration / Calculation / Sorting  →  Script (deterministic, 100% coverage)
Understanding / Judgment / Suggestion →  LLM (semantic analysis)
Verification / Validation            →  Independent agent or script (never self)
```

Data flows between these layers via JSON files (file-manifest.json, scan-plan.json,
report.md). Each layer's output is a deterministic function of its inputs.

## Requirements

- **Kiro IDE**
- **Claude Opus 4.6 / Sonnet 4.6** (1M context window)
- **Python 3.6+** (recommended, for scripts)
- **pandoc** (optional, for Word output)
