# v1.8.1 Quality Gate Inconsistency Analysis

**Date**: 2026-06-09
**Source**: PH-Lab 20260609_Sonnet_4.6_1.8.1_managed backend (3 runs)
**Model**: Claude Sonnet 4.6 × 3 runs
**Kit Version**: ops-code-review-kit v1.8.1 (full-scan mode)
**Target Code**: managed backend (lab-admin + lab-fss-admin, Java/Spring Boot)

---

## 1. Executive Summary

v1.8.1 introduced full-scan mode (reading ALL source files regardless of codebase
size), which solved file selection non-determinism identified in the v1.77 analysis.
However, **3 runs of the same model on the same code still produced inconsistent
Quality Gate results**:

| Run | Overall Gate | R&M Gate (admin) | R&M Gate (fss-admin) |
|-----|-------------|-----------------|---------------------|
| Run 1 | **FAIL** | FAIL | FAIL |
| Run 2 | **PASS** | PASS | PASS |
| Run 3 | **FAIL** | FAIL | FAIL |

The skill files were verified identical across all 3 runs (MD5 checksums match).
This eliminates configuration drift as a possible cause.

---

## 2. Verification: Full-Scan Works

Before analyzing what went wrong, we confirmed that v1.8.1's full-scan mode
works as designed:

- All 3 runs read the **same set of source files** (verified via reverse-engineering artifacts)
- No file was skipped or sampled in any run
- Module discovery was consistent (though naming varied: "ph-lab-admin" vs "lab-admin")

**Conclusion**: The file selection non-determinism from v1.77 is fully resolved.
The remaining inconsistency has a different root cause.

---

## 3. Root Cause Analysis

### Root Cause 1: Rule ID Hallucination (Primary — affects 2/3 runs)

The LLM fabricates SonarQube rule IDs that do not exist in the standards file,
or misattributes real IDs to wrong issues.

**Evidence:**

| Run | Fabricated/Misused Rule IDs | Impact |
|-----|----------------------------|--------|
| Run 1 | `java:S131` used for auth issues (actually "switch default clause"), `java:S2119` used for MD5 (actually "Random reuse") | False findings → inflated severity → FAIL |
| Run 2 | None — all IDs valid | Correct report → PASS |
| Run 3 | `java:S3330`, `java:S5122`, `java:S4784`, `java:S4790`, `java:S1148`, `java:S106` — 6 out of 10 IDs do not exist | False High P0 findings → FAIL |

