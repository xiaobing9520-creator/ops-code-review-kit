# SonarQube JavaScript Review Standards

This rule defines the SonarQube-based JavaScript/TypeScript code review criteria.
Apply these standards when the target project contains JavaScript or TypeScript
source code. Rules are sourced from SonarQube's JavaScript analyzer and organized
by review category.

Each rule includes its SonarQube rule key, severity, explanation, and
Noncompliant/Compliant code examples to guide pattern matching during review.

**Total: 77 rules (all classified as HIGH or BLOCKER)**

## Severity Mapping

| SonarQube Severity | Review Severity | Action |
|--------------------|----------------|--------|
| **Blocker** | Critical | Must fix before acceptance |
| **High** | High | Must fix or have documented mitigation plan |

---

## 1. Security Rules (25 rules)

These rules detect security vulnerabilities including injection attacks, XSS, credential leaks, and cryptographic weaknesses.

### javascript:S2598 — File uploads should be restricted

**Severity**: Blocker

Which component or framework contains the issue?

**Noncompliant code example**

```javascript
const Formidable = require('formidable');
```

**Compliant solution**

```javascript
const Formidable = require('formidable');


const form          = new Formidable();
form.uploadDir      = "/uploads/";
form.keepExtensions = false;
```

---

### javascript:S2755 — XML parsers should not be vulnerable to XXE attacks

**Severity**: Blocker

Which component or framework contains the issue? The following code contains examples of XML parsers that have external entity processing enabled. As a result, the parsers are vulnerable to XXE attacks if an attacker can control the XML file that is processed.

**Noncompliant code example**

```javascript
var libxmljs = require('libxmljs');
var fs = require('fs');

var xml = fs.readFileSync('xxe.xml', 'utf8');

libxmljs.parseXmlString(xml, {
    noblanks: true,
```

**Compliant solution**

```javascript
parseXmlString is safe by default.

var libxmljs = require('libxmljs');
var fs = require('fs');

var xml = fs.readFileSync('xxe.xml', 'utf8');

libxmljs.parseXmlString(xml);
```

---

### javascript:S2819 — Origins should be verified during cross-origin communications

**Severity**: Blocker

When sending a message, avoid using * for the target origin (it means no preference). Instead define it explicitly so the message will only be dispatched to this URI. When receiving the message, verify the origin to be sure that it is sent by an authorized sender.

**Noncompliant code example**

```javascript
When sending a message:

var iframe = document.getElementById("testiframe");
```

**Compliant solution**

```javascript
When sending a message:

var iframe = document.getElementById("testiframe");

iframe.contentWindow.postMessage("hello", "https://secure.example.com");


When receiving a message:

window.addEventListener("message", function(event) {
  if (event.origin !== "http://example.org")
    return;

  console.log(event.data)
});
```

---

### javascript:S4423 — Weak SSL/TLS protocols should not be used

**Severity**: Blocker

| Trustworthy Which component or framework contains the issue?

**Noncompliant code example**

```javascript
import { aws_apigateway as agw } from 'aws-cdk-lib';
new agw.DomainName(this, 'Example', {
    certificate: certificate,
    domainName: domainName,
```

**Compliant solution**

```javascript
import { aws_apigateway as agw } from 'aws-cdk-lib';
new agw.DomainName(this, 'Example', {
    certificate: certificate,
    domainName: domainName,

    securityPolicy: agw.SecurityPolicy.TLS_1_2,

});

import { aws_opensearchservice as os } from 'aws-cdk-lib';

new os.CfnDomain(this, 'Example', {
  domainEndpointOptions: {
    enforceHttps: true,

    tlsSecurityPolicy: 'Policy-Min-TLS-1-2-2019-07',

  },

});
```

---

### javascript:S4426 — Cryptographic keys should be robust

**Severity**: Blocker

| Trustworthy Which component or framework contains the issue? The following code examples either explicitly or implicitly generate keys. Note that there are differences in the size of the keys depending on the algorithm. Due to the mathematical properties of the algorithms, the security requirements for the key size vary depending on the algorithm. For example, a 256-bit ECC key provides about the same level of security as a 3072-bit RSA key and a 128-bit symmetric key.

**Noncompliant code example**

```javascript
Here is an example of a private key generation with RSA:

const crypto = require('crypto');

function callback(err, pub, priv) {}

var { privateKey, publicKey } = crypto.generateKeyPairSync('rsa', {
```

**Compliant solution**

```javascript
Here is an example of a private key generation with RSA:

const crypto = require('crypto');

function callback(err, pub, priv) {}

var { privateKey, publicKey } = crypto.generateKeyPairSync('rsa', {

    modulusLength: 2048,

    publicKeyEncoding:  { type: 'spki', format: 'pem' },
    privateKeyEncoding: { type: 'pkcs8', format: 'pem' }
  },
  callback);


Here is an example of a key generation with the Digital Signature Algorithm (DSA):

const crypto = require('crypto');

function callback(err, pub, priv) {}

var { privateKey, publicKey } = crypto.generateKeyPairSync('dsa', {

    modulusLength: 2048,

    publicKeyEncoding:  { type: 'spki', format: 'pem' },
    privateKeyEncoding: { type: 'pkcs8', format: 'pem' }
  },
  callback);


Here is an example of an Elliptic Curve (EC) initialization. It implicitly generates a private key whose size is indicated in the elliptic curve name:
```

---

### javascript:S4830 — Server certificates should be verified during SSL/TLS connections

**Severity**: Blocker

| Trustworthy Which component or framework contains the issue? The following code contains examples of disabled certificate validation. The certificate validation gets disabled by setting rejectUnauthorized to false. To enable validation set the value to true or do not set rejectUnauthorized at all to use the secure default value.

**Noncompliant code example**

```javascript
const https = require('node:https');

let options = {
  hostname: 'www.example.com',
  port: 443,
  path: '/',
  method: 'GET',

  rejectUnauthorized: false,

  secureProtocol: 'TLSv1_2_method'
};

let req = https.request(options, (res) => {
  res.on('data', (d) => {
    process.stdout.write(d);
  });
```

**Compliant solution**

```javascript
const https = require('node:https');

let options = {
  hostname: 'www.example.com',
  port: 443,
  path: '/',
  method: 'GET',
  secureProtocol: 'TLSv1_2_method'
};

let req = https.request(options, (res) => {
  res.on('data', (d) => {
    process.stdout.write(d);
  });

});

const tls = require('node:tls');

let options = {
    secureProtocol: 'TLSv1_2_method'
};

let socket = tls.connect(443, "www.example.com", options, () => {
  process.stdin.pipe(socket);
  process.stdin.resume();

});
```

---

### javascript:S5527 — Server hostnames should be verified during SSL/TLS connections

**Severity**: Blocker

Which component or framework contains the issue? The following code contains examples of disabled hostname validation. The hostname validation gets disabled by overriding checkServerIdentity with an empty implementation. It is highly recommended to use the original implementation.

**Noncompliant code example**

```javascript
const https = require('node:https');

let options = {
  hostname: 'www.example.com',
  port: 443,
  path: '/',
  method: 'GET',
```

**Compliant solution**

```javascript
const https = require('node:https');

let options = {
  hostname: 'www.example.com',
  port: 443,
  path: '/',
  method: 'GET',
  secureProtocol: 'TLSv1_2_method'
};

let req = https.request(options, (res) => {
  res.on('data', (d) => {
    process.stdout.write(d);
  });
});

const tls = require('node:tls');

let options = {
  secureProtocol: 'TLSv1_2_method'
};

let socket = tls.connect(443, "www.example.com", options, () => {
  process.stdin.pipe(socket);
  process.stdin.resume();
});
```

---

### javascript:S5542 — Encryption algorithms should be used with secure mode and padding scheme

**Severity**: Blocker

| Trustworthy Which component or framework contains the issue?

**Noncompliant code example**

```javascript
Example with a symmetric cipher, AES:

const crypto = require('crypto');
```

**Compliant solution**

```javascript
Example with a symmetric cipher, AES:

const crypto = require('crypto');


crypto.createCipheriv("AES-256-GCM", key, iv);
```

---

### javascript:S5547 — Cipher algorithms should be robust

**Severity**: Blocker

| Trustworthy Which component or framework contains the issue? The following code contains examples of algorithms that are not considered highly resistant to cryptanalysis and thus should be avoided.

**Noncompliant code example**

