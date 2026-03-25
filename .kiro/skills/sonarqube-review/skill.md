---
name: sonarqube-review
description: >
  Performs SonarQube rule-based code review for Java and JavaScript/TypeScript
  projects. Checks 222 SonarQube rules covering security, reliability, Spring
  Framework, testing quality, and code maintainability. Requires
  codebase-reverse-engineering artifacts. Outputs a structured SonarQube
  compliance report with findings mapped to SonarQube rule keys.
---

# SonarQube Rule-Based Review

You are a senior code quality engineer performing a SonarQube rule-based code
review. Your goal is to systematically check the codebase against 222 curated
SonarQube rules (145 Java + 77 JavaScript) at Blocker and High severity levels.

This review complements the four standard review dimensions (security,
reliability, performance, maintainability) by applying **language-specific,
pattern-level** checks that SonarQube would flag in a CI/CD pipeline.

## Prerequisites

The following artifacts MUST exist before running this skill:
- `code-review-artifacts/reverse-engineering/architecture.md`
- `code-review-artifacts/reverse-engineering/technology-and-dependencies.md`
- `code-review-artifacts/reverse-engineering/code-quality-baseline.md`

If these files do not exist, instruct the user to run `@codebase-reverse-engineering` first.

## Output

`code-review-artifacts/sonarqube-review/sonarqube-report.md`

## Applicable Languages

This review applies ONLY when the project contains:
- **Java** source files (`.java`) → apply `.kiro/rules/sonarqube-java-standards.md`
- **JavaScript/TypeScript** source files (`.js`, `.ts`, `.jsx`, `.tsx`, `.mjs`, `.cjs`) → apply `.kiro/rules/sonarqube-javascript-standards.md`

If the project contains neither Java nor JavaScript/TypeScript, generate a
short report noting "SonarQube review not applicable — no Java or JS/TS source
code detected" and skip the review.

If the project contains both languages, apply both rule sets.

## Review Process

### Step 1: Preparation

1. Read the reverse engineering artifacts to understand:
   - Programming languages used (determine which rule sets to apply)
   - Project structure and module layout
   - Frameworks in use (Spring/Spring Boot detection is critical for Java)
   - Build system and dependency management
2. Determine scope:
   - Small (< 50 source files): Check all source files
   - Medium (50-500 source files): Check all modules, sample files within each
   - Large (> 500 source files): Focus on core modules, entry points, and
     security-sensitive code paths
3. Read the applicable SonarQube rule standards from `.kiro/rules/`

### Step 2: Security Rule Scan

Security rules are highest priority. For each applicable language:

#### 2.1 Injection Attack Patterns

Systematically search for:
- **SQL Injection**: String concatenation/interpolation in SQL queries.
  Grep for patterns: `"SELECT`, `"INSERT`, `"UPDATE`, `"DELETE`, `+ "`,
  `${` in SQL strings, `.query(`, `.execute(` with string building
- **Command Injection**: User input in shell commands.
  Grep for: `Runtime.exec`, `ProcessBuilder`, `child_process.exec`,
  `child_process.spawn` with shell option
- **XSS**: Unescaped output in HTML responses.
  Grep for: `innerHTML`, `dangerouslySetInnerHTML`, `document.write`,
  `v-html`, template literal in HTML context
- **Path Traversal**: User input in file operations.
  Grep for: `new File(`, `Paths.get(`, `fs.readFile`, `fs.writeFile`
  with request parameters
- **NoSQL Injection**: User objects in query operators.
  Grep for: `$where`, `$regex`, `$gt`, `$ne` with user input
- **LDAP/XPath Injection**: User input in LDAP/XPath queries

For each finding, record:
- SonarQube rule key (e.g., `javasecurity:S3649`)
- File path and line number
- Code evidence (the vulnerable pattern)
- Whether the vulnerability is confirmed, potential, or mitigated

#### 2.2 Credential & Secret Scan

Grep across the entire codebase for:
- Variables/constants named: `password`, `passwd`, `secret`, `token`,
  `api_key`, `apiKey`, `access_key`, `accessKey`, `private_key`, `mnemonic`
- Hard-coded string values assigned to such variables
- Database connection strings with embedded credentials
- `.env` files committed to repository
- AWS/Azure/GCP credentials in source code

Map findings to: `java:S6437` / `javascript:S6437` / `javascript:S7639`

#### 2.3 Cryptography & TLS Scan

Grep for:
- Weak ciphers: `DES`, `3DES`, `RC4`, `Blowfish`, `ECB`
- Weak hashing: `MD5`, `SHA1` used for passwords
- Disabled verification: `rejectUnauthorized`, `setDefaultHostnameVerifier`,
  `ALLOW_ALL`, `checkServerIdentity`
