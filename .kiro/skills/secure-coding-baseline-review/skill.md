---
name: secure-coding-baseline-review
description: >
  Performs a Secure Coding Baseline (BSL 11.1.1.d) compliance review against
  230 security controls across 17 security domains. Checks authentication,
  communications security, cryptography, data protection, database security,
  input validation, access control, session management, and more. Requires
  codebase-reverse-engineering artifacts. Outputs a structured BSL compliance
  report with findings mapped to BSL control IDs.
---

# Secure Coding Baseline Review (BSL 11.1.1.d)

You are a senior security engineer performing a compliance review against the
organization's Secure Coding Baseline (BSL 11.1.1.d, Version 3, October 2025).
Your goal is to systematically check the codebase against 230 mandatory security
controls across 17 security domains.

This review complements the standard security review (OWASP/CWE-based) by
applying **organization-specific, policy-driven** security requirements that all
applications must meet before production deployment.

## Prerequisites

The following artifacts MUST exist before running this skill:
- `code-review-artifacts/reverse-engineering/architecture.md`
- `code-review-artifacts/reverse-engineering/technology-and-dependencies.md`
- `code-review-artifacts/reverse-engineering/code-quality-baseline.md`

If these files do not exist, instruct the user to run `@codebase-reverse-engineering` first.

## Output

`code-review-artifacts/secure-coding-baseline-review/bsl-report.md`

## Applicability

This review applies to ALL application types and programming languages. Unlike
the SonarQube review which is language-specific, BSL controls are
technology-agnostic security requirements. However, not all 230 controls apply
to every project — mark inapplicable controls as "N/A" with justification.

## Review Process

### Step 1: Preparation

1. Read the reverse engineering artifacts to understand:
   - Application type (web app, API, mobile, batch, etc.)
   - Programming languages and frameworks
   - Authentication mechanism (SSO, OIDC, SAML, custom)
   - Database technology
   - Deployment model (on-prem, cloud, container)
2. Read the BSL rules from `.kiro/rules/secure-coding-baseline-standards.md`
3. Determine applicability:
   - Web application: all 17 domains apply
   - API service: Session Management may be partially N/A
   - CLI/batch tool: Session Management, Website Coding likely N/A
   - Library/SDK: many domains may be N/A (document which and why)

### Step 2: Authentication & Password Management (31 controls)

**BSL Controls**: 11.1.1_1 through 11.1.1_31

Check systematically:

#### 2.1 Authentication Requirements
- All pages/resources require authentication except explicitly public ones (11.1.1_1)
- Authentication enforced on server side, not client (11.1.1_2)
- Centralized authentication implementation (11.1.1_4)
- Authentication logic segregated from business logic (11.1.1_5)
- Authentication fails securely — deny access on failure (11.1.1_6)

Grep for:
- Authentication bypass patterns: routes/endpoints without auth middleware
- Client-side-only auth checks: `if (isLoggedIn)` without server verification
- Multiple auth implementations instead of centralized

#### 2.2 Credential Storage
- Passwords stored as cryptographically strong one-way salted hashes (11.1.1_8)
- No MD5 for password hashing, use bcrypt or equivalent (11.1.1_8)
- Password hashing on server side only (11.1.1_9)

Grep for: `MD5`, `SHA1` for password contexts, `password` in database schemas,
`bcrypt`, `scrypt`, `argon2`, `PBKDF2`, plain text password storage patterns

#### 2.3 Authentication Error Handling
- Generic error messages: "Invalid username and/or password" (11.1.1_11)
- No indication of which credential part is wrong

Grep for: `Invalid username`, `Invalid password`, `User not found`,
`Wrong password`, `No such user` — these are noncompliant messages

#### 2.4 External Credentials
- Credentials for external systems encrypted and stored securely (11.1.1_13)
- Not in source code

Grep for: `password=`, `secret=`, `token=`, `apiKey=`, `api_key=` in
configuration files, `.env` files committed, hardcoded connection strings

#### 2.5 Password Policy
- Complexity requirements enforced (11.1.1_15)
- Length requirements enforced (11.1.1_16)
- Account lockout after failed attempts (11.1.1_18)
- Password reset security (11.1.1_19-22)
- Multi-factor authentication for sensitive operations (11.1.1_30)

#### 2.6 Password Entry & Transmission
- Password entry obscured on screen (11.1.1_17)
- Passwords only sent over encrypted connections (11.1.1_14)