```javascript
const crypto = require('crypto');
```

**Compliant solution**

```javascript
const crypto = require('crypto');


crypto.createCipheriv("AES-256-GCM", key, iv);
```

---

### javascript:S5659 — JWT should be signed and verified with strong cipher algorithms

**Severity**: Blocker

| Trustworthy Which component or framework contains the issue? jsonwebtoken The following code contains examples of JWT encoding and decoding without a strong cipher algorithm.

**Noncompliant code example**

```javascript
const jwt = require('jsonwebtoken');
```

**Compliant solution**

```javascript
const jwt = require('jsonwebtoken');


jwt.sign(payload, key, { algorithm: 'HS256' });

const jwt = require('jsonwebtoken');

jwt.verify(token, key, {
    expiresIn: 360000,

    algorithms: ['HS256']

}, callbackcheck);
```

---

### javascript:S5876 — A new session should be created during user authentication

**Severity**: Blocker

| Conventional Which component or framework contains the issue? Upon user authentication, it is crucial to regenerate the session identifier to prevent fixation attacks. Passport provides a mechanism to achieve this by using the req.session.regenerate() method. By calling this method after successful authentication, you can ensure that each user is assigned a new and unique session ID.

**Noncompliant code example**

```javascript
app.post('/login',
  passport.authenticate('local', { failureRedirect: '/login' }),
  function(req, res) {
```

**Compliant solution**

```javascript
app.post('/login',
  passport.authenticate('local', { failureRedirect: '/login' }),
  function(req, res) {

    let prevSession = req.session;
    req.session.regenerate((err) => {
      Object.assign(req.session, prevSession);
      res.redirect('/');
    });

  });
```

---

### javascript:S6317 — AWS IAM policies should limit the scope of permissions given

**Severity**: Blocker

| Conventional Which component or framework contains the issue? In this example, the IAM policy allows an attacker to update the code of any Lambda function. An attacker can achieve privilege escalation by altering the code of a Lambda that executes with high privileges.

**Noncompliant code example**

```javascript
import { aws_iam as iam } from 'aws-cdk-lib'

new iam.PolicyDocument({
    statements: [new iam.PolicyStatement({
        effect: iam.Effect.ALLOW,
        actions: ["lambda:UpdateFunctionCode"],
```

**Compliant solution**

```javascript
The policy is narrowed such that only updates to the code of certain Lambda functions (without high privileges) are allowed.

import { aws_iam as iam } from 'aws-cdk-lib'

new iam.PolicyDocument({
    statements: [new iam.PolicyStatement({
        effect: iam.Effect.ALLOW,
        actions: ["lambda:UpdateFunctionCode"],

        resources: ["arn:aws:lambda:us-east-2:123456789012:function:my-function:1"],

    })],
});
```

---

### javascript:S6437 — Credentials should not be hard-coded

**Severity**: Blocker

| Trustworthy Revoke the secret Revoke any leaked secrets and remove them from the application source code. Before revoking the secret, ensure that no other applications or processes are using it. Other usages of the secret will also be impacted when the secret is revoked. Analyze recent secret use When available, analyze authentication logs to identify any unintended or malicious use of the secret since its disclosure date. Doing this will allow determining if an attacker took advantage of the leaked secret and to what extent. This operation should be part of a global incident response process. Use a secret vault A secret vault should be used to generate and store the new secret. This will ensure the secret’s security and prevent any further unexpected disclosure. Depending on the...

**Noncompliant code example**

```javascript
const express = require('express');
const cookieParser = require('cookie-parser');

const app = express();
```

**Compliant solution**

```javascript
const express = require('express');
const cookieParser = require('cookie-parser');

const app = express();

const cookieSecret = process.env.SECRET;
app.use(cookieParser(cookieSecret));
```

---

### javascript:S7639 — Wallet phrases should not be hard-coded

**Severity**: Blocker

| Conventional Immediately generate a new wallet You cannot change the seed phrase for an existing wallet. A seed phrase is the master key from which all your wallet’s private keys are mathematically derived. Therefore, the correct procedure is not to "change" the phrase, but to move your funds to a new wallet with a new seed phrase. Then, transfer the assets from the old wallet to the new one. Store the phrase in a secure location Store this new backup in an extremely secure, offline location. Do not take a photo of it or store it on any internet-connected device. If you need to store it digitally, consider using a hardware wallet or a dedicated secret vault.

**Noncompliant code example**

```javascript
import { HDNodeWallet } from 'ethers'


const mnemonic = 'donate clutch sport betray purpose monitor lift blame slide spin crunch marriage'
```

**Compliant solution**

```javascript
import { HDNodeWallet } from 'ethers'


const mnemonic = process.env.SECRET
const mnemonicWallet = HDNodeWallet.fromPhrase(mnemonic)
```

---

### jssecurity:S2076 — OS commands should not be vulnerable to command injection attacks

**Severity**: Blocker

SonarArmor Jasmin (JavaScript) Which component or framework contains the issue? The following code is vulnerable to command injections because it is using untrusted inputs to set up a new process. Therefore an attacker can execute an arbitrary program that is installed on the system.

**Noncompliant code example**

```javascript
const { execSync } = require('child_process')



cmd = req.query.cmd
```

**Compliant solution**

```javascript
const { spawnSync } = require('child_process')



const cmdId = parseInt(req.query.cmdId)
let host = req.query.host
host = typeof host === "string"? host : "example.org"

const allowedCommands = [
    {exe:"/bin/ping", args:["-c","1","--"]},
    {exe:"/bin/host", args:["--"]}
]
const cmd = allowedCommands[cmdId]
spawnSync(cmd.exe, cmd.args.concat(host))
```

---

### jssecurity:S2083 — I/O function calls should not be vulnerable to path injection attacks

**Severity**: Blocker

SonarArmor Jasmin (JavaScript) Which component or framework contains the issue? The following code is vulnerable to path injection as it creates a path using untrusted data without validation. In this particular case, the code can be exploited with the following input to read arbitrary files outside of the intended directory: ../../../../

**Noncompliant code example**

```javascript
const path = require('path');

function (req, res) {
  const targetDirectory = "/data/app/resources/";

  const userFilename = path.join(targetDirectory, req.query.filename);
```

**Compliant solution**

```javascript
const path = require('path');

function (req, res) {
  const targetDirectory = "/data/app/resources/";

  const userFilename = req.query.filename;



  res.sendFile(userFilename, { root: targetDirectory });

}
```

---

### jssecurity:S2631 — Regular expressions should not be vulnerable to Denial of Service attacks

**Severity**: Blocker

SonarArmor Jasmin (JavaScript) Which component or framework contains the issue? The following noncompliant code is vulnerable to Regex Denial of Service (ReDoS) because untrusted data is used as a regex to scan a string without prior sanitization or validation.

**Noncompliant code example**

```javascript
const express = require('express');

const app = express();

app.get('/lookup', (req, res) => {
```

**Compliant solution**

```javascript
const express = require('express');

const escapeStringRegexp = require('escape-string-regexp');


const app = express();

app.get('/lookup', (req, res) => {

  const regex = RegExp(escapeStringRegexp(req.query.regex));


  if(regex.test(req.query.data)){
    res.send("It's a Match!");
  }else{
    res.send("Not a Match!");
  }
})
```

---

### jssecurity:S3649 — Database queries should not be vulnerable to injection attacks

**Severity**: Blocker

SonarArmor Jasmin (JavaScript) Which component or framework contains the issue? The following code is an example of an overly simple data retrieval function. It is vulnerable to SQL injection because user-controlled data is inserted directly into a query string: The application assumes that incoming data always has a specific range of characters and ignores that some characters may change the query logic to a malicious one. In this particular case, the query can be exploited with the following string: Using the UNION clause, an attacker would also be able to perform queries against other tables and combine the returned data within the same query result.

**Noncompliant code example**

```javascript
async function index(req, res) {
    const knex = req.app.get('knex');

    let loggedInUser = await knex('users')
```

**Compliant solution**

```javascript
async function index(req, res) {
    const knex = req.app.get('knex');

    let loggedInUser = await knex('users')

        .where('user', req.query.user)
        .where('pass', req.query.pass);


    res.send(JSON.stringify(loggedInUser));
    res.end();
}
```

---

### jssecurity:S5131 — Endpoints should not be vulnerable to reflected cross-site scripting (XSS) attacks

**Severity**: Blocker

