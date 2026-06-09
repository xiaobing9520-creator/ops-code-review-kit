# Release Notes

## v1.8.1

**Release Date**: 2026-06-09

**Focus**: Eliminate all file sampling — every scan reads ALL source files
regardless of codebase size, guaranteeing 100% deterministic Quality Gate results.

### Background

The Quality Gate Inconsistency Analysis on PH-Lab 20260601 revealed that
even with v1.8's Architecture-Role Pattern Matching, the same model (Opus 4.8)
running the same skill on the same code produced different Quality Gate results
across runs. Root cause: file selection still involved LLM judgment about which
files to read within the pattern-matching budget. When critical files (e.g.
Excel export methods with resource leaks) were in packages that didn't get
fully read, the corresponding Critical findings disappeared — flipping the
gate from FAIL to PASS.

**v1.8.1 solution**: Remove all sampling logic. Read every source file, every
time. This is the only way to guarantee that same code = same findings = same
Quality Gate, regardless of model, run number, or codebase size.

### Changed files

| File | Change |
|------|--------|
| `.kiro/skills/codebase-reverse-engineering/skill.md` | Replaced Step 0.4 (pattern matching + tiered budgets) with full-scan policy; removed scale-dependent file selection; updated D2.6; version bumped to v1.8.1 |
| `.kiro/steering.md` | Fixed hardcoded "9 reports" to formula "(2N+1)" |
| `README.md` | Updated version, scanning strategy section, FAQ, version history |
| `RELEASE_NOTES_1.8.1.md` | New |

---

### Change: Full-Scan Mode (replaces Architecture-Role Pattern Matching)

**Problem**: v1.8's pattern matching improved file selection accuracy, but the
LLM still had discretion in how it applied the budget rules (per-package caps,
Tier-2 fill decisions). This discretion introduced run-to-run variance:

| Run | Did the model read Excel export files? | S2095 Critical? | Gate |
|-----|---------------------------------------|-----------------|------|
| Opus run14 | Yes | Found | FAIL |
| Opus run15 | No | Not found | PASS |
| Opus 0606 | Yes | Found | FAIL |

**Solution**: No more budgets, caps, tiers, or selection logic. The new policy:

```
Read ALL source files in the file manifest, sorted alphabetically by path.
```

| v1.8 (old) | v1.8.1 (new) |
|------------|-------------|
| Small: read all | All sizes: read all |
| Medium: Tier-1 + Tier-2 fill to 5/package | — |
| Large: Tier-1 only, cap 3/package | — |

**Trade-off**: Large codebases (>500 files) will consume more tokens per scan.
This is an acceptable cost given that the primary goal is deterministic,
reproducible Quality Gate results.

**Determinism guarantee**: The read set = the full file manifest from Step 0.2.
No heuristics, no thresholds, no LLM judgment in file selection. Same codebase
= same files read in the same order = same output.

---

### Compatibility

- All other skills (sonarqube-review, secure-coding-baseline-review,
  security-review, batch-scan, summary-report, rescan, acceptance-report,
  rm-report-validator): unchanged
- Output artifact structure: unchanged
- Quality Gate definition: unchanged
- Module discovery logic: unchanged from v1.8
- Determinism rules D1-D5, D7: unchanged; D2.6 simplified (no tier logic)
- Report naming convention: unchanged

### Migration from v1.8

1. Replace the `.kiro/` directory:
   ```bash
   rm -rf /path/to/target-project/.kiro
   cp -r ops-code-review-kit-1.8.1/.kiro /path/to/target-project/
   ```

2. Re-run `@codebase-reverse-engineering` then `@batch-scan` to regenerate
   all artifacts with full-scan coverage.

### Action required

Re-run `@codebase-reverse-engineering` to regenerate architecture artifacts.
The full-scan mode will read all source files, producing the most complete and
deterministic architecture documentation possible.
