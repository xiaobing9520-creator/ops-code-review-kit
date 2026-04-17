# Secure Coding Baseline Standards (BSL 11.1.1.d)

**Source**: BSL 11.1.1.d - Secure Coding Baseline - Details
**Issued by**: Group Security - GRC
**Version**: 3 (October 2025)
**Classification**: Internal
**Total Controls**: 230

This baseline defines the minimum set of security measures for all IT systems,
software, application and app development throughout the complete development lifecycle.

**Mandatory compliance**: Use of "must/shall" indicates mandatory compliance.
Use of "should/may" means compliance is normally expected and highly recommended.

## Impact Area Legend

- **C** = Confidentiality
- **I** = Integrity
- **A** = Availability

---

## 1. Authentication & Password Management (31 controls)

Controls for authentication mechanisms, password policies, credential storage, and identity management.

### 11.1.1_1 — Authentication & Password Management

**Impact**: C/I/A

Require authentication for all pages and resources, except those specifically intended to be public.

---

### 11.1.1_2 — Authentication & Password Management

**Impact**: C/I/A

All authentication controls must be enforced on a trusted system (e.g., The server/program/service) using the Philips approved and/or provided Identity and Access Management solutions. Use the Logical access control Standard as mandatory input.

---

### 11.1.1_3 — Authentication & Password Management

**Impact**: C/I/A

Establish and utilize standard, tested, authentication services whenever possible  using the Philips approved and/or provided Identity and Access Management solutions. Use the Logical access control Standard  as mandatory input

---

### 11.1.1_4 — Authentication & Password Management

**Impact**: C/I/A

Use a centralized implementation for all authentication controls, including libraries that call external authentication services using the Philips approved and/or provided Identity and Access Management solutions. Use the Logical access control Standard  as mandatory input

---

### 11.1.1_5 — Authentication & Password Management

**Impact**: C/I/A

Segregate authentication logic from the resource being requested and use redirection to and from the centralized authentication control

---

### 11.1.1_6 — Authentication & Password Management

**Impact**: C/I/A

All authentication controls should fail securely

---

### 11.1.1_7 — Authentication & Password Management

**Impact**: C/I/A

All administrative and account management functions must be at least as secure as the primary authentication mechanism.

---

### 11.1.1_8 — Authentication & Password Management

**Impact**: C/I/A

If your application manages a credential store, it must ensure that only cryptographically strong one-way salted hashes of passwords are stored and that the table/file that stores the passwords and keys is write-able only by the application.

> **Implementation Guidance**: Do not use the MD5 algorithm if it can be avoided and never store passwords in plain text form in the database, use hashing algorithm to obfuscate such as the bcrypt.

---

### 11.1.1_9 — Authentication & Password Management

**Impact**: C/I/A

Password hashing must be implemented on a trusted system (e.g., The server)   using the Philips approved and/or provided Identity and Access Management solutions. Use the Logical access control Standard  as mandatory input

---

### 11.1.1_10 — Authentication & Password Management

**Impact**: 

Validate the authentication data only on completion of all data input, especially for sequential authentication implementations√√√

---

### 11.1.1_11 — Authentication & Password Management

**Impact**: C/I/A

Authentication failure responses should not indicate which part of the authentication data was incorrect. For example, instead of "Invalid username" or "Invalid password", just use "Invalid username and/or password" for both. Error responses must be truly identical in both display and source code

---

### 11.1.1_12 — Authentication & Password Management

**Impact**: C/I/A

Utilize authentication for connections to external systems that involve sensitive information or functions

---

### 11.1.1_13 — Authentication & Password Management

**Impact**: C/I/A

Authentication credentials for accessing services external to the application should be encrypted and stored in a protected location on a trusted system. The source code is NOT a secure location. The Philips approved and/or provided Identity and Access Management solutions must be used. Use the Logical access control Standard  as mandatory input

---

### 11.1.1_14 — Authentication & Password Management

**Impact**: C/I/A

Only send non-temporary passwords over an encrypted connection or as encrypted data, such as in an encrypted email.

---

### 11.1.1_15 — Authentication & Password Management

**Impact**: C/I/A

Enforce password and pincode complexity requirements established by the Philips Credential baseline, or regulation in case regulation requires higher requirement.

---

### 11.1.1_16 — Authentication & Password Management

**Impact**: C/I/A

Enforce password or pincode length requirements established by the Philips Credential baseline or regulation in case regulation requires higher password length.

---

### 11.1.1_17 — Authentication & Password Management

**Impact**: C/I/A

Password entry should be obscured on the user's screen.

---

### 11.1.1_18 — Authentication & Password Management

**Impact**: C/I/A

Enforce account disabling after an established number of invalid login attempts. The account must be disabled for a period of time sufficient to discourage brute force guessing of credentials, but not so long as to allow for a denial-of-service attack to be performed. The P hilips Credential  baseline must be followed for this.

---

### 11.1.1_19 — Authentication & Password Management

**Impact**: C/I/A

Password reset and changing operations require the same level of controls as account creation and authentication.

---

### 11.1.1_20 — Authentication & Password Management

**Impact**: C/I/A

Password reset must following the Philips rules on passwords as defined in the Philips Logical Access Control Policy, Standard and associated Baselines.

---

### 11.1.1_21 — Authentication & Password Management

**Impact**: C/I/A

If using email based resets, only send email to a pre- registered address with a temporary link/password.

---

### 11.1.1_22 — Authentication & Password Management

**Impact**: C/I/A

Temporary passwords and links should have an expiration time of max 20 minutes, according to the credential baseline.

---

### 11.1.1_23 — Authentication & Password Management

**Impact**: C/I/A

Password change must be enforced at first log on and adhere to the credential baseline.

---

### 11.1.1_24 — Authentication & Password Management

**Impact**: C/I/A

Notify users when a password reset occurs.

---

### 11.1.1_25 — Authentication & Password Management

**Impact**: C/I/A

Prevent pas sword re-use according the credential baseline.

---

### 11.1.1_26 — Authentication & Password Management

**Impact**: C/I/A

Passwords should be at least one day old before they can be changed, to prevent attacks on password re-use.A new password can be only be set/changed once per day as required in the credential baseline1 day

---

### 11.1.1_27 — Authentication & Password Management

**Impact**: C/I/A

Enforce password changes based on requirements established in policy or regulation. Critical systems may require more frequent changes. The time between resets mus t be administratively controlled and adhere to the Credential Baseline.