SonarArmor Jasmin (JavaScript) Which component or framework contains the issue? The following code is vulnerable to cross-site scripting because it returns an HTML response that contains unsanitized user input. If you do not intend to send HTML code to clients, the vulnerability can be fixed by specifying the type of data returned in the response. For example, you can use the JsonResponse class to safely return JSON messages.

**Noncompliant code example**

```javascript
function (req, res) {

    json = JSON.stringify({ "data": req.query.input });
    res.send(json);

};
```

**Compliant solution**

```javascript
function (req, res) {

    res.json({ "data": req.query.input });

};


It is also possible to set the content-type header manually using the content_type parameter when creating an HttpResponse object.
```

---

### jssecurity:S5146 — HTTP request redirections should not be open to forging attacks

**Severity**: Blocker

SonarArmor Jasmin (JavaScript) Which component or framework contains the issue? The following noncompliant code example is vulnerable to open redirection as it constructs a URL with user-controllable data. This URL is then used to redirect the user without being first validated. An attacker can leverage this to manipulate users into performing unwanted redirects.

**Noncompliant code example**

```javascript
server.get('/redirect', (request, response) => {
```

**Compliant solution**

```javascript
server.get('/redirect', (request, response) => {

   const url = request.query.url;
   if (url.startsWith("https://www.example.com/")) {
      response.redirect(url);
   }

});
```

---

### jssecurity:S5147 — NoSQL operations should not be vulnerable to injection attacks

**Severity**: Blocker

SonarArmor Jasmin (JavaScript) Which component or framework contains the issue? The following code is vulnerable to a NoSQL injection because the database query is built using untrusted JavaScript objects that are extracted from user inputs. Here the application assumes the user-submitted parameters are always strings, while they might contain more complex structures. An array or dictionary input might tamper with the expected query behavior.

**Noncompliant code example**

```javascript
const { MongoClient } = require('mongodb');

function (req, res) {

    let query = { user: req.query.user, city: req.query.city };


    MongoClient.connect(url, (err, db) => {
        db.collection("users")
```

**Compliant solution**

```javascript
const { MongoClient } = require('mongodb');

function (req, res) {

    let query = { user: req.query.user.toString(), city: req.query.city.toString() };


    MongoClient.connect(url, (err, db) => {
        db.collection("users")

        .find(query)

        .toArray((err, docs) => { });
    });
}
```

---

### jssecurity:S5334 — Dynamic code execution should not be vulnerable to injection attacks

**Severity**: Blocker

SonarArmor Jasmin (JavaScript) Which component or framework contains the issue? The following code is vulnerable to arbitrary code execution because it builds a JavaScript code snippet from untrusted data. This piece of code is then used as an operand for a dangerous evaluation MongoDB operator. When performing a database query that way, the MongoDB server will interpret the JavaScript code as part of the data retrieval process. This might lead to arbitrary code execution on the database server.

**Noncompliant code example**

```javascript
const client = new MongoClient(mongoURI);
async function run() {
    const database = client.db('example');
    const products = database.collection('product');

    const query = { $where: `isString(this.${req.query.prop})`};
```

**Compliant solution**

```javascript
const client = new MongoClient(mongoURI);
async function run() {

    const allowed = ["name", "price", "stock"]

    let propId = req.query.propId

    const database = client.db('example');
    const products = database.collection('product');

    const query = { $where: `isString(this.${allowed[propId]})`};
    const product = await products.findOne(query);

}
run().catch(console.dir);
```

---

### jssecurity:S5696 — DOM updates should not lead to cross-site scripting (XSS) attacks

**Severity**: Blocker

SonarArmor Jasmin (JavaScript) Which component or framework contains the issue? The following code is vulnerable to DOM-based cross-site scripting because it uses unsanitized URL parameters to alter the DOM of its webpage. Because the user input is not sanitized here and the used DOM property is vulnerable to XSS, it is possible to inject arbitrary code in the user’s browser through this example.

**Noncompliant code example**

```javascript
The Element.innerHTML property is used to replace the contents of the root element with user-supplied contents. The innerHTML property does not sanitize its input, thus allowing for code injection.

const rootEl = document.getElementById('root');
const queryParams = new URLSearchParams(document.location.search);
const input = queryParams.get("input");
```

**Compliant solution**

```javascript
The HTMLElement.innerText property does not create DOM elements out of its input, rather treating its input as a string. This makes it a safe alternative to Element.innerHTML depending on the use case.

const rootEl = document.getElementById('root');
const queryParams = new URLSearchParams(document.location.search);
const input = queryParams.get("input");


rootEl.innerText = input;
```

---

### jssecurity:S6096 — Extracting archives should not lead to zip slip vulnerabilities

**Severity**: Blocker

SonarArmor Jasmin (JavaScript) Which component or framework contains the issue? The following code is vulnerable to Zip Slip as it is constructing a path using an archive entry name. This path is then used to copy a file without being validated first. Therefore, it can be leveraged by an attacker to overwrite arbitrary files.

**Noncompliant code example**

```javascript
const AdmZip = require("adm-zip");
const upload = require('multer');

app.get('/example', upload.single('file'), (req, res) => {
    const zip = new AdmZip(req.file.buffer);
    const zipEntries = zip.getEntries();

    zipEntries.forEach(function (zipEntry) {
```

**Compliant solution**

```javascript
const AdmZip = require("adm-zip");
const upload = require('multer');


const unzipTargetDir = "/example/directory/";


app.get('/example', upload.single('file'), (req, res) => {
    const zip = new AdmZip(req.file.buffer);
    const zipEntries = zip.getEntries();

    zipEntries.forEach(function (zipEntry) {

        const canonicalPath = path.normalize(unzipTargetDir + zipEntry.entryName);
        if (canonicalPath.startsWith(unzipTargetDir)) {
            let writer = fs.createWriteStream(canonicalPath);
            writer.write(zipEntry.getData().toString("utf8"));
        }

    });
});
```

---

### jssecurity:S6105 — DOM updates should not lead to open redirect vulnerabilities

**Severity**: Blocker

SonarArmor Jasmin (JavaScript) Which component or framework contains the issue? The following noncompliant code example is vulnerable to open redirection as it constructs a URL with user-controllable data. This URL is then used to redirect the user without being first validated. An attacker can leverage this to manipulate users into performing unwanted redirects.

**Noncompliant code example**

```javascript
The following example is vulnerable to open redirection through the following URL: https://example.com/redirect?url=https://evil.com;

const queryParams = new URLSearchParams(document.location.search);
const redirectUrl = queryParams.get("url");
```

**Compliant solution**

```javascript
const queryParams = new URLSearchParams(document.location.search);
const redirectUrl = queryParams.get("url");


if (redirectUrl.startsWith("https://www.example.com/")) {
    document.location = redirectUrl;
}
```

---

## 2. Reliability & Bug Prevention Rules (5 rules)

These rules detect patterns that cause runtime errors, async issues, and control flow defects.

### javascript:S1143 — Jump statements should not occur in "finally" blocks

**Severity**: Blocker

Having a jump statement (`return`, `break`, `continue`, or `throw`) inside a `finally` block can lead to unexpected behavior. If you use a `return` statement inside the `finally` block, it will override any previous return statements in the `try` or `catch` blocks. Jump statements in `finally` can also hide or suppress the original exception from `try` or `catch` blocks.

This rule reports on all usages of jump statements from a `finally` block.

**Noncompliant code example:**

```javascript
async function foo() {
    let result, connection;
    try {
        connection = await connect();
        result = connection.send(1);
    } catch(err) {
        console.error(err.message);
    } finally {
        if (connection) {
            connection.close();
        }
        return result; // Noncompliant: jump statement in finally
    }
}
```

**Compliant solution:**

```javascript
async function foo() {
    let result, connection;
    try {
        connection = await connect();
        result = connection.send(1);
    } catch(err) {
        console.error(err.message);
    } finally {
        if (connection) {
            connection.close();
        }
    }
    return result;
}
```

---

### javascript:S2189 — Loops should not be infinite

**Severity**: Blocker

A loop is a control structure that allows a block of code to be executed repeatedly until a certain condition is met. An infinite loop is a loop that runs indefinitely without ever terminating — the loop condition is always true, and the loop never exits. Infinite loops can cause a program to hang or crash.

This rule raises an issue on `for`, `while` and `do...while` loops where no clear exit condition has been found.

