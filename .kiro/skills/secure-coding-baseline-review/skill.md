---
name: secure-coding-baseline-review
description: >
  Generates a Security report for a single module based on the Philips Secure
  Coding Baseline (BSL 11.1.1.d, 230 controls across 17 security domains).
  Strict control-to-ID mapping, quality gate, fix priorities (P0–P3), and
  LLM-discovered issues isolated in appendix.
---

# Security Review (Philips Secure Coding Baseline)

You are a senior security engineer. Generate a **Security** report for the
specified module by checking it against the Philips Secure Coding Baseline
(BSL 11.1.1.d, Version 3, 230 controls).

## Prerequisites

- `code-review-artifacts/reverse-engineering/` artifacts must exist.
  If not, instruct the user to run `@codebase-reverse-engineering` first.
- The module path must be specified by the user or the batch-scan orchestrator.

## Output

`code-review-artifacts/[MODULE_NAME]_Security_Report_[YYYY-MM-DD].md`

## Applicability

This review applies to ALL programming languages and application types. Mark
inapplicable controls as N/A with justification.

---

## CRITICAL CONSTRAINTS

### Constraint 0: Unified Finding Header

Every finding in this report MUST begin with the following 4-line header block,
placed immediately after the finding title, before any other fields:

```
**Risk Level**: CRITICAL / HIGH / MEDIUM / LOW
**CVSS Score**: [score] ([severity])
**File**: `[file/path.java:line]`
**Associated CVE**: [CVE-ID / CVE-ID pattern / N/A — code logic defect (CWE-ID)]
```

Rules for each field:
- **Risk Level**: Derived from the CVSS score (see Constraint 2).
- **CVSS Score**: Always computed for Security report findings. Include the full
  CVSS vector string on a separate line below.
- **File**: Exact file path and line number where the issue was found.
- **Associated CVE**: Associate a CVE if a known CVE pattern matches. If no CVE matches,
  use `N/A — code logic defect (CWE-xxx)`.

This header format is shared across ALL report types (R&M, Security, Security Review)
to ensure consistent presentation when reports are compared side-by-side.

### Constraint 1: Strict Control-to-ID Mapping

Every issue in the main report body MUST map to a specific BSL control in
`.kiro/rules/secure-coding-baseline-standards.md`. For each issue:
- Provide the **exact BSL Control ID** (e.g., `11.1.1_41`)
- Provide the **exact control description** from the standards file
- Assign severity based on the control's security domain and impact

**Prohibitions:**
- Do NOT report issues with control IDs not found in the standards file
- Do NOT invent BSL control IDs

### Constraint 2: Severity Classification (CVSS v3.1)

Assign severity by computing a CVSS v3.1 Base Score per the definitions in
`.kiro/rules/secure-coding-baseline-standards.md` (Appendix A). Evaluate all
8 metrics (AV/AC/PR/UI/S/C/I/A) and produce the full vector string.

| Severity | CVSS Range | Typical Control Areas |
|----------|-----------|----------------------|
| **Critical** | 9.0 – 10.0 | Injection prevention, credential storage, authentication bypass, encryption failures |
| **High** | 7.0 – 8.9 | Access control, session management, TLS configuration, logging gaps |
| **Medium** | 4.0 – 6.9 | Configuration, coding practices, design requirements |
| **Low** | 0.1 – 3.9 | Informational coding practices, minor config gaps |

Every finding MUST also include a `Associated CVE` field per the CVE Association
Rules in Appendix A of the standards file.

### Constraint 3: LLM-Discovered Issues Go to Appendix

Security issues found that cannot map to a BSL control ID go to the
**Appendix** section only. They do NOT affect the quality gate.

---

## Review Process

### Step 1: Preparation

1. Read reverse engineering artifacts for the module
2. Read BSL standards from `.kiro/rules/secure-coding-baseline-standards.md`
3. Determine applicable domains based on application type
4. Build a control checklist — every applicable control gets checked

### Step 2: Domain-by-Domain Scanning

Scan the module against each of the 17 BSL security domains:

1. **Authentication & Password Management** (11.1.1_1 – 11.1.1_31)
   - Authentication enforcement, credential storage, password policy
   - Grep for: auth bypass patterns, MD5/SHA1 password hashing, hardcoded credentials
   