---

### 11.1.1_28 — Authentication & Password Management

**Impact**: C/I/A

Change all vendor-supplied default passwords and user IDs or disable the associated accounts.

> **Implementation Guidance**: ID's for registered identities must never be re-used as required in the Identity and Account baseline.

---

### 11.1.1_29 — Authentication & Password Management

**Impact**: C/I/A

Re-authenticate users prior to performing critical operations

---

### 11.1.1_30 — Authentication & Password Management

**Impact**: C/I/A

Use Multi-Factor Authentication for highly sensitive or high value transactional accounts as defined by the Philips Logical Access Control Policy, Standard and baselines.

---

### 11.1.1_31 — Authentication & Password Management

**Impact**: C/I/A

If using third party code for authentication, inspect the code carefully to ensure it is not affected by any malicious code

---

## 2. Communications Security (8 controls)

Controls for TLS/SSL configuration, encrypted connections, and secure communication channels.

### 11.1.1_32 — Communications Security

**Impact**: C/I

Disable weak cipher suites and vulnerable versions of SSL/TLS.

> **Implementation Guidance**: Use TLS 1.2 or greater and disable all null, export, 40-bit or DES cipher suites.

---

### 11.1.1_33 — Communications Security

**Impact**: C/I

TLS certificates must be valid and have the correct domain name, not be expired, and be installed with intermediate certificates when required.

> **Implementation Guidance**: Only TLS 1.2 or higher must be used and a valid certificate.

---

### 11.1.1_34 — Communications Security

**Impact**: C/I

Failed TLS connections must not fall back to an insecure connection

---

### 11.1.1_35 — Communications Security

**Impact**: C/I

Utilize TLS connections for all content requiring authenticated access and for all other sensitive information

---

### 11.1.1_36 — Communications Security

**Impact**: C/I

Utilize TLS for connections to external systems that involve sensitive information or functions

---

### 11.1.1_37 — Communications Security

**Impact**: C/I

Utilize a single standard TLS implementation that is configured appropriately.

---

### 11.1.1_38 — Communications Security

**Impact**: C/I

Specify character encodings for all connections

---

### 11.1.1_39 — Communications Security

**Impact**: C/I

Filter parameters containing sensitive information from the HTTP referer, when linking to external sites.

---

## 3. Cryptography (7 controls)

Controls for cryptographic implementations, key management, and secure random number generation.

### 11.1.1_40 — Cryptography

**Impact**: C/I

All cryptographic functions used to protect secrets from the application user must be implemented on a trusted system (e.g., The server) following the Philips Cryptography Security Standard and baseline in addition to the controls in this baseline.

---

### 11.1.1_41 — Cryptography

**Impact**: C/I

Do not store any cryptographic keys in the code used for protecting secrets in your application code.

> **Implementation Guidance**: Keys must be stored in a vault.

---

### 11.1.1_42 — Cryptography

**Impact**: C/I

Protect master secrets from unauthorized access (restricted to service access) and keep it at secure location (e.g., Vault). Nobody (even Admin) must be able to export the master key from the protected location.

---

### 11.1.1_43 — Cryptography

**Impact**: C/I

Cryptographic modules should fail securely

---

### 11.1.1_44 — Cryptography

**Impact**: C/I

All random numbers, random file names, random GUIDs, and random strings should be generated using the cryptographic module’s approved random number generator when these random values are intended to be un-guessable

---

### 11.1.1_45 — Cryptography

**Impact**: C/I

Cryptographic modules used must comply to FIPS 140-2. See cryptography standard and baseline for more detailed information about FIPS 140-2

---

### 11.1.1_46 — Cryptography

**Impact**: C/I

The Philips Cryptography Standard and baseline must be complied with for key management.

---

## 4. Data Protection (13 controls)

Controls for sensitive data handling, storage, caching, and information disclosure prevention.

### 11.1.1_47 — Data Protection

**Impact**: C/I/A

Implement least privilege, restrict users to only the functionality, data and system information that is required to perform their tasks. As defined in the Logical Access Control Standard.

---

### 11.1.1_48 — Data Protection

**Impact**: C/I/A

Protect all cached or temporary copies of sensitive data stored on the server from unauthorized access and purge those temporary working files a soon as they are no longer required.

---

### 11.1.1_49 — Data Protection

**Impact**: C/I/A

Encrypt highly sensitive stored information, like authentication verification data, even on the server side. Always use well vetted algorithms, see "Cryptographic" within this baseline and the Philips Cryptography Security standard and baseline for additional guidance.

---

### 11.1.1_50 — Data Protection

**Impact**: C/I/A

Protect server-side source-code from being downloaded by a user

---

### 11.1.1_51 — Data Protection

**Impact**: C/I/A

Do not store passwords, connection strings or other sensitive information in clear text or in any non-cryptographically secure manner on the client side. This includes embedding in insecure formats like: MS viewstate, Adobe flash or compiled code.

---

### 11.1.1_52 — Data Protection

**Impact**: C/I/A

Remove comments in user accessible production code that may reveal backend system or other sensitive information

---

### 11.1.1_53 — Data Protection

**Impact**: C/I/A

Remove unnecessary application and system documentation as this can reveal useful information to attackers

---

### 11.1.1_54 — Data Protection

**Impact**: C/I/A

Do not include sensitive information in HTTP GET request parameters.

---

### 11.1.1_55 — Data Protection

**Impact**: C/I/A

Disable auto complete features on forms expected to contain sensitive information, including authentication

---

### 11.1.1_56 — Data Protection

**Impact**: C/I/A

Disable client side caching on pages containing sensitive information. Cache-Control: no-store, may be used in conjunction with the HTTP header control "Pragma: no- cache", which is less effective, but is HTTP/1.0 backward compatible.

---

### 11.1.1_57 — Data Protection

**Impact**: C/I/A

The application should support the removal of sensitive data when that data is no longer required. (e.g. personal information or certain financial data)

---

### 11.1.1_58 — Data Protection

**Impact**: C/I/A

Implement appropriate logical access controls for sensitive data stored on the server. This includes cached data, temporary files and data that should be accessible only by specific system users

---

### 11.1.1_59 — Data Protection

**Impact**: C/I/A

Use industry accepted methods for the secure disposal of data from storage media and that data must not be recoverable by any forensic emans.

---

## 5. Database Security (14 controls)

Controls for database access security, parameterized queries, connection management, and database hardening.