**Noncompliant code example:**

```javascript
for (;;) {  // Noncompliant: end condition omitted
  // ...
}

let j = 0;
while (true) { // Noncompliant: constant end condition
  j++;
}

let k;
let b = true;
while (b) { // Noncompliant: constant end condition
  k++;
}
```

**Compliant solution:**

```javascript
for (let i = 0; i < 5; i++) {
  // ...
}

let j = 0;
while (true) {
  j++;
  if (j < 5) {
    break;
  }
}

let k;
let b = true;
while (b) {
  k++;
  b = k < 10;
}
```

---

### javascript:S3516 — Function returns should not be invariant

**Severity**: Blocker

When a function has multiple return statements and returns the same value in more than one of them, it can lead to several potential problems: It can make the code more difficult to understand and maintain, as the reader may be unsure why the same value is being returned multiple times. This can introduce ambiguity and increase the chances of misunderstanding the function’s intent. The use of multiple return statements with the same value might lead someone to assume that each return corresponds to a distinct case or outcome. However, if they all return the same value, it can be misleading and may indicate an oversight or mistake in the code. When the function needs to be modified or extended in the future, having multiple identical return statements can make it harder to implement changes correctly across all occurrences. This can introduce bugs and inconsistencies in the codebase. Code readability is crucial for maintainability and collaboration. Having repetitive return statements can lead to unnecessary code duplication, which should be avoided in favor of creating modular and clean code. This often happens in functions that perform a conditional side effect but always return the same value. This rule raises an issue when a function contains several return statements that all return the same value.

**Noncompliant code example:**

```javascript
if (a < 0) {
    return false;
  }

  if (a > 10) {
    g(a); // side effect

    return false;

  }
  return false;
}


To address this, you should refactor the function to use a single return statement with a variable storing the value to be returned. This way, the code becomes more concise, easier to understand, and reduces the likelihood of introducing errors when making changes in the future. By using a single return point, you can also enforce consistency and prevent unexpected return values.

function f(a, g) {

  if (a > 10) {
    g(a); // side effect
  }
  return false;
}

```

---

### javascript:S4123 — "await" should only be used with promises

**Severity**: Blocker

type-dependent Promises are objects that represent the eventual completion or failure of an asynchronous operation. They provide a way to handle asynchronous operations in a more organized and manageable manner. To use await, you need to ensure that you are calling a function or an expression that returns a promise. The reason await should only be used on a promise is that it expects the operand to be a promise object. When you use await, it waits for the promise to be resolved or rejected and then returns the resolved value or throws the rejection reason, respectively. If the operand of await is not a promise, awaiting it is redundant and might not have been the developer’s intent. If you try to use await on a non-promise value, such as a regular object or a primitive type, it will not...

**await x; // Noncompliant: x is a number, not a promise**

```javascript
You should only use await on promises because it is designed to handle asynchronous operations and works in conjunction with the Promise API to provide a clean and intuitive way to write asynchronous code in JavaScript.

const x = Promise.resolve(42);
await x;


When calling a function that returns a promise as the last expression, you might forget to return it, especially if you refactored your code from a single-expression arrow function.

function foo() {

  Promise.resolve(42);

}
async function bar() {
```

---

### javascript:S7746 — Promise.resolve() and Promise.reject() should not be used in async functions or promise callbacks

**Severity**: Blocker

This rule raises an issue when Promise.resolve() or Promise.reject() are returned or yielded in async functions, async generators, or promise callback methods (then/catch/finally). In JavaScript, async functions and promise callback methods automatically wrap return values in promises. Using Promise.resolve() or Promise.reject() in these contexts creates unnecessary complexity and redundancy. When you return a value from an async function, it’s automatically wrapped in a resolved promise. Similarly, when you return from a .then(), .catch(), or .finally() callback, the value is automatically wrapped in a promise. For error handling, throwing an error is more idiomatic and clearer than returning Promise.reject(). The throw statement clearly indicates that an error condition has occurred,...

**  return Promise.resolve(result); // Noncompliant**

```javascript
};

Compliant code example
const fetchData = async () => {
  const result = await getData();

  return result;

};

Documentation
eslint-plugin-unicorn - Rule no-useless-promise-resolve-reject
MDN - async function - Comprehensive guide to async functions and their behavior
MDN - Promise.resolve() - Documentation for Promise.resolve() method
MDN - Using Promises - Guide to working with promises in JavaScript
```

---

## 3. Testing Quality Rules (4 rules)

These rules ensure test correctness and completeness.

### javascript:S2187 — Test files should contain at least one test case

**Severity**: Blocker

Adaptability Add test cases to the file or delete it if it isn’t needed anymore.

**Noncompliant code example**

```javascript
// eval.test.js


/* no test cases */
```

**Compliant solution**

```javascript
// eval.test.js


it('1 + 2 should give 3', () => {
    expect(1 + 2).toBe(3);
});
```

---

### javascript:S2699 — Tests should include assertions

**Severity**: Blocker

Adaptability

An assertion is a statement within the unit test that checks whether a particular condition is true or false. Without assertions, a unit test doesn't actually verify anything, making it ineffective in catching potential bugs or regressions. It will always pass, regardless of the implementation.

This rule raises an issue when one of the following assertion libraries is imported but no assertion is used in a test: chai, sinon, vitest, supertest.

**Noncompliant code example:**

```javascript
const expect = require("chai").expect;

describe("No assertions", function() {
    it("don't test anything", function() { // Noncompliant
        const str = "";
    });
});
```

**Compliant solution:**

```javascript
const expect = require("chai").expect;

describe("Assertions", function() {
    it("test something", function() {
        const str = "";
        expect(str).to.be.a("string");
    });
});
```

---

### javascript:S2970 — Assertions should be complete

**Severity**: Blocker

Adaptability

An incomplete assertion refers to a situation where an assertion is written but lacks some necessary components or conditions, making it insufficient to fully validate the expected behavior. This rule checks for incomplete assertions with Chai.js in the following cases:

- When `assert.fail`, `expect.fail` or `should.fail` are present but not called
- When an `expect(...)` or `should` assertion is not followed by an assertion method, such as `equal`
- When an `expect` or `should` assertion ends with a chainable getter (such as `.that`) or a modifier (such as `.deep`)
- When an `expect` or `should` assertion function (such as `.throw`) is not called

**Noncompliant code example:**

```javascript
const assert = require('chai').assert;
const expect = require('chai').expect;

describe("incomplete assertions", function() {
    const value = 42;

    it("uses chai 'assert'", function() {
        assert.fail; // Noncompliant: Missing the call to 'fail'
    });

    it("uses chai 'expect'", function() {
        expect(1 == 1); // Noncompliant: Should chain with 'to.equal'
        expect(value.toString).to.throw; // Noncompliant: Missing the type of the exception
    });
});
```

**Compliant solution:**

```javascript
const assert = require('chai').assert;
const expect = require('chai').expect;

describe("complete assertions", function() {
    const value = 42;

    it("uses chai 'assert'", function() {
        assert.fail();
    });

    it("uses chai 'expect'", function() {
        expect(1).to.equal(1);
        expect(value.toString).to.throw(TypeError);
    });
});
```

---

### javascript:S6079 — Tests should not execute any code after "done()" is called

**Severity**: Blocker

The `done` callback of Mocha is used to signal the end of an asynchronous test. It is important not to follow the `done` callback with code because the test may not have completed yet, and the code may execute before the test is finished. Since code after `done()` has no guarantee of running in the correct test context, it may be assigned to a different test, no test, or completely ignored.

**Noncompliant code example:**

```javascript
const expect = require("chai").expect;

describe(‘My test suite’, function() {
  it(‘should do something asynchronously’, function(done) {
    setTimeout(function() {
      expect(2 + 2).to.equal(4);
      expect(‘hello’).to.have.lengthOf(5);
      done();
      console.log(‘Test has completed.’); // Noncompliant: code after done()
    }, 1000);
  });
});
```

**Compliant solution:**

```javascript
const expect = require("chai").expect;

describe(‘My test suite’, function() {
  it(‘should do something asynchronously’, function(done) {
    setTimeout(function() {
      expect(2 + 2).to.equal(4);
      expect(‘hello’).to.have.lengthOf(5);
      console.log(‘Test has completed.’);
      done(); // done() is last
    }, 1000);
  });
});
```

---