2. **Communications Security** (11.1.1_32 – 11.1.1_39)
   - TLS configuration, secure transport
   - Grep for: TLSv1.0, SSLv3, `rejectUnauthorized: false`, `http://` URLs

3. **Cryptography** (11.1.1_40 – 11.1.1_46)
   - Secure random, no deprecated crypto, no keys in source
   - Grep for: `Math.random()`, `java.util.Random`, DES, RC4, hardcoded keys

4. **Data Protection** (11.1.1_47 – 11.1.1_59)
   - Encryption at rest, client-side data exposure
   - Grep for: `localStorage.*password`, sensitive data in GET params

5. **Database Security** (11.1.1_60 – 11.1.1_73)
   - Parameterized queries, DB access credentials
   - Grep for: SQL string concatenation, hardcoded connection strings

6. **Error Handling & Logging** (11.1.1_74 – 11.1.1_98)
   - No stack traces to client, security event logging
   - Grep for: `printStackTrace()`, sensitive data in logs

7. **File Management** (11.1.1_99 – 11.1.1_112)
   - Upload validation, path traversal prevention
   - Grep for: `new File(request.`, dynamic include/require

8. **General Coding Practices** (11.1.1_113 – 11.1.1_124)
   - No OS commands, no eval(), race condition protection
   - Grep for: `Runtime.exec`, `eval(`, `Function(`

9. **Input Validation** (11.1.1_125 – 11.1.1_139)
   - Server-side validation, canonicalization
   - Grep for: missing server-side validation, `../` in path handling

10. **Logical Access Control** (11.1.1_140 – 11.1.1_162)
    - Server-side authorization, IDOR prevention
    - Grep for: endpoints without auth middleware, direct object references

11. **Memory Management** (11.1.1_163 – 11.1.1_172)
    - Buffer safety, resource cleanup (N/A for managed languages mostly)

12. **Output Encoding** (11.1.1_173 – 11.1.1_178)
    - XSS prevention, contextual encoding
    - Grep for: `innerHTML`, `dangerouslySetInnerHTML`, `document.write`

13. **Secure Design** (11.1.1_179 – 11.1.1_187)
    - Threat modeling, security tests, tier segregation

14. **Security Configuration** (11.1.1_188 – 11.1.1_193)
    - Dependency management, vulnerability remediation

15. **Security Logging** (11.1.1_194 – 11.1.1_201)
    - Event monitoring, audit trails

16. **Session Management** (11.1.1_202 – 11.1.1_216)
    - Cookie security, CSRF protection, session lifecycle
    - Grep for: missing Secure/HttpOnly flags, CSRF tokens

17. **System Configuration** (11.1.1_217 – 11.1.1_228)
    - Patching, test code removal, HTTP method restrictions

For each control violation found, record:
- BSL Control ID and description
- Severity (Critical / High / Medium)
- File path and code snippet
- Root cause and business impact
- Fix recommendation
- Fix priority (P0–P3)

### Step 3: Assign Fix Priority

| Priority | Meaning | Typical Scenarios |
|----------|---------|-------------------|
| **P0** | Must fix before release | Credential exposure, injection, auth bypass; some Medium |
| **P1** | Short-term fix (1–2 weeks) | High-risk access control / session issues |
| **P2** | Medium-term fix (1 month) | Configuration gaps, logging improvements |
| **P3** | Long-term optimization | Design-level improvements, process controls |

Medium-severity issues MUST have explicit P0–P3 assignment.
A Medium issue rated P0 causes the quality gate to **Fail**.

### Step 4: Self-Validation

1. Every issue's BSL Control ID exists in the standards file
2. Every Medium issue has a P0–P3 label
3. Issues without valid BSL Control IDs are in the Appendix only
4. All applicable controls have been evaluated

### Step 5: Quality Gate Evaluation

```
Pass conditions (ALL must be true):
  - 0 Critical issues
  - 0 High issues
  - 0 Medium issues with priority P0
Otherwise: Fail
```

### Step 6: Generate Report

---

## Report Template