### 11.1.1_60 — Database Security

**Impact**: C/I/A

The Philips baseline for either generic or specific databases must be complied to if available, in addition to all secure coding controls mentioned in this secure coding standard, Website secure coding baseline and API Baseline.

---

### 11.1.1_61 — Database Security

**Impact**: C/I/A

Use strongly typed parameterized queries.

> **Implementation Guidance**: A parameterized query is a query in which placeholders are used for parameters and the parameter values are supplied at execution time.

---

### 11.1.1_62 — Database Security

**Impact**: C/I/A

Utilize input validation and output encoding of this secure coding baseline and be sure to address meta characters. If these fail, do not run the database command

---

### 11.1.1_63 — Database Security

**Impact**: C/I/A

Ensure that variables are strongly typed

---

### 11.1.1_64 — Database Security

**Impact**: C/I/A

The application should use the lowest possible level of privilege when accessing the database

---

### 11.1.1_65 — Database Security

**Impact**: C/I/A

Use secure credentials for database access

---

### 11.1.1_66 — Database Security

**Impact**: C/I/A

Connection strings should not be hard coded within the application. Connection strings should be stored in a separate configuration file on a trusted system and they should be encrypted.

> **Implementation Guidance**: Encryption must adhere to the Cryptography security standard and baseline.

---

### 11.1.1_67 — Database Security

**Impact**: C/I/A

Use stored procedures to abstract data access and allow for the removal of permissions to the base tables in the database.

---

### 11.1.1_68 — Database Security

**Impact**: C/I/A

Close the connection as soon as possible for the application.

---

### 11.1.1_69 — Database Security

**Impact**: C/I/A

Remove or change all default database administrative passwords as defined in the credential baseline.

> **Implementation Guidance**: Utilize strong passwords/phrases or implement multi-factor authentication.

---

### 11.1.1_70 — Database Security

**Impact**: C/I/A

Turn off all unnecessary database functionality (e.g., unnecessary stored procedures or services, utility packages, install only the minimum set of features and options required (surface area reduction)).

---

### 11.1.1_71 — Database Security

**Impact**: C/I/A

Remove unnecessary default vendor content (e.g., sample schemas).

---

### 11.1.1_72 — Database Security

**Impact**: C/I/A

Disable any default accounts that are not required to support business requirements as defined in the identity & account baseline.

---

### 11.1.1_73 — Database Security

**Impact**: C/I/A

The application should connect to the database with different credentials for every trust distinction (e.g., user, read-only user, guest, administrators).

---

## 6. Error Handling & Logging (25 controls)

Controls for secure error handling, exception management, and security event logging.

### 11.1.1_74 — Error Handling & Logging

**Impact**: I

Do not disclose sensitive information in error responses, including system details, session identifiers or account information.

---

### 11.1.1_75 — Error Handling & Logging

**Impact**: I

Use error handlers that do not display debugging or stack trace information.

---

### 11.1.1_76 — Error Handling & Logging

**Impact**: I

Implement generic error messages and use custom error pages.

---

### 11.1.1_77 — Error Handling & Logging

**Impact**: I

The application should handle application errors and not rely on the server configuration.

---

### 11.1.1_78 — Error Handling & Logging

**Impact**: I

Properly free allocated memory when error conditions occur.

---

### 11.1.1_79 — Error Handling & Logging

**Impact**: I

Error handling logic associated with security controls should deny access by default.

---

### 11.1.1_80 — Error Handling & Logging

**Impact**: I

All logging controls should be implemented on a trusted system (e.g., The server).

---

### 11.1.1_81 — Error Handling & Logging

**Impact**: I

Logging controls should support both success and failure of specified security events.

---

### 11.1.1_82 — Error Handling & Logging

**Impact**: I

Ensure logs contain important log event data.

---

### 11.1.1_83 — Error Handling & Logging

**Impact**: I

Ensure log entries that include un-trusted data will not execute as code in the intended log viewing interface or software.

---

### 11.1.1_84 — Error Handling & Logging

**Impact**: I

Restrict access to logs to only authorized individuals.

---

### 11.1.1_85 — Error Handling & Logging

**Impact**: I

Utilize a master routine for all logging operations.

---

### 11.1.1_86 — Error Handling & Logging

**Impact**: I

Do not store sensitive information in logs, including unnecessary system details, session identifiers or passwords.

---

### 11.1.1_87 — Error Handling & Logging

**Impact**: I

Ensure that a mechanism exists to conduct log analysis.

---

### 11.1.1_88 — Error Handling & Logging

**Impact**: I

Log all input validation failures.

---

### 11.1.1_89 — Error Handling & Logging

**Impact**: I

Log all authentication attempts, especially failures.

---

### 11.1.1_90 — Error Handling & Logging

**Impact**: I

Log all logical access control failures.

---

### 11.1.1_91 — Error Handling & Logging

**Impact**: I

Log all apparent tampering events, including unexpected changes to state data.

---

### 11.1.1_92 — Error Handling & Logging

**Impact**: I

Log attempts to connect with invalid or expired session tokens.

---

### 11.1.1_93 — Error Handling & Logging

**Impact**: I

Log all system exceptions.

---

### 11.1.1_94 — Error Handling & Logging

**Impact**: I

Log all administrative functions, including changes to the security configuration settings.

---

### 11.1.1_95 — Error Handling & Logging

**Impact**: I

Log all backend TLS connection failures.

---

### 11.1.1_96 — Error Handling & Logging

**Impact**: I

Log cryptographic module failures.

---

### 11.1.1_97 — Error Handling & Logging

**Impact**: I

Use a cryptographic hash function to validate log entry integrity.

---

### 11.1.1_98 — Error Handling & Logging

**Impact**: I

Logs (e.g. debug logs, system logs, etc.) should not contain any sensitive data.

---

## 7. File Management (14 controls)

Controls for file upload security, path traversal prevention, and secure file operations.

### 11.1.1_99 — File Management

**Impact**: C/I/A

Do not pass user supplied data directly to any dynamic include function.

---

### 11.1.1_100 — File Management

**Impact**: C/I/A

Require authentication before allowing a file to be uploaded.

---

### 11.1.1_101 — File Management

**Impact**: C/I/A

Limit the type of files that can be uploaded to only those types that are needed for business purposes.

---

### 11.1.1_102 — File Management

**Impact**: C/I/A

Validate uploaded files are the expected type by checking file headers. Checking for file type by extension alone is not sufficient.

