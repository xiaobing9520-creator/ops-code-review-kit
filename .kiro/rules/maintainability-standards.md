# Maintainability Review Standards

This rule defines the maintainability review criteria. Apply these standards
whenever reviewing code for long-term maintainability.

## Maintainability Index

Interpret on a 0-100 scale:
- 85-100: Excellent — Easy to maintain
- 65-84: Good — Maintainable with reasonable effort
- 50-64: Fair — Needs improvement
- 0-49: Poor — Difficult to maintain, high risk of introducing defects

## Technical Debt Ratio

Formula: estimated remediation cost / estimated development cost * 100%

- AAA Grade: < 5%
- Investment Grade: 5-10%
- Speculative: 10-20%
- Junk: > 20% (flag as High severity)

## Code Smell Density

- Acceptable: < 5 smells/KLOC
- Unacceptable: > 5 smells/KLOC

## Severity Classification

- **Critical**: Makes the codebase extremely difficult to safely modify
- **High**: Significantly increases maintenance cost and defect risk
- **Medium**: Increases effort for future changes
- **Low**: Minor improvement opportunity

## Complexity Anti-Patterns (MUST check)

1. **High Cyclomatic Complexity**
   - Functions with cyclomatic complexity > 15: flag as High
   - Functions with cyclomatic complexity > 10: flag as Medium
   - Count decision points: if, else if, case, &&, ||, ternary, catch

2. **Excessive Function Length**
   - Functions > 100 lines: flag as High
   - Functions > 50 lines: flag as Medium
   - Indicates function is doing too much and should be decomposed

3. **Excessive File Length**
   - Files > 500 lines: flag as Medium
   - Files > 1000 lines: flag as High

4. **Deep Nesting**
   - Code nested > 4 levels deep: flag as Medium
   - Code nested > 6 levels deep: flag as High

## Coupling Anti-Patterns (MUST check)

1. **Circular Dependencies**
   - Module A depends on Module B which depends on Module A
   - Severity: High

2. **God Class/Module**
   - Single class or module handling too many responsibilities
   - Indicators: many public methods, many dependencies, many lines
   - Severity: High

3. **Tight Coupling to Implementation**
   - Depending on concrete implementations instead of interfaces/abstractions
   - Direct instantiation of dependencies without injection
   - Severity: Medium

4. **Feature Envy**
   - Methods that access data from other classes more than their own
   - Severity: Low

## Duplication Anti-Patterns (MUST check)

1. **Copy-Paste Code Blocks**
   - Identical or near-identical code blocks in multiple locations
   - 3+ occurrences of the same logic: flag as High
   - 2 occurrences: flag as Medium

2. **Duplicated Business Logic**
   - Same business rule implemented differently in multiple places
   - Severity: High (risk of inconsistent behavior)

## Naming and Readability

1. **Unclear Naming**
   - Single-letter variables outside of loop counters/lambdas
   - Misleading names (name does not match behavior)
   - Inconsistent naming conventions within the same codebase
   - Severity: Low

2. **Missing Context**
   - Magic numbers without named constants
   - Complex boolean expressions without explanatory variables
   - Severity: Low

## Documentation Assessment

1. **Missing README or outdated README**
   - No setup instructions, no architecture overview
   - Severity: Medium

2. **Missing API documentation**
   - Public APIs without descriptions of parameters, returns, errors
   - Severity: Medium for external APIs, Low for internal

3. **Missing critical inline comments**
   - Complex algorithms or business rules without explanation
   - Workarounds or hacks without explaining why
   - Severity: Low

## Dependency Management

1. **Excessive Dependencies**
   - Dependencies that duplicate built-in language/framework capabilities
   - Severity: Low

2. **Abandoned Dependencies**
   - Dependencies with no updates in > 2 years and no active maintainer
   - Severity: Medium (reliability and security risk)

3. **Version Pinning**
   - Dependencies without pinned versions (using ranges or latest)
   - Severity: Medium (reproducibility risk)

## Project Structure

1. **No Clear Layering**
   - Business logic mixed with infrastructure code
   - No separation of concerns
   - Severity: Medium

2. **Inconsistent Project Structure**
   - Different modules following different structural patterns
   - Severity: Low

## NIST SSDF PW.7 Alignment

Per NIST SP 800-218 Practice PW.7 (Review code to identify vulnerabilities
and verify compliance with security requirements):
- Code review should verify that secure coding practices are followed
- Code review findings should be tracked and remediated
- This review process fulfills PW.7 requirements — note compliance in reports
