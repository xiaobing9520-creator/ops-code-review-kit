# SonarQube Java Review Standards

This rule defines the SonarQube-based Java code review criteria. Apply these
standards when the target project contains Java source code. Rules are sourced
from SonarQube's Java analyzer (Sonar Java + Java Security + Java Bugs +
Java Architecture) and organized by review category.

Total: 145 rules (45 Blocker, 100 High)

## Severity Mapping

| SonarQube Severity | Review Severity | Action |
|--------------------|----------------|--------|
| **Blocker** | Critical | Must fix before acceptance |
| **High** | High | Must fix or have documented mitigation plan |

---

## 1. Security Rules (37 rules)

These rules map to CWE/OWASP and overlap with the security-review dimension.
When both SonarQube rule and security-review identify the same issue, keep
the SonarQube rule ID for traceability.

### 1.1 Injection Attacks (Blocker)

| Rule Key | Title | CWE Mapping |
|----------|-------|-------------|
| javasecurity:S3649 | Database queries should not be vulnerable to injection attacks | CWE-89 |
| javasecurity:S2076 | OS commands should not be vulnerable to command injection attacks | CWE-78 |
| javasecurity:S5131 | Endpoints should not be vulnerable to reflected XSS attacks | CWE-79 |
| javasecurity:S5135 | Deserialization should not be vulnerable to injection attacks | CWE-502 |
| javasecurity:S5334 | Dynamic code execution should not be vulnerable to injection attacks | CWE-94 |
| javasecurity:S2078 | LDAP queries should not be vulnerable to injection attacks | CWE-90 |
| javasecurity:S5147 | NoSQL operations should not be vulnerable to injection attacks | CWE-943 |
| javasecurity:S5496 | Server-side templates should not be vulnerable to injection attacks | CWE-94 |
| javasecurity:S2091 | XPath expressions should not be vulnerable to injection attacks | CWE-643 |
| javasecurity:S2083 | I/O function calls should not be vulnerable to path injection attacks | CWE-22 |

**What to check**: String concatenation in SQL/OS/LDAP/NoSQL/XPath queries,
unparameterized queries, user input in template engines, unsanitized file paths.

### 1.2 Cross-Site Scripting & Request Forgery (Blocker)

| Rule Key | Title |
|----------|-------|
| javasecurity:S5131 | Endpoints should not be vulnerable to reflected XSS attacks |
| javasecurity:S7606 | WebViews should not be vulnerable to cross-app scripting attacks |
| javasecurity:S6384 | Components should not be vulnerable to intent redirection |

### 1.3 Credential & Secret Management (Blocker/High)

| Rule Key | Severity | Title |
|----------|----------|-------|
| java:S6437 | Blocker | Credentials should not be hard-coded |
| java:S2115 | Blocker | A secure password should be used when connecting to a database |
| java:S5344 | High | Passwords should not be stored in plaintext or with a fast hashing algorithm |
| java:S2053 | High | Password hashing functions should use an unpredictable salt |

**What to check**: Hardcoded strings assigned to variables named password/secret/token/key/credential,
database connection strings with embedded passwords, plaintext password storage, MD5/SHA1 used for
password hashing.

### 1.4 Cryptography & TLS (High)

| Rule Key | Title |
|----------|-------|
| java:S5547 | Cipher algorithms should be robust |
| java:S5542 | Encryption algorithms should be used with secure mode and padding scheme |
| java:S4426 | Cryptographic keys should be robust |
| java:S6432 | Counter Mode initialization vectors should not be reused |
| java:S3329 | Cipher Block Chaining IVs should be unpredictable |
| java:S4347 | Secure random number generators should not output predictable values |
| java:S5659 | JWT should be signed and verified with strong cipher algorithms |
| java:S4423 | Weak SSL/TLS protocols should not be used |
| java:S4830 | Server certificates should be verified during SSL/TLS connections |
| java:S5527 | Server hostnames should be verified during SSL/TLS connections |