- TLS version: `TLSv1`, `SSLv3`, `TLSv1.1`
- JWT: `alg.*none`, `HS256` where RS256 is expected

#### 2.4 XML & Archive Security

Grep for:
- XXE: `XMLInputFactory`, `DocumentBuilderFactory`, `SAXParserFactory`,
  `XMLReader` without feature disabling
- Zip slip: archive extraction without path validation

### Step 3: Reliability Rule Scan

#### 3.1 Resource Management (Java)

Search for `AutoCloseable` implementations and verify proper closing:
- Database connections (`Connection`, `Statement`, `ResultSet`)
- I/O streams (`InputStream`, `OutputStream`, `Reader`, `Writer`)
- Check for try-with-resources vs manual close in finally

Map to: `java:S2095`, `java:S2093`

#### 3.2 Concurrency Safety (Java)

Search for concurrency patterns:
- `synchronized` blocks with double-checked locking → `java:S2168`
- `Thread.sleep` inside `synchronized` → `java:S2276`
- Multiple lock acquisition → `java:S3046`
- `ThreadGroup` usage → `java:S3014`
- Locks not released in finally → `java:S2222`

#### 3.3 Async/Await Correctness (JavaScript)

Search for:
- `await` on non-Promise values → `javascript:S4123`
- `async` constructors → `javascript:S7059`
- Unnecessary `Promise.resolve/reject` in async → `javascript:S7746`

#### 3.4 Control Flow

Search for:
- Infinite loops (while(true) without break) → `S2189`
- Missing break in switch cases → `S128`
- return/throw/break in finally blocks → `S1143`

### Step 4: Spring Framework Scan (Java only, if Spring detected)

Only execute if Spring/Spring Boot is detected in dependencies.

#### 4.1 Dependency Injection

Search for:
- Multiple constructors with `@Autowired` → `java:S6818`
- `@Autowired` on fields in `@Configuration` classes → `java:S3305`
- Static field injection → `java:S7178`

#### 4.2 Component Configuration

Search for:
- `@SpringBootApplication` in default package → `java:S4602`
- `@SessionAttributes` without `setComplete` → `java:S3753`
- Self-invocation bypassing proxy → `java:S6809`
- Invalid SpEL expressions → `java:S6857`

#### 4.3 Web Security

Search for:
- Entity objects in `@RequestMapping` parameters → `java:S4684`
- `HttpSecurity` URL pattern ordering → `java:S4601`
- `@Async` in `@Configuration` class → `java:S6817`

### Step 5: Testing Quality Scan

Search for test files and check:
- Test methods without assertions → `S2699`
- Empty test classes → `S2187`
- Incomplete assertions (e.g., `assertThat()` without predicate) → `S2970`
- Code after `done()` callback (JS) → `javascript:S6079`
- Assertions in try blocks catching Error (Java) → `java:S5779`

### Step 6: Code Quality Scan

#### 6.1 Complexity

Estimate cognitive complexity for functions in core modules:
- Flag functions exceeding complexity threshold of 15 → `S3776`
- Flag deeply nested functions (> 4 levels for JS) → `javascript:S2004`

#### 6.2 Variable & Type Safety (JavaScript)

Search for:
- Implicit global variables (missing declaration) → `javascript:S2703`
- `var` instead of `let`/`const` → `javascript:S3504`
- `typeof x === "object"` or other invalid comparisons → `javascript:S4125`

#### 6.3 Common Anti-Patterns

Search for language-specific anti-patterns:
- **Java**: Empty methods, shadowed fields, String literal duplication,
  wildcard return types, manual GC calls
- **JavaScript**: Empty functions, extra arguments, missing compare function
  in sort(), mutable exports, absolute imports

### Step 7: Calculate Metrics

Compile metrics:

- **Total findings** by severity (Blocker → Critical, High → High)
- **Findings by category**: Security / Reliability / Spring / Testing / Code Quality
- **Findings by language**: Java / JavaScript
- **SonarQube compliance rate**: (total applicable rules - violations) / total applicable rules * 100%
- **Blocker compliance rate**: (blocker rules - blocker violations) / blocker rules * 100%

### Step 8: Generate SonarQube Report

Create `code-review-artifacts/sonarqube-review/sonarqube-report.md`:

```markdown
# SonarQube Rule-Based Review Report

**Review Date**: [date]
**Reviewer**: Kiro AI SonarQube Review
**Rule Sets Applied**: [Java (145 rules) / JavaScript (77 rules) / Both]
**Source**: SonarQube Blocker & High severity rules from organization's quality profile

## Executive Summary

**SonarQube Compliance Rating**: [score]/100
**Total Findings**: [count] (Critical: [n], High: [n])
**Blocker Compliance**: [n]% ([n] blocker violations out of [n] applicable blocker rules)
**Languages Scanned**: [Java / JavaScript / Both]

## Rule Set Applicability

| Language | Source Files | Applicable Rules | Rule Set |
|----------|-------------|-----------------|----------|
| Java | [n] files | [n] rules | sonarqube-java-standards.md |
| JavaScript/TS | [n] files | [n] rules | sonarqube-javascript-standards.md |

## Findings by Category

| Category | Critical | High | Total |
|----------|----------|------|-------|
| Security | [n] | [n] | [n] |
| Reliability & Bugs | [n] | [n] | [n] |
| Spring Framework | [n] | [n] | [n] |
| Testing Quality | [n] | [n] | [n] |
| Code Quality | [n] | [n] | [n] |
| **Total** | **[n]** | **[n]** | **[n]** |

## Critical Findings (SonarQube Blocker)

### [SQ-C-001] [Finding Title]
- **Severity**: Critical (SonarQube Blocker)
- **Rule**: [rule_key] — [rule title]
- **Category**: Security / Reliability / Spring / Testing / Code Quality
- **Location**: `[file:line]`
- **Description**: [What the issue is]
- **Evidence**: [Code snippet or pattern found]
- **Impact**: [Potential impact]
- **Remediation**: [Specific fix recommendation]

## High Severity Findings (SonarQube High)

### [SQ-H-001] [Finding Title]
- **Severity**: High (SonarQube High)
- **Rule**: [rule_key] — [rule title]
- **Category**: [category]
- **Location**: `[file:line]`
- **Description**: [What the issue is]
- **Evidence**: [Code snippet]
- **Remediation**: [Fix recommendation]

## Spring Framework Compliance (if applicable)

| Rule Key | Rule Title | Status | Details |
|----------|-----------|--------|---------|
| java:S6818 | @Autowired single constructor | Pass/Fail/N/A | [details] |
| java:S4602 | @SpringBootApplication not in default package | Pass/Fail/N/A | [details] |
| java:S3753 | @SessionAttributes setComplete | Pass/Fail/N/A | [details] |
| java:S6809 | No self-invocation bypassing proxy | Pass/Fail/N/A | [details] |
| [etc.] | | | |

## Testing Quality Assessment

| Rule Key | Rule Title | Status | Details |
|----------|-----------|--------|---------|
| S2699 | Tests include assertions | Pass/Fail/N/A | [details] |
| S2187 | Test files contain tests | Pass/Fail/N/A | [details] |
| S2970 | Assertions are complete | Pass/Fail/N/A | [details] |
| [etc.] | | | |

## SonarQube Rule Coverage Matrix

### Security Rules
| Rule Key | Title | Status |
|----------|-------|--------|
| [key] | [title] | Pass / Fail / N/A |

### Reliability Rules
| Rule Key | Title | Status |
|----------|-------|--------|
| [key] | [title] | Pass / Fail / N/A |

### Code Quality Rules (Blocker only)
| Rule Key | Title | Status |
|----------|-------|--------|
| [key] | [title] | Pass / Fail / N/A |

> Note: Only Blocker-level code quality rules are listed individually.
> High-level code quality rules are summarized in the findings sections above.

## Overlap with Standard Review Dimensions

Some SonarQube findings overlap with the four standard review dimensions:

| SonarQube Finding | Overlapping Dimension | Finding ID |
|-------------------|----------------------|------------|
| [SQ-C-xxx] [title] | Security / Reliability / etc. | [SEC-xxx / REL-xxx] |

When a finding appears in both this report and a dimension report, the
dimension report's finding ID takes precedence. This report provides
the additional SonarQube rule key for CI/CD traceability.

## Recommendations

### Immediate Actions (before acceptance)
1. [action — fix all Critical/Blocker findings]

### CI/CD Integration Recommendations
1. [Recommend adding these SonarQube rules to the project's quality gate]

### Short-term Improvements (within 30 days)
1. [action]
```

## Completion Message

```
SonarQube rule-based review complete.

Report saved to: code-review-artifacts/sonarqube-review/sonarqube-report.md

Languages scanned: [Java / JavaScript / Both]
Rules applied: [n] (Blocker: [n], High: [n])
SonarQube Compliance: [n]%

Critical findings (Blocker): [n]
High findings: [n]
Total findings: [n]

When ready, proceed with: @acceptance-report
```