## 4. Code Quality & Maintainability Rules (43 rules)

These rules detect complexity, naming, structural, and design anti-patterns.

### javascript:S1186 — Functions should not be empty

**Severity**: Blocker

**Noncompliant code example**

**Compliant solution**

```javascript
function shouldNotBeEmpty() {
  doSomething();

}


function notImplemented() {
  throw new Error("notImplemented() cannot be performed because ...");

}


function emptyOnPurpose() {
  // comment explaining why the method is empty

}
```

---

### javascript:S1219 — "switch" statements should not contain non-case labels

**Severity**: Blocker

Even if it is legal, mixing case and non-case labels in the body of a switch statement is very confusing and can even be the result of a typing error.

**Noncompliant code example**

```javascript
Case 1, the code is syntactically correct but the behavior is not the expected one

switch (day) {
  case MONDAY:
  case TUESDAY:
  WEDNESDAY:   // instead of "case WEDNESDAY"
    doSomething();
    break;
  ...
}


Case 2, the code is correct and behaves as expected but is hardly readable

switch (day) {
  case MONDAY:
    break;
  case TUESDAY:
    foo:for(i = 0 ; i < X ; i++) {
         /* ... */
        break foo;  // this break statement doesn't relate to the nesting case TUESDAY
         /* ... */
    }
    break;
    /* ... */
}
```

**Compliant solution**

```javascript
Case 1

switch (day) {
  case MONDAY:
  case TUESDAY:
  case WEDNESDAY:
    doSomething();
    break;
  ...
}


Case 2

switch (day) {
  case MONDAY:
    break;
  case TUESDAY:
    compute(args); // put the content of the labelled "for" statement in a dedicated method
    break;

    /* ... */
}
```

---

### javascript:S128 — Switch cases should end with an unconditional "break" statement

**Severity**: Blocker

When the execution is not explicitly terminated at the end of a switch case, it continues to execute the statements of the following case. While this is sometimes intentional, it often is a mistake which leads to unexpected behavior.

**Noncompliant code example**

```javascript
switch (myVariable) {
  case 1:
    foo();
    break;
  case 2:  // Both 'doSomething()' and 'doSomethingElse()' will be executed. Is it on purpose ?
    doSomething();
  default:
    doSomethingElse();
    break;
}
```

**Compliant solution**

```javascript
switch (myVariable) {
  case 1:
    foo();
    break;
  case 2:
    doSomething();
    break;
  default:
    doSomethingElse();
    break;
}
```

---

### javascript:S1314 — Octal values should not be used

**Severity**: Blocker

Integer literals starting with a zero are octal rather than decimal values. While using octal values is fully supported, most developers do not have experience with them. They may not recognize octal values as such, mistaking them instead for decimal values. Additionally, these literals will throw SyntaxError in strict mode. 0-prefixed octal literals have been deprecated since ECMAScript 5 and should not be used in modern JavaScript code.

**const myNumber = 010; // Noncompliant: Deprecated format**

```javascript
Use decimal syntax when possible as it is more readable.

const myNumber = 8;


If octal notation is required, use the standard syntax: a leading zero followed by a lowercase or uppercase Latin letter "O" (0o or 0O).

const myNumber = 0o10;
```

---

### javascript:S1527 — Future reserved words should not be used as identifiers

**Severity**: Blocker

The ECMAScript specification defines a set of special words as future keywords: `await`, `class`, `const`, `enum`, `export`, `extends`, `implements`, `import`, `interface`, `let`, `package`, `private`, `protected`, `public`, `static`, `super`, `yield`. Some are already adopted, others are reserved in strict mode. These future reserved words should be avoided as identifiers because they may cause syntax errors if ever adopted.

**Noncompliant code example:**

```javascript
var package = document.getElementsByName("foo"); // Noncompliant
var interface = 42; // Noncompliant
```

**Compliant solution:**

```javascript
var myPackage = document.getElementsByName("foo");
var myInterface = 42;
```

---

### javascript:S1994 — "for" loop increment clauses should modify the loops' counters

**Severity**: Blocker

It can be extremely confusing when a for loop’s counter is incremented outside of its increment clause. In such cases, the increment should be moved to the loop’s increment clause if at all possible.

**Noncompliant code example**

**Compliant solution**

```javascript
for (i = 0; i < 10; i++, j++) {
  // ...
}


Or

for (i = 0; i < 10; i++) {
  // ...
  j++;
}
```

---

### javascript:S2004 — Functions should not be nested too deeply

**Severity**: Blocker

brain-overload Adaptability

---

### javascript:S2430 — Constructor names should start with an upper case letter

**Severity**: Blocker

By convention, constructor function names should start with an upper case letter as a reminder that they should be called with the `new` keyword. A function is considered to be a constructor when it sets all of its arguments as object properties, and returns no value.

**Noncompliant code example:**

```javascript
function person (firstName, middleInitial, lastName) { // Noncompliant
  this.firstName = firstName;
  this.middleInitial = middleInitial;
  this.lastName = lastName;
}
```

**Compliant solution:**

```javascript
function Person (firstName, middleInitial, lastName) {
  this.firstName = firstName;
  this.middleInitial = middleInitial;
  this.lastName = lastName;
}

```

---

### javascript:S2703 — Variables should be declared explicitly

**Severity**: Blocker

Variable declaration is the process of creating a new variable and specifying its name. JavaScript provides three ways to declare variables: using the var, let, and const keywords. The var keyword is used to declare function-scoped or global-scoped variables, i.e. they are accessible throughout the function or the entire program, respectively. The let keyword is used to declare block-scoped variables, that is, variables accessible only within the nearest curly braces block where it is defined. The const keyword is used to declare variables that are constant, meaning their values cannot be reassigned. Explicitly declaring variables improves code readability and maintainability. It makes it clear to other developers that you are creating a new variable and sets expectations about its scope....

**  i = 1; // Noncompliant: i is global**

---

### javascript:S2871 — "Array.prototype.sort()" and "Array.prototype.toSorted()" should use a compare function

**Severity**: Blocker

type-dependent JavaScript provides built-in methods to sort arrays, making it convenient for developers to manipulate data. There are two primary ways to sort an array: Array.prototype.sort(): This method sorts the elements of an array in place and returns the sorted array. Array.prototype.toSorted(): This method is designed to return a new sorted array, leaving the original array unchanged. The default sort order is lexicographic (dictionary) order, based on the string representation of the elements. This means that when sorting an array of strings, numbers, or other elements, they are converted to strings and sorted according to their Unicode code points (UTF-16). For most cases, this default behavior is suitable when sorting an array of strings. However, it’s essential to be aware of...

**numbers.sort(); // Noncompliant: lexicographic sort**

```javascript
console.log(numbers); // Output: [1, 10, 2, 30, 5]


To sort numbers correctly, you must provide a custom comparison function that returns the correct ordering:

const numbers = [10, 2, 30, 1, 5];

numbers.sort((a, b) => a - b);
console.log(numbers); // Output: [1, 2, 5, 10, 30]


Even to sort strings, the default sort order may give unexpected results. Not only does it not support localization, it also doesn’t fully support Unicode, as it only considers UTF-16 code units. For example, in the code below, "eΔ" is surprisingly before and after "éΔ". To guarantee that the sorting is reliable and remains as such in the long run, it is necessary to provide a compare function that is both locale and Unicode aware - typically String.localeCompare.

const code1 = '\u00e9\u0394'; // "éΔ"
const code2 = '\u0065\u0301\u0394'; // "éΔ" using Unicode combining marks
const code3 = '\u0065\u0394'; // "eΔ"
```

---

### javascript:S3504 — Variables should be declared with "let" or "const"

**Severity**: Blocker

Variables declared with var are function-scoped, meaning they are accessible within the entire function in which they are defined. If a variable is declared using var outside of any function, it becomes a global variable and is accessible throughout the entire JavaScript program. let and const were introduced in ECMAScript 6 (ES6) as a block-scoped alternative to var. Variables declared with let have block scope, meaning they are limited to the block of code in which they are defined. A block is typically delimited by curly braces {}. Variables declared with const are also block-scoped, similar to let. However, const variables are immutable, meaning their value cannot be changed after assignment. This applies to the binding between the variable name and its value, but it does not mean the...

**var color = "blue"; // Noncompliant**

---

### javascript:S3735 — "void" should not be used

**Severity**: Blocker