**What to check**: DES/3DES/RC4 usage, ECB mode, keys < 2048 bits (RSA) or < 256 bits (AES),
static IVs, `java.util.Random` for security, disabled certificate validation, TLS < 1.2.

### 1.5 XML & File Security (Blocker/High)

| Rule Key | Severity | Title |
|----------|----------|-------|
| java:S2755 | Blocker | XML parsers should not be vulnerable to XXE attacks |
| java:S6373 | Blocker | XML parsers should not allow inclusion of arbitrary files |
| javasecurity:S6096 | Blocker | Extracting archives should not lead to zip slip vulnerabilities |
| java:S5445 | High | Insecure temporary file creation methods should not be used |

### 1.6 Authentication & Session (Blocker/High)

| Rule Key | Severity | Title |
|----------|----------|-------|
| java:S3753 | Blocker | @Controller classes using @SessionAttributes must call setComplete |
| java:S5876 | High | A new session should be created during user authentication |
| java:S2254 | High | HttpServletRequest.getRequestedSessionId() should not be used |
| java:S4433 | High | LDAP connections should be authenticated |

### 1.7 Redirect & Forgery (Blocker)

| Rule Key | Title |
|----------|-------|
| javasecurity:S5146 | HTTP request redirections should not be open to forging attacks |

### 1.8 Denial of Service (High)

| Rule Key | Title |
|----------|-------|
| javasecurity:S2631 | Regular expressions should not be vulnerable to DoS attacks |
| javasecurity:S6390 | Thread suspensions should not be vulnerable to DoS attacks |

---

## 2. Reliability & Bug Prevention Rules (32 rules)

### 2.1 Resource Management (Blocker)

| Rule Key | Title |
|----------|-------|
| java:S2095 | Resources should be closed |
| java:S2093 | Try-with-resources should be used |

**What to check**: Database connections, file streams, HTTP clients, sockets opened
without try-with-resources or finally blocks. Any `AutoCloseable` not in a
try-with-resources statement.

### 2.2 Concurrency & Thread Safety (Blocker)

| Rule Key | Title |
|----------|-------|
| java:S2168 | Double-checked locking should not be used |
| java:S3046 | "wait" should not be called when multiple locks are held |
| java:S2276 | "wait(...)" should be used instead of "Thread.sleep(...)" when a lock is held |
| java:S2236 | Methods "wait()", "notify()" and "notifyAll()" should not be called on Thread instances |
| java:S3014 | "ThreadGroup" should not be used |
| java:S2274 | "Object.wait()" and "Condition.await()" should be called inside a "while" loop |
| java:S2235 | "IllegalMonitorStateException" should not be caught |
| java:S2222 | Locks should be released on all paths |
| java:S2122 | "ScheduledThreadPoolExecutor" should not have 0 core threads |

**What to check**: `synchronized` blocks with double-checked locking pattern,
`Thread.sleep()` inside `synchronized`, nested lock acquisition, missing
`volatile` on shared fields, locks not released in finally blocks.

### 2.3 Infinite Loops & Recursion (Blocker)

| Rule Key | Title |
|----------|-------|
| java:S2189 | Loops should not be infinite |
| javabugs:S2190 | Recursion should not be infinite |
| java:S3516 | Methods returns should not be invariant |

### 2.4 Null Safety & Type Safety (High)

| Rule Key | Title |
|----------|-------|
| java:S2447 | "null" should not be returned from a "Boolean" method |
| javabugs:S6466 | Accessing an array element should not trigger ArrayIndexOutOfBoundsException |
| javabugs:S6320 | Cast operations should not trigger ClassCastException |
| javabugs:S6416 | Calls to methods should not trigger an exception |
| java:S6104 | Map computeIfAbsent/computeIfPresent should not be used to add null values |
| java:S6816 | Nullable injected fields and parameters should provide a default value |
| javabugs:S3518 | Zero should not be a possible denominator |

