# SonarQube JavaScript Review Standards

This rule defines the SonarQube-based JavaScript/TypeScript code review criteria.
Apply these standards when the target project contains JavaScript or TypeScript
source code. Rules are sourced from SonarQube's JavaScript analyzer (Sonar JS +
JS Security + JS Architecture) and organized by review category.

Total: 77 rules (all classified as HIGH or BLOCKER)

## Severity Mapping

| SonarQube Severity | Review Severity | Action |
|--------------------|----------------|--------|
| **Blocker** | Critical | Must fix before acceptance |
| **High** | High | Must fix or have documented mitigation plan |

---

## 1. Security Rules (25 rules)

### 1.1 Injection Attacks (Blocker)

| Rule Key | Title | CWE Mapping |
|----------|-------|-------------|
| jssecurity:S3649 | Database queries should not be vulnerable to injection attacks | CWE-89 |
| jssecurity:S2076 | OS commands should not be vulnerable to command injection attacks | CWE-78 |
| jssecurity:S5131 | Endpoints should not be vulnerable to reflected XSS attacks | CWE-79 |
| jssecurity:S5334 | Dynamic code execution should not be vulnerable to injection attacks | CWE-94 |
| jssecurity:S5147 | NoSQL operations should not be vulnerable to injection attacks | CWE-943 |
| jssecurity:S2083 | I/O function calls should not be vulnerable to path injection attacks | CWE-22 |

**What to check**: String concatenation in SQL queries, `eval()` with user input,
unsanitized input in `child_process.exec()`, MongoDB query objects from user input,
`fs` operations with user-controlled paths.

### 1.2 Cross-Site Scripting & DOM Security (Blocker)

| Rule Key | Title |
|----------|-------|
| jssecurity:S5696 | DOM updates should not lead to XSS attacks |
| jssecurity:S6105 | DOM updates should not lead to open redirect vulnerabilities |
| jssecurity:S5131 | Endpoints should not be vulnerable to reflected XSS attacks |
| javascript:S2819 | Origins should be verified during cross-origin communications |

**What to check**: `innerHTML`, `document.write()`, `postMessage` without origin
check, `location.href` set from user input, React `dangerouslySetInnerHTML`.

### 1.3 Credential & Secret Management (Blocker)

| Rule Key | Title |
|----------|-------|
| javascript:S6437 | Credentials should not be hard-coded |
| javascript:S7639 | Wallet phrases should not be hard-coded |
| javascript:S6317 | AWS IAM policies should limit the scope of permissions given |

**What to check**: String literals assigned to variables named password/secret/token/key,
`*` in IAM policy actions/resources, mnemonic phrases in source code.

### 1.4 Cryptography & TLS (Blocker)

| Rule Key | Title |
|----------|-------|
| javascript:S5547 | Cipher algorithms should be robust |
| javascript:S5542 | Encryption algorithms should be used with secure mode and padding scheme |
| javascript:S4426 | Cryptographic keys should be robust |
| javascript:S5659 | JWT should be signed and verified with strong cipher algorithms |
| javascript:S4423 | Weak SSL/TLS protocols should not be used |
| javascript:S4830 | Server certificates should be verified during SSL/TLS connections |
| javascript:S5527 | Server hostnames should be verified during SSL/TLS connections |

**What to check**: `createCipher` (deprecated), DES/RC4 usage, `rejectUnauthorized: false`,
`checkServerIdentity` disabled, JWT with `alg: 'none'`, TLS < 1.2.

### 1.5 File & Archive Security (Blocker)

| Rule Key | Title |
|----------|-------|
| jssecurity:S6096 | Extracting archives should not lead to zip slip vulnerabilities |
| javascript:S2598 | File uploads should be restricted |

### 1.6 Redirect & Session (Blocker)

| Rule Key | Title |
|----------|-------|
| jssecurity:S5146 | HTTP request redirections should not be open to forging attacks |
| javascript:S5876 | A new session should be created during user authentication |

### 1.7 Denial of Service (Blocker)

| Rule Key | Title |
|----------|-------|
| jssecurity:S2631 | Regular expressions should not be vulnerable to DoS attacks |

### 1.8 XML Security (Blocker)

| Rule Key | Title |
|----------|-------|
| javascript:S2755 | XML parsers should not be vulnerable to XXE attacks |

---

## 2. Reliability & Bug Prevention Rules (5 rules)

### 2.1 Async/Await Correctness (Blocker)

| Rule Key | Title |
|----------|-------|
| javascript:S4123 | "await" should only be used with promises |
| javascript:S7059 | Constructors should not contain asynchronous operations |
| javascript:S7746 | Promise.resolve() and Promise.reject() should not be used in async functions or promise callbacks |

**What to check**: `await` on non-Promise values, `async constructor()`,
unnecessary `Promise.resolve()` wrapping in async functions.

### 2.2 Control Flow Defects (Blocker)

| Rule Key | Title |
|----------|-------|
| javascript:S3516 | Function returns should not be invariant |
| javascript:S2189 | Loops should not be infinite |
| javascript:S1143 | Jump statements should not occur in finally blocks |