type-dependent The void operator evaluates its argument and always returns undefined. void allows using any expression where an undefined is expected. However, using void makes code more difficult to understand, as the intent is often unclear.

**if (parameter === void 42) { // Noncompliant**

```javascript
// ...
}
```

---

### javascript:S3776 — Cognitive Complexity of functions should not be too high

**Severity**: Blocker

brain-overload Adaptability Reducing cognitive complexity can be challenging. Here are a few suggestions: Extract complex conditions in a new function. Mixed operators in condition will increase complexity. Extracting the condition in a new function with an appropriate name will reduce cognitive load. Break down large functions. Large functions can be hard to understand and maintain. If a function is doing too many things, consider breaking it down into smaller, more manageable functions. Each function should have a single responsibility. Avoid deep nesting by returning early. To avoid the nesting of conditions, process exceptional cases first and return early. Use null-safe operations (if available in the language). When available the .? or ?? operator replaces multiple tests and...

**Noncompliant code example**

```javascript
The code is using a complex condition and has a cognitive cost of 3.

function calculateFinalPrice(user, cart) {
  let total = calculateTotal(cart);

  if (user.hasMembership                       // +1 (if)
    && user.orders > 10                        // +1 (more than one condition)
    && user.accountActive
    && !user.hasDiscount
    || user.orders === 1) {                    // +1 (change of operator in condition)
      total = applyDiscount(user, total);

  }
  return total;
}
```

**Compliant solution**

```javascript
Even if the cognitive complexity of the whole program did not change, it is easier for a reader to understand the code of the calculateFinalPrice function, which now only has a cognitive cost of 1.

function calculateFinalPrice(user, cart) {
  let total = calculateTotal(cart);

  if (isEligibleForDiscount(user)) {       // +1 (if)
    total = applyDiscount(user, total);

  }
  return total;
}


function isEligibleForDiscount(user) {
  return user.hasMembership
    && user.orders > 10                     // +1 (more than one condition)
    && user.accountActive
    && !user.hasDiscount
    || user.orders === 1                    // +1 (change of operator in condition)
}


Break down large functions.
```

---

### javascript:S3785 — "in" should not be used with primitive types

**Severity**: Blocker

type-dependent

---

### javascript:S3796 — Callbacks of array methods should have return statements

**Severity**: Blocker

type-dependent

---

### javascript:S3812 — Parentheses should be used when negating "in" and "instanceof" operations

**Severity**: Blocker

Not being aware of JavaScript’s operator precedence rules can lead to unexpected results. For instance, `!key in dict` looks for a boolean value (`!key`) in `dict`, while `!(key in dict)` looks for a string and inverts the result. The same applies for `!obj instanceof SomeClass`. This rule raises an issue when the left operand of an `in` or `instanceof` operator is negated with `!`.

**Noncompliant code example:**

```javascript
if (!key in dict) { // Noncompliant: evaluates as (!key) in dict
  doTheThing();
}

if (!obj instanceof SomeClass) { // Noncompliant
  doOtherThing();
}
```

**Compliant solution:**

```javascript
if (!(key in dict)) {
  doTheThing();
}

if (!(obj instanceof SomeClass)) {
  doOtherThing();
}
```

---

### javascript:S3834 — "new" operator should not be used with Symbol and BigInt

**Severity**: Blocker

Using the `new` operator with `Symbol` and `BigInt` will throw a TypeError because they are not intended to be used as constructors. Unlike `String` or `Number`, `Symbol` and `BigInt` are primitive types introduced later in the language without constructor behavior.

**Noncompliant code example:**

```javascript
let foo = new Symbol('abc'); // Noncompliant: TypeError
let bar = new BigInt(123);   // Noncompliant: TypeError
```

**Compliant solution:**

```javascript
let foo = Symbol('abc');
let bar = BigInt(123);
```

---

### javascript:S3854 — "super()" should be invoked appropriately

**Severity**: Blocker

The `super()` call must be used carefully in class constructors:
- `super()` cannot be invoked in the constructor of a non-derived class
- `super()` must be invoked in the constructor of a derived class
- `super()` must be invoked before `this` and `super` keywords can be used
- `super()` can only be invoked in a constructor, not in any other method
- `super()` cannot be invoked multiple times in the same constructor

**Noncompliant code example:**

```javascript
class Dog extends Animal {
  constructor(name) {
    this.name = name; // Noncompliant: used ‘this’ before super()
    super();
    super.doSomething();
  }
}
```

**Compliant solution:**

```javascript
class Dog extends Animal {
  constructor(name) {
    super();
    this.name = name;
    super.doSomething();
  }
}
```

---

### javascript:S3972 — Conditionals should start on new lines

**Severity**: Blocker

Placing an `if` statement on the same line as the closing `}` from a preceding `if`/`else`/`else if` block can lead to confusion. It may indicate a missing `else` statement or create ambiguity for maintainers who might not understand the two statements are unconnected.

**Noncompliant code example:**

```javascript
if (condition1) {
  // ...
} if (condition2) {  // Noncompliant
  //...
}
```

**Compliant solution:**

```javascript
// Either separate them visually:
if (condition1) {
  // ...
}

if (condition2) {
  //...
}

// Or use else if if they are exclusive:
if (condition1) {
  // ...
} else if (condition2) {
  //...
}
```

---

### javascript:S4125 — "typeof" expressions should only be compared to valid values

**Severity**: Blocker

The `typeof` operator returns a limited set of strings: `"undefined"`, `"boolean"`, `"number"`, `"string"`, `"symbol"`, `"function"`, `"object"`, `"bigint"`. Comparing a `typeof` expression to anything else will always be `false`.

**Noncompliant code example:**

```javascript
function isNumber(x) {
  return typeof x === "Number"; // Noncompliant: should be "number"
}
```

**Compliant solution:**

```javascript
function isNumber(x) {
  return typeof x === "number";
}
```

---

### javascript:S4275 — Getters and setters should access the expected fields

**Severity**: Blocker

In classes with multiple fields, copy-paste errors can cause getters/setters to access the wrong field. This rule raises an issue when a setter does not update the corresponding field, or a getter does not access the corresponding field. Underscore prefixes are supported (`setX()` can assign to `_x`).

**Noncompliant code example:**

```javascript
class A {
  #y: number = 0;

  setY(val: number) { // Noncompliant: field '#y' is not updated
    this.#x = val;
  }
}
```

**Compliant solution:**

```javascript
class A {
  #y: number = 0;

  setY(val: number) {
    this.#y = val;
  }
}
```

---

### javascript:S4524 — "default" clauses should be last

**Severity**: Blocker

For readability purposes, the `default` clause should be at the beginning or the end of the `switch` statement. This rule raises an issue if the `default` clause is not the first or the last case.

**Noncompliant code example:**

```javascript
switch (param) {
  case 0:
    doSomething();
    break;
  default: // Noncompliant: default is not first or last
    error();
    break;
  case 1:
    doSomethingElse();
    break;
}
```

**Compliant solution:**

```javascript
switch (param) {
  case 0:
    doSomething();
    break;
  case 1:
    doSomethingElse();
    break;
  default:
    error();
    break;
}
```

---

### javascript:S5260 — Table cells should reference their headers

**Severity**: Blocker

accessibility If a <td> cell has a headers attribute, it should reference only IDs of headers in the same column and row. Note that it is usually better to use scope attributes of <th> headers instead of headers attribute. headers attribute requires you to list every corresponding <th> header’s id, which is error-prone and makes the code less maintainable. See W3C WAI Web Accessibility Tutorials for more information. If your table is too complex, it might be better to split it into multiple small tables as it improves both readability and maintainability. This rule raises an issue when the headers attribute of a <td> cell contains IDs which don’t belong to a header in the same row or column.

**Noncompliant code example**

```javascript
<table border="1">
<caption>
    Rental price
</caption>
<thead>
    <tr>
        <td></td>
        <th id="small" scope="col">
            Small car
        </th>
        <th id="big" scope="col">
            Big Car
        </th>
    </tr>
</thead>
<tbody>
    <tr>
        <th id="paris" class="span" colspan="3" scope="colgroup">
            Paris
        </th>
        </tr>
        <tr>
        <th headers="paris" id="day1">
            1 day
        </th>
```

---

### javascript:S5856 — Regular expressions should be syntactically valid

**Severity**: Blocker

type-dependent Skip to rules filters Quality Profiles Quality Gates Clear All Filters Software quality Security Hotspots Show Security Hotspots Only Available Since Security Category Quality Profile Prioritized Rules Regular expressions should be syntactically valid type-dependent Regular expressions have their own syntax that is understood by regular expression engines. Those engines will throw an exception at runtime if they are given a regular expression that does not conform to that syntax. To avoid syntax errors, special characters should be escaped with backslashes when they are intended to be matched literally and references to capturing groups should use the correctly spelled name or number of the group. To match a literal string, rather than a regular expression, either all...

**Noncompliant code example**

```javascript
new RegExp("([");
str.match("([");
```

**Compliant solution**

```javascript
new RegExp("\\(\\[");
str.match("\\(\\[");
str.replace("([", "{");
```

---

### javascript:S6859 — Imports should not use absolute paths

**Severity**: Blocker

Adaptability Replace the absolute path with one that is relative to your current file.

**Noncompliant code example**

```javascript
import { foo } from '/home/project/api/bar.js';
```

**Compliant solution**

```javascript
import { foo } from '../api/bar.js';
```

---

### javascript:S6861 — Mutable variables should not be exported

**Severity**: Blocker

Exporting mutable variables (`let`) can lead to unpredictable behavior. Use `const` for exported values, or encapsulate mutable state in a class or factory function.

**Noncompliant code example:**

```javascript
export let mutableVar = "initial value"; // Noncompliant
```

**Compliant solution:**

```javascript
export const immutableVar = "constant value";

// Or encapsulate mutable state:
class MyClass {
  constructor() {
    this.mutableVar = "initial value";
  }
}

export function createMyClass() {
  return new MyClass();
}
```

---

### javascript:S6958 — Literals should not be used as functions

**Severity**: Blocker

Calling a literal throws a TypeError, and is likely the result of an unintentional error in the code. This rule raises an issue when an attempt is made to use a literal as a function or tag function.

**Noncompliant code example:**

```javascript
let x = "hello"(); // Noncompliant: string literal used as function
let y = 42();      // Noncompliant: number literal used as function
let z = true`template`; // Noncompliant: literal used as tag function
```

---

### javascript:S7059 — Constructors should not contain asynchronous operations

**Severity**: Blocker

Constructors should not be asynchronous because they are meant to initialize an instance synchronously. The instance will be returned before the asynchronous operation completes, which can lead to issues if code expects the object to be fully initialized. Returning a promise from a constructor leads to unexpected results with inheritance and `instanceof`.

**Noncompliant code example:**

```javascript
class MyClass {
  constructor() {
    this.data = await fetchData(); // Noncompliant: async in constructor
  }
}
```

**Compliant solution:**

```javascript
// Option 1: Use an async initialization method
class MyClass {
  constructor() {
    this.data = null;
  }

  async initialize() {
    this.data = await fetchData();
  }
}

(async () => {
  const myObject = new MyClass();
  await myObject.initialize();
})();

// Option 2: Use a static factory method
class MyClass {
  constructor(data) {
    this.data = data;
  }

  static async create() {
    const data = await fetchData();
    return new MyClass(data);
  }
}

(async () => {
  const myObject = await MyClass.create();
})();
```
```

---

### javascript:S7724 — ESLint disable comments should specify which rules to disable

**Severity**: Blocker

This rule raises an issue when ESLint disable comments (eslint-disable, eslint-disable-line, or eslint-disable-next-line) are used without specifying which rules to disable. ESLint disable comments allow developers to suppress linting warnings and errors in specific parts of their code. While this can be useful for legitimate cases where a rule doesn’t apply, using blanket disable comments without specifying rules creates several problems. When you use /* eslint-disable / without naming specific rules, you disable *all ESLint rules for that section of code. This means that if new issues are introduced later - like undefined variables, syntax errors, or security vulnerabilities - they won’t be reported by ESLint. Blanket disables also make code reviews less effective. When reviewers see //...

**const unusedVar = 'test'; // Noncompliant**

```javascript
Compliant code example
/* eslint-disable no-console, no-unused-vars */

console.log('Debug message');

const unusedVar = 'test';

Documentation
eslint-plugin-unicorn - Rule no-abusive-eslint-disable
ESLint - Disabling Rules - Official ESLint documentation on how to disable rules with comments
ESLint - Configuring ESLint - Complete guide to ESLint configuration including ignoring files
```

---

### javascript:S7725 — Getters and setters should not recursively access the same property

**Severity**: Blocker

Skip to rules filters Quality Profiles Quality Gates Clear All Filters Software quality Security Hotspots Show Security Hotspots Only Available Since Security Category Quality Profile Prioritized Rules Getters and setters should not recursively access the same property This rule raises an issue when a getter or setter method recursively accesses the same property it defines, which causes infinite recursion. When a getter or setter method accesses the same property it defines, it creates infinite recursion that leads to a stack overflow error. For example, when you write get bar() { return this.bar; }, calling the getter triggers itself repeatedly because this.bar invokes the same getter method. This creates an endless loop that consumes all available stack memory. The same problem occurs...

**    return this.name; // Noncompliant**

```javascript
},
  set name(value) {
```

---

### javascript:S7727 — Function references should not be passed directly to iterator methods

**Severity**: Blocker

This is an issue when passing a function reference directly to array iterator methods like map, forEach, filter, find, some, every, reduce, reduceRight, or flatMap. Array iterator methods in JavaScript pass multiple arguments to their callback functions: the current element, the index, and the entire array. When you pass a function reference directly to these methods, the function receives all these arguments, not just the element. This can cause unexpected behavior in two scenarios: Function signature changes: If the referenced function is later modified to accept additional parameters, it may start using the index or array arguments unintentionally, leading to different behavior. Unintended parameter usage: The function might already accept multiple parameters for other purposes,...

**const result = numbers.map(parseInt); // Noncompliant**

```javascript
Compliant code example
const numbers = [1, 2, 3];

const result = numbers.map(element => parseInt(element));

Documentation
eslint-plugin-unicorn - Rule no-array-callback-reference
MDN - Array.prototype.map() - Documentation for the map method and its callback parameters
MDN - Array iteration methods - Overview of all array iteration methods and their callback signatures
```

---

### javascript:S7739 — Objects should not have a "then" property

**Severity**: Blocker

Skip to rules filters Quality Profiles Quality Gates Clear All Filters Software quality Security Hotspots Show Security Hotspots Only Available Since Security Category Quality Profile Prioritized Rules Objects should not have a "then" property This rule raises an issue when an object, class, or module defines a property or method named then. JavaScript treats objects with a then property as "thenable" - similar to Promises. This can cause unexpected behavior when these objects are used with await expressions or dynamic imports. When JavaScript encounters an object with a then property in an await expression, it assumes the object is Promise-like and tries to resolve it. This can lead to: Code execution being suspended indefinitely if the then method doesn’t behave like a Promise...

**  then() { // Noncompliant**

```javascript
console.log('Action completed');
  }
};