**Script verification** (using v1.9's `validate-report.py`):
```
Run 3 ph-lab-admin: 9 findings extracted, 8 invalid (to Appendix)
After removing fabricated rules: Quality Gate = PASS
```

**Key insight**: Run 3's FAIL was triggered by `java:S3330` (cookie HttpOnly) — a
rule that **does not exist** in the organization's SonarQube standards. If this
single fabricated rule were removed, the gate would flip to PASS.

---

### Root Cause 2: Quality Gate Logic Misapplication (affects 1/3 runs)

The Quality Gate rule is clearly defined:
```
FAIL if: Critical > 0 OR (High AND P0)
PASS otherwise.
High P1/P2/P3 and Medium: NEVER block.
```

Run 3 violated this rule:
- `ph-lab-admin` R&M report: Critical = 0, High P0 = 0
- Expected gate: **PASS**
- Actual output: "**FAIL** — 4 High-severity issues require documented mitigation"

The LLM invented a non-existent gate rule ("High issues require mitigation =
FAIL") that contradicts the explicit formula in `steering.md`.

---

### Root Cause 3: Severity Inflation (affects 1/3 runs)

Run 1 escalated `java:S1186` (Methods should not be empty) from its
standards-defined severity of **High** to **CRITICAL**, with justification:
"authentication is non-functional."

The `steering.md` explicitly states:
> "Table-driven severity — R&M severity = exact severity in the SonarQube
> standards file. Never infer or 'judge' severity."

This single escalation flipped the gate from PASS to FAIL. The LLM applied its
own judgment ("this empty method is critical because it handles auth") rather
than using the table-driven severity from the standards file.

---

### Root Cause 4: Finding Set Instability (affects all 3 runs)

Even with identical file input, each run reported **completely different issues**:

| Run 1 Focus | Run 2 Focus | Run 3 Focus |
|-------------|-------------|-------------|
| Auth bypass patterns | Cognitive complexity | MD5 token generation |
| Export endpoint resource leaks | Empty methods (@Override) | ThreadLocal cleanup |
| JSESSIONID session fixation | @Configuration bean issues | Cookie flag missing |
| Autocloseable violations | String literal duplication | Anonymous endpoint exposure |

The LLM "chooses" which of 222 rules to match against which code patterns. This
choice is non-deterministic — the same code is analyzed through different "lenses"
each time.

---

## 4. Why Self-Validation Failed

v1.8.1 includes an inline `@rm-report-validator` step that instructs the LLM to:
1. Check each Rule ID exists in the standards file (V-01)
2. Verify severity matches (V-02)
3. Verify description matches (V-03)

**Run 3 claims the validator ran** ("Validator Note" present in output), yet the
report still contains **6 out of 10 fabricated rule IDs**.

This confirms a fundamental limitation: **LLM self-validation is unreliable**.
The same inference process that fabricates a rule ID also "validates" it as
correct, because the model is equally confident in both steps.

---

## 5. Detailed Comparison Table

| Aspect | Run 1 | Run 2 | Run 3 |
|--------|-------|-------|-------|
| Module naming | ph-lab-admin | lab-admin | ph-lab-admin |
| Files read | All | All | All |
| admin R&M gate | FAIL (empty .md!) | PASS | FAIL (wrong logic) |
| admin Security gate | FAIL (2 Critical) | PASS | FAIL (High P0) |
| fss R&M gate | FAIL (3 Critical) | PASS | FAIL (High P0) |
| fss Security gate | FAIL (4 Critical) | PASS | FAIL (High P0) |
| Rule ID accuracy | ~40% misattributed | 100% valid | 40% fabricated |
| Severity accuracy | S1186 High→CRITICAL | Correct | Correct |
| Gate logic | Correct formula | Correct formula | Wrong formula |
| Validator ran | Unclear | Yes (corrections visible) | Claims yes, ineffective |
| Overall conclusion | Over-reporting | Accurate | Over-reporting |

---

## 6. Impact Assessment

### For the customer (PH-Lab operations team):

- **2 out of 3 runs** produce incorrect FAIL results, requiring manual review
- The **only correct run** (Run 2) happened to also be the one where the validator
  actually worked
- Without expertise to verify rule IDs, the customer cannot distinguish correct
  from incorrect reports
- This undermines trust in the toolkit's Quality Gate determination

### For the toolkit:

- Full-scan mode works — file coverage is no longer the problem
- The problem has shifted from "input determinism" to "output determinism"
- LLM self-validation is not a reliable safeguard
- The root cause is architectural: deterministic operations (rule lookup, gate
  calculation) are mixed into the same LLM pass as non-deterministic operations
  (code analysis)

---

## 7. What v1.8.1 Solved vs. What Remains Unsolved

| Problem | v1.8.1 Status | Evidence |
|---------|---------------|----------|
| File selection non-determinism | ✅ SOLVED | All 3 runs read identical file sets |
| Rule ID accuracy | ❌ UNSOLVED | 2/3 runs have fabricated/misattributed IDs |
| Quality Gate formula application | ❌ UNSOLVED | 1/3 runs applies wrong formula |
| Severity fidelity | ❌ UNSOLVED | 1/3 runs inflates severity |
| Finding set stability | ❌ UNSOLVED | 3 completely different issue sets |
| Self-validation reliability | ⚠️ PARTIAL | Only works in 1/3 runs |

---

## 8. Lessons Learned

### Lesson 1: Full-scan is necessary but not sufficient

Reading all files guarantees identical input to the LLM, but the LLM's response
to identical input varies. The non-determinism lives in the "analysis" phase,
not the "reading" phase.

### Lesson 2: LLM self-validation has a fundamental conflict of interest

Asking the same model to both generate and validate rule IDs is like asking a
student to grade their own test. The validation step uses the same "knowledge"
(which may be wrong) as the generation step.

### Lesson 3: Deterministic operations must be performed by deterministic code

Rule ID lookup, severity mapping, and Quality Gate calculation are all
deterministic operations that should produce identical results regardless of
how many times you run them. These should NOT be performed by an LLM.

### Lesson 4: The problem has a clear boundary

The LLM is good at:
- Understanding code patterns and identifying potential bugs
- Explaining the business impact of issues
- Generating fix recommendations

The LLM is unreliable at:
- Accurately recalling specific IDs from a 12K-line reference file
- Counting findings and applying thresholds (Quality Gate)
- Consistently choosing the same severity from a mapping table

This boundary defines the architecture for the next version.

---

## 9. Recommended Solution (implemented in v1.9)

Based on this analysis, v1.9 implements a **three-layer architecture**:

```
Layer 1 (LLM): Find issues + describe them
    ↓ generates report.md
Layer 2 (Script): validate-report.py — verify rule IDs & severities
    ↓ corrections applied
Layer 3 (Script): compute-gate.py — deterministic PASS/FAIL
    ↓ authoritative gate result
```

Additionally, v1.9 introduces:
- **Dimension-based scanning**: 5 mandatory dimensions with explicit rule
  checklists, reducing the "random walk" behavior
- **Adversarial verification**: Each finding is challenged with exclusion
  conditions before inclusion, reducing false positives

### Verification (v1.9 scripts against v1.8.1 data):

| Report | v1.8.1 Gate | v1.9 Script Gate | Notes |
|--------|-------------|-----------------|-------|
| Run 3 admin R&M | FAIL | **PASS** | 8/9 fabricated rules removed |
| Run 2 admin R&M | PASS | **PASS** | All valid, 4 severity corrections |
| Run 1 fss R&M | FAIL | **Needs correction** | S1186 CRITICAL→HIGH, then PASS |

**If v1.9 scripts had been in place, all 3 runs would have produced PASS** —
demonstrating that the actual code (managed backend) has no gate-blocking issues,
and all FAIL results were artifacts of LLM hallucination.

---

## 10. Appendix: Fabricated Rule IDs Found

The following rule IDs appeared in scan reports but **do not exist** in the
organization's SonarQube standards file (`sonarqube-java-standards.md`, 222 rules):

| Fabricated ID | Used For | Appeared In |
|---------------|----------|-------------|
| `java:S3330` | Cookie HttpOnly attribute | Run 3 |
| `java:S5122` | ThreadLocal cleanup | Run 3 |
| `java:S4784` | Regular expression DoS | Run 3 |
| `java:S4790` | Hashing/MD5 security | Run 3, Run 1 |
| `java:S1148` | printStackTrace usage | Run 3 |
| `java:S106` | System.out.println | Run 3 |
| `java:S2068` | Hardcoded credentials | Run 1 |

Additionally, the following real rule IDs were **misattributed** (used for
issues they don't cover):

| Real ID | Actual Definition | Misused For |
|---------|------------------|-------------|
| `java:S131` | Switch default clause | Authentication bypass |
| `java:S2119` | Random object reuse | MD5 hashing weakness |