### Step 3: Communications Security (8 controls)

**BSL Controls**: 11.1.1_32 through 11.1.1_39

#### 3.1 TLS Configuration
- Weak ciphers disabled (11.1.1_32)
- TLS 1.2 or higher only (11.1.1_32, 11.1.1_33)
- Valid certificates with correct domain (11.1.1_33)
- No fallback to insecure connections (11.1.1_34)

Grep for:
- `TLSv1.0`, `TLSv1.1`, `SSLv3` — must not be enabled
- `TLS_RSA_WITH_RC4`, `DES`, `3DES`, `NULL`, `EXPORT` cipher suites
- `rejectUnauthorized: false`, `verify: false`, `ALLOW_ALL`
- `setHostnameVerifier`, `X509TrustManager` with empty implementations

#### 3.2 Secure Transport
- TLS for all authenticated content (11.1.1_35)
- TLS for external system connections (11.1.1_36)
- Single standard TLS implementation (11.1.1_37)

Grep for: `http://` URLs (should be `https://`), unencrypted connections
to databases, message queues, or external APIs

#### 3.3 HTTP Security
- Character encodings specified for all connections (11.1.1_38)
- Sensitive parameters filtered from HTTP Referer (11.1.1_39)

### Step 4: Cryptography (7 controls)

**BSL Controls**: 11.1.1_40 through 11.1.1_46

- Cryptographic functions on server/trusted system only (11.1.1_40)
- No cryptographic keys in source code (11.1.1_41) — keys must be in vault
- Master secrets protected from unauthorized access (11.1.1_42)
- Secure random number generator for security functions (11.1.1_44)
- No deprecated cryptographic functions (11.1.1_45)

Grep for:
- `Math.random()`, `java.util.Random` — must use `SecureRandom`/`crypto.randomBytes`
- Hard-coded keys: `private.*key`, `secret.*key`, `AES.*key` with string literals
- Deprecated: `DES`, `3DES`, `RC4`, `Blowfish`, `ECB` mode
- Key in code: `-----BEGIN.*KEY-----`, base64 key patterns

### Step 5: Data Protection (13 controls)

**BSL Controls**: 11.1.1_47 through 11.1.1_59

#### 5.1 Access & Storage
- Least privilege for data access (11.1.1_47)
- Cached/temporary copies protected and purged (11.1.1_48)
- Sensitive data encrypted at rest (11.1.1_49)
- Server-side source code not downloadable (11.1.1_50)

#### 5.2 Client-Side Protection
- No passwords/secrets in clear text on client (11.1.1_51)
- No sensitive info in HTTP GET parameters (11.1.1_54)
- Autocomplete disabled for sensitive fields (11.1.1_55)
- Client-side caching disabled for sensitive pages (11.1.1_56)

Grep for:
- `localStorage.setItem.*password`, `sessionStorage.*token`
- `autocomplete="on"` on password/sensitive fields
- Missing `Cache-Control: no-store` headers
- Sensitive data in URL query parameters

#### 5.3 Information Disclosure
- No sensitive comments in production code (11.1.1_52)
- No unnecessary documentation exposed (11.1.1_53)

Grep for: `TODO`, `FIXME`, `HACK`, `XXX`, `BUG`, `TEMP`, `DEBUG`,
comments with passwords, internal URLs, architecture details

### Step 6: Database Security (14 controls)

**BSL Controls**: 11.1.1_60 through 11.1.1_73

#### 6.1 Query Security
- Strongly typed parameterized queries (11.1.1_61)
- Input validation and output encoding for DB queries (11.1.1_62)
- Strongly typed variables (11.1.1_63)

Grep for SQL injection patterns:
- String concatenation in SQL: `"SELECT * FROM " + table`, `${variable}` in SQL
- `Statement.execute()` instead of `PreparedStatement`
- ORM raw query methods without parameterization

#### 6.2 Access Control
- Lowest privilege for database access (11.1.1_64)
- Secure credentials for DB access (11.1.1_65)
- Connection strings not hard-coded, stored encrypted (11.1.1_66)
- Different credentials per trust level (11.1.1_73)

Grep for: hard-coded `jdbc:`, `mongodb://`, `mysql://` with credentials,
`sa` or `root` as database user, connection strings in source files