Compliant code example
const userAction = {
  userId: 123,

  complete() {

    console.log('Action completed');
  }
};

Documentation
eslint-plugin-unicorn - Rule no-thenable
MDN - Promise Resolution - Explains how JavaScript resolves thenable objects
MDN - await operator - Documentation on how await handles thenable objects
MDN - Dynamic imports - Information about dynamic import behavior with thenable modules
```

---

### javascript:S7740 — Variables should not be assigned the value of "this"

**Severity**: Blocker

This rule raises an issue when this is assigned to a variable. Assigning this to a variable is an outdated JavaScript pattern that creates unnecessary complexity and reduces code readability. In JavaScript, the value of this depends on how a function is called. Before ES6, developers commonly assigned this to a variable (like self, that, or foo) to preserve the context when calling functions where this would have a different value. This pattern has several drawbacks: It creates additional variables that clutter the scope It can cause confusion about which context is being referenced It makes the code harder to understand and maintain It’s prone to errors if the wrong variable is used Modern JavaScript provides better alternatives that eliminate the need for this pattern. Arrow functions...

**	foo.bar(); // Noncompliant**

```javascript
}, 1000);

Compliant code example
setTimeout(() => {
	this.bar();

}, 1000);

Documentation
eslint-plugin-unicorn - Rule no-this-assignment
MDN - Arrow Functions - Comprehensive guide to arrow functions and lexical this binding
MDN - Function.prototype.bind() - Documentation for the bind() method to explicitly set function context
MDN - this keyword - Complete reference for understanding this binding in JavaScript
```

---

### javascript:S7761 — Data attributes should be accessed using ".dataset"

**Severity**: Blocker

| Conventional Skip to rules filters Quality Profiles Quality Gates Clear All Filters Software quality Security Hotspots Show Security Hotspots Only Available Since Security Category Quality Profile Prioritized Rules Data attributes should be accessed using ".dataset" | Conventional This rule raises an issue when getAttribute(), setAttribute(), removeAttribute(), or hasAttribute() are used with data attributes (attributes starting with data-). The .dataset property provides a cleaner, more semantic way to work with HTML data attributes compared to generic attribute methods. Data attributes are a special category of HTML attributes designed to store custom data. The browser provides the .dataset API specifically for this purpose, which offers several advantages: Cleaner syntax:...

**const value = element.getAttribute('data-user-name'); // Noncompliant**

```javascript
Compliant code example
const value = element.dataset.userName;
// or with destructuring
const {userName} = element.dataset;

