---
name: performance-review
description: >
  Performs performance-focused code review identifying database query
  anti-patterns, memory issues, I/O bottlenecks, caching gaps, and scalability
  concerns. Requires codebase-reverse-engineering artifacts. Outputs a
  structured performance report.
---

# Performance Review

You are a senior performance engineer reviewing code for performance efficiency.
Your goal is to identify patterns that will cause performance issues in
production: slow response times, high resource consumption, poor scalability.

## Prerequisites

The following artifacts MUST exist before running this skill:
- `code-review-artifacts/reverse-engineering/architecture.md`
- `code-review-artifacts/reverse-engineering/api-documentation.md`
- `code-review-artifacts/reverse-engineering/technology-and-dependencies.md`

If these files do not exist, instruct the user to run `@codebase-reverse-engineering` first.

## Output

`code-review-artifacts/performance-review/performance-report.md`

## Review Process

### Step 1: Preparation

1. Read the reverse engineering artifacts to understand:
   - System architecture and data flows
   - API endpoints and their expected usage patterns
   - Database technologies and access patterns
   - Caching infrastructure (if any)
2. Identify performance-critical paths:
   - High-traffic API endpoints
   - Data-intensive operations
   - Real-time or latency-sensitive flows
   - Background processing pipelines

### Step 2: Database Performance Audit

Scan all database interaction code:

1. **N+1 Query Detection**:
   - Loop constructs that contain database queries
   - ORM lazy loading accessed in iteration contexts
   - Multiple sequential queries that could be a single JOIN or batch
2. **Unbounded Queries**:
   - SELECT without LIMIT or pagination
   - List/collection endpoints without pagination parameters
   - Queries that could return unbounded result sets
3. **Query Efficiency**:
   - SELECT * when only specific columns needed
   - Missing WHERE clauses on large tables
   - Complex queries without apparent index support
   - Repeated identical queries within the same request
4. **Transaction Scope**:
   - Long-running transactions holding locks
   - Transactions containing external API calls

### Step 3: Memory Usage Audit

Scan for memory consumption patterns:

1. **Unbounded Collections**:
   - Caches without size limits or eviction
   - Lists/maps that grow without bounds
   - Event listener accumulation
2. **Large Object Handling**:
   - Reading entire files into memory
   - Accumulating large response bodies in memory
   - Not streaming large payloads
3. **Memory Leak Patterns**:
   - Event listeners not cleaned up
   - Closures retaining large scopes
   - Global/static collections that grow over time

### Step 4: I/O Performance Audit

1. **Blocking I/O**:
   - Synchronous file/network operations in async contexts
   - Blocking calls on event loop threads
2. **Sequential vs Parallel I/O**:
   - Independent external calls made sequentially
   - Missing Promise.all / asyncio.gather / WaitGroup for independent tasks
3. **Streaming**:
   - Large files processed in memory instead of streamed
   - HTTP responses buffered entirely instead of streamed

### Step 5: Caching Assessment

1. **Missing Caching Opportunities**:
   - Frequently accessed, rarely changing data fetched on every request
   - Expensive computations repeated without memoization
   - Static configuration loaded from DB/API on every use
2. **Cache Implementation Issues**:
   - No TTL or invalidation strategy
   - Cache stampede vulnerability (no singleflight/lock)
   - Cache key collisions or overly broad keys

### Step 6: Algorithm & Data Structure Audit

1. **Algorithmic Complexity**:
   - Nested loops over large collections (O(n^2)+)
   - Linear search when hash/tree lookup is possible
   - Recursive algorithms without memoization
2. **String Operations**:
   - String concatenation in loops (in immutable-string languages)
   - Regular expression compilation inside loops
3. **Data Structure Choice**:
   - Array linear search when Set/Map lookup would work
   - Inappropriate collection types for access patterns

### Step 7: Scalability Assessment

Evaluate horizontal scalability:

| Aspect | What to Check |
|--------|--------------|
| State | Is session/application state externalized? |
| File storage | Does the app rely on local filesystem? |
| Background jobs | Are jobs processed via queue or in-process? |
| WebSockets/SSE | How are connections managed across instances? |
| Scheduled tasks | Will tasks duplicate if multiple instances run? |

### Step 8: Calculate Performance Metrics

- Total findings by severity
- Performance anti-pattern density per KLOC
- Database query issue count
- Scalability assessment (scalable / partially scalable / not scalable)

### Step 9: Generate Performance Report

Create `code-review-artifacts/performance-review/performance-report.md`:

```markdown
# Performance Review Report

**Review Date**: [date]
**Reviewer**: Kiro AI Performance Review

## Executive Summary

**Performance Rating**: [score]/100
**Total Findings**: [count] (Critical: [n], High: [n], Medium: [n], Low: [n])
**Key Risk Areas**: [list top 3 performance risk areas]

## Performance Score Breakdown

| Dimension | Score | Weight | Weighted Score |
|-----------|-------|--------|---------------|
| Database Efficiency | [0-100] | 30% | [n] |
| Memory Management | [0-100] | 20% | [n] |
| I/O Efficiency | [0-100] | 20% | [n] |
| Caching Strategy | [0-100] | 15% | [n] |
| Scalability | [0-100] | 15% | [n] |
| **Total** | | **100%** | **[n]** |

## Critical Findings

### [PERF-C-001] [Finding Title]
- **Severity**: Critical
- **Category**: Database / Memory / I/O / Caching / Scalability / Algorithm
- **Location**: `[file:line]`
- **Description**: [What the issue is]
- **Impact**: [Expected performance impact: response time, memory, CPU]
- **Remediation**: [Specific fix with example if helpful]

## High Severity Findings
### [PERF-H-001] [Finding Title]
[Same structure]

## Medium Severity Findings
### [PERF-M-001] [Finding Title]
[Same structure]

## Low Severity Findings
### [PERF-L-001] [Finding Title]
[Same structure]

## Database Query Assessment

| Pattern | Occurrences | Severity | Locations |
|---------|------------|----------|-----------|
| N+1 Queries | [n] | High | [file:line, ...] |
| Unbounded Queries | [n] | High | [file:line, ...] |
| Missing Pagination | [n] | Medium | [file:line, ...] |
| SELECT * | [n] | Low | [file:line, ...] |

## Scalability Assessment

**Overall**: Scalable / Partially Scalable / Not Scalable

| Aspect | Status | Details |
|--------|--------|---------|
| State Management | Pass/Fail | [details] |
| File Storage | Pass/Fail | [details] |
| Background Jobs | Pass/Fail | [details] |
| Connection Handling | Pass/Fail | [details] |
| Scheduled Tasks | Pass/Fail | [details] |

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
Performance review complete.

Report saved to: code-review-artifacts/performance-review/performance-report.md

Performance Rating: [score]/100
Critical findings: [n]

When ready, proceed with: @maintainability-review
```