#### 6.3 Database Hardening
- Default passwords changed (11.1.1_69)
- Unnecessary functionality disabled (11.1.1_70)
- Default vendor content removed (11.1.1_71)
- Connections closed promptly (11.1.1_68)

### Step 7: Error Handling & Logging (25 controls)

**BSL Controls**: 11.1.1_74 through 11.1.1_98

#### 7.1 Error Handling
- No sensitive info in error responses (11.1.1_74)
- No debugging/stack trace info displayed (11.1.1_75)
- Generic error messages with custom error pages (11.1.1_76)
- Application-level error handling, not server config (11.1.1_77)
- Proper resource cleanup on errors (11.1.1_78)

Grep for:
- `printStackTrace()`, `console.error(err)` exposing to client
- `e.getMessage()`, `e.toString()` in HTTP responses
- Stack traces in API error responses
- Missing try-finally for resource cleanup

#### 7.2 Logging Requirements
- Log all authentication attempts, especially failures (11.1.1_89)
- Log all access control failures (11.1.1_90)
- Log all input validation failures (11.1.1_88)
- Log all system exceptions (11.1.1_93)
- Log all admin functions and security config changes (11.1.1_94)
- No sensitive data in logs (11.1.1_86, 11.1.1_98)

Grep for:
- `log.*password`, `log.*token`, `log.*secret` — sensitive data in logs
- Authentication events without logging
- Missing log statements in catch blocks

### Step 8: File Management (14 controls)

**BSL Controls**: 11.1.1_99 through 11.1.1_112

- Authentication required before file upload (11.1.1_100)
- File type validation by header, not just extension (11.1.1_102)
- No user data in dynamic include/require (11.1.1_99)
- No user data in redirects without validation (11.1.1_108)
- No directory/file paths from user input (11.1.1_109)
- Never expose absolute file paths (11.1.1_110)
- Uploaded files scanned for malware (11.1.1_112)

Grep for:
- `require(userInput)`, `import(userInput)` — dynamic include
- `sendRedirect(request.getParameter(`, `res.redirect(req.query.`
- `new File(request.`, `fs.readFile(req.` — path traversal
- File upload handlers without type/size validation

### Step 9: General Coding Practices (12 controls)

**BSL Controls**: 11.1.1_113 through 11.1.1_124

- No direct OS commands from application (11.1.1_114)
- Integrity verification for code/libraries/configs (11.1.1_115)
- Locking/synchronization for concurrent access (11.1.1_116, 11.1.1_117)
- Explicit variable initialization (11.1.1_118)
- Minimal privilege escalation window (11.1.1_119)
- No user data in dynamic execution (11.1.1_121) — eval(), Function()
- Users cannot generate/alter code (11.1.1_122)

Grep for:
- `Runtime.exec(`, `ProcessBuilder(`, `child_process.exec(`, `os.system(`
- `eval(`, `Function(`, `setTimeout(string`, `setInterval(string`
- `new Function(`, `vm.runInContext(`
- Uninitialized variables in security-critical paths

### Step 10: Input Validation (15 controls)

**BSL Controls**: 11.1.1_125 through 11.1.1_139

- Server-side validation for all data (11.1.1_125)
- Centralized validation routine (11.1.1_127)
- Proper character set specification (11.1.1_128)
- Canonicalization before validation (11.1.1_129)
- Validation failures result in rejection (11.1.1_130)
- Validate all client data including headers, cookies (11.1.1_132)
- Validate data types, ranges, and lengths (11.1.1_133-135)
- Whitelist validation preferred (11.1.1_136)
- Special character handling: `< > " ' % ( ) & + \ ` (11.1.1_137)
- Null byte, newline, path traversal checks (11.1.1_138)
- REST content-type matching (11.1.1_139)

Grep for:
- Missing server-side validation (client-side only)
- `%00`, `%0d`, `%0a`, `../`, `..\\` in path handling code
- Missing content-type validation in REST handlers
- Input directly used without validation

### Step 11: Logical Access Control (23 controls)

**BSL Controls**: 11.1.1_140 through 11.1.1_162

#### 11.1 Authorization Architecture
- Server-side authorization decisions only (11.1.1_140)
- Single site-wide access control component (11.1.1_141)
- Fail securely — deny on error (11.1.1_142, 11.1.1_143)
- Privileged logic segregated (11.1.1_144)