Documentation
eslint-plugin-unicorn - Rule prefer-dom-node-dataset
MDN: HTMLElement.dataset - Official documentation for the dataset API
MDN: Using data attributes - Guide on using HTML data attributes effectively
```

---

### javascript:S7767 — Bitwise operators should not be used to truncate numbers

**Severity**: Blocker

Using bitwise operators like `| 0`, `~~`, `>> 0`, `<< 0`, or `^ 0` to truncate numbers is a common hack but creates problems: the intent is unclear, and they only work correctly for numbers within the 32-bit signed integer range (-2,147,483,648 to 2,147,483,647).

**Noncompliant code example:**

```javascript
const result = value | 0; // Noncompliant
const truncated = ~~value; // Noncompliant
```

**Compliant solution:**

```javascript
const result = Math.trunc(value);
```

---

### javascript:S7768 — Modern DOM manipulation methods should be used instead of legacy alternatives

**Severity**: Blocker

Legacy DOM manipulation methods like `replaceChild()`, `insertBefore()`, `insertAdjacentText()`, or `insertAdjacentElement()` require more verbose code and often need unnecessary parent node traversal. Modern equivalents are cleaner and more readable.

**Noncompliant code example:**

```javascript
parentNode.replaceChild(newElement, oldElement); // Noncompliant
parentNode.insertBefore(newElement, referenceElement); // Noncompliant
```

**Compliant solution:**

```javascript
oldElement.replaceWith(newElement);
referenceElement.before(newElement);
```

---

### javascript:S7774 — Methods should be accessed from prototypes, not instances

**Severity**: Blocker

Accessing methods from empty instances like `[]` or `{}` is less clear and less efficient than accessing directly from the prototype. `Array.prototype.slice.apply()` makes intent crystal clear compared to `[].slice.apply()`.

**Noncompliant code example:**

```javascript
const array = [].slice.apply(arrayLike); // Noncompliant
const hasOwn = {}.hasOwnProperty.call(obj, ‘key’); // Noncompliant
```

**Compliant solution:**

```javascript
const array = Array.prototype.slice.apply(arrayLike);
const hasOwn = Object.prototype.hasOwnProperty.call(obj, ‘key’);
```

---

### javascript:S7783 — "trimLeft()" and "trimRight()" should be replaced with "trimStart()" and "trimEnd()"

**Severity**: Blocker

`trimLeft()` and `trimRight()` are deprecated aliases for `trimStart()` and `trimEnd()`. They exist only for backward compatibility and may be removed in future JavaScript versions.

**Noncompliant code example:**

```javascript
const leftTrimmed = text.trimLeft(); // Noncompliant
const rightTrimmed = text.trimRight(); // Noncompliant
```

**Compliant solution:**

```javascript
const leftTrimmed = text.trimStart();
const rightTrimmed = text.trimEnd();
```

---

### javascript:S888 — Equality operators should not be used in "for" loop termination conditions

**Severity**: Blocker

Testing for loop termination using an equality operator (`==` and `!=`) is dangerous, because it could set up an infinite loop. Using a broader relational operator instead casts a wider net, and makes it harder to accidentally write an infinite loop.

**Noncompliant code example:**

```javascript
for (var i = 1; i != 10; i += 2) { // Noncompliant: i goes 1,3,5,7,9,11... never == 10
  //...
}
```

**Compliant solution:**

```javascript
for (var i = 1; i < 10; i += 2) {
  //...
}
```

**Exceptions:** Equality operators are ignored when the loop counter starts below the ending value and increments by 1, or when the test is against `null`.

---

### javascript:S930 — Function calls should not pass extra arguments

**Severity**: Blocker

When you call a function in JavaScript and provide more arguments than the function expects, the extra arguments are simply ignored. This can obscure the function’s intended use and lead to unexpected behavior.

**Noncompliant code example:**

```javascript
function sum(a, b) {
  return a + b;
}

sum(1, 2, 3); // Noncompliant: extra argument ‘3’ is ignored
```

**Compliant solution:**

```javascript
function sum(...args) {
  return args.reduce((a, b) => a + b, 0);
}

sum(1, 2, 3); // All arguments are handled
```

---

### jsarchitecture:S7788 — Relationships should align with the intended architecture

**Severity**: Blocker

Sonar Architecture (JavaScript) architecture Adaptability Remove or refactor the deviating dependency. This may involve replacing the dependency with an allowed one, moving code to appropriate files or directories, or introducing new abstractions. The exact solution depends on your project’s specific situation and the code deviating the intended architecture.

**Noncompliant code example**

```javascript
If the intended architecture prohibits files in directory panels to depend on files in repos, then the following code example is noncompliant:

// panels/ShowCustomersPanel.js


import { CustomerRepo } from '../repos/CustomerRepo.js';


export class ShowCustomersPanel {
  constructor() {

    this.customerRepo = ...;
    this.customers = this.customerRepo.findAll();

  }
}
```

**Compliant solution**

```javascript
A solution could be to call into the service layer instead.

// panels/ShowCustomersPanel.js


import { CustomerService } from '../services/CustomerService.js';


export class ShowCustomersPanel {
  constructor() {

    this.customerService = ...;
    this.customers = this.customerService.getAllCustomers();

  }
}
```

---

### jsarchitecture:S7789 — Files should be located according to the intended architecture

**Severity**: Blocker

Sonar Architecture (JavaScript) architecture Adaptability Move the relevant file to its intended location or rename the relevant directory as intended.

**Noncompliant code example**

```javascript
If the intended architecture declares developers should use the directory name ./panel, not ./panels, then the following code example is noncompliant:

// panels/ShowCustomersPanel.js


export class ShowCustomersPanel {
  // ...
}
```

**Compliant solution**

```javascript
The solution is to move the file to its appropriate directory, or respectively, to rename the directory panels to panel.

// panel/ShowCustomersPanel.js


export class ShowCustomersPanel {
  // ...
}
```

---

### jsarchitecture:S8134 — Forbidden relationships should be removed to solve tangles as directed by the project's architect

**Severity**: Blocker

Sonar Architecture (JavaScript) architecture Adaptability Remove or refactor the problematic dependency. This may involve replacing the dependency with an allowed one, moving code to appropriate files or folders, or introducing new abstractions. The exact solution depends on your project’s specific situation.

**Noncompliant code example**

```javascript
The following code contains a circular dependency: order.js → customer.js → order.js, and order.js → product.js → order.js. Both cycles are connected through order.js, forming a tangle of two cycles.

// order.js
import { Customer } from './customer.js';
import { Product } from './product.js';

export class Order {
    constructor() {
        this.customer = new Customer();
        this.products = [];
    }
}

// customer.js

import { Order } from './order.js';



export class Customer {
    constructor() {
        this.orders = [];
    }
}


// product.js

import { Order } from './order.js';



export class Product {
```

**Compliant solution**

```javascript
The issue can be resolved by refactoring the structure. Two service functions can replace the dependencies customer.js → order.js and product.js → order.js.

// order.js
import { Customer } from './customer.js';
import { Product } from './product.js';

export class Order {
    constructor() {
        this.customer = new Customer();
        this.products = [];
    }
}

// customer.js

export class Customer { }


// product.js

export class Product { }



// orderService.js
export function getOrdersByCustomer(customer) {
    // Implementation to get orders by customer

}


export function getOrdersByProduct(product) {
    // Implementation to get orders by product
```

---