---

### 11.1.1_103 — File Management

**Impact**: C/I/A

Do not save files in the same web context as the application. Files should either go to the content server or in the database.

---

### 11.1.1_104 — File Management

**Impact**: C/I/A

Prevent or restrict the uploading of any file that may be interpreted by the web server.

---

### 11.1.1_105 — File Management

**Impact**: C/I/A

Turn off execution privileges on file upload directories

---

### 11.1.1_106 — File Management

**Impact**: C/I/A

Implement safe uploading in UNIX by mounting the targeted file directory as a logical drive using the associated path or the chrooted environment.

---

### 11.1.1_107 — File Management

**Impact**: C/I/A

When referencing existing files, use a white list of allowed file names and types. Validate the value of the parameter being passed and if it does not match one of the expected values, either reject it or use a hard coded default file value for the content instead.

---

### 11.1.1_108 — File Management

**Impact**: C/I/A

Do not pass user supplied data into a dynamic redirect. If this must be allowed, then the redirect should accept only validated, relative path URLs.

---

### 11.1.1_109 — File Management

**Impact**: C/I/A

Do not pass directory or file paths, use index values mapped to pre-defined list of paths.

---

### 11.1.1_110 — File Management

**Impact**: C/I/A

Never send the absolute file path to the client.

---

### 11.1.1_111 — File Management

**Impact**: C/I/A

Ensure application files and resources are read-only.

---

### 11.1.1_112 — File Management

**Impact**: C/I/A

Scan user uploaded files for viruses and malware.

---

## 8. General Coding Practices (12 controls)

Controls for secure coding fundamentals including race conditions, privilege management, and code integrity.

### 11.1.1_113 — General Coding Practices

**Impact**: C/I/A

Use tested and approved managed code rather than creating new unmanaged code for common tasks.

---

### 11.1.1_114 — General Coding Practices

**Impact**: C/I/A

Utilize task specific built-in APIs to conduct operating system tasks. Do not allow the application to issue commands directly to the Operating System, especially through the use of application initiated command shells.

> **Implementation Guidance**: The API Standard and baseline must be used and adhered to when coding/using APIs.

---

### 11.1.1_115 — General Coding Practices

**Impact**: C/I/A

Use checksums or hashes to verify the integrity of interpreted code, libraries, executables, and configuration files .

---

### 11.1.1_116 — General Coding Practices

**Impact**: C/I/A

Utilize locking to prevent multiple simultaneous requests or use a synchronization mechanism to prevent race conditions.

---

### 11.1.1_117 — General Coding Practices

**Impact**: C/I/A

Protect shared variables and resources from inappropriate concurrent access.

---

### 11.1.1_118 — General Coding Practices

**Impact**: C/I/A

Explicitly initialize all your variables and other data stores, either during declaration or just before the first usage.

---

### 11.1.1_119 — General Coding Practices

**Impact**: C/I/A

In cases where the application must run with elevated privileges, raise privileges as late as possible, and drop them as soon as possible.

---

### 11.1.1_120 — General Coding Practices

**Impact**: C/I/A

Avoid calculation errors by understanding your programming language's underlying representation and how it interacts with numeric calculation. Pay close attention to byte size discrepancies, precision, signed/unsigned distinctions, truncation, conversion and casting between types, "not-a- number" calculations, and how your language handles numbers that are too large or too small for its underlying representation.

---

### 11.1.1_121 — General Coding Practices

**Impact**: C/I/A

Do not pass user supplied data to any dynamic execution function.

---

### 11.1.1_122 — General Coding Practices

**Impact**: C/I/A

Restrict users from generating new code or altering existing code.

---

### 11.1.1_123 — General Coding Practices

**Impact**: C/I/A

Review all secondary applications, third party code and libraries to determine business necessity and validate safe functionality, as these can introduce new vulnerabilities

---

### 11.1.1_124 — General Coding Practices

**Impact**: C/I/A

Implement safe updating. If the application will utilize automatic updates, then use cryptographic signatures for your code and ensure your download clients verify those signatures. Use encrypted channels to transfer the code from the host server.

---

## 9. Input Validation (15 controls)

Controls for input validation, data sanitization, and injection prevention.

### 11.1.1_125 — Input Validation

**Impact**: C/I

Conduct all data validation on a trusted system (e.g., The server).

> **Implementation Guidance**: Systematic check: Correctness (e.g. quantity is numeric), Business rules (e.g. reservation occurs in the future), Warnings (e.g. certain dates can not be selected because of holiday), Information Security (e.g. Check on security threats like SQL commands), Risk Controls (e.g. prevent orders beyond certain authorized amount).

---

### 11.1.1_126 — Input Validation

**Impact**: C/I

Identify all data sources and classify them into trusted and untrusted.

> **Implementation Guidance**: Validate all data from untrusted sources (e.g., Databases, file streams, etc).

---

### 11.1.1_127 — Input Validation

**Impact**: C/I

There should be a centralized input validation routine for the application.

---

### 11.1.1_128 — Input Validation

**Impact**: C/I

Specify proper character sets, for all sources of input.

> **Implementation Guidance**: Such as UTF-8.

---

### 11.1.1_129 — Input Validation

**Impact**: C/I

Encode data to a common character set before validating (Canonicalize).

---

### 11.1.1_130 — Input Validation

**Impact**: C/I

All validation failures should result in input rejection.

---

### 11.1.1_131 — Input Validation

**Impact**: C/I

Determine if the system supports UTF-8 extended character sets and if so, validate after UTF-8 decoding is completed.

---

### 11.1.1_132 — Input Validation

**Impact**: C/I

Validate all client provided data before processing, including all parameters, URLs and HTTP header content (e.g. Cookie names and values). Be sure to include automated post backs from JavaScript, Flash or other embedded code.

---

### 11.1.1_133 — Input Validation

**Impact**: C/I

Validate for expected data types.

---

### 11.1.1_134 — Input Validation

**Impact**: C/I

Validate data range.

---

### 11.1.1_135 — Input Validation

**Impact**: C/I

Validate data length.

---

### 11.1.1_136 — Input Validation

**Impact**: C/I

Validate all input against a "white" list of allowed characters, whenever possible.

---

### 11.1.1_137 — Input Validation

**Impact**: C/I

