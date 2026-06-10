# Release Notes

## v1.9

**Release Date**: 2026-06-10

**Focus**: Three-layer architecture — LLM dimension scanning + adversarial
verification + external deterministic validation scripts. Eliminates rule ID
hallucination and Quality Gate logic errors through separation of concerns.

### Background

The v1.8.1 Quality Gate Inconsistency Analysis on PH-Lab 20260609 showed that
full-scan mode (reading ALL source files) solved file selection determinism but
NOT output determinism. The same model (Sonnet 4.6) running the same skill on
the same code produced Quality Gate results of FAIL/PASS/FAIL across 3 runs.

Root causes identified:
1. **Rule ID hallucination** — LLM fabricates non-existent rule IDs (60% of runs)
2. **Quality Gate logic misapplication** — LLM invents non-existent gate rules
3. **Severity inflation** — LLM overrides standard-defined severity
4. **Finding set instability** — completely different issues reported each run

**v1.9 solution**: Separate deterministic operations (rule lookup, severity
mapping, gate calculation) from non-deterministic operations (code analysis,
pattern matching) using a three-layer architecture.

### Architecture: Three-Layer Approach

```
┌─────────────────────────────────────────────────────────┐
│  Layer 1: LLM (Non-Deterministic)                       │
│  - Dimension-based scanning (5 mandatory dimensions)    │
│  - Adversarial verification (attempt to disprove each)  │
│  - Generates initial report with candidate findings     │
└──────────────────────────┬──────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│  Layer 2: validate-report.py (Deterministic)            │
│  - Verifies every Rule ID exists in standards JSON      │
│  - Verifies severity matches standards exactly          │
│  - Moves invalid findings to Appendix                   │
└──────────────────────────┬──────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│  Layer 3: compute-gate.py (Deterministic)               │
│  - Parses validated findings                            │
│  - Applies gate formula: FAIL if Critical OR High+P0    │
│  - Authoritative PASS/FAIL determination                │
└─────────────────────────────────────────────────────────┘
```

### New: Dimension-Based Scanning

Instead of free-form code analysis, the LLM scans through 5 mandatory dimensions:

| Dimension | Focus | Key Rules |
|-----------|-------|-----------|
| 1. Resource Management | Streams, connections, handles | S2095, S2189, S2142 |
| 2. Null Safety | NullPointerException prevention | S2259, S2637, S3518 |
| 3. Exception Handling | Error handling correctness | S1181, S108, S1186 |
| 4. Concurrency | Thread safety | S2445, S2168, S2696 |
| 5. Spring/Config | Framework-specific issues | S6818, S4601, S3776 |

Each dimension has mandatory rules that must be explicitly checked and reported
as Found / Not Found / N/A. This eliminates the "random walk" behavior where
different runs choose to check different rules.

### New: Adversarial Verification

Every candidate finding undergoes adversarial verification before inclusion in
the report. The LLM must actively attempt to DISPROVE each finding by checking
exclusion conditions:

| Category | Example Exclusion |
|----------|------------------|
| Resource leak | Is it in try-with-resources? Is it Spring-managed? |
| Empty method | Is it @Override placeholder? Is it adapter pattern? |
| Null deref | Is there a null-check earlier? Is it @NonNull? |
| Concurrency | Is the lock effectively final? Single-threaded context? |

This reduces false positives and produces more reliable findings.

### New: External Validation Scripts

Two Python scripts in `.kiro/scripts/` provide deterministic post-processing:

#### validate-report.py
- Extracts all Rule IDs from the report
- Checks each against `sonarqube_rules.json` (222 rules)
- Flags non-existent rules (V-01), severity mismatches (V-02), title mismatches (V-03)
- Outputs machine-readable `_validation.json` for downstream processing

#### compute-gate.py
- Parses validated findings by severity and priority
- Applies the Quality Gate formula deterministically
- Supports single-report and multi-report summary modes
- Exit code: 0=PASS, 1=FAIL (usable in CI/CD pipelines)

### New: Compact Rule Index

`.kiro/rules/sonarqube-rule-index.txt` — a one-line-per-rule index (222 lines)
in format `rule_key|severity|title`. This fits entirely in the LLM's attention
window and serves as the lookup table for rule verification during generation.

### Changed Files

| File | Change |
|------|--------|
| `.kiro/skills/sonarqube-review/skill.md` | Complete rewrite: dimension scanning, adversarial verification, external validation steps |
| `.kiro/skills/batch-scan/skill.md` | Integrated three-layer workflow |
| `.kiro/skills/codebase-reverse-engineering/skill.md` | Version bump to v1.9 |
| `.kiro/steering.md` | Added rules D7 (rule existence) and D8 (external gate authority) |
| `.kiro/scripts/validate-report.py` | New — deterministic rule validation |
| `.kiro/scripts/compute-gate.py` | New — deterministic gate calculation |
| `.kiro/rules/sonarqube-rule-index.txt` | New — compact rule index |
| `README.md` | Updated for v1.9 |
| `RELEASE_NOTES_1.9.md` | New |

### What This Solves

| v1.8.1 Problem | v1.9 Solution | Mechanism |
|----------------|---------------|-----------|
| Rule ID hallucination (60%) | Eliminated | validate-report.py rejects non-existent IDs |
| Severity inflation | Eliminated | validate-report.py enforces standards severity |
| Gate logic misapplication | Eliminated | compute-gate.py applies formula deterministically |
| Finding set instability | Reduced | Dimension scanning constrains what gets checked |
| False positives | Reduced | Adversarial verification challenges each finding |

### Compatibility

- All other skills unchanged: secure-coding-baseline-review, security-review,
  summary-report, rescan, acceptance-report, rm-report-validator
- Output artifact structure: unchanged
- Quality Gate definition: unchanged
- Module discovery: unchanged
- Full-scan policy: unchanged (inherited from v1.8.1)
- Requires Python 3.6+ for validation scripts

### Migration from v1.8.1

1. Replace the `.kiro/` directory:
   ```bash
   rm -rf /path/to/target-project/.kiro
   cp -r ops-code-review-kit-1.9/.kiro /path/to/target-project/
   ```

2. Copy `sonarqube_rules.json` to the project root (required by validation scripts):
   ```bash
   cp ops-code-review-kit-1.9/sonarqube_rules.json /path/to/target-project/
   ```

3. Re-run `@codebase-reverse-engineering` then `@batch-scan`.

### Prerequisites

- Python 3.6+ (for validation scripts)
- Kiro IDE
- pandoc (optional, for Word output)
