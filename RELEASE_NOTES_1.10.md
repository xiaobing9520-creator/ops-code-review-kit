# Release Notes — v1.10

**Release Date**: 2026-06-15

## Summary

v1.10 structurally eliminates the primary source of non-determinism in code
review scans: LLM file-reading decisions. Testing v1.9 on the same codebase
(lab-admin-web) produced inconsistent results across runs (18 vs 11 issues)
because the LLM non-deterministically selected which files to read, despite
explicit "Read ALL" instructions.

v1.10 solves this by removing LLM file-selection entirely. Files are assigned
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

### 1. file-manifest.json (Phase 1)

Generated during reverse engineering. Contains per-file:
- **description**: One-line functional summary
- **tokens**: Approximate token count for batch planning
- **imports / imported_by**: Dependency edges for graph construction
- **security_signals**: grep-detected patterns (v-html, hardcoded-secret, md5-usage, localStorage, console-log, eval-usage, innerHTML, http-url)
- **quality_signals**: grep-detected patterns (empty-catch, var-declaration)

Signals are deterministic (same file → same grep → same signals) and serve as
the completeness checklist for Phase 4.

### 2. scan-planner.py (Phase 2)

New Python script that reads file-manifest.json and produces scan-plan.json:
- Builds a dependency graph from import/imported_by relationships
- Finds connected components (files that MUST be in the same context window)
- Greedily assigns components to batches respecting a token budget (800K default)
- Alphabetical tie-breaking guarantees identical plans on every run
- Falls back to single-batch mode if python3 is unavailable

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
- Added **Step 0.5**: Generate file-manifest.json with per-file descriptions,
  token counts, dependency edges, and grep signals
- Version header updated to v1.10

### @batch-scan
- Complete rewrite for 5-phase architecture
- Now orchestrates scan-planner.py, Agent A, Agent B, and report assembly
- Reports per module: 2 → 3 (added Verification Report)
- Total reports: (2N+1) → (3N+1)

### @sonarqube-review
- Now receives files pre-loaded in context (doesn't self-select)
- Uses quality_signals from file-manifest.json as completeness checklist
- Version header updated to v1.10

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
| `.kiro/scripts/scan-planner.py` | Deterministic context window batch planner |
| `.kiro/skills/verification-agent/skill.md` | Agent B adversarial verification skill |

## Breaking Changes

- Report count per module increased from 2 to 3 (Verification Report added)
- `scan-plan.json` is now a required intermediate artifact (auto-generated)
- `file-manifest.json` is now a required intermediate artifact (auto-generated)
- Batch-scan final output uses post-verification counts (not Agent A raw counts)

## Migration from v1.9

1. Replace the `.kiro/` directory with the v1.10 version
2. No changes needed to rule files (`.kiro/rules/` unchanged)
3. Python 3.6+ recommended (for scan-planner.py); falls back gracefully if unavailable
4. Existing `code-review-artifacts/` from v1.9 runs can remain; v1.10 will overwrite

## Requirements

- **Kiro IDE**
- **Claude Opus 4.6 / Sonnet 4.6** (1M context window)
- **Python 3.6+** (recommended, for scripts)
- **pandoc** (optional, for Word output)