If any potentially hazardous characters must be allowed as input, be sure that you implement additional controls like output encoding, secure task specific APIs and accounting for the utilization of that data throughout the application. Examples of common hazardous characters include: < > " ' % ( ) & + \ \' \"

---

### 11.1.1_138 — Input Validation

**Impact**: C/I

If your standard validation routine cannot address the following inputs, then they should be checked discretelyo   Check for null bytes (%00) o   Check for new line characters (%0d, %0a, \r, \n) o   Check for “dot-dot-slash" (../ or ..\) path alterations characters. In cases where UTF-8 extended character set encoding is supported, address alternate representation like: %c0%ae%c0%ae/  (Utilize canonicalization to address double encoding or other forms of obfuscation attacks)

---

### 11.1.1_139 — Input Validation

**Impact**: C/I

A REST request or response body should match the intended content type in the header. Otherwise this could cause misinterpretation at the consumer/producer side and lead to code injection/execution.

> **Implementation Guidance**: Document all supported content types in your API.

---

## 10. Logical Access Control (23 controls)

Controls for authorization, access control enforcement, privilege management, and RBAC.

### 11.1.1_140 — Logical Access Control

**Impact**: C/I/A

Use only trusted system objects, e.g. server side session objects, for making access authorization decisions.

---

### 11.1.1_141 — Logical Access Control

**Impact**: C/I/A

Use a single site-wide component to check access authorization. This includes libraries that call external authorization services.

---

### 11.1.1_142 — Logical Access Control

**Impact**: C/I/A

Logical Access controls should fail securely

---

### 11.1.1_143 — Logical Access Control

**Impact**: C/I/A

Deny all access if the application cannot access its security configuration information.

---

### 11.1.1_144 — Logical Access Control

**Impact**: C/I/A

Segregate privileged logic from other application code.

---

### 11.1.1_145 — Logical Access Control

**Impact**: C/I/A

Restrict access to files or other resources, including those outside the application's direct control, to only authorized users.

---

### 11.1.1_146 — Logical Access Control

**Impact**: C/I/A

Restrict access to protected functions to only authorized. users

---

### 11.1.1_147 — Logical Access Control

**Impact**: C/I/A

Restrict access to API Services to only authorized users.

> **Implementation Guidance**: The API Standard and baseline must be used and adhered to when coding/using APIs.

---

### 11.1.1_148 — Logical Access Control

**Impact**: C/I/A

Restrict direct object references to only authorized users.

---

### 11.1.1_149 — Logical Access Control

**Impact**: C/I/A

Restrict access to services to only authorized users.

---

### 11.1.1_150 — Logical Access Control

**Impact**: C/I/A

Restrict access  to application data to only authorized users.

---

### 11.1.1_151 — Logical Access Control

**Impact**: C/I/A

Restrict access to user and data attributes and policy information used by access controls.

---

### 11.1.1_152 — Logical Access Control

**Impact**: C/I/A

Restrict access security-relevant configuration information to only authorized users.

---

### 11.1.1_153 — Logical Access Control

**Impact**: C/I/A

Server side implementation and presentation layer representations of logical access control rules must match.

---

### 11.1.1_154 — Logical Access Control

**Impact**: C/I/A

If state data must be stored on the client, use encryption and integrity checking on the server side to catch state tampering.

---

### 11.1.1_155 — Logical Access Control

**Impact**: C/I/A

Enforce application logic flows to comply with business rules.

---

### 11.1.1_156 — Logical Access Control

**Impact**: C/I/A

Limit the number of transactions a single user or device can perform in a given period of time.

> **Implementation Guidance**: The transactions/time should be above the actual business requirement, but low enough to deter automated attacks. To be determined per application based on "normal transactions/time behaviour baseline" and an upper threshold to prevent unusual high transaction rates/volumes.

---

### 11.1.1_157 — Logical Access Control

**Impact**: C/I/A

Use the "referer" header as a supplemental check only, it should never be the sole authorization check, as it is can be spoofed

---

### 11.1.1_158 — Logical Access Control

**Impact**: C/I/A

Implement account auditing and enforce the disabling of unused accounts (e.g., After no more than 30 days from the expiration of an account’s password.) as defined in the Identity & Account baseline.

---

### 11.1.1_159 — Logical Access Control

**Impact**: C/I/A

The application must support disabling of accounts and terminating sessions when authorization ceases (e.g., Changes to role, employment status, business process, etc.).

---

### 11.1.1_160 — Logical Access Control

**Impact**: C/I/A

Service accounts or accounts supporting connections to or from external systems should have the least privilege possible.

---

### 11.1.1_161 — Logical Access Control

**Impact**: C/I/A

Create a specific application Access Control Policy document containing the application's business rules, data types and access authorization criteria and/or processes so that access can be properly provisioned and controlled. This includes identifying access requirements for both the data and system resources.

> **Implementation Guidance**: The Logical Access Control Policy, Standard and associated Baselines of the Security Management Framework (SMF) must be adhered to and used as mandatory input for when setting up an application Access Control Policy document.

---

### 11.1.1_162 — Logical Access Control

**Impact**: C/I/A

No anonymous access (including anonymous connections) is allowed, unless the purpose is to share information publicly in line with the classification, as decided by the business owner.

> **Implementation Guidance**: When anonymous access is permitted, access must be in line with the access control policy and logs must be created and stored for audit purposes that only public classified information and assets are shared.

---

## 11. Memory Management (9 controls)

Controls for buffer overflow prevention, memory safety, and resource cleanup.

### 11.1.1_163 — Memory Management

**Impact**: C/I/A

Utilize input and output control for un-trusted data

---

### 11.1.1_164 — Memory Management

**Impact**: C/I/A

Double check that the buffer is as large as specified

---

### 11.1.1_165 — Memory Management

**Impact**: C/I/A

When using functions that accept a number of bytes to copy, such as strncpy(), be aware that if the destination buffer size is equal to the source buffer size,

> **Implementation Guidance**: It may not NULL-terminate the string.

---

### 11.1.1_166 — Memory Management

**Impact**: C/I/A

Check buffer boundaries if calling the function in a loop and make sure there is no danger of writing past the allocated space

---

### 11.1.1_167 — Memory Management

**Impact**: C/I/A

Truncate all input strings to a reasonable length before passing them to the copy and concatenation functions.

---

### 11.1.1_168 — Memory Management

**Impact**: C/I/A

Specifically close resources, don’t rely on garbage collection. (e.g., connection objects, file handles, etc.).

---

### 11.1.1_169 — Memory Management

