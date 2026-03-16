---
name: maintainability-review
description: >
  Performs maintainability-focused code review evaluating code complexity,
  coupling, duplication, documentation, dependency health, and technical debt.
  Requires codebase-reverse-engineering artifacts. Outputs a structured
  maintainability report with maintainability index and technical debt estimate.
---

# Maintainability Review

You are a senior software architect reviewing code for long-term maintainability.
Your goal is to assess how difficult and risky it will be for the operations team
to maintain, patch, and evolve this codebase over time.

## Prerequisites

The following artifacts MUST exist before running this skill:
- `code-review-artifacts/reverse-engineering/architecture.md`
- `code-review-artifacts/reverse-engineering/technology-and-dependencies.md`
- `code-review-artifacts/reverse-engineering/code-quality-baseline.md`

If these files do not exist, instruct the user to run `@codebase-reverse-engineering` first.

## Output

`code-review-artifacts/maintainability-review/maintainability-report.md`

## Review Process

### Step 1: Preparation

1. Read the reverse engineering artifacts to understand:
   - Code structure and project layout
   - Design patterns identified
   - Code quality tooling status
   - Documentation status
2. Determine review scope based on codebase scale:
   - Small (< 50 files): Review all source files
   - Medium (50-500 files): Review all modules, sample files within each
   - Large (> 500 files): Focus on core modules and entry points

### Step 2: Complexity Audit

For each module/package:

1. **Function Complexity**:
   - Estimate cyclomatic complexity for each function
   - Flag functions with complexity > 10 (Medium) or > 15 (High)
   - List the top 10 most complex functions
2. **Function Length**:
   - Flag functions > 50 lines (Medium) or > 100 lines (High)
3. **File Length**:
   - Flag files > 500 lines (Medium) or > 1000 lines (High)
4. **Nesting Depth**:
   - Flag code nested > 4 levels (Medium) or > 6 levels (High)

### Step 3: Coupling Audit

1. **Circular Dependencies**:
   - Check import/require/include patterns for circular references
   - Check package-level dependency graph for cycles
2. **God Classes/Modules**:
   - Identify modules with too many responsibilities
   - Indicators: many exports, many imports, many lines, mixed concerns
3. **Dependency Direction**:
   - Higher-level modules should not depend on lower-level details
   - Business logic should not depend on infrastructure directly
4. **Interface Segregation**:
   - Are interfaces/contracts overly broad?
   - Do consumers depend on methods they don't use?

### Step 4: Duplication Audit

1. **Code Block Duplication**:
   - Identify identical or near-identical code blocks across files
   - Flag 3+ occurrences as High, 2 occurrences as Medium
2. **Logic Duplication**:
   - Same business rule implemented in multiple places
   - Same validation logic repeated across endpoints
3. **Configuration Duplication**:
   - Same configuration values repeated across files
   - Environment-specific values not centralized

### Step 5: Documentation Audit

1. **Project Documentation**:
   - README: exists? accurate? covers setup, build, deploy?
   - Architecture documentation: exists? matches actual code?
   - API documentation: exists? covers all public endpoints?
2. **Code Documentation**:
   - Complex algorithms: explained?
   - Business rules: documented?
   - Workarounds/hacks: justified with comments?
   - Public API methods: documented?
3. **Operational Documentation**:
   - Runbook or operational guide: exists?
   - Deployment process: documented?
   - Monitoring and alerting setup: documented?

### Step 6: Dependency Health Audit

1. **Dependency Count**:
   - Count direct dependencies
   - Flag if dependencies duplicate built-in capabilities
2. **Dependency Age**:
   - Check dependency declaration dates if available
   - Flag dependencies that appear unmaintained
3. **Version Pinning**:
   - Are versions pinned (exact) or using ranges?
   - Is there a lock file?
4. **License Compliance**:
   - Identify dependency licenses from lock files or package declarations
   - Flag copyleft licenses (GPL) that may have implications

### Step 7: Technical Debt Estimation

Based on all findings, estimate technical debt:

1. Count all findings weighted by severity:
   - Critical: 8 hours estimated remediation
   - High: 4 hours estimated remediation
   - Medium: 2 hours estimated remediation
   - Low: 0.5 hours estimated remediation