```markdown
# [MODULE_NAME] Security Report

**Repository / Module**: [name]
**Scan Date**: [YYYY-MM-DD]
**Review Standards**: Philips Secure Coding Baseline (BSL 11.1.1.d v3)
**Rule ID Format**: `11.1.1_[number]` (BSL control identifier)

---

## 1. Review Summary

### 1.1 Issue Statistics by Security Domain

| Security Domain | Critical | High | Medium | Total |
|----------------|----------|------|--------|-------|
| Authentication & Password Mgmt | [n] | [n] | [n] | [n] |
| Communications Security | [n] | [n] | [n] | [n] |
| Cryptography | [n] | [n] | [n] | [n] |
| Data Protection | [n] | [n] | [n] | [n] |
| Database Security | [n] | [n] | [n] | [n] |
| Error Handling & Logging | [n] | [n] | [n] | [n] |
| File Management | [n] | [n] | [n] | [n] |
| General Coding Practices | [n] | [n] | [n] | [n] |
| Input Validation | [n] | [n] | [n] | [n] |
| Logical Access Control | [n] | [n] | [n] | [n] |
| Memory Management | [n] | [n] | [n] | [n] |
| Output Encoding | [n] | [n] | [n] | [n] |
| Secure Design | [n] | [n] | [n] | [n] |
| Security Configuration | [n] | [n] | [n] | [n] |
| Security Logging | [n] | [n] | [n] | [n] |
| Session Management | [n] | [n] | [n] | [n] |
| System Configuration | [n] | [n] | [n] | [n] |
| **Total** | **[n]** | **[n]** | **[n]** | **[n]** |

### 1.2 Quality Gate

**Status: [PASS / FAIL]**

| Criteria | Threshold | Actual | Result |
|----------|-----------|--------|--------|
| Critical issues | 0 | [n] | Pass/Fail |
| High issues | 0 | [n] | Pass/Fail |
| Medium issues with P0 priority | 0 | [n] | Pass/Fail |

---

## 2. Issue Details

### SEC-01: [Brief title]

**Risk Level**: [CRITICAL / HIGH / MEDIUM / LOW]
**CVSS Score**: [score] ([severity])
**File**: `[file/path.java:line]`
**Associated CVE**: [CVE-ID / CVE-ID pattern / N/A — code logic defect (CWE-ID)]

- **BSL Control**: `11.1.1_[xx]` — [Control description from standards]
- **Security Domain**: [domain name]
- **CVSS Vector**: `CVSS:3.1/AV:_/AC:_/PR:_/UI:_/S:_/C:_/I:_/A:_`
- **Fix Priority**: [P0 / P1 / P2 / P3]

**Code**:
```java
// Noncompliant code snippet
```

**Root Cause & Business Impact**:
[Explain why this is a security problem and what business risk it poses]

**Fix Recommendation**:
[Specific, actionable fix for THIS code — not generic advice]

**Impact of Not Fixing**:
[What happens if this issue is left unresolved — security risk description]

---

[Repeat for each issue: SEC-02, SEC-03, etc.]

---

## 3. Fix Priority Summary

| Priority | Count | Description |
|----------|-------|-------------|
| P0 | [n] | Must fix before release |
| P1 | [n] | Fix within 1–2 weeks |
| P2 | [n] | Fix within 1 month |
| P3 | [n] | Long-term optimization |

### P0 Issues (Release Blockers)

| Issue ID | BSL Control | Severity | Location | Description |
|----------|-------------|----------|----------|-------------|
| [SEC-01] | [11.1.1_xx] | [Critical] | [file:line] | [brief] |

---

## 4. BSL Compliance Summary

| Metric | Value |
|--------|-------|
| Total BSL controls | 230 |
| Applicable controls | [n] |
| Compliant (Pass) | [n] |
| Non-compliant (Fail) | [n] |
| Not applicable (N/A) | [n] |
| Compliance rate | [n]% |

---

## 5. Appendix: Additional Security Findings (General Best Practices)

> The following security issues were identified during review but do NOT map
> to any BSL control in the specified standards. They are based on general
> security best practices (e.g., OWASP, CWE) and are provided for reference
> only. They do NOT affect the quality gate determination.

### APP-01: [Title]
- **Source**: General best practices (not in BSL control set)
- **Location**: `[file:line]`
- **Description**: [issue description]
- **Recommendation**: [fix suggestion]

[If none: "No additional findings outside the BSL control set."]
```

## Completion Message

```
Security report generated.
Output: code-review-artifacts/[MODULE]_Security_Report_[DATE].md

Quality Gate: [PASS / FAIL]
Issues: Critical=[n], High=[n], Medium=[n] (P0=[n])
BSL Compliance: [n]% ([n] applicable controls checked)
```