**Impact**: C/I/A

Use non-executable stacks when available.

---

### 11.1.1_170 — Memory Management

**Impact**: C/I/A

Avoid the use of known vulnerable functions (e.g., printf, strcat, strcpy etc.).

---

### 11.1.1_171 — Memory Management

**Impact**: C/I/A

Properly free allocated memory upon the completion of functions and at all exit points.

---

## 12. Output Encoding (7 controls)

Controls for output encoding, XSS prevention, and injection-safe data rendering.

### 11.1.1_172 — Output Encoding

**Impact**: C/I

Conduct all encoding on a trusted system (e.g., The server).

---

### 11.1.1_173 — Output Encoding

**Impact**: C/I

Utilize a standard, tested routine for each type of outbound encoding.

---

### 11.1.1_174 — Output Encoding

**Impact**: C/I

Contextually output encode all data returned to the client that originated outside the application's trust boundary. HTML entity encoding is one example, but does not work in all cases.

---

### 11.1.1_175 — Output Encoding

**Impact**: C/I

Encode all characters unless they are known to be safe for the intended interpreter.

---

### 11.1.1_176 — Output Encoding

**Impact**: C/I

Contextually sanitize all output of un-trusted data to queries for SQL, XML, and LDAP.

---

### 11.1.1_177 — Output Encoding

**Impact**: C/I

Command execution should not be allowed from the application.

---

### 11.1.1_178 — Output Encoding

**Impact**: C/I

Sanitize all output of un-trusted data to operating system commands.

---

## 13. Secure Design (9 controls)

Controls for threat modeling, security architecture, testing, and SDLC integration.

### 11.1.1_179 — Secure Design

**Impact**: C/I/A

Use threat modeling for critical authentication, access control, business logic, and key flows

---

### 11.1.1_180 — Secure Design

**Impact**: C/I/A

Integrate security language and controls into user stories

---

### 11.1.1_181 — Secure Design

**Impact**: C/I/A

Integrate plausibility checks at each tier of your application (from frontend to backend)

---

### 11.1.1_182 — Secure Design

**Impact**: C/I/A

Write unit and integration tests to validate that all critical flows are resistant to the threat model. Compile use cases and misue-cases for each tier of your application.

---

### 11.1.1_183 — Secure Design

**Impact**: C/I/A

Segregate tier layers on the system and network layers depending on the exposure and protection needs.

---

### 11.1.1_184 — Secure Design

**Impact**: C/I/A

Segregate tenants robustly by design throughout all tiers.

---

### 11.1.1_185 — Secure Design

**Impact**: C/I/A

Limit resource consumption by user or service.

---

### 11.1.1_186 — Secure Design

**Impact**: C/I/A

Implement a SDLC process for application design, development, deployment, and operation in accordance with security requirements defined by the organization.

---

### 11.1.1_187 — Secure Design

**Impact**: C/I/A

Philips Container/microservices baseline must be complied when microservices are running within a container or a groups containers.

---

## 14. Security Configuration (6 controls)

Controls for secure deployment, dependency management, and vulnerability remediation.

### 11.1.1_188 — Security Configuration

**Impact**: C/I/A

Implement automation for secure, standardized and compliant applications deployment.

---

### 11.1.1_189 — Security Configuration

**Impact**: C/I/A

Define and Implement automatic remediation process to remmediate  application vulnerabilitites.

---

### 11.1.1_190 — Security Configuration

**Impact**: C/I/A

Remove unused dependencies, unnecessary features, components, files, and documentation.

---

### 11.1.1_191 — Security Configuration

**Impact**: C/I/A

Continuously inventory the versions of both client-side and server-side components (e.g., frameworks, libraries) and their dependencies using tools like versions, OWASP Dependency Check, retire.js, etc. Continuously monitor sources like Common Vulnerability and Exposures (CVE) and National Vulnerability Database (NVD) for vulnerabilities in the components. Use software composition analysis tools to automate the process. Subscribe to email alerts for security vulnerabilities related to components you use.

---

### 11.1.1_192 — Security Configuration

**Impact**: C/I/A

Only obtain components from official sources over secure links. Prefer signed packages to reduce the chance of including a modified, malicious component (See A08:2021- Software and Data Integrity Failures).

---

### 11.1.1_193 — Security Configuration

**Impact**: C/I/A

Monitor for libraries and components that are unmaintained or do not create security patches for older versions. If patching is not possible, consider deploying a virtual patch to monitor, detect, or protect against the discovered issue.

---

## 15. Security Logging (8 controls)

Controls for security monitoring, audit trails, and incident response logging.

### 11.1.1_194 — Security Logging

**Impact**: I

The Philips Logging Standard must be followed in addition to the specific controls for Logging and Error Handling & Logging mentioned within this standard.

---

### 11.1.1_195 — Security Logging

**Impact**: C/I/A

Monitor security related events within applications and the underlying infrastructure. Implement automation to  send alerts to responsible stakeholders based on corresponding metrics.

---

### 11.1.1_196 — Security Logging

**Impact**: C/I/A

Application owner must implement and document which logs, meta data and system events need to be logged.

---

### 11.1.1_197 — Security Logging

**Impact**: C/I/A

Ensure all login, access control, and server-side input validation failures can be logged with sufficient user context to identify suspicious or malicious accounts and held for enough time to allow delayed forensic analysis.

---

### 11.1.1_198 — Security Logging

**Impact**: C/I/A

Ensure that logs are generated in a format that log management solutions can easily consume.

---

### 11.1.1_199 — Security Logging

**Impact**: C/I/A

Ensure log data is encoded correctly to prevent injections or attacks on the logging or monitoring systems.

---

### 11.1.1_200 — Security Logging

**Impact**: C/I/A

Ensure high-value transactions have an audit trail with integrity controls to prevent tampering or deletion, such as append-only database tables or similar.

---

### 11.1.1_201 — Security Logging

**Impact**: C/I/A

Establish or adopt an incident response and recovery plan.

---

## 16. Session Management (15 controls)

Controls for session security, cookie configuration, and session lifecycle management.

### 11.1.1_202 — Session Management

**Impact**: C/I

Use the server or framework’s session management controls. The application should only recognize these session identifiers as valid.

---

### 11.1.1_203 — Session Management

**Impact**: C/I

Session identifier creation must always be done on a trusted system (e.g., The server).

---

### 11.1.1_204 — Session Management

**Impact**: C/I