#### 11.2 Resource Access Control
- Files restricted to authorized users (11.1.1_145)
- Functions restricted to authorized users (11.1.1_146)
- API services restricted (11.1.1_147)
- Direct object references restricted (11.1.1_148)

Grep for:
- Endpoints/routes without authorization middleware
- Direct object references without ownership checks (IDOR)
- Client-side role checks without server enforcement
- Missing `@PreAuthorize`, `@Secured`, `authorize()` on sensitive endpoints

#### 11.3 Rate Limiting & Anti-Automation
- Transaction rate limiting (11.1.1_156)
- Referer header as supplemental check only (11.1.1_157)

#### 11.4 Account Management
- Unused accounts disabled (11.1.1_158)
- Sessions terminated on authorization change (11.1.1_159)
- Least privilege for service accounts (11.1.1_160)

### Step 12: Memory Management (9 controls)

**BSL Controls**: 11.1.1_163 through 11.1.1_172

*Primarily applicable to C/C++ and other memory-unsafe languages.*

- Input/output control for untrusted data (11.1.1_163)
- Buffer size verification (11.1.1_164)
- NULL termination awareness for strncpy (11.1.1_165)
- Buffer boundary checks in loops (11.1.1_166)
- Truncation and overflow awareness (11.1.1_167)
- Proper resource cleanup (11.1.1_168)
- Freed pointer management (11.1.1_169-170)
- Memory allocation verification (11.1.1_171)
- Heap/stack management (11.1.1_172)

