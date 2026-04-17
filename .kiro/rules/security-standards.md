# Security Review Standards

This rule defines the security review criteria. Apply these standards whenever
reviewing code for security issues.

## Severity Classification (CVSS v3.1)

Severity MUST be determined by computing a CVSS v3.1 Base Score using the
official vector string. Do NOT estimate scores — evaluate each metric:

| Metric | Values |
|--------|--------|
| Attack Vector (AV) | Network / Adjacent / Local / Physical |
| Attack Complexity (AC) | Low / High |
| Privileges Required (PR) | None / Low / High |
| User Interaction (UI) | None / Required |
| Scope (S) | Unchanged / Changed |
| Confidentiality (C) | None / Low / High |
| Integrity (I) | None / Low / High |
| Availability (A) | None / Low / High |

### Score → Severity Mapping

| Severity | CVSS Range | Disposition |
|----------|-----------|-------------|
| Critical | 9.0 – 10.0 | Must be fixed before acceptance. Zero tolerance. |
| High | 7.0 – 8.9 | Must be fixed or have documented mitigation plan. |
| Medium | 4.0 – 6.9 | Should be fixed. Acceptable with risk acknowledgment. |
| Low | 0.1 – 3.9 | Recommended fix. Does not block acceptance. |
| Info | 0.0 | Informational observation, no security impact. |

### CVE Association Rules

Every finding MUST include a `关联 CVE` field, following these rules:

1. **Known vulnerability pattern** — if the code matches a known CVE's vulnerable
   pattern (e.g., Shiro hardcoded key → CVE-2016-4437, Log4j JNDI lookup →
   CVE-2021-44228, Fastjson autoType → CVE-2022-25845), cite the CVE directly.
2. **Vulnerable dependency** — if a dependency version is known to be affected by
   a CVE (from Trivy/SCA reports or known advisories), cite all applicable CVEs.
3. **Code logic flaw** — for custom code vulnerabilities (missing authorization,
   IDOR, business logic errors) that have no matching CVE, use:
   `关联 CVE: N/A — 代码逻辑缺陷 (CWE-[ID])`
4. **Similar pattern** — if the code exhibits a pattern similar to but not exactly
   matching a known CVE, use: `关联 CVE: CVE-XXXX-XXXXX 模式 (相似漏洞模式)`

## Vulnerability Density Thresholds

- Excellent: < 0.1 vulnerabilities/KLOC
- Good: 0.1-0.3 vulnerabilities/KLOC
- Acceptable: 0.3-0.5 vulnerabilities/KLOC
- Unacceptable: > 0.5 vulnerabilities/KLOC

## Blocking Rules (CWE Top 5 — immediate reject if found)

These patterns MUST be flagged as Critical:

1. **CWE-79 Cross-Site Scripting (XSS)**
   - User input rendered in HTML without encoding/escaping
   - `innerHTML`, `dangerouslySetInnerHTML`, `v-html` with unvalidated data
   - Template injection in server-side rendering

2. **CWE-89 SQL Injection**
   - String concatenation or interpolation in SQL queries
   - Dynamic query building without parameterization
   - ORM raw query methods with unvalidated input

3. **CWE-352 Cross-Site Request Forgery (CSRF)**
   - State-changing endpoints without CSRF token validation
   - Missing SameSite cookie attributes on session cookies

4. **CWE-20 Improper Input Validation**
   - External input used without validation (type, length, format, range)
   - Relying solely on client-side validation
   - Missing validation on file uploads (type, size, content)

5. **CWE-78 OS Command Injection**
   - User input passed to shell commands (exec, system, spawn, popen)
   - Unsanitized input in subprocess calls

## High Severity Rules (CWE Top 6-25)

These patterns MUST be flagged as High:

6. **CWE-787 Out-of-bounds Write** — Buffer overflows, array index errors
7. **CWE-416 Use After Free** — Memory safety issues
8. **CWE-22 Path Traversal** — File path construction with user input without sanitization
9. **CWE-862 Missing Authorization** — Endpoints or functions without authorization checks
10. **CWE-476 NULL Pointer Dereference** — Unhandled null/undefined references

## OWASP Top 10 Check Matrix

For every review, systematically check:

| OWASP ID | Category | What to Look For |
|----------|----------|-----------------|
| A01 | Broken Access Control | Missing auth checks, IDOR, privilege escalation paths, CORS misconfiguration |
| A02 | Cryptographic Failures | Hardcoded secrets, weak algorithms (MD5/SHA1 for passwords), missing encryption for sensitive data, plaintext credentials in config |
| A03 | Injection | SQL/NoSQL/OS/LDAP injection, template injection, header injection |
| A04 | Insecure Design | Missing rate limiting, no input validation strategy, trust boundary violations |
| A05 | Security Misconfiguration | Debug mode enabled, default credentials, overly permissive CORS, verbose error messages exposing internals |
| A06 | Vulnerable Components | Known vulnerable dependencies, outdated frameworks, unmaintained libraries |
| A07 | Authentication Failures | Weak password requirements, missing MFA support, insecure session management, credential stuffing vulnerability |
| A08 | Data Integrity Failures | Insecure deserialization, unsigned updates, untrusted CI/CD pipeline inputs |
| A09 | Logging Failures | Missing security event logging, sensitive data in logs, no audit trail for critical operations |
| A10 | SSRF | URL fetching with user-controlled input without allowlist validation |

## Hardcoded Secrets Detection

ALWAYS check for these patterns (flag as Critical):
- API keys, tokens, passwords in source code
- Private keys or certificates in repository
- Database connection strings with embedded credentials
- AWS access keys, Azure keys, GCP service account keys
- `.env` files committed to repository
- Secrets in Docker build args or environment variables in Dockerfiles

## Infrastructure Security (if IaC is present)

- S3 buckets: public access blocked, encryption enabled
- IAM policies: least privilege, no wildcard permissions
- Security groups: no unrestricted inbound (0.0.0.0/0) on sensitive ports
- Database instances: not publicly accessible, encryption at rest enabled
- Logging: CloudTrail/audit logging enabled
- Container images: non-root user, minimal base image, no secrets in layers