Session management controls should use well vetted algorithms that ensure sufficiently random session identifiers.

---

### 11.1.1_205 — Session Management

**Impact**: C/I

Set the domain and path for cookies containing authenticated session identifiers to an appropriately restricted value for the application.

---

### 11.1.1_206 — Session Management

**Impact**: C/I

Logout functionality should fully terminate the associated session or connection.

---

### 11.1.1_207 — Session Management

**Impact**: C/I

Logout functionality should be available from all pages protected by authorization.

---

### 11.1.1_208 — Session Management

**Impact**: C/I

Establish a session inactivity timeout that is as short as possible, based on balancing risk and business functional requirements. In most cases it should be no more than several hours. Define max 2 hours for timeout, or less depending on sensitivity of application or business requirements.

---

### 11.1.1_209 — Session Management

**Impact**: C/I

If a session was established before login, close that session and establish a new session after a successful login.

---

### 11.1.1_210 — Session Management

**Impact**: C/I

Generate a new session identifier on any re-authentication.

---

### 11.1.1_211 — Session Management

**Impact**: C/I

Do not allow concurrent logins with the same user ID.

> **Implementation Guidance**: Do not permit duplicate concurrent user sessions from different machines and verify that the application limits the number of active concurrent sessions.

---

### 11.1.1_212 — Session Management

**Impact**: C/I

Protect server side session data from unauthorized access, by other users of the server, by implementing appropriate access controls on the server.

---

### 11.1.1_213 — Session Management

**Impact**: C/I

Supplement standard session management for sensitive server-side operations, like account management, by utilizing per-session strong random tokens or parameters. This method can be used to prevent Cross Site Request Forgery attacks.

---

### 11.1.1_214 — Session Management

**Impact**: C/I

Supplement standard session management for highly sensitive or critical operations by utilizing per-request, as opposed to per-session, strong random tokens or parameters.

---

### 11.1.1_215 — Session Management

**Impact**: C/I

Enable the "secure" attribute for cookies transmitted over a TLS connection.

> **Implementation Guidance**: The TLS Connection must be 1.2 or higher.

---

### 11.1.1_216 — Session Management

**Impact**: C/I

Set cookies with the HttpOnly attribute, unless you specifically require client-side scripts within your application to read or set a cookie's value.

---

## 17. System Configuration (12 controls)

Controls for server hardening, HTTP security headers, and deployment environment security.

### 11.1.1_217 — System Configuration

**Impact**: C/I/A

Ensure servers, frameworks and system components are running the latest approved version.

---

### 11.1.1_218 — System Configuration

**Impact**: C/I/A

Ensure servers, frameworks and system components have all patches issued for the version in use.

---

### 11.1.1_219 — System Configuration

**Impact**: C/I/A

Turn off directory listings.

---

### 11.1.1_220 — System Configuration

**Impact**: C/I/A

When exceptions occur, fail securely.

---

### 11.1.1_221 — System Configuration

**Impact**: C/I/A

Remove all unnecessary functionality and files.

---

### 11.1.1_222 — System Configuration

**Impact**: C/I/A

Remove test code or any functionality not intended for production, prior to deployment.

---

### 11.1.1_223 — System Configuration

**Impact**: C/I/A

Prevent disclosure of your directory structure in the robots.txt file by placing directories not intended for public indexing into an isolated parent directory. Then "Disallow" that entire parent directory in the robots.txt file rather than Disallowing each individual directory.

---

### 11.1.1_224 — System Configuration

**Impact**: C/I/A

Disable unnecessary HTTP methods, such as WebDAV extensions. If an extended HTTP method that supports file handling is required, utilize a well-vetted authentication mechanism.

---

### 11.1.1_225 — System Configuration

**Impact**: C/I/A

The security configuration store for the application should be able to be output in human readable form to support auditing.

---

### 11.1.1_226 — System Configuration

**Impact**: C/I/A

Implement an asset management system and register system components and software in it.The asset management system must be set up according to the Asset Management Standard.

---

### 11.1.1_227 — System Configuration

**Impact**: C/I/A

Isolate development environments from the production network and provide access only to authorized development and test groups. Development environments are often configured less securely than production environments and attackers may use this difference to discover shared weaknesses or as an avenue for exploitation.

---

### 11.1.1_228 — System Configuration

**Impact**: C/I/A

Implement a software change control system to manage and record changes to the code both in development and production.

---

## 18. Vulnerability Testing Practices (1 controls)

Controls for penetration testing and security assessment requirements.

### 11.1.1_229 — Vulnerability Testing Practices

**Impact**: C/I/A

Stake holder/Application owner must perform periodic penetration testing, when going to production and/or changes to the application. Testing must be performed by third parties.

---

## 19. Website Coding (1 controls)

Controls for website-specific security requirements.

### 11.1.1_230 — Website Coding

**Impact**: 

When building, developing, coding a website, beside this secure coding baseline the Website secure Coding baseline must be adhered to.√√√ Philips General Business Principles (GBP) The Philips General Business Principles (GBP) apply to all employees of Philips and its controlled subsidiaries. The GBP are not all encompassing but formulate minimum standards of behavior. The underlying policies form an integral part of the GBP, including the information security policies and standards where this baseline is based on. If you are ever in doubt about a course of action, ask yourself the following question: Is it consistent with the content of the GBP? Is it ethical? Is it legal? Will it reflect well on Philips and myself? Would I want to be treated this way? Would I want to read about this in the newspaper? If you are uncertain, discuss the matter with your colleagues, seek guidance from either your manager or local GBP Compliance Officer, or go to: https://share.philips.com/sites/Intranet_General_Business_Principles References Abbreviations and definitions used in this document can be found on the Group Security Portal: https://share.philips.com/sites/STS020170831152504/gs/Lists/Security%20Terminology/AllItems.aspx The Security Management Framework (SMF), consisting of all policies, standards, baselines and guidelines, can be found on the Group Security Portal: https://share.philips.com/sites/STS020170831152504/gs/Library/Forms/Domain%20view.aspx Other non-SMF documents that have contributed to this policy or that are referenced in this baseline are: * Security Requirements; Philips IT – Reference page, Version 3.0: https://share.philips.com/sites/CMSPUBLISHING020120920093047/Wiki/Pages/Requirements.aspx * Secure Coding Guidelines; Philips IT – Reference page, Version 3.0. https://share.philips.com/sites/CMSPUBLISHING020120920093047/Wiki/Pages/SecureCodingGuidelines.aspx * Software Development at Philips (SW CoE) * IT BIA Template https://share-intra.philips.com/sites/STS20151001133003/SitePages/Home.aspx * NIST Cloud Computing Reference Architecture (CCRA) * Philips Brand Guidelines https://www.ourbrand.philips.com/login/

