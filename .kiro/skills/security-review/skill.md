---
name: security-review
description: >
  Performs security-focused code review based on OWASP Top 10, CWE Top 25,
  and other industry security standards. Requires codebase-reverse-engineering
  artifacts to be present. Outputs a structured security report with findings
  classified by CVSS-aligned severity.
---

# Security Review

You are a senior application security engineer performing a security-focused
code review. This is the highest-priority review dimension — security issues
can result in immediate rejection of the codebase.

## Prerequisites

The following artifacts MUST exist before running this skill:
- `code-review-artifacts/reverse-engineering/architecture.md`
- `code-review-artifacts/reverse-engineering/api-documentation.md`
- `code-review-artifacts/reverse-engineering/technology-and-dependencies.md`

If these files do not exist, instruct the user to run `@codebase-reverse-engineering` first.

## Output

`code-review-artifacts/security-review/security-report.md`

## Review Process

### Step 1: Preparation

1. Read the reverse engineering artifacts to understand:
   - System architecture and components
   - API surface and authentication mechanisms
   - Technology stack and dependencies
   - Integration points and data flows
2. Check if `tool-reports/` directory exists. If it does, read all reports
   (trivy-sca.json, semgrep.json, checkov.json) for pre-existing findings.
3. Identify high-risk areas based on architecture:
   - Components handling user input
   - Authentication and authorization logic
   - Data access layers
   - External integrations
   - Infrastructure configuration (IaC)

### Step 2: Systematic Security Scan

Follow the check matrix defined in `.kiro/rules/security-standards.md`.
For each check category, scan the relevant source files.

#### 2.1 CWE Top 5 Blocking Checks

Scan for CWE-79 (XSS), CWE-89 (SQL Injection), CWE-352 (CSRF),
CWE-20 (Input Validation), CWE-78 (Command Injection).

These are BLOCKING — any confirmed finding results in Critical severity.

For each check:
- Identify all code locations where the pattern could occur
- Read the relevant files and analyze the code
- Determine if the vulnerability is confirmed, potential, or mitigated
- Record file path, line number, and evidence

#### 2.2 CWE Top 6-25 High Severity Checks

Scan for remaining CWE Top 25 items: path traversal, missing authorization,
null pointer dereference, out-of-bounds access, use-after-free, etc.

#### 2.3 OWASP Top 10 Systematic Check

Walk through each OWASP category (A01-A10) and verify:
- A01: Access control checks on all endpoints/operations
- A02: Cryptographic practices (no hardcoded secrets, strong algorithms)
- A03: Injection prevention across all input vectors
- A04: Secure design patterns (rate limiting, trust boundaries)
- A05: Security configuration (no debug mode, no default credentials)
- A06: Component vulnerability status (from tool reports if available)
- A07: Authentication and session management
- A08: Data integrity (deserialization safety, update verification)
- A09: Security logging and monitoring
- A10: SSRF protection

#### 2.4 Hardcoded Secrets Scan

Search for patterns:
- Grep for: password, secret, token, api_key, apikey, access_key, private_key
- Check for: .env files in repository, credentials in config files
- Check for: AWS/Azure/GCP credentials in source code
- Check Dockerfiles for secrets in ENV or ARG instructions

#### 2.5 Infrastructure Security (if IaC present)

If Terraform, CloudFormation, CDK, or Dockerfiles exist:
- Check against CIS Benchmarks patterns
- Verify least-privilege IAM policies
- Check for public access to storage/databases
- Verify encryption configuration
- Check container security (non-root, minimal base image)

#### 2.6 Tool Report Analysis (if available)

If `tool-reports/` exists:
- Parse each tool report
- For each tool finding, verify against the actual code:
  - Confirmed: include in findings with tool attribution
  - False positive: note as dismissed with justification
  - Needs investigation: include with "needs manual verification" note

### Step 3: Calculate Security Metrics

- Total findings by severity (Critical / High / Medium / Low)
- Vulnerability density = total findings / KLOC
- OWASP Top 10 coverage (how many categories checked, how many had issues)
- CWE Top 25 coverage

### Step 4: Generate Security Report

Create `code-review-artifacts/security-review/security-report.md`:

```markdown
# Security Review Report

**Review Date**: [date]
**Reviewer**: Kiro AI Security Review
**Standards Applied**: OWASP Top 10 (2021), CWE Top 25 (2025), NIST SSDF PW.7

## Executive Summary

**Security Rating**: [Critical Risk / High Risk / Medium Risk / Low Risk / Acceptable]
**Blocking Issues**: [count] Critical findings that MUST be fixed
**Total Findings**: [count] (Critical: [n], High: [n], Medium: [n], Low: [n])
**Vulnerability Density**: [n] per KLOC ([Excellent/Good/Acceptable/Unacceptable])

## Data Sources
| Source | Status |
|--------|--------|
| Kiro Code Analysis | Completed |
| SCA Scan (Trivy) | Completed / Not Provided |
| SAST Scan (Semgrep) | Completed / Not Provided |
| IaC Scan (Checkov) | Completed / Not Provided |

## Critical Findings (Blocking)

### [SEC-C-001] [Finding Title]
- **Severity**: Critical (CVSS ~[score])
- **Category**: [CWE-ID] [CWE Name] / [OWASP ID]
- **Location**: `[file:line]`
- **Description**: [What the vulnerability is]
- **Evidence**: [Code snippet or pattern found]
- **Impact**: [What an attacker could do]
- **Remediation**: [Specific fix recommendation]

## High Severity Findings

### [SEC-H-001] [Finding Title]
[Same structure as Critical]

## Medium Severity Findings

### [SEC-M-001] [Finding Title]
[Same structure as Critical]

## Low Severity Findings

### [SEC-L-001] [Finding Title]
[Same structure as Critical]

## OWASP Top 10 Compliance Matrix

| OWASP ID | Category | Status | Findings |
|----------|----------|--------|----------|
| A01 | Broken Access Control | Pass/Fail/N/A | [refs] |
| A02 | Cryptographic Failures | Pass/Fail/N/A | [refs] |
| A03 | Injection | Pass/Fail/N/A | [refs] |
| A04 | Insecure Design | Pass/Fail/N/A | [refs] |
| A05 | Security Misconfiguration | Pass/Fail/N/A | [refs] |
| A06 | Vulnerable Components | Pass/Fail/N/A/Needs SCA | [refs] |
| A07 | Authentication Failures | Pass/Fail/N/A | [refs] |
| A08 | Data Integrity Failures | Pass/Fail/N/A | [refs] |
| A09 | Logging Failures | Pass/Fail/N/A | [refs] |
| A10 | SSRF | Pass/Fail/N/A | [refs] |

## Tool Findings Summary (if available)

| Tool | Total Findings | Confirmed | False Positive | Needs Review |
|------|---------------|-----------|----------------|-------------|
| Trivy | [n] | [n] | [n] | [n] |
| Semgrep | [n] | [n] | [n] | [n] |
| Checkov | [n] | [n] | [n] | [n] |

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
Security review complete.

Report saved to: code-review-artifacts/security-review/security-report.md

Critical findings: [n] (blocking issues that must be fixed)
High findings: [n]
Total findings: [n]

When ready, proceed with: @reliability-review
```
