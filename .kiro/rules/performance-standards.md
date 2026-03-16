# Performance Review Standards

This rule defines the performance review criteria. Apply these standards
whenever reviewing code for performance efficiency.

## Response Time Benchmarks

- Instant perception: < 0.1s (UI interactions, cache hits)
- Smooth response: < 1.0s (API calls, simple queries)
- Acceptable: < 10s (complex operations, batch processing)
- Unacceptable: > 10s without async/progress feedback

These are design targets. During static review, identify code patterns that
are likely to violate these benchmarks.

## Resource Utilization Targets

- CPU: < 70% average utilization under normal load
- Memory: < 80% peak utilization
- Disk I/O: < 50% capacity

During static review, identify code patterns that cause excessive resource
consumption.

## Severity Classification

- **Critical**: Will cause production performance failure (OOM, timeout, resource exhaustion)
- **High**: Will cause noticeable performance degradation under normal load
- **Medium**: May cause performance issues under peak load
- **Low**: Suboptimal performance pattern, minor impact

## Database Query Anti-Patterns (MUST check)

1. **N+1 Query Problem** — Querying in a loop instead of batch/join
   - Looping over a collection and executing a query per item
   - ORM lazy loading in loop contexts
   - Severity: High

2. **Unbounded Queries** — SELECT without LIMIT/pagination
   - Fetching all rows from a table without pagination
   - Missing cursor-based or offset-based pagination on list APIs
   - Severity: High

3. **Missing Indexes** — Queries on columns without apparent index
   - WHERE/ORDER BY/JOIN on columns not covered by indexes
   - Full table scans on large tables
   - Severity: Medium (confirm with actual schema if available)

4. **Unnecessary Data Fetching** — SELECT * when only specific columns needed
   - Severity: Low

## Memory Anti-Patterns (MUST check)

1. **Unbounded Collections** — Lists/maps that grow without limit
   - Caching without eviction policy or size limit
   - Accumulating data in memory without flushing
   - Severity: Critical

2. **Large Object Retention** — Holding references to large objects longer
   than needed
   - Storing entire file contents in memory for processing
   - Not streaming large payloads
   - Severity: High

3. **Memory Leaks** — Event listeners not removed, closures retaining large
   scopes, circular references preventing GC
   - Severity: High

## I/O Anti-Patterns (MUST check)

1. **Synchronous Blocking I/O** — Blocking calls in async/event-driven contexts
   - Synchronous file reads in Node.js request handlers
   - Blocking HTTP calls in async Python code
   - Severity: High

2. **Sequential I/O When Parallel is Possible** — Making independent external
   calls one after another instead of in parallel
   - Severity: Medium

3. **Missing Streaming** — Loading entire files/responses into memory instead
   of streaming
   - Severity: Medium for large payloads, Low for small payloads

## Caching Patterns (check if applicable)

1. **No Caching Strategy** — Frequently accessed, rarely changing data fetched
   from database/API on every request
   - Severity: Medium

2. **Cache Invalidation Issues** — Cache without TTL, no invalidation mechanism,
   stale data risks
   - Severity: Medium

3. **Cache Stampede Risk** — No protection against thundering herd on cache
   miss (missing lock/singleflight pattern)
   - Severity: Medium

## Scalability Assessment

Evaluate whether the application can scale horizontally:

| Aspect | Scalable Pattern | Non-Scalable Pattern |
|--------|-----------------|---------------------|
| State | External state store (Redis, DB) | In-memory session/state |
| File storage | Object storage (S3, GCS) | Local filesystem |
| Background jobs | Message queue + workers | In-process threads/timers |
| Configuration | External config service | Local config files |
| Logging | Centralized logging | Local log files |

Flag non-scalable patterns as Medium severity.

## Algorithm Complexity

Flag these when found:
- Nested loops over large collections (O(n^2) or worse): High
- Recursive algorithms without memoization on overlapping subproblems: Medium
- String concatenation in loops (in languages where strings are immutable): Low
