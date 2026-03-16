# Reliability Review Standards

This rule defines the reliability review criteria. Apply these standards
whenever reviewing code for reliability and operational stability.

## Defect Density Thresholds

- Excellent: < 0.1 defects/KLOC
- Good: 0.1-0.5 defects/KLOC
- Acceptable: 0.5-1.0 defects/KLOC
- Unacceptable: > 1.0 defects/KLOC

Calculation: number of identified defects / lines of code in thousands.

## Severity Classification

- **Critical**: Will cause production outage or data loss/corruption
- **High**: Will cause service degradation or intermittent failures
- **Medium**: May cause issues under specific conditions (edge cases, load)
- **Low**: Minor issue unlikely to affect production stability

## Error Handling Patterns (MUST check)

Flag as defects when found:

1. **Empty catch blocks** — Exceptions swallowed without logging or handling
2. **Generic catch-all** — Catching all exceptions without differentiation
3. **Missing error handling on external calls** — HTTP requests, database
   queries, file I/O, message queue operations without try/catch or error
   callbacks
4. **Unchecked return values** — Ignoring error returns from functions
5. **Missing null/undefined checks** — Accessing properties on potentially
   null objects without guards (especially data from external sources)

## Resource Management (MUST check)

Flag as defects when found:

1. **Resource leaks** — Database connections, file handles, network sockets,
   streams not properly closed/released (missing finally/defer/using/with)
2. **Missing connection pool configuration** — Direct connection creation
   without pooling for databases or HTTP clients
3. **Unbounded resource consumption** — No limits on queue depth, cache size,
   thread count, connection count
4. **Missing cleanup on shutdown** — No graceful shutdown handler to release
   resources

## Timeout and Circuit Breaker (MUST check)

Flag as defects when found:

1. **No timeout on external calls** — HTTP requests, database queries, RPC
   calls without timeout configuration
2. **No retry with backoff** — Transient failure recovery relies on immediate
   retry or no retry at all
3. **No circuit breaker** — Cascading failure possible when downstream service
   is unavailable
4. **Synchronous blocking calls** — Blocking the main thread/event loop on
   I/O operations in async contexts

## Concurrency Issues (MUST check)

Flag as defects when found:

1. **Race conditions** — Shared mutable state without synchronization
2. **Deadlock potential** — Multiple locks acquired in inconsistent order
3. **Thread safety violations** — Non-thread-safe data structures used in
   concurrent contexts
4. **Missing atomic operations** — Check-then-act patterns without atomicity

## 12-Factor App Compliance (Operations Readiness)

These factors directly impact operational stability. Check each one:

| Factor | What to Check | Severity if Missing |
|--------|--------------|-------------------|
| Factor 3: Config | Configuration externalized via environment variables or config service (not hardcoded) | High |
| Factor 6: Stateless | Application processes are stateless; session data stored in external backing service | High |
| Factor 9: Disposability | Fast startup, graceful shutdown with SIGTERM handling, in-flight request draining | High |
| Factor 11: Logs | Logs written to stdout/stderr as event streams (not to local files) | Medium |
| Factor 4: Backing services | Databases, caches, queues treated as attached resources via config | Medium |
| Factor 8: Concurrency | Process model supports horizontal scaling | Medium |

## Health Check and Observability

Flag as Medium if missing:

1. **No health check endpoint** — No `/health` or `/healthz` or equivalent
2. **No readiness probe** — No way to determine if service is ready to
   receive traffic
3. **No structured logging** — Logs are unstructured free text without
   correlation IDs, timestamps, or log levels
4. **No metrics exposure** — No application metrics endpoint or integration
   with metrics collection

## Test Coverage Assessment

- Unit test files present and cover core business logic: required
- Integration test files present for external service interactions: recommended
- No tests at all: flag as High severity reliability risk
