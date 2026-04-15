---
name: sonarqube-review
description: >
  Performs SonarQube rule-based code review for Java and JavaScript/TypeScript
  projects. Checks ONLY the rules defined in the organization's curated
  standards files (145 Java + 77 JavaScript, Blocker and High severity).
  Requires codebase-reverse-engineering artifacts. Outputs a structured
  SonarQube compliance report with findings mapped to SonarQube rule keys.
---

# SonarQube Rule-Based Review

You are a senior code quality engineer performing a SonarQube rule-based code
review. Your goal is to systematically check the codebase against the
organization's curated SonarQube rules at Blocker and High severity levels.

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

---

## CRITICAL CONSTRAINTS

### Constraint 1: Rule Set Boundary — ONLY Report Rules From Standards Files

You MUST ONLY report findings that correspond to rules explicitly defined in
the applicable standards files:
- `.kiro/rules/sonarqube-java-standards.md` (145 Java rules)
- `.kiro/rules/sonarqube-javascript-standards.md` (77 JavaScript rules)

**Strict prohibitions:**
- Do NOT report issues based on SonarQube rules that are not listed in these files
- Do NOT infer, guess, or recall SonarQube rule IDs from your training data
- Do NOT add rules you "know" from SonarQube even if you find obvious code problems
- If you find a genuine code issue that doesn't match ANY rule in the standards files, do NOT include it in this report — it may be covered by other review dimensions (security-review, reliability-review, etc.)

### Constraint 2: Severity MUST Come From Standards Files Only

The severity for each finding MUST be taken verbatim from the standards file:
- If a rule says `**Severity**: Blocker` in the standards → report as **Blocker**
- If a rule says `**Severity**: High` in the standards → report as **High**

**Strict prohibitions:**
- Do NOT use any other severity level (Critical, Major, Minor, Info are NOT valid)
- Do NOT override the standards file severity with SonarQube defaults from your knowledge
- Do NOT use the legacy SonarQube severity system (Blocker/Critical/Major/Minor/Info)
- The ONLY valid severity values in this report are **Blocker** and **High**

### Constraint 3: SonarQube Classification Awareness

Some rules in the standards files correspond to what SonarQube classifies as
**Security Hotspots** (not traditional Vulnerabilities). Security Hotspots in
SonarQube do not carry a traditional severity level — instead they require
manual review. In this review, we use the severity assigned in the standards
file regardless of SonarQube's classification.

When reporting a finding for a Security Hotspot-type rule, add this annotation:

```
> **SonarQube Classification**: Security Hotspot — requires manual review to
> confirm as vulnerability. Severity in this report is based on the
> organization's risk assessment, not SonarQube's default classification.
```

Common Security Hotspot rules include (but are not limited to):
- Credential/secret rules (S6437, S2115)
- Cryptography rules (weak hash, weak cipher)
- Cookie security rules
- CORS configuration rules
- Permission/access control rules
- Debug feature rules

---

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
3. **Read the applicable SonarQube rule standards from `.kiro/rules/`**
4. **Build a checklist of all rule keys from the standards file** — this
   checklist is your scanning scope. You will check each rule and mark it
   as Pass / Fail / N/A.

### Step 2: Rule-by-Rule Scanning — Security Rules

Process each **Security** rule from the standards file one by one:

For each rule:
1. Read its definition in the standards file: rule key, severity,
   noncompliant/compliant examples
2. Search the codebase for the noncompliant patterns described in the rule
3. Use targeted grep/search patterns appropriate to the rule:
   - Injection rules: search for string concatenation in SQL/commands/queries
   - Credential rules: search for hard-coded passwords, secrets, API keys
   - Cryptography rules: search for weak ciphers (DES, MD5, SHA1 for passwords)
   - XML rules: search for XML parser configurations without security features
   - Authentication rules: search for session/cookie/auth configurations
4. If a match is found → record finding with the **exact rule key** and
   **exact severity** from the standards file