---

## Appendix A: Severity Classification (CVSS v3.1)

Severity MUST be determined by computing a CVSS v3.1 Base Score using the
official vector string. Do NOT estimate scores — evaluate each metric:

| Metric | Values |
|--------|--------|
| Attack Vector (AV) | Network / Adjacent / Local / Physical |
| Attack Complexity (AC) | Low / High |
| Privileges Required (PR) | None / Low / High |
| User Interaction (UI) | None / Required |
| Scope (S) | Unchanged / Changed |
| Confidentiality (C) | None / Low / High |
| Integrity (I) | None / Low / High |
| Availability (A) | None / Low / High |

### Score → Severity Mapping

| Severity | CVSS Range | Disposition |
|----------|-----------|-------------|
| Critical | 9.0 – 10.0 | Must be fixed before acceptance. Zero tolerance. |
| High | 7.0 – 8.9 | Must be fixed or have documented mitigation plan. |
| Medium | 4.0 – 6.9 | Should be fixed. Acceptable with risk acknowledgment. |
| Low | 0.1 – 3.9 | Recommended fix. Does not block acceptance. |
| Info | 0.0 | Informational observation, no security impact. |

### CVE Association Rules

Every finding MUST include a `关联 CVE` field, following these rules:

1. **Known vulnerability pattern** — if the code matches a known CVE's vulnerable
   pattern (e.g., Shiro hardcoded key → CVE-2016-4437, Log4j JNDI lookup →
   CVE-2021-44228, Fastjson autoType → CVE-2022-25845), cite the CVE directly.
2. **Vulnerable dependency** — if a dependency version is known to be affected by
   a CVE (from Trivy/SCA reports or known advisories), cite all applicable CVEs.
3. **Code logic flaw** — for custom code vulnerabilities (missing authorization,
   IDOR, business logic errors) that have no matching CVE, use:
   `关联 CVE: N/A — 代码逻辑缺陷 (CWE-[ID])`
4. **Similar pattern** — if the code exhibits a pattern similar to but not exactly
   matching a known CVE, use: `关联 CVE: CVE-XXXX-XXXXX 模式 (相似漏洞模式)`

## Appendix B: Vulnerability Density Thresholds

- Excellent: < 0.1 vulnerabilities/KLOC
- Good: 0.1-0.3 vulnerabilities/KLOC
- Acceptable: 0.3-0.5 vulnerabilities/KLOC
- Unacceptable: > 0.5 vulnerabilities/KLOC

## Appendix C: Blocking Rules (CWE Top 5 — immediate reject if found)

These patterns MUST be flagged as Critical:

1. **CWE-79 Cross-Site Scripting (XSS)**
   - User input rendered in HTML without encoding/escaping
   - `innerHTML`, `dangerouslySetInnerHTML`, `v-html` with unvalidated data
   - Template injection in server-side rendering

2. **CWE-89 SQL Injection**
   - String concatenation or interpolation in SQL queries
   - Dynamic query building without parameterization
   - ORM raw query methods with unvalidated input

3. **CWE-352 Cross-Site Request Forgery (CSRF)**
   - State-changing endpoints without CSRF token validation
   - Missing SameSite cookie attributes on session cookies

4. **CWE-20 Improper Input Validation**
   - External input used without validation (type, length, format, range)
   - Relying solely on client-side validation
   - Missing validation on file uploads (type, size, content)

5. **CWE-78 OS Command Injection**
   - User input passed to shell commands (exec, system, spawn, popen)
   - Unsanitized input in subprocess calls

## Appendix D: High Severity Rules (CWE Top 6-25)

These patterns MUST be flagged as High:

6. **CWE-787 Out-of-bounds Write** — Buffer overflows, array index errors
7. **CWE-416 Use After Free** — Memory safety issues
8. **CWE-22 Path Traversal** — File path construction with user input without sanitization
9. **CWE-862 Missing Authorization** — Endpoints or functions without authorization checks
10. **CWE-476 NULL Pointer Dereference** — Unhandled null/undefined references

## Appendix E: OWASP Top 10 Check Matrix

For every review, systematically check:

| OWASP ID | Category | What to Look For |
|----------|----------|-----------------|
| A01 | Broken Access Control | Missing auth checks, IDOR, privilege escalation paths, CORS misconfiguration |
| A02 | Cryptographic Failures | Hardcoded secrets, weak algorithms (MD5/SHA1 for passwords), missing encryption for sensitive data, plaintext credentials in config |
| A03 | Injection | SQL/NoSQL/OS/LDAP injection, template injection, header injection |
| A04 | Insecure Design | Missing rate limiting, no input validation strategy, trust boundary violations |
| A05 | Security Misconfiguration | Debug mode enabled, default credentials, overly permissive CORS, verbose error messages exposing internals |
| A06 | Vulnerable Components | Known vulnerable dependencies, outdated frameworks, unmaintained libraries |
| A07 | Authentication Failures | Weak password requirements, missing MFA support, insecure session management, credential stuffing vulnerability |
| A08 | Data Integrity Failures | Insecure deserialization, unsigned updates, untrusted CI/CD pipeline inputs |
| A09 | Logging Failures | Missing security event logging, sensitive data in logs, no audit trail for critical operations |
| A10 | SSRF | URL fetching with user-controlled input without allowlist validation |

## Appendix F: Hardcoded Secrets Detection

ALWAYS check for these patterns (flag as Critical):
- API keys, tokens, passwords in source code
- Private keys or certificates in repository
- Database connection strings with embedded credentials
- AWS access keys, Azure keys, GCP service account keys
- `.env` files committed to repository
- Secrets in Docker build args or environment variables in Dockerfiles

## Appendix G: Infrastructure Security (if IaC is present)

- S3 buckets: public access blocked, encryption enabled
- IAM policies: least privilege, no wildcard permissions
- Security groups: no unrestricted inbound (0.0.0.0/0) on sensitive ports
- Database instances: not publicly accessible, encryption at rest enabled
- Logging: CloudTrail/audit logging enabled
- Container images: non-root user, minimal base image, no secrets in layers
