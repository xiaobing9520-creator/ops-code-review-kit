---
name: reliability-review
description: >
  Performs reliability-focused code review evaluating error handling, resource
  management, fault tolerance, concurrency safety, and 12-Factor App operational
  readiness. Requires codebase-reverse-engineering artifacts. Outputs a
  structured reliability report.
---

# Reliability Review

You are a senior site reliability engineer (SRE) performing a reliability-focused
code review. Your perspective is operational — you are evaluating whether this
code will run reliably in production under real-world conditions.

## Prerequisites

The following artifacts MUST exist before running this skill:
- `code-review-artifacts/reverse-engineering/architecture.md`
- `code-review-artifacts/reverse-engineering/technology-and-dependencies.md`
- `code-review-artifacts/reverse-engineering/code-quality-baseline.md`

If these files do not exist, instruct the user to run `@codebase-reverse-engineering` first.

## Output

`code-review-artifacts/reliability-review/reliability-report.md`

## Review Process

### Step 1: Preparation

1. Read the reverse engineering artifacts to understand:
   - System architecture and component interactions
   - External dependencies and integration points
   - Technology stack and frameworks
   - Existing test coverage status
2. Identify reliability-critical paths:
   - Request handling chains (entry point to response)
   - Data processing pipelines
   - Background job / async task flows
   - External service communication paths

### Step 2: Error Handling Audit

For each reliability-critical path identified:

1. **Trace the request/data flow** from entry to exit
2. **Check every external call** (DB, HTTP, queue, file I/O):
   - Is there error handling (try/catch, error callback, Result type)?
   - Is the error logged with sufficient context?
   - Is there a meaningful response/fallback on failure?
3. **Check for anti-patterns**:
   - Empty catch blocks
   - Generic catch-all without differentiation
   - Swallowed exceptions (caught but not logged or handled)
   - Unchecked return values from functions that can fail

Record each finding with file path, line number, and the specific pattern.

### Step 3: Resource Management Audit

Scan all code that creates or acquires resources:

1. **Database connections**: Properly pooled? Connections released after use?
   Connection pool size configured?
2. **File handles**: Opened files properly closed in finally/defer/using/with?
3. **Network connections**: HTTP clients properly configured with timeouts
   and connection limits?
4. **Streams**: Streams properly closed/drained? Backpressure handled?
5. **Event listeners**: Listeners removed when no longer needed?
6. **Timers/intervals**: Cleared on shutdown?

### Step 4: Fault Tolerance Audit

Check resilience patterns:

1. **Timeout configuration**:
   - Every external call (HTTP, DB, RPC) must have a timeout
   - Scan for calls without timeout parameters
2. **Retry strategy**:
   - Transient failures should have retry with exponential backoff
   - Retries should be idempotent
   - Retry count should be bounded
3. **Circuit breaker**:
   - Cascading failure protection for downstream dependencies
   - Check if circuit breaker libraries are used (e.g., resilience4j, opossum, polly)
4. **Graceful degradation**:
   - What happens when a non-critical dependency is down?
   - Are there fallback behaviors?

### Step 5: Concurrency Safety Audit

If the application uses concurrency:

1. **Shared mutable state**: Any shared state without proper synchronization?
2. **Lock ordering**: Multiple locks acquired? Consistent order?
3. **Async/await correctness**: Proper await on all async operations?
   Unhandled promise rejections?
4. **Thread-safe collections**: Correct usage of concurrent data structures?

### Step 6: 12-Factor App Assessment

Evaluate operational readiness against 12-Factor principles:

| Factor | Check Method |
|--------|-------------|
| Config (F3) | Grep for hardcoded URLs, ports, credentials, connection strings. Check for env var or config service usage |
| Stateless (F6) | Check for in-memory session storage, local file writes for state, static mutable variables holding request state |
| Disposability (F9) | Check for SIGTERM handler, graceful shutdown logic, in-flight request draining, startup time concerns |
| Logs (F11) | Check if logs go to stdout/stderr vs local files. Check for structured logging with levels and correlation IDs |
| Backing services (F4) | Check if DB/cache/queue connections are configurable via environment |
| Concurrency (F8) | Check if horizontal scaling is possible (no shared local state between instances) |

### Step 7: Test Coverage Assessment

1. Are there test files? Where are they located?
2. Do tests cover the critical paths identified in Step 1?
3. Are there integration tests for external service interactions?
4. Is there a test framework configured?
5. Is there a coverage configuration or report?

### Step 8: Calculate Reliability Metrics

- Total defects found by severity
- Defect density = total defects / KLOC
- 12-Factor compliance score (N of 6 key factors met)
- Error handling coverage (% of external calls with proper error handling)

### Step 9: Generate Reliability Report

Create `code-review-artifacts/reliability-review/reliability-report.md`:

```markdown
# Reliability Review Report

**Review Date**: [date]
**Reviewer**: Kiro AI Reliability Review
**Standards Applied**: 12-Factor App, Defect Density Analysis

## Executive Summary

**Reliability Rating**: [score]/100
**Defect Density**: [n] defects/KLOC ([Excellent/Good/Acceptable/Unacceptable])
**12-Factor Compliance**: [n]/6 key factors met
**Total Findings**: [count] (Critical: [n], High: [n], Medium: [n], Low: [n])

## Reliability Score Breakdown

| Dimension | Score | Weight | Weighted Score |
|-----------|-------|--------|---------------|
| Error Handling | [0-100] | 25% | [n] |
| Resource Management | [0-100] | 20% | [n] |
| Fault Tolerance | [0-100] | 20% | [n] |
| Concurrency Safety | [0-100] | 10% | [n] |
| 12-Factor Compliance | [0-100] | 15% | [n] |
| Test Coverage | [0-100] | 10% | [n] |
| **Total** | | **100%** | **[n]** |

## Critical Findings

### [REL-C-001] [Finding Title]
- **Severity**: Critical
- **Category**: Error Handling / Resource Management / Fault Tolerance / Concurrency / 12-Factor
- **Location**: `[file:line]`
- **Description**: [What the issue is]
- **Impact**: [How this could cause a production incident]
- **Remediation**: [Specific fix recommendation]

## High Severity Findings
### [REL-H-001] [Finding Title]
[Same structure]

## Medium Severity Findings
### [REL-M-001] [Finding Title]
[Same structure]

## Low Severity Findings
### [REL-L-001] [Finding Title]
[Same structure]

## 12-Factor App Compliance

| Factor | Status | Details |
|--------|--------|---------|
| F3: Config | Pass/Fail | [details] |
| F4: Backing Services | Pass/Fail | [details] |
| F6: Stateless | Pass/Fail | [details] |
| F8: Concurrency | Pass/Fail | [details] |
| F9: Disposability | Pass/Fail | [details] |
| F11: Logs | Pass/Fail | [details] |

## Error Handling Coverage

| Critical Path | External Calls | Handled | Unhandled |
|--------------|---------------|---------|-----------|
| [path name] | [n] | [n] | [n] |

## Test Coverage Assessment

- **Unit Tests**: Present / Absent - [details]
- **Integration Tests**: Present / Absent - [details]
- **Critical Path Coverage**: [assessment]
- **Overall Assessment**: [Adequate / Insufficient / None]

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
Reliability review complete.

Report saved to: code-review-artifacts/reliability-review/reliability-report.md

Reliability Rating: [score]/100
Defect Density: [n] defects/KLOC
Critical findings: [n]

When ready, proceed with: @performance-review
```