### 2.5 Control Flow Defects (Blocker/High)

| Rule Key | Severity | Title |
|----------|----------|-------|
| java:S128 | Blocker | Switch cases should end with an unconditional break statement |
| java:S1219 | Blocker | switch statements should not contain non-case labels |
| java:S2178 | Blocker | Short-circuit logic should be used in boolean contexts |
| java:S1143 | High | Jump statements should not occur in finally blocks |
| java:S1163 | High | Exceptions should not be thrown in finally blocks |
| java:S4970 | High | Derived exceptions should not hide their parents' catch blocks |

### 2.6 Transactional Integrity (Blocker)

| Rule Key | Title |
|----------|-------|
| java:S2229 | Methods should not call same-class methods with incompatible @Transactional values |

---

## 3. Spring Framework Rules (14 rules)

Apply these ONLY when the project uses Spring/Spring Boot.

### 3.1 Dependency Injection (High)

| Rule Key | Title |
|----------|-------|
| java:S6818 | @Autowired should only be used on a single constructor |
| java:S3305 | Factory method injection should be used in @Configuration classes |
| java:S7178 | Injecting data into static fields is not supported by Spring |
| java:S6816 | Nullable injected fields and parameters should provide a default value |

### 3.2 Component Configuration (Blocker/High)

| Rule Key | Severity | Title |
|----------|----------|-------|
| java:S4602 | Blocker | @SpringBootApplication and @ComponentScan should not be used in the default package |
| java:S3753 | Blocker | @Controller classes using @SessionAttributes must call setComplete |
| java:S6817 | High | @Async annotation on methods in @Configuration class |
| java:S6809 | High | Methods with Spring proxy should not be called via "this" |
| java:S6857 | High | SpEL expression should have a valid syntax |

### 3.3 Web & Data (High)

| Rule Key | Title |
|----------|-------|
| java:S4684 | Persistent entities should not be used as arguments of @RequestMapping methods |
| java:S4601 | HttpSecurity URL patterns should be correctly ordered |
| java:S6814 | Optional REST parameters should have an object type |
| java:S7186 | Methods returning Page/Slice must take Pageable as input parameter |

### 3.4 Scheduling & Events (High)

| Rule Key | Title |
|----------|-------|
| java:S7184 | @Scheduled annotation should only be applied to no-arg methods |
| java:S7185 | @EventListener methods should have one parameter at most |
| java:S7190 | Methods annotated with @BeforeTransaction/@AfterTransaction must respect the contract |

---

## 4. Testing Quality Rules (14 rules)

### 4.1 Test Completeness (Blocker)

| Rule Key | Title |
|----------|-------|
| java:S2699 | Tests should include assertions |
| java:S2187 | TestCases should contain tests |
| java:S2970 | Assertions should be complete |
| java:S2188 | JUnit test cases should call super methods |

### 4.2 Test Correctness (High)

| Rule Key | Title |
|----------|-------|
| java:S5845 | Assertions comparing incompatible types should not be made |
| java:S5779 | Assertion methods should not be used within try block of try-catch catching Error |
| java:S5783 | Only one method invocation is expected when testing checked exceptions |
| java:S5826 | setUp() and tearDown() should be correctly annotated starting with JUnit4 |
| java:S5790 | JUnit5 inner test classes should be annotated with @Nested |
| java:S2186 | JUnit assertions should not be used in "run" methods |
| java:S5969 | Mocking all non-private methods of a class should be avoided |
| java:S5846 | Empty lines should not be tested with regex MULTILINE flag |
| java:S5803 | Class members annotated with @VisibleForTesting should not be accessed from production code |
| java:S6002 | Regex lookahead assertions should not be contradictory |

---

## 5. Code Quality & Maintainability Rules (52 rules)

### 5.1 Complexity (High)

| Rule Key | Title | Threshold |
|----------|-------|-----------|
| java:S3776 | Cognitive Complexity of methods should not be too high | Default: 15 |