5. If no match is found → mark rule as "Pass" or "N/A"

### Step 3: Rule-by-Rule Scanning — Reliability & Bug Prevention Rules

Process each **Reliability** rule from the standards file:

For each rule:
1. Read its definition, noncompliant examples
2. Search for matching patterns:
   - Resource management: unclosed streams, connections, missing try-with-resources
   - Concurrency: synchronized blocks, Thread.sleep in locks, ThreadLocal leaks
   - Control flow: infinite loops, missing break in switch, dead code
   - Null safety: null pointer dereferences, missing null checks
3. Record findings or mark as Pass/N/A

### Step 4: Rule-by-Rule Scanning — Spring Framework Rules (Java only)

Only execute if Spring/Spring Boot is detected in dependencies.

Process each **Spring Framework** rule from the standards file:
- Dependency injection patterns (@Autowired usage)
- Component configuration (@SpringBootApplication location, @SessionAttributes)
- Web security (entity binding, URL pattern ordering)
- Async/proxy patterns

### Step 5: Rule-by-Rule Scanning — Testing Quality Rules

Process each **Testing Quality** rule from the standards file:
- Test methods without assertions
- Empty test classes
- Incomplete assertions
- Assertions in try blocks

### Step 6: Rule-by-Rule Scanning — Code Quality Rules

Process each **Code Quality** rule from the standards file:
- Cognitive complexity thresholds
- Variable and type safety patterns
- Common anti-patterns (empty methods, duplicated strings, etc.)

### Step 7: Self-Validation (MANDATORY)

Before generating the final report, perform these validation checks:

#### 7.1 Rule ID Validation
For **every** finding in your draft report:
- Verify the rule key (e.g., `java:S2095`) exists in the applicable standards file
- **Remove** any finding whose rule key is not found in the standards file
- If you cannot locate the rule key in the standards, the finding MUST be excluded

#### 7.2 Severity Validation
For **every** finding:
- Cross-check the severity against the standards file definition for that rule
- If the severity in your finding differs from the standards file, **correct it**
  to match the standards file
- Confirm that only "Blocker" or "High" severity values are used

#### 7.3 Rule Key Format Validation
- Java rule keys must match: `java:Sxxxx` or `javasecurity:Sxxxx`
- JavaScript rule keys must match: `javascript:Sxxxx`
- Flag and remove any rule keys that don't match these patterns

#### 7.4 Completeness Check
- Verify that every rule in the standards file has been evaluated
  (marked as Pass, Fail, or N/A)
- Count the number of findings and compare against the total applicable rules

### Step 8: Calculate Metrics

Compile metrics from validated findings only:

- **Total findings** by severity: Blocker count, High count
- **Findings by category**: Security / Reliability / Spring / Testing / Code Quality
- **Findings by language**: Java / JavaScript (if both apply)
- **Rule coverage**: Total rules checked / Total applicable rules
- **Compliance rate**: (applicable rules - violations) / applicable rules * 100%
- **Blocker compliance rate**: (blocker rules - blocker violations) / blocker rules * 100%

### Step 9: Generate SonarQube Report

Create `code-review-artifacts/sonarqube-review/sonarqube-report.md`:

```markdown
# SonarQube Rule-Based Review Report

**Review Date**: [date]
**Reviewer**: Kiro AI SonarQube Review
**Rule Sets Applied**: [Java (145 rules) / JavaScript (77 rules) / Both]
**Source**: Organization's SonarQube quality profile — Blocker & High severity only

## Executive Summary

**SonarQube Compliance Rating**: [score]/100
**Total Findings**: [count] (Blocker: [n], High: [n])
**Blocker Compliance**: [n]% ([n] blocker violations out of [n] applicable blocker rules)
**Languages Scanned**: [Java / JavaScript / Both]

## Rule Set Applicability

| Language | Source Files | Applicable Rules | Rule Set |
|----------|-------------|-----------------|----------|
| Java | [n] files | [n] rules | sonarqube-java-standards.md |
| JavaScript/TS | [n] files | [n] rules | sonarqube-javascript-standards.md |

## Findings by Category

| Category | Blocker | High | Total |
|----------|---------|------|-------|
| Security | [n] | [n] | [n] |
| Reliability & Bugs | [n] | [n] | [n] |
| Spring Framework | [n] | [n] | [n] |
| Testing Quality | [n] | [n] | [n] |
| Code Quality | [n] | [n] | [n] |
| **Total** | **[n]** | **[n]** | **[n]** |

## Blocker Findings (Must Fix Before Acceptance)

### [SQ-B-001] [Finding Title]
- **Severity**: Blocker
- **Rule**: [rule_key] — [rule title from standards file]
- **Category**: Security / Reliability / Spring / Testing / Code Quality
- **Location**: `[file:line]`
- **Description**: [What the issue is]
- **Evidence**: [Code snippet or pattern found]
- **Impact**: [Potential impact]
- **Remediation**: [Specific fix recommendation]

[If the rule is a Security Hotspot type:]
> **SonarQube Classification**: Security Hotspot — requires manual review to
> confirm as vulnerability. Severity in this report is based on the
> organization's risk assessment.

## High Findings (Must Fix or Document Mitigation)

### [SQ-H-001] [Finding Title]
- **Severity**: High
- **Rule**: [rule_key] — [rule title from standards file]
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
| [etc.] | | | |

## Testing Quality Assessment

| Rule Key | Rule Title | Status | Details |
|----------|-----------|--------|---------|
| S2699 | Tests include assertions | Pass/Fail/N/A | [details] |
| [etc.] | | | |

## SonarQube Rule Coverage Matrix

### Security Rules
| Rule Key | Title | Severity | Status |
|----------|-------|----------|--------|
| [key] | [title] | Blocker/High | Pass / Fail / N/A |

### Reliability Rules
| Rule Key | Title | Severity | Status |
|----------|-------|----------|--------|
| [key] | [title] | Blocker/High | Pass / Fail / N/A |

### Code Quality Rules
| Rule Key | Title | Severity | Status |
|----------|-------|----------|--------|
| [key] | [title] | Blocker/High | Pass / Fail / N/A |

## Rule Set Coverage Summary

**Rule Set Scope**: This report covers ONLY the [n] rules defined in the
organization's SonarQube quality profile (Blocker & High severity).

| Metric | Value |
|--------|-------|
| Total rules in standards | [n] |
| Rules checked | [n] |
| Rules with findings (Fail) | [n] |
| Rules passed (Pass) | [n] |
| Rules not applicable (N/A) | [n] |

> **Important**: This report does NOT cover SonarQube rules outside the
> organization's curated rule set. Code issues detected by other review
> dimensions (security-review, reliability-review, etc.) may overlap with
> SonarQube rules not included here.

## Overlap with Standard Review Dimensions

Some SonarQube findings overlap with the four standard review dimensions:

| SonarQube Finding | Overlapping Dimension | Finding ID |
|-------------------|----------------------|------------|
| [SQ-B-xxx] [title] | Security / Reliability / etc. | [SEC-xxx / REL-xxx] |

When a finding appears in both this report and a dimension report, the
dimension report's finding ID takes precedence. This report provides
the additional SonarQube rule key for CI/CD traceability.

## Recommendations

### Immediate Actions (before acceptance)
1. [action — fix all Blocker findings]

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
Rules in standards: [n] (Blocker: [n], High: [n])
Rules checked: [n]
Rules with findings: [n]

Blocker findings: [n]
High findings: [n]
Total findings: [n]

SonarQube Compliance: [n]%

Note: This report covers ONLY the rules defined in the organization's
curated SonarQube quality profile. Other code quality issues may be
covered by the four standard review dimensions.

When ready, proceed with: @acceptance-report
```