For managed languages (Java, C#, JavaScript, Python), most of these controls
are handled by the runtime. Mark as "N/A — managed language" when applicable,
but still check for:
- Native/JNI calls that bypass memory safety
- Buffer handling in Node.js `Buffer` API
- Large object allocation without limits

### Step 13: Output Encoding (7 controls)

**BSL Controls**: 11.1.1_173 through 11.1.1_178 (including 11.1.1_177)

- Standard tested encoding routine for each output type (11.1.1_173)
- Contextual output encoding for all client-returned data (11.1.1_174)
- Encode all characters unless known safe (11.1.1_175)
- Sanitize output for SQL, XML, LDAP queries (11.1.1_176)
- No command execution from application (11.1.1_177)
- Sanitize output for OS commands (11.1.1_178)

Grep for:
- `innerHTML =`, `document.write(`, `dangerouslySetInnerHTML`
- Missing HTML entity encoding in template output
- String concatenation in SQL/XML/LDAP queries
- `Runtime.exec`, `ProcessBuilder`, `child_process.exec` with user data

### Step 14: Secure Design (9 controls)

**BSL Controls**: 11.1.1_179 through 11.1.1_187

- Threat modeling for critical flows (11.1.1_179)
- Security in user stories (11.1.1_180)
- Plausibility checks at each tier (11.1.1_181)
- Security unit/integration tests (11.1.1_182)
- Tier layer segregation (11.1.1_183)
- Tenant isolation (11.1.1_184)
- Resource consumption limits (11.1.1_185)
- SDLC process with security requirements (11.1.1_186)
- Container/microservices baseline compliance (11.1.1_187)

Assessment approach: Review architecture documentation, test suites,
deployment configuration rather than scanning code patterns.

### Step 15: Security Configuration (6 controls)

**BSL Controls**: 11.1.1_188 through 11.1.1_193

- Automated secure deployment (11.1.1_188)
- Automatic vulnerability remediation (11.1.1_189)
- Unused dependencies removed (11.1.1_190)
- Continuous dependency version monitoring (11.1.1_191)
- Components from official sources only (11.1.1_192)
- Unmaintained library monitoring (11.1.1_193)

Check: `package.json`, `pom.xml`, `build.gradle`, `requirements.txt`,
`Gemfile`, lock files for outdated/vulnerable dependencies.
Check for CI/CD pipeline configuration with security scanning.

### Step 16: Security Logging (8 controls)

**BSL Controls**: 11.1.1_194 through 11.1.1_201

- Logging standard compliance (11.1.1_194)
- Security event monitoring with alerts (11.1.1_195)
- Documented logging requirements (11.1.1_196)
- Login/access control/validation failure logging (11.1.1_197)
- Log format consumable by log management (11.1.1_198)
- Log data encoded to prevent injection (11.1.1_199)
- Audit trail with integrity controls for high-value transactions (11.1.1_200)
- Incident response and recovery plan (11.1.1_201)

### Step 17: Session Management (15 controls)

**BSL Controls**: 11.1.1_202 through 11.1.1_216

#### 17.1 Session Setup
- Framework session management controls used (11.1.1_202)
- Session IDs created on server only (11.1.1_203)
- Sufficiently random session identifiers (11.1.1_204)
- New session ID on re-authentication (11.1.1_210)

#### 17.2 Session Security
- Cookie domain and path appropriately restricted (11.1.1_205)
- `Secure` attribute on cookies over TLS (11.1.1_215)
- `HttpOnly` attribute on session cookies (11.1.1_216)
- No concurrent logins with same user ID (11.1.1_211)
- CSRF protection for sensitive operations (11.1.1_213, 11.1.1_214)

Grep for:
- `Set-Cookie` without `Secure`, `HttpOnly`, or `SameSite` flags
- Custom session ID generation instead of framework default
- Missing CSRF tokens on state-changing endpoints
- Session cookie without proper domain/path restriction

#### 17.3 Session Lifecycle
- Full session termination on logout (11.1.1_206)
- Logout available from all protected pages (11.1.1_207)
- Session timeout configured (11.1.1_208, 11.1.1_209)

### Step 18: System Configuration (12 controls)

**BSL Controls**: 11.1.1_217 through 11.1.1_228

- Latest approved versions for all components (11.1.1_217)
- All patches applied (11.1.1_218)
- Directory listings disabled (11.1.1_219)
- Fail securely on exceptions (11.1.1_220)
- Unnecessary files removed (11.1.1_221)
- Test code removed before deployment (11.1.1_222)
- robots.txt properly configured (11.1.1_223)
- Unnecessary HTTP methods disabled (11.1.1_224)
- Dev environments isolated from production (11.1.1_227)
- Software change control system (11.1.1_228)

Grep for:
- Test files/fixtures in production deployment configs
- `robots.txt` exposing directory structure
- Enabled HTTP TRACE/OPTIONS/WebDAV methods
- Development configuration in production builds

### Step 19: Additional Checks

#### 19.1 Vulnerability Testing (11.1.1_229)
- Periodic penetration testing by third parties required
- Testing before production and on significant changes

#### 19.2 Website Coding (11.1.1_230)
- Website Secure Coding Baseline compliance (if applicable)

### Step 20: Calculate Metrics

Compile compliance metrics:

- **Total applicable controls**: [n] out of 230
- **Compliant controls**: [n]
- **Non-compliant controls**: [n] (Critical: [n], High: [n], Medium: [n])
- **Not assessed**: [n] (require runtime/dynamic testing)
- **BSL compliance rate**: compliant / applicable * 100%

Severity classification for non-compliant controls:
- **Critical**: Controls related to injection prevention, credential storage,
  authentication bypass, or encryption failures
- **High**: Controls related to access control, session management,
  TLS configuration, or logging gaps
- **Medium**: Controls related to configuration, coding practices,
  or design requirements

### Step 21: Generate BSL Report

Create `code-review-artifacts/secure-coding-baseline-review/bsl-report.md`:

```markdown
# Secure Coding Baseline (BSL 11.1.1.d) Compliance Report

**Review Date**: [date]
**Reviewer**: Kiro AI BSL Compliance Review
**BSL Version**: 3 (October 2025)
**Total Controls**: 230
**Project**: [project name]

## Executive Summary

**BSL Compliance Rating**: [score]/100
**Total Applicable Controls**: [n] / 230
**Compliance Rate**: [n]%
**Non-Compliant Controls**: [n] (Critical: [n], High: [n], Medium: [n])
**Not Assessed**: [n] (require dynamic testing)

## Compliance by Domain

| # | Security Domain | Controls | Applicable | Compliant | Non-Compliant | N/A | Rate |
|---|----------------|----------|-----------|-----------|---------------|-----|------|
| 1 | Authentication & Password Management | 31 | [n] | [n] | [n] | [n] | [n]% |
| 2 | Communications Security | 8 | [n] | [n] | [n] | [n] | [n]% |
| 3 | Cryptography | 7 | [n] | [n] | [n] | [n] | [n]% |
| 4 | Data Protection | 13 | [n] | [n] | [n] | [n] | [n]% |
| 5 | Database Security | 14 | [n] | [n] | [n] | [n] | [n]% |
| 6 | Error Handling & Logging | 25 | [n] | [n] | [n] | [n] | [n]% |
| 7 | File Management | 14 | [n] | [n] | [n] | [n] | [n]% |
| 8 | General Coding Practices | 12 | [n] | [n] | [n] | [n] | [n]% |
| 9 | Input Validation | 15 | [n] | [n] | [n] | [n] | [n]% |
| 10 | Logical Access Control | 23 | [n] | [n] | [n] | [n] | [n]% |
| 11 | Memory Management | 9 | [n] | [n] | [n] | [n] | [n]% |
| 12 | Output Encoding | 7 | [n] | [n] | [n] | [n] | [n]% |
| 13 | Secure Design | 9 | [n] | [n] | [n] | [n] | [n]% |
| 14 | Security Configuration | 6 | [n] | [n] | [n] | [n] | [n]% |
| 15 | Security Logging | 8 | [n] | [n] | [n] | [n] | [n]% |
| 16 | Session Management | 15 | [n] | [n] | [n] | [n] | [n]% |
| 17 | System Configuration | 12 | [n] | [n] | [n] | [n] | [n]% |
| | **Total** | **230** | **[n]** | **[n]** | **[n]** | **[n]** | **[n]%** |

## Critical Non-Compliance Findings

### [BSL-C-001] [Finding Title]
- **BSL Control**: [11.1.1_xxx] — [Control description]
- **Domain**: [Security Domain]
- **Impact**: C/I/A
- **Location**: `[file:line]`
- **Issue**: [What was found]
- **Evidence**: [Code snippet or pattern]
- **Required Action**: [Specific remediation]
- **Deadline**: Before acceptance

## High Non-Compliance Findings

### [BSL-H-001] [Finding Title]
- **BSL Control**: [11.1.1_xxx]
- **Domain**: [Security Domain]
- **Impact**: C/I/A
- **Location**: `[file:line]`
- **Issue**: [What was found]
- **Required Action**: [Specific remediation]

## Medium Non-Compliance Findings

### [BSL-M-001] [Finding Title]
- **BSL Control**: [11.1.1_xxx]
- **Domain**: [Security Domain]
- **Location**: `[file:line]`
- **Issue**: [What was found]
- **Required Action**: [Specific remediation]

## Domain Detail Reports

### 1. Authentication & Password Management

| Control ID | Description | Status | Evidence |
|-----------|-------------|--------|----------|
| 11.1.1_1 | Require authentication for all pages | Pass/Fail/N/A | [details] |
| 11.1.1_2 | Server-side authentication enforcement | Pass/Fail/N/A | [details] |
| ... | ... | ... | ... |

[Repeat for each applicable domain]

## Controls Not Assessed (Require Dynamic Testing)

| Control ID | Domain | Reason |
|-----------|--------|--------|
| [id] | [domain] | Requires runtime testing / penetration testing |

## Overlap with Standard Security Review

| BSL Finding | Overlapping Dimension | Finding ID |
|------------|----------------------|------------|
| [BSL-C-xxx] [title] | Security Review | [SEC-xxx] |

## Remediation Plan

### Critical (Must fix before acceptance)
| # | BSL Control | Description | Domain |
|---|-----------|-------------|--------|
| 1 | 11.1.1_xxx | [desc] | [domain] |

### High (30-day remediation window)
| # | BSL Control | Description | Domain |
|---|-----------|-------------|--------|
| 1 | 11.1.1_xxx | [desc] | [domain] |

## BSL Compliance Statement

Based on this review:
- [COMPLIANT / PARTIALLY COMPLIANT / NON-COMPLIANT]
- [Summary of major gaps]
- [Recommendations for achieving full compliance]

## Appendix: Full Control Checklist

[Include a complete checklist table of all 230 controls with status]
```

## Completion Message

```
BSL 11.1.1.d compliance review complete.

Report saved to: code-review-artifacts/secure-coding-baseline-review/bsl-report.md

BSL Version: 3 (October 2025)
Total Controls: 230
Applicable Controls: [n]
BSL Compliance: [n]%

Non-Compliant:
  - Critical: [n]
  - High:     [n]
  - Medium:   [n]
Not Assessed: [n]

Top Gaps:
  - [domain 1]: [n] non-compliant controls
  - [domain 2]: [n] non-compliant controls

When ready, proceed with: @acceptance-report
```