### 5.2 Naming & Structure (Blocker/High)

| Rule Key | Severity | Title |
|----------|----------|-------|
| java:S1845 | Blocker | Methods and field names should not be the same or differ only by capitalization |
| java:S2387 | Blocker | Child class fields should not shadow parent class fields |
| java:S1190 | Blocker | Future keywords should not be used as names |
| java:S115 | High | Constant names should comply with a naming convention |
| java:S1598 | High | Package declaration should match source file directory |
| java:S2176 | High | Class names should not shadow interfaces or superclasses |

### 5.3 Object-Oriented Design (Blocker/High)

| Rule Key | Severity | Title |
|----------|----------|-------|
| java:S2975 | Blocker | "clone" should not be overridden |
| java:S2157 | High | Cloneables should implement clone |
| java:S1113 | High | Object.finalize() should not be overridden |
| java:S1174 | High | Object.finalize() should remain protected when overriding |
| java:S1175 | High | Signature of finalize() should match Object.finalize() |
| java:S2151 | High | runFinalizersOnExit should not be called |
| java:S2062 | High | readResolve methods should be inheritable |
| java:S1948 | High | Fields in Serializable class should be transient or serializable |
| java:S6209 | High | Members ignored during record serialization should not be used |
| java:S2638 | High | Method overrides should not change contracts |

### 5.4 Architecture (High)

| Rule Key | Title |
|----------|-------|
| javaarchitecture:S7789 | Classes should be located according to the intended architecture |
| javaarchitecture:S8134 | Forbidden relationships should be removed to solve tangles |
| javaarchitecture:S7788 | Relationships should align with the intended architecture |

### 5.5 Code Patterns (Blocker/High)

| Rule Key | Severity | Title |
|----------|----------|-------|
| java:S2695 | Blocker | PreparedStatement and ResultSet methods should be called with valid indices |
| java:S2275 | Blocker | Printf-style format strings should not lead to unexpected behavior |
| java:S2437 | Blocker | Unnecessary bit operations should not be performed |
| java:S2689 | Blocker | Files opened in append mode should not be used with ObjectOutputStream |
| java:S3252 | High | Static base class members should not be accessed via derived types |
| java:S2696 | High | Instance methods should not write to static fields |
| java:S2390 | High | Classes should not access own subclasses during class initialization |
| java:S4275 | High | Getters and setters should access the expected fields |
| java:S1186 | High | Methods should not be empty |
| java:S1214 | High | Interfaces should not solely consist of constants |
| java:S1452 | High | Generic wildcard types should not be used in return types |
| java:S1215 | High | Execution of the Garbage Collector should be triggered only by the JVM |
| java:S2119 | High | Random objects should be reused |
| java:S1192 | High | String literals should not be duplicated |
| java:S131 | High | switch statements should have default clauses |
| java:S3973 | High | A conditionally executed single line should be denoted by indentation |
| java:S3972 | High | Conditionals should start on new lines |
| java:S2479 | High | Whitespace and control characters in literals should be explicit |

### 5.6 Regex (High)

| Rule Key | Title |
|----------|-------|
| java:S5856 | Regular expressions should be syntactically valid |
| java:S5996 | Regex boundaries should not be used in a way that can never be matched |
| java:S5994 | Regex patterns following a possessive quantifier should not always fail |
| java:S6001 | Back references should only refer to capturing groups matched before the reference |

### 5.7 Performance Optimization (High)

| Rule Key | Title |
|----------|-------|
| java:S5361 | String#replace should be preferred to String#replaceAll |
| java:S4635 | String offset-based methods should be preferred for finding substrings |
| java:S6876 | Reverse iteration should utilize reversed view |
| java:S6877 | Reverse view should be used instead of reverse copy in read-only cases |
| java:S6881 | Virtual threads should be used for tasks with heavy blocking operations |
| javabugs:S6322 | Unsupported methods should not be called on some collection implementations |