---

## 3. Testing Quality Rules (4 rules)

### 3.1 Test Completeness (Blocker)

| Rule Key | Title |
|----------|-------|
| javascript:S2699 | Tests should include assertions |
| javascript:S2187 | Test files should contain at least one test case |
| javascript:S2970 | Assertions should be complete |
| javascript:S6079 | Tests should not execute any code after done() is called |

**What to check**: Test functions with no `expect()`/`assert()` calls, empty
test files, `expect()` without matcher, code after Mocha/Jest `done()` callback.

---

## 4. Code Quality & Maintainability Rules (42 rules)

### 4.1 Complexity (Blocker)

| Rule Key | Title | Threshold |
|----------|-------|-----------|
| javascript:S3776 | Cognitive Complexity of functions should not be too high | Default: 15 |
| javascript:S2004 | Functions should not be nested too deeply | Default: 4 levels |

### 4.2 Variable Declaration (Blocker)

| Rule Key | Title |
|----------|-------|
| javascript:S2703 | Variables should be declared explicitly |
| javascript:S3504 | Variables should be declared with "let" or "const" |
| javascript:S7740 | Variables should not be assigned the value of "this" |
| javascript:S6861 | Mutable variables should not be exported |

**What to check**: Missing `var`/`let`/`const` (implicit globals), `var` usage
where `let`/`const` is appropriate, `const self = this` pattern, `export let`.

### 4.3 Control Flow (Blocker)

| Rule Key | Title |
|----------|-------|
| javascript:S128 | Switch cases should end with an unconditional break statement |
| javascript:S1219 | switch statements should not contain non-case labels |
| javascript:S4524 | default clauses should be last |
| javascript:S888 | Equality operators should not be used in for loop termination conditions |
| javascript:S1994 | for loop increment clauses should modify the loops' counters |
| javascript:S3972 | Conditionals should start on new lines |

### 4.4 Type Safety (Blocker)

| Rule Key | Title |
|----------|-------|
| javascript:S3785 | "in" should not be used with primitive types |
| javascript:S3834 | "new" operator should not be used with Symbol and BigInt |
| javascript:S4125 | "typeof" expressions should only be compared to valid values |
| javascript:S7767 | Bitwise operators should not be used to truncate numbers |
| javascript:S1314 | Octal values should not be used |

### 4.5 Function & Class Patterns (Blocker)

| Rule Key | Title |
|----------|-------|
| javascript:S1186 | Functions should not be empty |
| javascript:S930 | Function calls should not pass extra arguments |
| javascript:S3854 | super() should be invoked appropriately |
| javascript:S2430 | Constructor names should start with an upper case letter |
| javascript:S3735 | void should not be used |
| javascript:S6958 | Literals should not be used as functions |
| javascript:S7727 | Function references should not be passed directly to iterator methods |

### 4.6 Array & Object Patterns (Blocker)

| Rule Key | Title |
|----------|-------|
| javascript:S2871 | Array.prototype.sort() and Array.prototype.toSorted() should use a compare function |
| javascript:S3796 | Callbacks of array methods should have return statements |
| javascript:S7739 | Objects should not have a "then" property |
| javascript:S7774 | Methods should be accessed from prototypes, not instances |

### 4.7 Getter/Setter (Blocker)

| Rule Key | Title |
|----------|-------|
| javascript:S4275 | Getters and setters should access the expected fields |
| javascript:S7725 | Getters and setters should not recursively access the same property |

### 4.8 Module & Import (Blocker)

| Rule Key | Title |
|----------|-------|
| javascript:S6859 | Imports should not use absolute paths |
| javascript:S1527 | Future reserved words should not be used as identifiers |

### 4.9 Modern JavaScript (Blocker)

| Rule Key | Title |
|----------|-------|
| javascript:S7783 | trimLeft()/trimRight() should be replaced with trimStart()/trimEnd() |
| javascript:S7768 | Modern DOM manipulation methods should be used instead of legacy alternatives |
| javascript:S7761 | Data attributes should be accessed using ".dataset" |
| javascript:S3812 | Parentheses should be used when negating "in" and "instanceof" operations |

### 4.10 Regex (Blocker)

| Rule Key | Title |
|----------|-------|
| javascript:S5856 | Regular expressions should be syntactically valid |

### 4.11 Accessibility (Blocker)

| Rule Key | Title |
|----------|-------|
| javascript:S5260 | Table cells should reference their headers |

### 4.12 Tooling (Blocker)

| Rule Key | Title |
|----------|-------|
| javascript:S7724 | ESLint disable comments should specify which rules to disable |

### 4.13 Architecture (Blocker)

| Rule Key | Title |
|----------|-------|
| jsarchitecture:S7789 | Files should be located according to the intended architecture |
| jsarchitecture:S8134 | Forbidden relationships should be removed to solve tangles |
| jsarchitecture:S7788 | Relationships should align with the intended architecture |