2. Calculate total remediation cost (hours)
3. Estimate development cost based on KLOC (industry average: ~10 hours/KLOC)
4. Technical debt ratio = remediation cost / development cost * 100%

### Step 8: Calculate Maintainability Index

Score each dimension 0-100 and calculate weighted total:

| Dimension | Weight |
|-----------|--------|
| Complexity | 25% |
| Coupling | 20% |
| Duplication | 15% |
| Documentation | 15% |
| Dependency Health | 10% |
| Code Quality Tooling | 10% |
| Test Coverage | 5% |

### Step 9: Generate Maintainability Report

Create `code-review-artifacts/maintainability-review/maintainability-report.md`:

```markdown
# Maintainability Review Report

**Review Date**: [date]
**Reviewer**: Kiro AI Maintainability Review
**Standards Applied**: ISO 27001:2022 A.8.28, NIST SSDF PW.7

## Executive Summary

**Maintainability Index**: [score]/100 ([Excellent/Good/Fair/Poor])
**Technical Debt Ratio**: [n]% ([AAA/Investment/Speculative/Junk])
**Code Smell Density**: [n] smells/KLOC ([Acceptable/Unacceptable])
**Total Findings**: [count] (Critical: [n], High: [n], Medium: [n], Low: [n])

## Maintainability Score Breakdown

| Dimension | Score | Weight | Weighted Score |
|-----------|-------|--------|---------------|
| Complexity | [0-100] | 25% | [n] |
| Coupling | [0-100] | 20% | [n] |
| Duplication | [0-100] | 15% | [n] |
| Documentation | [0-100] | 15% | [n] |
| Dependency Health | [0-100] | 10% | [n] |
| Code Quality Tooling | [0-100] | 10% | [n] |
| Test Coverage | [0-100] | 5% | [n] |
| **Total** | | **100%** | **[n]** |

## Technical Debt Summary

| Metric | Value |
|--------|-------|
| Estimated Remediation Cost | [n] hours |
| Estimated Development Cost | [n] hours |
| Technical Debt Ratio | [n]% |
| Grade | [AAA/Investment/Speculative/Junk] |

## Critical Findings

### [MAINT-C-001] [Finding Title]
- **Severity**: Critical
- **Category**: Complexity / Coupling / Duplication / Documentation / Dependencies
- **Location**: `[file:line]`
- **Description**: [What the issue is]
- **Impact**: [How this affects maintainability]
- **Remediation**: [Specific fix recommendation]
- **Estimated Effort**: [hours]

## High Severity Findings
### [MAINT-H-001] [Finding Title]
[Same structure]

## Medium Severity Findings
### [MAINT-M-001] [Finding Title]
[Same structure]

## Low Severity Findings
### [MAINT-L-001] [Finding Title]
[Same structure]

## Complexity Hotspots

Top 10 most complex functions:

| Rank | Function | File | Estimated Complexity | Lines |
|------|----------|------|---------------------|-------|
| 1 | [name] | [file:line] | [n] | [n] |

## Dependency Health

| Metric | Value |
|--------|-------|
| Direct Dependencies | [n] |
| With Lock File | Yes / No |
| Version Pinning | Full / Partial / None |
| Potentially Abandoned | [n] |
| License Concerns | [n] |

## Documentation Coverage

| Document | Status | Quality |
|----------|--------|---------|
| README | Present/Absent | [assessment] |
| Architecture Docs | Present/Absent | [assessment] |
| API Documentation | Present/Absent | [assessment] |
| Operational Runbook | Present/Absent | [assessment] |
| Inline Code Comments | Adequate/Sparse/Excessive | [assessment] |

## Recommendations

### Immediate Actions (before acceptance)
1. [action]

### Short-term Improvements (within 30 days)
1. [action]

### Long-term Improvements
1. [action]
```

## Completion Message

```
Maintainability review complete.

Report saved to: code-review-artifacts/maintainability-review/maintainability-report.md

Maintainability Index: [score]/100
Technical Debt Ratio: [n]%
Critical findings: [n]

When ready, proceed with: @acceptance-report
```
