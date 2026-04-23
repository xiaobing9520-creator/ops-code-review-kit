# SonarQube JavaScript Review Standards

This rule defines the SonarQube-based JavaScript/TypeScript code review criteria.
Apply these standards when the target project contains JavaScript or TypeScript
source code. Rules are sourced from SonarQube's JavaScript analyzer and organized
by review category.

Each rule includes its SonarQube rule key, severity, explanation, and
Noncompliant/Compliant code examples to guide pattern matching during review.

**Total: 259 rules (77 Blocker, 182 Medium)**

## Severity System

This file uses SonarQube's **MQR (Multi-Quality Rule)** severity system.
Rules in this file cover Blocker, High, and Medium severity levels.

| Severity in This File | Report Severity | Required Action |
|-----------------------|-----------------|-----------------|
| **Blocker** | Critical | Must fix before release (P0) |
| **High** | High | Must fix or have documented mitigation (P0/P1) |
| **Medium** | Medium | Assign P0–P3; P0 blocks release |

### Important Notes on Severity

- When reporting findings, map severity to report labels as shown above:
  Blocker → Critical, High → High, Medium → Medium.
- Do NOT use legacy SonarQube labels (Major, Minor, Info).
- Do NOT override severities with values from external sources or general
  knowledge of SonarQube rules.
- Medium-severity issues MUST be assigned a fix priority (P0–P3).

### SonarQube Classification Note

Some rules in this file correspond to what SonarQube classifies as **Security
Hotspots** rather than traditional Bugs or Vulnerabilities. In SonarQube's
web interface, Security Hotspot rules do not display a traditional severity
level — they require manual review instead. In this file, we assign a severity
based on the organization's risk assessment.

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


---

# Medium-Severity Rules

The following rules are classified as **Medium** severity in the
organization's SonarQube quality profile. Medium-severity issues
MUST be assigned a fix priority (P0–P3). A Medium issue rated P0
will cause the quality gate to **Fail**.

## 10. Security Rules — Medium (3 rules)

### jssecurity:S5144 — Server-side requests should not be vulnerable to forging attacks

**Severity**: Medium

Server-Side Request Forgery (SSRF) occurs when attackers can coerce a server to perform arbitrary requests on their behalf.

**Noncompliant code example**

```javascript
const axios = require('axios');
const express = require('express');

const app = express();

app.get('/example', async (req, res) => {
    try {
        await axios.get(req.query.url); // Noncompliant
        res.send("OK");
    } catch (err) {
        console.error(err);
        res.send("ERROR");
    }
})
```

**Compliant solution**

```javascript
const axios = require('axios');
const express = require('express');

const schemesList = ["http:", "https:"];
const domainsList = ["trusted1.example.com", "trusted2.example.com"];

app.get('/example', async (req, res) => {
    const url = (new URL(req.query.url));

    if (schemesList.includes(url.protocol) && domainsList.includes(url.hostname)) {
        try {
            await axios.get(url);
            res.send("OK");
        } catch (err) {
            console.error(err);
            res.send("ERROR");
        }
    }else {
        res.send("INVALID_URL");
    }
})
```

---

### jssecurity:S6287 — Applications should not create session cookies from untrusted input

**Severity**: Medium

Session Cookie Injection occurs when a web application assigns session cookies to users using untrusted data.

**Noncompliant code example**

```javascript
import express from "express";
import cookieParser from "cookie-parser";

const app = express();
app.use(cookieParser());

app.get("/checkcookie", (req, res) => {
    if (req.cookies["connect.sid"] === undefined) {
        const cookie = req.query.cookie;
        res.cookie("connect.sid", cookie); // Noncompliant
    }

    return res.redirect("/welcome");
});
```

**Compliant solution**

```javascript
import express from "express";
import cookieParser from "cookie-parser";

const app = express();
app.use(cookieParser());

app.get("/checkcookie", (req, res) => {
    if (req.cookies["connect.sid"] === undefined) {
        return res.redirect("/getcookie");
    }

    return res.redirect("/welcome");
});
```

---

### jssecurity:S7044 — Server-side requests should not be vulnerable to traversing attacks

**Severity**: Medium

Path Traversal Server-Side Request Forgery is a sub-class of Server-Side Request Forgery (SSRF). In this type of attack, the attacker manipulates
the path of the URL in the server-side request, rather than controlling the entire URL. This can lead to unauthorized access to endpoints or data by
altering the request path.

**Noncompliant code example**

```javascript
const axios = require('axios');
const express = require('express');

const app = express();

app.get('/example', async (req, res) => {
    const id = req.query.id;

    try {
        await axios.get(`https://example.com/user/${id}`); // Noncompliant
        res.send("OK");
    } catch (err) {
        console.error(err);
        res.send("ERROR");
    }
})
```

**Compliant solution**

```javascript
const axios = require('axios');
const express = require('express');

const app = express();

app.get('/example', async (req, res) => {
    const id = encodeURIComponent(req.query.id);

    try {
        await axios.get(`https://example.com/user/?id=${id}`);
        res.send("OK");
    } catch (err) {
        console.error(err);
        res.send("ERROR");
    }
})
```

---

## 11. Reliability & Bug Prevention Rules — Medium (8 rules)

### javascript:S2688 — "NaN" should not be used in comparisons

**Severity**: Medium

In JavaScript, 
`NaN`
 stands for "Not-a-Number." It is a special value representing a numeric data type that is not a valid number.

---

### javascript:S3696 — Literals should not be thrown

**Severity**: Medium

In JavaScript, throwing literals (primitive values like strings, numbers, booleans, etc.) as exceptions is generally discouraged. While it is
syntactically valid to throw literals, it is considered a best practice to throw instances of the 
`Error`
 class or its subclasses
instead.

---

### javascript:S6544 — Promises should not be misused

**Severity**: Medium

Promises need to be resolved or awaited to return the expected value, otherwise, they return the promise object.

**Noncompliant code example**

```javascript
(async function foo() {
  const result = await bar();
  // work with result
})();
```

**Compliant solution**

```javascript
const promise = new Promise((resolve, reject) => {
  // ...
  resolve(false)
});
if (promise) {
  // ...
}
```

---

### javascript:S6679 — "Number.isNaN()" should be used to check for "NaN" value

**Severity**: Medium

Comparing the value to itself may be either a refactoring error or an outdated way of checking if the value is of a numeric data type but not a
valid number. This special numeric value is represented by 
`NaN`
 global property, where 
`NaN`
 stands for "Not-a-Number".

---

### javascript:S6671 — Literals should not be used for promise rejection

**Severity**: Medium

The use of literals (primitive values such as strings, numbers, booleans, etc.) for promise rejection is generally discouraged. While it is
syntactically valid to provide literals as a rejected promise value, it is considered best practice to use instances of the Error class or its
subclasses instead.

---

### javascript:S4634 — Shorthand promises should be used

**Severity**: Medium

In JavaScript, a promise is an object representing the eventual completion or failure of an asynchronous operation. It is a way to handle
asynchronous operations more elegantly and avoid the "callback hell".

**Noncompliant code example**

```javascript
const result = Promise.resolve(42);
result.then(value => {
  console.log(value); // Output: 42
});
```

**Compliant solution**

```javascript
const error = new Error('Something went wrong');
const promise = Promise.reject(error);
```

---

### javascript:S3984 — Errors should not be created without being thrown

**Severity**: Medium

Errors should not be created without being thrown because they can confuse and make it difficult to debug code. When an error is thrown, it means
that something unexpected has happened, and the program cannot continue executing as expected. By creating an error without throwing it, it may appear
as if everything is working correctly, but in reality, an underlying issue must be addressed.

```

if (x < 0) {
  new Error("x must be nonnegative"); // Noncompliant: Creating an error without throwing it
}

```

You should make sure to always throw an error that you create using the 
`throw`
 keyword.

```

if (x < 0) {
  throw new Error("x must be nonnegative");
}

```

---

### javascript:S4822 — Promise rejections should not be caught by "try" blocks

**Severity**: Medium

An exception thrown inside a promise will not be caught by a nesting 
`try`
 block due to the asynchronous nature of execution.

---

## 12. Testing Quality Rules — Medium (11 rules)

### javascript:S6523 — Optional chaining should not be used if returning "undefined" throws an error

**Severity**: Medium

The optional chaining operator 
`?.`
 allows to access a deeply nested property, returning 
`undefined`
 if the property or any
intermediate object is 
`undefined`
.

**Noncompliant code example**

```javascript
(event?.callback ?? defaultCallback)();
```

**Compliant solution**

```javascript
(event?.callback || defaultCallback)();
```

---

### javascript:S6582 — Optional chaining should be preferred

**Severity**: Medium

Optional chaining allows to safely access nested properties or methods of an object without having to check for the existence of each intermediate
property manually. It provides a concise and safe way to access nested properties or methods without having to write complex and error-prone

`null`
/
`undefined`
 checks.

This rule flags logical operations that can be safely replaced with the 
`?.`
 optional chaining operator.

**Noncompliant code example**

```javascript
function foo(obj, arr, fn) {
    if (obj && obj.value) {}
    if (arr && arr[0])    {}
    if (fn && fn(42))     {}
}
```

**Compliant solution**

```javascript
function foo(obj, arr, fn) {
    if (obj?.value) {}
    if (arr?.[0])   {}
    if (fn?.(42))   {}
}
```

---

### javascript:S6426 — Exclusive tests should not be committed to version control

**Severity**: Medium

When using testing frameworks like Mocha and Jest, appending 
`.only()`
 to the test function allows running a single test case for a
file. Using 
`.only()`
 means no other test from this file is executed. This is useful when debugging a specific use case.

```

describe("MyClass", function () {
    it.only("should run correctly", function () { // Noncompliant
        /*...*/
    });
});

```

However, it should not be used in production or development, as it is likely a leftover from debugging and serves no purpose in those contexts. It
is strongly recommended not to include 
`.only()`
 usages in version control.

```

describe("MyClass", function () {
    it("should run correctly", function () {
        /*...*/
    });
});

```

---

### javascript:S5863 — Assertions should not be given twice the same argument

**Severity**: Medium

Assertions are statements that check whether certain conditions are true. They are used to validate that the actual results of a code snippet match
the expected outcomes. By using assertions, developers can ensure that their code behaves as intended and identify potential bugs or issues early in
the development process.

---

### javascript:S5973 — Tests should be stable

**Severity**: Medium

Unstable / flaky tests are tests which sometimes pass and sometimes fail, without any code change. Obviously, they slow down developments when
developers have to rerun failed tests. However, the real problem is that you can’t completely trust these tests, they might fail for many different
reasons and you don’t know if any of them will happen in production.

Some tools, such as Jest, enable developers to automatically retry flaky tests. This might be acceptable as a temporary solution, but it should
eventually be fixed. The more flaky tests you add, the more chances there are for a bug to arrive in production.

This rule raises an issue when these functions are called with a value higher than 
`0`
: * 
`jest.retry()`
 *

`this.retries()`
 inside a Mocha test case

**Noncompliant code example**

```javascript
jest.retryTimes(3); // Noncompliant

describe('API.foo()', function() {
  it('should return 5 when computing ...', function() {
    doSomethingUnstable();
  });
});
```

---

### javascript:S3415 — Assertion arguments should be passed in the correct order

**Severity**: Medium

Assertions are statements that check whether certain conditions are true. They are used to validate that the actual results of a code snippet match
the expected outcomes. By using assertions, developers can ensure that their code behaves as intended and identify potential bugs or issues early in
the development process.

**Noncompliant code example**

```javascript
const assert = require('chai').assert;
const expect = require('chai').expect;
const should = require('chai').should();

it("inverts arguments", function() {
    assert.equal(42, aNumber); // Noncompliant: actual value is passed as first argument and expected as second argument
    expect(42).to.equal(aNumber); // Noncompliant: actual value is passed as first argument and expected as second argument
    should.fail(42, aNumber);  // Noncompliant: actual value is passed as first argument and expected as second argument
});
```

**Compliant solution**

```javascript
const assert = require('chai').assert;
const expect = require('chai').expect;
const should = require('chai').should();

it("inverts arguments", function() {
    assert.equal(aNumber, 42);
    expect(aNumber).to.equal(42);
    should.fail(aNumber, 42);
});
```

---

### javascript:S5958 — Tests should check which exception is thrown

**Severity**: Medium

Assertions are statements that check whether certain conditions are true. They are used to validate that the actual results of a code snippet match
the expected outcomes. By using assertions, developers can ensure that their code behaves as intended and identify potential bugs or issues early in
the development process.

---

### javascript:S6080 — Disabling Mocha timeouts should be explicit

**Severity**: Medium

Setting timeouts with Mocha allows you to control the maximum time a test case or suite can take to execute. However, incorrect usage or excessive
timeout values can lead to undesired consequences and impact the effectiveness of your test suite. For example, setting a timeout by calling

---

### javascript:S6092 — Chai assertions should have only one reason to succeed

**Severity**: Medium

A unit test assertion should have only one reason to succeed because it helps to ensure that the test is focused and specific. When a test has
multiple reasons to succeed, it becomes difficult to determine the root cause of a failure if the test fails. This can lead to confusion and wasted
time trying to debug the test.

---

### javascript:S1862 — "if/else if" chains and "switch" cases should not have the same condition

**Severity**: Medium

Both 
`if-else`
 chains and 
`switch`
 statements are used for conditional branching, but they differ in their syntax and the way
they handle multiple conditions.

---

### javascript:S1607 — Tests should not be skipped without providing a reason

**Severity**: Medium

Disabling unit tests lead to a lack of visibility into why tests are ignored, a decline in code quality as underlying problems remain unaddressed,
and an increased maintenance burden due to the accumulation of disabled tests. It can also create a false sense of security about the stability of the
codebase and pose challenges for new developers who may lack the context to understand why tests were disabled. Proper documentation and clear reasons
for disabling tests are essential to ensure they are revisited and re-enabled once the issues are resolved.

**Noncompliant code example**

```javascript
describe('foo', function() {
  it.skip('should do something', function(done) { // Noncompliant
    done();
  });
});
```

**Compliant solution**

```javascript
describe('foo', function() {
  // Reason: There is a bug in the code
  it.skip('should do something', function(done) { // Compliant
    done();
  });
});
```

---

## 13. Accessibility Rules — Medium (26 rules)

### javascript:S6821 — DOM elements with ARIA roles should have a valid non-abstract role

**Severity**: Medium

ARIA (Accessible Rich Internet Applications) attributes are used to enhance the accessibility of web content and web applications. These attributes
provide additional information about an element’s role, state, properties, and values to assistive technologies like screen readers.

This rule checks that when using the 
`role`
 property in DOM elements, its value is a valid non-abstract ARIA role.

This rule does not cover non-DOM elements, such as custom components.

**Noncompliant code example**

```javascript
<div role="meth" aria-label="a^{2} + b^{2} = c^{2}">
  a<sup>2</sup> + b<sup>2</sup> = c<sup>2</sup>
</div>
```

**Compliant solution**

```javascript
<div role="math" aria-label="a^{2} + b^{2} = c^{2}">
  a<sup>2</sup> + b<sup>2</sup> = c<sup>2</sup>
</div>
```

---

### javascript:S6822 — No redundant ARIA role

**Severity**: Medium

ARIA (Accessible Rich Internet Applications) attributes are used to enhance the accessibility of web content and web applications. These attributes
provide additional information about an element’s role, state, properties, and values to assistive technologies like screen readers.

---

### javascript:S6823 — DOM elements with the `aria-activedescendant` property should be accessible via the tab key

**Severity**: Medium

ARIA (Accessible Rich Internet Applications) attributes are used to enhance the accessibility of web content and web applications. These attributes
provide additional information about an element’s role, state, properties, and values to assistive technologies like screen readers.

**Noncompliant code example**

```javascript
<div aria-activedescendant={descendantId}>
  {content}
</div>
```

**Compliant solution**

```javascript
<div aria-activedescendant={descendantId} tabIndex={0}>
  {content}
</div>
```

---

### javascript:S6824 — No ARIA role or property for unsupported DOM elements

**Severity**: Medium

ARIA (Accessible Rich Internet Applications) attributes are used to enhance the accessibility of web content and web applications. These attributes
provide additional information about an element’s role, state, properties, and values to assistive technologies like screen readers.

This rule checks that ARIA roles or 
`aria-*`
 attributes are not used in unsupported DOM elements, which are mostly invisible such as

`meta`
, 
`html`
 or 
`head`
.

**Noncompliant code example**

```javascript
<title aria-hidden="false">My beautiful web page</title>
```

**Compliant solution**

```javascript
<title>My beautiful web page</title>
```

---

### javascript:S6825 — Focusable elements should not have "aria-hidden" attribute

**Severity**: Medium

ARIA (Accessible Rich Internet Applications) is a set of attributes that define ways to make web content and web applications more accessible to
people with disabilities. The 
`aria-hidden`
 attribute is used to indicate that an element and all of its descendants are not visible or
perceivable to any user as implemented by assistive technologies.

**Noncompliant code example**

```javascript
<button aria-hidden="true">Click me</button>
```

**Compliant solution**

```javascript
<button>Click me</button>
```

---

### javascript:S6807 — DOM elements with ARIA roles should have the required properties

**Severity**: Medium

ARIA (Accessible Rich Internet Applications) attributes are used to enhance the accessibility of web content and web applications. These attributes
provide additional information about an element’s role, state, properties, and values to assistive technologies like screen readers.

Each role in ARIA has a set of required attributes that must be included for the role to be properly understood by assistive technologies. These
attributes are known as "required aria-* properties".

For example, if an element has a role of "checkbox", it must also include the aria-checked property. This property indicates whether the checkbox
is checked (true), unchecked (false), or in a mixed state (mixed).

This rule checks that each element with a defined ARIA role also has all required attributes.

**Noncompliant code example**

```javascript
<div role="checkbox">Unchecked</div> {/* Noncompliant: aria-checked is missing */}
```

**Compliant solution**

```javascript
<div role="checkbox" aria-checked={isChecked}>Unchecked</div>
```

---

### javascript:S6811 — DOM elements with ARIA role should only have supported properties

**Severity**: Medium

ARIA properties, also known as "aria-* properties", are special attributes used in HTML to enhance the accessibility of web elements. They provide
additional semantics to help assistive technologies, like screen readers, interpret the element.

**Noncompliant code example**

```javascript
<div role="checkbox" aria-checked={isChecked}>Unchecked</div>
```

---

### javascript:S6819 — Prefer tag over ARIA role

**Severity**: Medium

ARIA (Accessible Rich Internet Applications) roles are used to make web content and web applications more accessible to people with disabilities.
However, you should not use an ARIA role on a generic element (like 
`span`
 or 
`div`
) if there is a semantic HTML tag with
similar functionality, just use that tag instead.

---

### javascript:S6843 — Interactive DOM elements should not have non-interactive ARIA roles

**Severity**: Medium

Interactive DOM elements are elements that users can interact with. These include buttons, links, form inputs, and other elements that can be
clicked, focused, or otherwise manipulated by the user. ARIA roles, on the other hand, are used to improve accessibility by providing additional
semantic information about an element’s purpose and behavior. ARIA roles can be divided into two categories: interactive roles and non-interactive
roles.

**Noncompliant code example**

```javascript
function myButton() {
    return <button role="article">Click me!</button>; // Noncompliant; "button" is interactive, but "article" isn't
}
```

**Compliant solution**

```javascript
function myButton() {
    return <button role="button">Click me!</button>;
}
```

---

### javascript:S6845 — Non-interactive DOM elements should not have the `tabIndex` property

**Severity**: Medium

The misuse of the 
`tabIndex`
 attribute can lead to several issues:

 Navigation Confusion: It can confuse users who rely on keyboard navigation, as they might expect to tab through interactive elements like links
  and buttons, not static content. 

 Accessibility Issues: It can create accessibility problems, as assistive technologies provide their own page navigation mechanisms based on the
  HTML of the page. Adding unnecessary tabindexes can disrupt this. 

 Increased Tab Ring Size: It unnecessarily increases the size of the page’s tab ring, making navigation more cumbersome.

**Noncompliant code example**

```javascript
<div tabIndex="0" />
```

**Compliant solution**

```javascript
<div />
```

---

### javascript:S6840 — DOM elements should use the "autocomplete" attribute correctly

**Severity**: Medium

Not providing autocomplete values in form fields can lead to content inaccessibility. The function of each standard input field, which gathers a
person’s personal data, is systematically determined according to the list of 
[53 Input Purposes
for User Interface Components](https://www.w3.org/TR/WCAG21/#input-purposes)
. If the necessary autocomplete attribute values are absent, screen readers will not be able to identify and read
these fields. This lack of information can hinder users, particularly those using screen readers, from properly navigating and interacting with
forms.

For screen readers to operate effectively, it is imperative that the autocomplete attribute values are not only valid but also correctly
applied.

**Noncompliant code example**

```javascript
function MyInput() {
    return <input type="text" autocomplete="foo" />; // Noncompliant
}
```

**Compliant solution**

```javascript
function MyInput() {
    return <input type="text" autocomplete="name" />;
}
```

---

### javascript:S6841 — "tabIndex" values should be 0 or -1

**Severity**: Medium

Positive 
`tabIndex`
 values can disrupt the natural tab order of the webpage. This can be confusing for screen reader users who rely on a
logical tab order to navigate through the content. If the tab order doesn’t match the visual or logical order of elements, users may struggle to
understand the page structure.

Therefore, it’s recommended to avoid using positive 
`tabIndex`
 values.

**Noncompliant code example**

```javascript
function MyDiv() {
    return (
        <div>
            <span tabIndex="5">foo</span> // Noncompliant
            <span tabIndex="3">bar</span> // Noncompliant
            <span tabIndex="1">baz</span> // Noncompliant
            <span tabIndex="2">qux</span> // Noncompliant
        </div>
    );
}
```

**Compliant solution**

```javascript
function MyDiv() {
    return (
        <div>
            <span tabIndex="0">foo</span>
            <span tabIndex="-1">bar</span>
            <span tabIndex={0}>baz</span>
            <span>qux</span>
        </div>
    );
}
```

---

### javascript:S6842 — Non-interactive DOM elements should not have interactive ARIA roles

**Severity**: Medium

Non-interactive DOM elements are those that do not have built-in interactivity or do not require user interaction. Examples include

**Noncompliant code example**

```javascript
function myListElement() {
    return <li role="button">Foo</li>; // Noncompliant; "li" isn't interactive, but "button" is
}
```

**Compliant solution**

```javascript
function myListElement() {
    return <li role="listitem">Foo</li>;
}
```

---

### javascript:S6846 — DOM elements should not use the "accesskey" property

**Severity**: Medium

The 
`accesskey`
 attribute, despite its potential utility, is fraught with numerous issues that limit its effectiveness and
usability:

---

### javascript:S6850 — Heading elements should have accessible content

**Severity**: Medium

Heading elements are represented by the tags 
`<h1>`
 through 
`<h6>`
, with 
`<h1>`
 being the
highest level and 
`<h6>`
 being the lowest. These elements are used to structure the content of the page and create a hierarchical
outline that can be followed by users and search engines alike.

**Noncompliant code example**

```javascript
function JavaScript101() {
  return (
    <>
      <h1>JavaScript Programming Guide</h1>
      <p>An introduction to JavaScript programming and its applications.</p>

      <h2>JavaScript Basics</h2>
      <p>Understanding the basic concepts in JavaScript programming.</p>

      <h3>Variables</h3>
      <p>Explanation of what variables are and how to declare them in JavaScript.</p>

      <h3 aria-hidden>Data Types</h3> // Noncompliant
      <p>Overview of the different data types in JavaScript.</p>

      <h3 /> // Noncompliant
      <p>Understanding how to declare and use functions in JavaScript.</p>
    </>
  );
}
```

**Compliant solution**

```javascript
function JavaScript101() {
  return (
    <>
      <h1>JavaScript Programming Guide</h1>
      <p>An introduction to JavaScript programming and its applications.</p>

      <h2>JavaScript Basics</h2>
      <p>Understanding the basic concepts in JavaScript programming.</p>

      <h3>Variables</h3>
      <p>Explanation of what variables are and how to declare them in JavaScript.</p>

      <h3>Data Types</h3>
      <p>Overview of the different data types in JavaScript.</p>

      <h3>Functions</h3>
      <p>Understanding how to declare and use functions in JavaScript.</p>
    </>
  );
}
```

---

### javascript:S6851 — Images should have a non-redundant alternate description

**Severity**: Medium

`alt`
 attributes, also known as "alt tags" or "alt descriptions," are used to specify alternative text that is rendered when an image
cannot be displayed. They are crucial for improving web accessibility, as they provide a text description of images for users who rely on screen
readers.

**Noncompliant code example**

```javascript
function MyImage() {
    return <img src="sunrise.jpg" alt="image of a sunrise" />; // Noncompliant: "Image, image of a sunrise"
}
```

**Compliant solution**

```javascript
function MyImage() {
    return <img src="sunrise.jpg" alt="a sunrise over a mountain range" />;
}
```

---

### javascript:S1656 — Variables should not be self-assigned

**Severity**: Medium

There is no reason to re-assign a variable to itself. Either this statement is redundant and should be removed, or the re-assignment is a mistake
and some other value or variable was intended for the assignment instead.

Noncompliant code example

```

function setName(name) {
    name = name;
}

```

Compliant solution

```

function setName(name) {
    this.name = name;
}

```

---

### javascript:S2814 — Variables and functions should not be redeclared

**Severity**: Medium

Redeclaration refers to the act of declaring a variable or function with the same name more than once within the same scope. In JavaScript,
variable and function redeclarations are allowed but can lead to unexpected behavior and potential bugs in your code.

---

### javascript:S6793 — ARIA properties in DOM elements should have valid values

**Severity**: Medium

ARIA (Accessible Rich Internet Applications) attributes are used to enhance the accessibility of web content and web applications. These attributes
provide additional information about an element’s role, state, properties, and values to assistive technologies like screen readers.

This rule checks that the values of ARIA attributes "aria-*" in DOM elements are valid.

**Noncompliant code example**

```javascript
<span aria-hidden="ok">foo</span>
```

**Compliant solution**

```javascript
<span aria-hidden="true">foo</span>
```

---

### javascript:S6522 — Import variables should not be reassigned

**Severity**: Medium

Assigning a value to an import variable will cause a runtime error and will raise a compilation error in TypeScript.

---

### javascript:S5254 — HTML elements should have a valid language attribute

**Severity**: Medium

Screen readers require a specified language to function correctly. Without it, they default to the user’s set language, causing issues for
multilingual users. Specifying a valid language ensures correct pronunciation and a less confusing experience.

**Noncompliant code example**

```javascript
<html></html>
```

**Compliant solution**

```javascript
<html lang="en"></html>
```

---

### javascript:S5257 — HTML "<table>" should not be used for layout purposes

**Severity**: Medium

HTML <table> elements should not be used for layout purposes as it can confuse screen readers. It is recommended to use CSS instead.

This rule raises an issue on every 
`<table>`
 element containing a 
`role`
 attribute set to 
`"presentation"`

or 
`"none"`
, which is how 
[W3C recommends](https://www.w3.org/WAI/tutorials/tables/tips/)
 marks layout tables.

Noncompliant code example

```

<table role="presentation"><!-- Noncompliant -->
<!-- ... -->
</table>

```

---

### javascript:S6443 — React state setter function should not be called with its matching state variable

**Severity**: Medium

React components have built-in 
`state`
 data. This data is used to store component property values. When 
`state`
 changes, the
component is re-rendered. React provides the 
`useState`
 hook to manage the 
`state`
. 
`useState`
 returns a state
variable retaining the data and a state setter function to update its value.

---

### javascript:S2392 — Variables should be used in the blocks where they are declared

**Severity**: Medium

The 
`var`
 statement declares variables that are function-scoped or globally-scoped. 
`var`
 declarations are hoisted, meaning
declaring a variable anywhere in the code is equivalent to declaring it at the top of the function or the script.

---

### javascript:S2259 — Properties of variables with "null" or "undefined" values should not be accessed

**Severity**: Medium

In JavaScript, 
`null`
 and 
`undefined`
 are primitive values that do not have properties or methods. When accessing a property
on a 
`null`
 or 
`undefined`
 value, JavaScript tries to access the property of an object that does not exist, which results in a

`TypeError`
.

This can cause the program to crash or behave unexpectedly, which can be difficult to debug.

**Noncompliant code example**

```javascript
let foo = null;
console.log(foo.bar); // Noncompliant: TypeError will be thrown
```

**Compliant solution**

```javascript
let foo;
if (foo != null) {
  console.log(foo.bar);
}
```

---

### javascript:S3500 — "const" variables should not be reassigned

**Severity**: Medium

Variables declared with 
`const`
 cannot be reassigned using the assignment operator.

---

## 14. React Rules — Medium (24 rules)

### javascript:S6747 — JSX elements should not use unknown properties and attributes

**Severity**: Medium

React components often render HTML elements, and developers can pass various props (properties) to these elements. However, React has its own set
of supported properties and attributes, and it’s essential to avoid using unknown or invalid properties when working with such elements to prevent
unexpected behavior at runtime.

The rule reports any instances where you are using a property or attribute that is not recognized by React or the HTML element you are
rendering.

**Noncompliant code example**

```javascript
class Welcome extends React.Component {
  render() {
    return <div class="hello">Hello, World!</div>; // Noncompliant: 'class' is a reserved keyword in JavaScript
  }
}
```

**Compliant solution**

```javascript
class Welcome extends React.Component {
  render() {
    return <div className="hello">Hello, World!</div>;
  }
}
```

---

### javascript:S6746 — In React "this.state" should not be mutated directly

**Severity**: Medium

React does not always propagate component state changes to the underlying DOM elements immediately. If you modify the state during an already
ongoing update cycle, the change may be delayed until the next update. React tries to keep 
`this.state`
 in sync with what is currently in
the DOM, so you should never directly modify 
`this.state`
 yourself. Instead, use the asynchronous 
`setState`
 method instead,
which allows React to properly manage the current state, trigger the new update cycle, or batch the updates together if necessary.

---

### javascript:S6748 — React "children" should not be passed as prop

**Severity**: Medium

When using JSX the component children should be passed between opening and closing tags. Passing children in a 
`children`
 prop may work
sometimes, but will lead to errors if children are passed both as nested components and 
`children`
 prop at the same time.

When not using JSX, the children should be passed to 
`createElement()`
 method as extra arguments after the 
`props`

object.

```

<div children='Children' />
<Foo children={<Bar />} />

React.createElement("div", { children: 'Children' })

```

To fix the code, remove the 
`children`
 prop and pass the children between opening and closing JSX tags or as extra arguments to

`createElement()`
 function.

```

<div>Children</div>
<Foo><Bar /></Foo>

React.createElement("div", {}, 'Children');

```

---

### javascript:S6756 — "setState" should use a callback when referencing the previous state

**Severity**: Medium

In React, calling 
`setState`
 is the primary way to update a component’s state. However, calling 
`setState`
 is often
asynchronous. React batches state updates for performance reasons, which means that when you call 
`setState`
, React doesn’t immediately
update the state and trigger a re-render. Instead, it schedules the update for later, and multiple 
`setState`
 calls within the same event
handler or function may be batched together. This can lead to unexpected behavior if you assume that state updates are immediate. Therefore, you
should not rely on their values for calculating the next state.

---

### javascript:S6757 — "this" should not be used in functional components

**Severity**: Medium

Referring to 
`this`
 in React functional components would be an error because the components are just regular JavaScript functions and do
not have an object associated with them. Functional components receive their props as a first argument to the component function, so you can access
them directly, and it is a common practice to destructure them right away.

---

### javascript:S6750 — The return value of "ReactDOM.render" should not be used

**Severity**: Medium

In React, the 
`ReactDOM.render()`
 method is used to render a React component into a DOM element. It has a return value, but it’s
generally recommended not to use it. The method might return a reference to the root 
`ReactComponent`
 instance, but it can be unpredictable
and may not always be useful. Indeed, the return value can vary depending on the version of React you’re using and the specific circumstances in which
it’s called.

---

### javascript:S6481 — React Context Provider values should have stable identities

**Severity**: Medium

Whenever the 
`value`
 property of React context changes, React will rerender the context and all its child nodes and consumers. In
JavaScript, things like object literals or function expressions will create a new identity every time they are evaluated. Such constructions should
not be directly used as context 
`value`
 because React will always consider they have changed. This can significantly impact
performance.

---

### javascript:S6788 — React's "findDOMNode" should not be used

**Severity**: Medium

In React, 
`findDOMNode`
 is used to get the browser DOM node given a component instance. However, using 
`findDOMNode`
 is
fragile because the connection between the JSX node and the code manipulating the corresponding DOM node is not explicit. For example, changing the
external structure of returned JSX will affect the return value of 
`findDOMNode`
. There are also other 
[caveats](https://react.dev/reference/react-dom/findDOMNode#caveats)
 when using 
`findDOMNode`
.

---

### javascript:S6789 — React's "isMounted" should not be used

**Severity**: Medium

React 
`isMounted()`
 is primarily used to avoid calling 
`setState()`
 after a component has unmounted, because calling

---

### javascript:S6438 — Comments inside JSX expressions should be enclosed in curly braces

**Severity**: Medium

JSX lets you write HTML-like markup inside a JavaScript file, commonly used in React.

---

### javascript:S6435 — React "render" functions should return a value

**Severity**: Medium

In React, the 
`render`
 function is a required method in a class component that defines what will be rendered to the user interface (UI).
It is responsible for returning a value, typically a JSX (JavaScript XML) expression, that describes the structure and appearance of the component’s
UI.

---

### javascript:S6791 — React legacy lifecycle methods should not be used

**Severity**: Medium

React works in two phases: render and commit.

**Noncompliant code example**

```javascript
class myComponent extends React.Component {
  constructor(props) {
      super(props);
  }

  componentWillMount() { // Noncompliant: "componentWillMount" is deprecated
      if (localStorage.getItem("token")) {
          this.setState({logged_in: true});
      }
  }
  // ...
}
```

**Compliant solution**

```javascript
class myComponent extends React.Component {
  constructor(props) {
      super(props);

      if (localStorage.getItem("token")) {
          this.setState({logged_in: true});
      }
  }
  // ...
}
```

---

### javascript:S6766 — JSX special characters should be escaped

**Severity**: Medium

If JSX special characters (
`>`
, 
`}`
) appear unescaped in the element body, this may be either because you simply forgot to
escape them or because there is a problem with the JSX tag or expression (for example, misplaced or duplicate closing 
`>`
 or

---

### javascript:S6763 — "shouldComponentUpdate" should not be defined when extending "React.PureComponent"

**Severity**: Medium

In React, a 
`PureComponent`
 is a class component that is optimized for performance by implementing a shallow comparison of props and
state. It is a subclass of the regular React 
`Component`
 class and provides a default implementation of the

---

### javascript:S6761 — "children" and "dangerouslySetInnerHTML" should not be used together

**Severity**: Medium

React has a special prop called 
`dangerouslySetInnerHTML`
 that allows you to assign a raw HTML string to the underlying DOM

---

### javascript:S6774 — React components should validate prop types

**Severity**: Medium

In JavaScript, props are typically passed as plain objects, which can lead to errors and confusion when working with components that have specific
prop requirements. However, it lacks of type safety and clarity when passing props to components in a codebase.

By defining types for component props, developers can enforce type safety and provide clear documentation for the expected props of a component.
This helps catch potential errors at compile-time. It also improves code maintainability by making it easier to understand how components should be
used and what props they accept.

**Noncompliant code example**

```javascript
import PropTypes from 'prop-types';

function Hello({ firstname, lastname }) {
  return <div>Hello {firstname} {lastname}</div>; // Noncompliant: 'lastname' type is missing
}
Hello.propTypes = {
  firstname: PropTypes.string.isRequired
};

// Using legacy APIs

class Hello extends React.Component {
  render() {
    return <div>Hello {this.props.firstname} {this.props.lastname}</div>; // Noncompliant: 'lastname' type is missing
  }
}
Hello.propTypes = {
  firstname: PropTypes.string.isRequired,
};
```

**Compliant solution**

```javascript
import PropTypes from 'prop-types';

function Hello({ firstname, lastname }) {
  return <div>Hello {firstname} {lastname}</div>;
}
Hello.propTypes = {
  firstname: PropTypes.string.isRequired,
  lastname: PropTypes.string.isRequired,
};

// Using legacy APIs

class Hello extends React.Component {
  render() {
    return <div>Hello {this.props.firstname} {this.props.lastname}</div>;
  }
}
Hello.propTypes = {
  firstname: PropTypes.string.isRequired,
  lastname: PropTypes.string.isRequired,
};
```

---

### javascript:S6477 — JSX list components should have a key property

**Severity**: Medium

To optimize the rendering of React list components, a unique identifier (UID) is required for each list item. This UID lets React identify the item
throughout its lifetime. To provide it, use the 
`key`
 attribute of the list item. When the 
`key`
 attribute is missing, React
will default to using the item’s index inside the list component. If the element ordering changes, it will cause keys to not match up between renders,
recreating the DOM. It can negatively impact performance and may cause issues with the component state.

---

### javascript:S6479 — JSX list components should not use array indexes as key

**Severity**: Medium

To optimize the rendering of React list components, a unique identifier (UID) is required for each list item. This UID lets React identify the item
throughout its lifetime. Avoid array indexes since the order of the items may change, which will cause keys to not match up between renders,
recreating the DOM. It can negatively impact performance and may cause issues with the component state.

---

### javascript:S6440 — React Hooks should be properly called

**Severity**: Medium

React relies on the order in which Hooks are called to correctly preserve the state of Hooks between multiple 
`useState`
 and

---

### javascript:S6478 — React components should not be nested

**Severity**: Medium

React components should not be nested, as their state will be lost on each re-render of their parent component, possibly introducing bugs. This
will also impact performance as child components will be recreated unnecessarily.

---

### javascript:S6441 — Unused methods of React components should be removed

**Severity**: Medium

Methods that are never executed are dead code and should be removed. Cleaning out dead code decreases the size of the maintained codebase, making
it easier to understand the program and preventing bugs from being introduced.

---

### javascript:S6439 — React components should not render non-boolean condition values

**Severity**: Medium

Logical AND (
`&&`
) operator is sometimes used to conditionally render in React (aka short-circuit evaluation). For example,

---

### javascript:S6442 — React's useState hook should not be used directly in the render function or body of a component

**Severity**: Medium

React’s 
`useState`
 hook setter function should not be called directly in the body of a component, as it would produce an infinite render
loop. A re-rendering occurs whenever the state of a component changes. Since a hook setter function changes the component’s state, it also triggers
re-rendering.

---

### javascript:S6486 — JSX list components keys should match up between renders

**Severity**: Medium

To optimize the rendering of React list components, a unique identifier (UID) is required in the 
`key`
 attribute for each list item.
This UID lets React identify the item throughout its lifetime. Using generated values like 
`Math.random()`
 or 
`Date.now()`
 is
discouraged as their return value will differ between calls, causing the keys to not match up between renders, recreating the DOM. Also, this may
cause bugs if values collide.

---

## 15. Code Quality & Maintainability Rules — Medium (110 rules)

### javascript:S6627 — Users should not use internal APIs

**Severity**: Medium

The public API of a framework, plugin, or library is the way its provider intended it to be used. API stability and compatibility (within the same
major version number) of a library are guaranteed only for its public API.

Internal APIs are mere implementation details and are prone to breaking changes as the implementation of the library changes. No guarantees are
being made about them. Therefore, users should not use internal APIs, even when visible.

What is the potential impact?

Code Stability

If not fixed, your code might break when the library is upgraded to a new version, even if only the minor version number or the patch number
changes.

**Noncompliant code example**

```javascript
import { _parseWith } from './node_modules/foo/helpers'
```

**Compliant solution**

```javascript
import { parse } from 'foo'
```

---

### javascript:S7060 — Module should not import itself

**Severity**: Medium

When a module imports itself it has no effect. This means that the import statement does nothing useful and serves no purpose. This can happen
during refactoring or when a developer mistakenly imports the module itself.

To fix the problem remove the self-import statement.

```

// file: foo.js
import foo from './foo'; // Noncompliant

const foo = require('./foo'); // Noncompliant

```

```

// file: index.js
import index from '.'; // Noncompliant

const index = require('.'); // Noncompliant

```

---

### javascript:S7790 — Templates should not be constructed dynamically

**Severity**: Medium

Constructing templates by dynamically inserting strings coming from third-party sources is an anti-pattern which creates code that is brittle,
difficult to read, and challenging to debug.

Moreover, in the long run, this practice progressively increases the likelihood of introducing 
Server-Side Template Injections
(SSTI)
, sometimes in complex ways that are hard to detect.
 An SSTI is the insertion of third-party data (like user data) within
templates, which enables attackers to execute arbitrary commands on the underlying operating system.

**Noncompliant code example**

```javascript
const pug = require('pug');

const pugTemplate = `
doctype html
html
  head
    title=${pageTitle}
  body
    ${userInput}
`;

const compiledFunction = pug.compile(pugTemplate); // Sensitive

compiledFunction();
```

**Compliant solution**

```javascript
const pug = require('pug');

const pugTemplate = `
doctype html
html
  head
    title= pageTitle
  body
    h1= mainHeading
    p.message= message
`;

const compiledFunction = pug.compile(pugTemplate);

const templateData = {
  pageTitle: 'Safe Template Example',
  mainHeading: 'Welcome!',
  message: 'This content is passed securely as data to the template.'
};
compiledFunction(templateData);
```

---

### javascript:S3799 — Destructuring patterns should not be empty

**Severity**: Medium

Destructuring is a convenient way of extracting multiple values from data stored in (possibly nested) objects and arrays. It can make code more
concise and expressive by directly extracting values or properties needed from arrays or objects. However, it is possible to define an empty pattern
that has no effect, where no variables are bound to the destructured values.

---

### javascript:S2685 — "arguments.caller" and "arguments.callee" should not be used

**Severity**: Medium

In JavaScript, 
`arguments`
 is a built-in array-like object automatically available within the scope of all non-arrow functions. It
allows you to access the arguments the function was called with, even if the number of arguments passed during the function call does not match the
number declared in the function signature. 
`arguments`
 has entries for each argument, with the first entry’s index at 
`0`
.

---

### javascript:S6836 — "case" and "default" clauses should not contain lexical declarations

**Severity**: Medium

The ECMAScript specification allows for creating block-level lexical declarations (
`let`
, 
`const`
, 
`function`
, and

---

### javascript:S878 — Comma operator should not be used

**Severity**: Medium

The comma operator takes two expressions, executes them from left to right, and returns the result of the second one. The use of this operator is
generally detrimental to the readability and reliability of code, and the same effect can be achieved by other means.

---

### javascript:S1068 — Unused private class members should be removed

**Severity**: Medium

The private class members were introduced in ES2022 and use 
`#`
 (hash) symbol prefix. It is possible to declare private fields, methods,
getters and setters as well as their static counterparts. The private members are only accessible from within the current class body and aren’t
inherited by subclasses. They also cannot be removed with 
`delete`
 operator.

---

### javascript:S6638 — Binary expressions should not always return the same value

**Severity**: Medium

An expression that always produces the same result, regardless of the inputs, is unnecessary and likely indicates a programmer’s error. This can
come from

 confusing operator precedence 

 expecting strict equality between different types 

 expecting objects to be compared by value 

 expecting empty objects to be 
`false`
 or 
`null`
 

 mistyping 
`>=`
 for 
`⇒`
 

This can also happen when you put an assignment in a logical sub-expression. While not strictly a bug, this practice is confusing and should be
avoided.

**Noncompliant code example**

```javascript
!foo == null;
a + b ?? c;
x === [];
(foo=0) && bar;
```

**Compliant solution**

```javascript
foo != null;
a + (b ?? c);
x.length === 0;
```

---

### javascript:S6844 — Anchor tags should not be used as buttons

**Severity**: Medium

Misusing 
`<a>`
 tags as buttons can lead to several issues:

**Noncompliant code example**

```javascript
const MyComponent = () => {
    return <>
        <a href="javascript:void(0)" onClick={foo}>Perform action</a>
        <a href="#" onClick={foo}>Perform action</a>
        <a onClick={foo}>Perform action</a>
    </>;
};
```

**Compliant solution**

```javascript
const MyComponent = () => {
    return <>
      <button onClick={foo}>Perform action</button>
      <a href="#section" onClick={foo}>Perform action</a>
    </>;
};
```

---

### javascript:S6847 — Non-interactive elements shouldn't have event handlers

**Severity**: Medium

Attaching event handlers to non-interactive HTML elements can lead to significant accessibility issues. These elements, such as

`<div>`
 and 
`<span>`
, are not designed to interact with assistive technologies like screen readers, making it
difficult for users with disabilities to navigate and interact with the website. Additionally, these elements may not be focusable or provide visual
feedback when interacted with, resulting in a confusing and potentially frustrating user experience. Therefore, to maintain an accessible and
user-friendly website, event handlers should be used exclusively with interactive elements.

The rule only considers the handlers 
`onClick`
, 
`onMouseDown`
, 
`onMouseUp`
, 
`onKeyPress`
,

`onKeyDown`
, and 
`onKeyUp`
.

**Noncompliant code example**

```javascript
<li onClick={() => void 0} />
<div onClick={() => void 0} role="listitem" />
```

**Compliant solution**

```javascript
<div onClick={() => void 0} role="button" />
<div onClick={() => void 0} role="presentation" />
<input type="text" onClick={() => void 0} /> // Interactive element does not require role.
<button onClick={() => void 0} className="foo" /> // button is interactive.
<div onClick={() => void 0} role="button" aria-hidden /> // This is hidden from the screenreader.
```

---

### javascript:S6848 — Non-interactive DOM elements should not have an interactive handler

**Severity**: Medium

Non-interactive DOM elements are HTML elements that are not designed to be interacted with by the user, for instance 
`<div>`
,

**Noncompliant code example**

```javascript
<div onClick={() => {}} />; // Noncompliant
```

**Compliant solution**

```javascript
<div onClick={() => {}} role="button" />;
```

---

### javascript:S1536 — Function argument names should be unique

**Severity**: Medium

Function parameter names should be unique in JavaScript. Unique parameter names ensure that there is no ambiguity in referring to specific
parameters within the function body. If multiple parameters share the same name, it becomes unclear which parameter is being referred to when using
that name within the function.

---

### javascript:S6852 — Elements with an interactive role should support focus

**Severity**: Medium

Lack of focusability can hinder navigation and interaction with the website, resulting in an exclusionary user experience and possible violation of
accessibility guidelines.

**Noncompliant code example**

```javascript
<!-- Element with mouse/keyboard handler has no tabindex -->
<span onclick="submitForm();" role="button">Submit</span>

<!-- Anchor element without href is not focusable -->
<a onclick="showNextPage();" role="button">Next page</a>
```

**Compliant solution**

```javascript
<!-- Element with mouse handler has tabIndex -->
<span onClick="doSomething();" tabIndex="0" role="button">Submit</span>

<!-- Focusable anchor with mouse handler -->
<a href="javascript:void(0);" onClick="doSomething();"> Next page </a>
```

---

### javascript:S6853 — Label elements should have a text label and an associated control

**Severity**: Medium

When a label element lacks a text label or an associated control, it can lead to several issues:

**Noncompliant code example**

```javascript
<input type="text" />
<label>Favorite food</label>
```

**Compliant solution**

```javascript
<label>
  <input type="text" />
  Favorite food
</label>
```

---

### javascript:S1534 — Member names should not be duplicated within a class or object literal

**Severity**: Medium

JavaScript allows duplicate property names in classes and object literals. The last occurrence will overwrite previous definitions. Therefore,
having more than one occurrence will have no effect and may cause misunderstandings and bugs.

---

### javascript:S905 — Non-empty statements should change control flow or have at least one side-effect

**Severity**: Medium

When writing code, it is important to ensure that each statement serves a purpose and contributes to the overall functionality of the program. When
they have no side effects or do not change the control flow, they can either indicate a programming error or be redundant:

 The code does not behave as intended: The statements are expected to have an effect but they do not. This can be caused by mistyping,
  copy-and-paste errors, etc. 

 The statements are residual after a refactoring. 

Exceptions

The rule does not raise an issue on statements containing only a semicolon (
`;`
).

**Noncompliant code example**

```javascript
function getResult() {
    let result = 42;
    if (shouldBeZero()) {
        result == 0; // Noncompliant: no side effect, was an assignment intended?
    }
    return result;
}
```

**Compliant solution**

```javascript
var msg = "Hello, "
  "World!"; // Noncompliant; have we forgotten '+' operator on previous line?
```

---

### javascript:S1751 — Loops with at most one iteration should be refactored

**Severity**: Medium

A loop with at most one iteration is equivalent to the use of an 
`if`
 statement to conditionally execute one piece of code. No developer
expects to find such a use of a loop statement. If the initial intention of the author was really to conditionally execute one piece of code, an

---

### javascript:S1763 — All code should be reachable

**Severity**: Medium

Unreachable code is the code whose statements cannot be executed under any circumstances. Jump statements, like 
`return`
,

`break`
, 
`continue`
, and 
`throw`
, alter the normal flow of control within a program, making it possible to skip
certain parts of the code, terminate loops prematurely, or exit from functions. So any statements that come after a jump are effectively
unreachable.

Unreachable statements can be a sign of a logical error or oversight in the program’s design, leading to unexpected behavior at runtime.

```

function func(a) {
  let i = 10;
  return i + a;
  i++; // Noncompliant: this is never executed
}

```

Identify and remove unreachable statements from your code.

```

function func(a) {
  let i = 10;
  return i + a;
}

```

---

### javascript:S1788 — Function parameters with default values should be last

**Severity**: Medium

Default parameter values allow callers to specify as many or as few arguments as they want while getting the same functionality and minimizing
boilerplate, wrapper code, making a function easier to use.

---

### javascript:S2301 — Methods should not contain selector parameters

**Severity**: Medium

A selector parameter is a 
`boolean`
 parameter that’s used to determine which of two paths to take through a method. Specifying such a
parameter may seem innocuous, particularly if it’s well-named.

---

### javascript:S2432 — Setters should not return values

**Severity**: Medium

In JavaScript, a setter is a special type of function that is used to set the value of a property on an object. Setters are defined using the

---

### javascript:S6666 — Spread syntax should be used instead of "apply()"

**Severity**: Medium

The spread operator is a more concise and more readable way to pass arguments to a function that takes a variable number of arguments (variadic
function). Prior to ES2015, the only way to call such functions with a variable number of arguments was to use the 
`.apply()`
 method.

```

foo.apply(undefined, args); // Noncompliant: use spread syntax instead of .apply()
foo.apply(null, args); // Noncompliant: use spread syntax instead of .apply()
obj.foo.apply(obj, args); // Noncompliant: use spread syntax instead of .apply()

```

Using 
`.apply()`
 is no longer necessary in such cases - replace it with a spread operator applied to the array of arguments.

```

foo( ...args);
foo( ...args);
obj.foo( ...args);

```

---

### javascript:S107 — Functions should not have too many parameters

**Severity**: Medium

Functions with a long parameter list are difficult to use because maintainers must figure out the role of each parameter and keep track of their
position.

---

### javascript:S6660 — If statements should not be the only statement in else blocks

**Severity**: Medium

When 
`if`
 is the only statement in the 
`else`
 block, it is better to use 
`else if`
 because it simplifies the code
and makes it more readable.

---

### javascript:S6661 — Object spread syntax should be used instead of "Object.assign"

**Severity**: Medium

When merging objects or copying properties from one object to another, use the object spread syntax instead of 
`Object.assign()`
. The
object spread syntax was introduced in ES2018 and allows shallow-cloning or merging of objects with a more concise and readable syntax.

---

### javascript:S108 — Nested blocks of code should not be left empty

**Severity**: Medium

An empty code block is confusing. It will require some effort from maintainers to determine if it is intentional or indicates the implementation is
incomplete.

```

for (let i = 0; i < length; i++) {}  // Noncompliant: is the block empty on purpose, or is code missing?

```

Removing or filling the empty code blocks takes away ambiguity and generally results in a more straightforward and less surprising code.

Exceptions

The rule ignores:

 code blocks that contain comments 

 
`catch`
 blocks

---

### javascript:S6557 — Ends of strings should be checked with "startsWith()" and "endsWith()"

**Severity**: Medium

When writing code, it is quite common to test patterns against string ends. For a long time, JavaScript did not provide proper support for this use
case. As a result, developers have been relying on various programming subtleties to check the start or end of a string. Examples are getting the
index of a substring, slicing the beginning of a string, extracting a substring from the head, matching a regular expression beginning or ending with
a pattern, and so on.

While these approaches are all technically valid, they look more like hacking than anything else, blur the developer’s intent, but more importantly
affect code readability.

Since ES2015, JavaScript provides 
`String#startsWith`
 and 
`String#endsWith`
, which are the preferred ways to test patterns
against string ends.

**Noncompliant code example**

```javascript
const str = 'abc';

str[0] === 'a';
str.charAt(0) === 'a';
str.indexOf('abc') === 0;
str.slice(0, 3) === 'abc';
str.substring(0, 3) === 'abc';
str.match(/^abc/) != null;
/^abc/.test(str);
```

**Compliant solution**

```javascript
str.startsWith('abc');
```

---

### javascript:S6676 — Calls to ".call()" and ".apply()" methods should not be redundant

**Severity**: Medium

If the function call can be written in a normal way, then calling that function with 
`.call()`
 or 
`.apply()`
 methods is
redundant and can be removed without affecting the behavior of the code.

---

### javascript:S6790 — String references should not be used

**Severity**: Medium

React Refs provide a way to access DOM nodes or React elements created in the render method.

---

### javascript:S6643 — Prototypes of builtin objects should not be modified

**Severity**: Medium

By default, JavaScript allows you to modify native object prototypes, such as 
`Array`
, 
`String`
, 
`Object`
, and so
on. This means you can add new properties or methods to native objects or override existing ones. While this flexibility can be useful in some
instances, it can lead to unexpected behavior, bugs, and compatibility issues.

The rule forbids extending or modifying native JavaScript objects or prototypes, as prototypes of builtin objects should not be modified
altogether.

```

Object.prototype.universe = 42;
Object.defineProperty(Array.prototype, "size", { value: 0 });

```

---

### javascript:S6535 — Unnecessary character escapes should be removed

**Severity**: Medium

The 
`\`
 (backslash) character indicates that the next character should be treated as a literal character rather than as a special
character or string delimiter. For instance, it is common to escape single quotes inside a string literal using the single quote delimiter like

---

### javascript:S6657 — Octal escape sequences should not be used

**Severity**: Medium

Octal escape sequences in string literals have been deprecated since ECMAScript 5 and should not be used in modern JavaScript code.

Many developers may not have experience with this format and may confuse it with the decimal notation.

```

let message = "Copyright \251"; // Noncompliant

```

The better way to insert special characters is to use Unicode or hexadecimal escape sequences.

```

let message1 = "Copyright \u00A9";  // unicode
let message2 = "Copyright \xA9";    // hexadecimal

```

---

### javascript:S6534 — Numbers should not lose precision

**Severity**: Medium

Numbers in JavaScript are stored in 
[double-precision 64-bit binary
format IEEE 754](https://en.wikipedia.org/wiki/Double-precision_floating-point_format)
. Like any other number encoding occupying a finite number of bits, it is unable to represent all numbers.

**Noncompliant code example**

```javascript
const myNumber = Number(myBigInt);
const myBigInt = BigInt(myNumber);
```

**Compliant solution**

```javascript
const foo = 2312123211345545367  // Noncompliant: will be stored as 2312123211345545000
const bar = BigInt(2312123211345545367);  // Noncompliant: parameter is first parsed as an integer and thus rounded
```

---

### javascript:S6772 — Spacing between inline elements should be explicit

**Severity**: Medium

React JSX differs from the HTML standard in the way it handles newline characters and surrounding whitespace. HTML collapses multiple whitespace
characters (including newlines) into a single whitespace, but JSX removes such sequences completely, leaving no space between inline elements
separated by the line break. This difference in behavior can be confusing and may result in unintended layout, for example, missing whitespace between
the link content and the surrounding text.

---

### javascript:S4140 — Sparse arrays should not be created with extra commas

**Severity**: Medium

A sparse array is an array in which the elements do not occupy a contiguous range of indices. In other words, there are gaps (or "holes") between
the elements in the array, where some indices have no corresponding value assigned to them.

---

### javascript:S7721 — Functions should be moved to the highest possible scope

**Severity**: Medium

When functions are defined in nested scopes unnecessarily, it creates several problems:

---

### javascript:S7729 — Array method callbacks should not use the "thisArg" parameter

**Severity**: Medium

JavaScript array methods accept an optional 
`thisArg`
 parameter that sets the 
`this`
 context for the callback function.
However, using this parameter often leads to confusion and less readable code.

---

### javascript:S7750 — Array methods ".find()" and ".findLast()" should be preferred over ".filter()" for single element retrieval

**Severity**: Medium

Using 
`.filter()`
 to find a single element is inefficient and unclear in intent.

---

### javascript:S7751 — Array flattening should use the native "flat()" method

**Severity**: Medium

ES2019 introduced the 
`Array#flat()`
 method as the standard way to flatten arrays. This method is more readable and expressive than
legacy techniques.

---

### javascript:S7753 — "indexOf()" and "lastIndexOf()" should be used instead of "findIndex()" and "findLastIndex()" for simple equality searches

**Severity**: Medium

The 
`findIndex()`
 and 
`findLastIndex()`
 methods are designed for complex search operations that require custom logic. When
you only need to find the index of a specific value using strict equality comparison, these methods are unnecessarily complex.

---

### javascript:S7733 — HTTP GET and HEAD requests should not include a request body

**Severity**: Medium

The HTTP specification defines that GET and HEAD requests should not contain a request body. When you provide a body with these methods, the Fetch
API throws a 
`TypeError`
 at runtime.

---

### javascript:S7734 — Default imports and exports should use the dedicated syntax

**Severity**: Medium

JavaScript provides two ways to import and export default values: the dedicated default syntax and the named syntax with explicit

---

### javascript:S7737 — Objects should not be used as default parameters

**Severity**: Medium

Using object literals as default parameters creates unexpected behavior when the function is called with partial objects.

---

### javascript:S7760 — Default parameters should be used instead of reassigning parameters with literal fallback values

**Severity**: Medium

Reassigning function parameters using the logical OR operator (
`||`
) creates different behavior than using default parameters, which can
lead to unexpected results.

---

### javascript:S7762 — DOM nodes should be removed using "remove()" instead of "removeChild()"

**Severity**: Medium

The traditional way to remove a DOM element in JavaScript was to call 
`parentNode.removeChild(childNode)`
. This approach requires you to
first access the parent node, then call 
`removeChild`
 with the child node as an argument.

---

### javascript:S7742 — Polyfills should not be used when native support is available in target environments

**Severity**: Medium

Polyfills are JavaScript libraries that provide modern functionality to older environments that don’t support it natively. While polyfills are
essential for supporting legacy browsers or older Node.js versions, they become unnecessary overhead when all your target environments already support
the feature natively.

---

### javascript:S7772 — Node.js built-in modules should be imported using the "node:" protocol

**Severity**: Medium

When importing Node.js built-in modules, using the 
`node:`
 protocol makes it explicitly clear that you’re importing a core Node.js
module rather than a third-party package from npm.

---

### javascript:S7773 — Number static methods and properties should be preferred over global equivalents

**Severity**: Medium

ECMAScript 2015 introduced static methods and properties on the 
`Number`
 constructor to replace several global functions and values.
Using these 
`Number`
 equivalents provides several benefits:

---

### javascript:S7776 — Arrays used only for existence checks should be Sets

**Severity**: Medium

Using 
`Array#includes()`
 for existence checks can lead to performance problems, especially with larger datasets.

---

### javascript:S7785 — Top-level await should be preferred over wrapped async operations

**Severity**: Medium

JavaScript’s top-level await feature allows you to use 
`await`
 directly at the module level without wrapping async operations in
functions. This makes code cleaner and more readable.

---

### javascript:S2310 — Loop counters should not be assigned within the loop body

**Severity**: Medium

Loop counters, such as variables used to track the iteration count in loops, should not be assigned from within the loop body to avoid unexpected
behavior and bugs. It can inadvertently lead to an infinite loop or make the loop behavior more complex and harder to reason about.

---

### javascript:S1854 — Unused assignments should be removed

**Severity**: Medium

Dead stores refer to assignments made to local variables that are subsequently never used or immediately overwritten. Such assignments are
unnecessary and don’t contribute to the functionality or clarity of the code. They may even negatively impact performance. Removing them enhances code
cleanliness and readability. Even if the unnecessary operations do not do any harm in terms of the program’s correctness, they are - at best - a waste
of computing resources.

**Noncompliant code example**

```javascript
function foo(y) {
  let x = 100; // Noncompliant: dead store
  x = 150;     // Noncompliant: dead store
  x = 200;
  return x + y;
}
```

**Compliant solution**

```javascript
function foo(y) {
  let x = 200; // Compliant: no unnecessary assignment
  return x + y;
}
```

---

### javascript:S6959 — "Array.reduce()" calls should include an initial value

**Severity**: Medium

The 
`Array.prototype.reduce()`
 method in JavaScript is used to apply a function against an accumulator and each element in the array
(from left to right) to reduce it to a single output value. It is a convenient method that can simplify logic in your code.

---

### javascript:S2639 — Empty character classes should not be used

**Severity**: Medium

Character classes in regular expressions will match any of the characters enclosed in the square brackets (
`[abc]`
 will match

`a`
, 
`b`
 or 
`c`
).

You can specify a range of characters using a hyphen (
`-`
). If the hyphen appears as the first or last character, it will be matched as
a literal hyphen.

An empty character class (
`[]`
) will not match any character because the set of matching characters is empty. So the regular expression
will not work as you intended.

```

/^foo[]/.test(str); // Noncompliant: always returns "false"

```

Use a non-empty character class or a different regular expression pattern that achieves the desired result.

```

/^foo/.test(str);

```

---

### javascript:S6397 — Character classes in regular expressions should not contain only one character

**Severity**: Medium

Character classes in regular expressions are a convenient way to match one of several possible characters by listing the allowed characters or
ranges of characters. If a character class contains only one character, the effect is the same as just writing the character without a character
class.

Thus, having only one character in a character class is usually a simple oversight that remained after removing other characters of the class.

Noncompliant code example

```

/a[b]c/
/[\^]/

```

Compliant solution

```

/abc/
/\^/
/a[*]c/ // Compliant, see Exceptions

```

Exceptions

This rule does not raise when the character inside the class is a metacharacter. This notation is sometimes used to avoid escaping (e.g.,

`[.]{3}`
 to match three dots).

---

### javascript:S1764 — Identical expressions should not be used on both sides of a binary operator

**Severity**: Medium

Using the same value on both sides of a binary operator is a code defect. In the case of logical operators, it is either a copy/paste error and,
therefore, a bug, or it is simply duplicated code and should be simplified. In the case of bitwise operators and most binary mathematical operators,
having the same value on both sides of an operator yields predictable results and should be simplified as well.

---

### javascript:S2589 — Boolean expressions should not be gratuitous

**Severity**: Medium

Control flow constructs like 
`if`
-statements allow the programmer to direct the flow of a program depending on a boolean expression.
However, if the condition is always true or always false, only one of the branches will ever be executed. In that case, the control flow construct and
the condition no longer serve a purpose; they become 
gratuitous
.

**Noncompliant code example**

```javascript
if (a) {
  if (a) { // Noncompliant
    doSomething();
  }
}
```

**Compliant solution**

```javascript
if (a) {
  if (b) {
    doSomething();
  }
}

// or
if (a) {
  doSomething();
}
```

---

### javascript:S1134 — Track uses of "FIXME" tags

**Severity**: Medium

`FIXME`
 tags are commonly used to mark places where a bug is suspected, but which the developer wants to deal with later.

Sometimes the developer will not have the time or will simply forget to get back to that tag.

This rule is meant to track those tags and to ensure that they do not go unnoticed.

```

function divide(numerator, denominator) {
  return numerator / denominator;              // FIXME denominator value might be  0
}

```

---

### javascript:S2234 — Parameters should be passed in the correct order

**Severity**: Medium

Consistent naming between arguments and parameters reduces the chances of making mistakes, such as passing the wrong value to a parameter or
omitting an argument in a function call. When the names of arguments in a function call match the names of the function parameters, it contributes to
clearer, more readable code.

---

### javascript:S3686 — Functions should be called consistently with or without "new"

**Severity**: Medium

JavaScript has the 
`new`
 keyword that is used in conjunction with constructor functions to create new instances of objects. When you use
the 
`new`
 keyword with a function, it signifies that the function is intended to be used as a constructor function to create objects.

---

### javascript:S5850 — Alternatives in regular expressions should be grouped when used with anchors

**Severity**: Medium

Regular expressions are used for pattern matching within strings. They can be defined upon special characters, meaning symbols or metacharacters
with a reserved meaning that convey specific instructions to the regex engine. These characters are not treated as literals but have special functions
in defining patterns, among which stand out anchors and disjunctions.

---

### javascript:S5860 — Names of regular expressions named groups should be used

**Severity**: Medium

When using regular expressions, a capturing group provides extra information about the matched pattern. Named groups will store the matched
contents on the 
`groups`
 property of the returned matches.

---

### javascript:S2201 — Return values from functions without side effects should not be ignored

**Severity**: Medium

When a function is called, it executes its block of code and uses a 
`return`
 statement within the function to specify the value that the
function will produce as its result. This returned value can then be used or assigned to a variable in the calling code.

---

### javascript:S4624 — Template literals should not be nested

**Severity**: Medium

Template literals, also known as template strings, allow for string interpolation and multiline strings in JavaScript. They provide a more
convenient and flexible way to work with strings compared to traditional string concatenation or manipulation.

---

### javascript:S5868 — Unicode Grapheme Clusters should be avoided inside regex character classes

**Severity**: Medium

When placing Unicode 
[Grapheme Clusters](https://unicode.org/glossary/#grapheme_cluster)
 (characters which require to be encoded in
multiple 
[Code Points](https://unicode.org/glossary/#code_point)
) inside a character class of a regular expression, this will likely lead
to unintended behavior.

---

### javascript:S5869 — Character classes in regular expressions should not contain the same character twice

**Severity**: Medium

Character classes in regular expressions are a convenient way to match one of several possible characters by listing the allowed characters or
ranges of characters. If the same character is listed twice in the same character class or if the character class contains overlapping ranges, this
has no effect.

**Noncompliant code example**

```javascript
/[0-99]/ // Noncompliant, this won't actually match strings with two digits
/[0-9.-_]/ // Noncompliant, .-_ is a range that already contains 0-9 (as well as various other characters such as capital letters)
/[a-z0-9\d]/ // Noncompliant, \d matches a digit and is equivalent to [0-9]
```

**Compliant solution**

```javascript
/[0-9]{1,2}/
/[0-9.\-_]/
/[a-z\d]/
```

---

### javascript:S1119 — Labels should not be used

**Severity**: Medium

In JavaScript, labels are identifiers that allow you to name blocks of code, such as loops and conditional statements. They are used in conjunction
with statements like 
`break`
 and 
`continue`
 to control the flow of execution within nested loops and conditionals.

---

### javascript:S2681 — Multiline blocks should be enclosed in curly braces

**Severity**: Medium

Having inconsistent indentation and omitting curly braces from a control structure, such as an 
`if`
 statement or 
`for`
 loop,
is misleading and can induce bugs.

---

### javascript:S3531 — Generators should explicitly "yield" a value

**Severity**: Medium

In JavaScript, a generator is a special type of function that can be paused and resumed during its execution. It allows you to define an iterative
algorithm by writing a function that can maintain its internal state and produce a sequence of values over time.

---

### javascript:S1121 — Assignments should not be made from within sub-expressions

**Severity**: Medium

A common code smell that can hinder the clarity of source code is making assignments within sub-expressions. This practice involves assigning a
value to a variable inside a larger expression, such as within a loop or a conditional statement.

**Noncompliant code example**

```javascript
if (val = value() && check()) { // Noncompliant
  // ...
}
```

**Compliant solution**

```javascript
val = value();
if (val && check()) {
  // ...
}
```

---

### javascript:S1479 — "switch" statements should not have too many "case" clauses

**Severity**: Medium

When 
`switch`
 statements have large sets of 
`case`
 clauses, it is usually an attempt to map two sets of data. A real map
structure would be more readable and maintainable, and should be used instead.

---

### javascript:S5843 — Regular expressions should not be too complicated

**Severity**: Medium

A complex regular expression is one that exhibits several or all of the following characteristics. It can be quite lengthy, containing multiple
nested or repeated groups, numerous alternations, extensive use of backreferences and escape characters, lookaheads, lookbehinds, and other advanced
features. Additionally, complex regular expressions may lack proper comments and documentation, making them challenging to comprehend and maintain.
Overly complicated regular expressions are hard to read and maintain and can easily cause hard-to-find bugs.

---

### javascript:S2692 — "indexOf" checks should not be for positive numbers

**Severity**: Medium

Most checks against an 
`indexOf`
 value compare it with -1 because 0 is a valid index. Checking against 
`> 0`
 ignores the
first element, which is likely a bug.

```

let arr = ["blue", "red"];

if (arr.indexOf("blue") > 0) { // Noncompliant
  // ...
}

```

Moreover, if the intent is merely to check the presence of the element, and if your browser version supports it, consider using

`includes`
 instead.

```

let arr = ["blue", "red"];

if (arr.includes("blue")) {
  // ...
}

```

This rule raises an issue when an 
`indexOf`
 value retrieved from an array is tested against 
`> 0`
.

---

### javascript:S3782 — Arguments to built-in functions should match documented types

**Severity**: Medium

The types of the arguments that built-in functions accept are specified in the JavaScript language specification. Calls to these functions should
conform to the documented types as they are designed to work with specific data types. If the arguments passed to these functions do not match the
expected types, it can lead to type errors or unexpected behavior.

---

### javascript:S3358 — Ternary operators should not be nested

**Severity**: Medium

Nested ternaries are hard to read and can make the order of operations complex to understand.

---

### javascript:S3579 — Array indexes should be numeric

**Severity**: Medium

In JavaScript, array indexes should be numeric because arrays are implemented as objects with numeric keys. When an array is created, it is
actually an object with properties that are numeric keys. These keys are used to access and assign values stored in the array.

---

### javascript:S3699 — The return value of void functions should not be used

**Severity**: Medium

When a function in JavaScript does not have a return statement or if it has a return statement without a value, it implicitly returns

`undefined`
. This means that a function without a return statement or with an empty return statement is, in a way, a "void" function, as it
doesn’t return any specific value.

Therefore, attempting to use the return value of a void function in JavaScript is meaningless, and it can lead to unexpected behavior or
errors.

Noncompliant code example

```

function foo() {
  console.log("Hello, World!");
}

let a = foo(); // Noncompliant: Assigning the return value of a void function

```

You should not use in any way the return value of a void function.

Compliant solution

```

function foo() {
  console.log("Hello, World!");
}

foo();

```

---

### javascript:S2123 — Values should not be uselessly incremented

**Severity**: Medium

A value that is incremented or decremented and then not stored is at best wasted code and at worst a bug.

Noncompliant code example

```

function pickNumber() {
  let i = 0;
  i = i++; // Noncompliant; i is still zero

  return i++; // Noncompliant; 0 returned
}

```

Compliant solution

```

function pickNumber() {
  let i = 0;
  i++;

  return ++i;
}

```

---

### javascript:S2137 — Special identifiers should not be bound or assigned

**Severity**: Medium

JavaScript has special identifiers that, while not reserved, still should not be used as identifiers. They form the JavaScript standard built-in
objects and global properties. They are available in all environments. Some examples are:

---

### javascript:S2251 — A "for" loop update clause should move the counter in the right direction

**Severity**: Medium

In a 
`for`
 loop, the update clause is responsible for modifying the loop counter variable in the appropriate direction to control the
loop’s iteration. It determines how the loop counter variable changes with each iteration of the loop. The loop counter should move in the right
direction to prevent infinite loops or unexpected behavior.

---

### javascript:S2757 — Non-existent operators '=+', '=-' and '=!' should not be used

**Severity**: Medium

Using operator pairs (
`=+`
, 
`=-`
, or 
`=!`
) that look like reversed single operators (
`+=`
,

`-=`
 or 
`!=`
) is confusing. They compile and run but do not produce the same result as their mirrored counterpart.

```

let target =-5;
let num = 3;

target =- num;  // Noncompliant: target = -3. Is that the expected behavior?
target =+ num; // Noncompliant: target = 3

```

This rule raises an issue when 
`=+`
, 
`=-`
, or 
`=!`
 are used without any space between the operators and when there
is at least one whitespace after.

Replace the operators with a single one if that is the intention

```

let target =-5;
let num = 3;

target -= num;  // target = -8

```

Or fix the spacing to avoid confusion

```

let target =-5;
let num = 3;

target = - num;  // target = -3

```

---

### javascript:S2870 — "delete" should not be used on arrays

**Severity**: Medium

The 
`delete`
 operator can be used to remove a property from any object. Arrays are objects, so the 
`delete`
 operator can be
used on them too.

---

### javascript:S2999 — "new" should only be used with functions and classes

**Severity**: Medium

JavaScript has the 
`new`
 keyword that is used in conjunction with constructor functions to create new instances of objects. When you use
the 
`new`
 keyword with a function, it signifies that the function is intended to be used as a constructor function to create objects.

---

### javascript:S1515 — Functions should not be defined inside loops

**Severity**: Medium

Defining functions inside loops in JavaScript can lead to several issues and is generally considered bad practice. The main problems associated
with this approach are related to performance, scope, and potential unintended behavior:

---

### javascript:S1529 — Bitwise operators should not be used in boolean contexts

**Severity**: Medium

Bitwise operations are operations that manipulate individual bits in binary representations of numbers. These operations work at the binary level,
treating numbers as sequences of 32 bits (in 32-bit environments) or 64 bits (in 64-bit environments). However, they should not be used in a boolean
context because they have different behaviors compared to logical operators when applied to boolean values:

---

### javascript:S1871 — Two branches in a conditional structure should not have exactly the same implementation

**Severity**: Medium

When the same code is duplicated in two or more separate branches of a conditional, it can make the code harder to understand, maintain, and can
potentially introduce bugs if one instance of the code is changed but others are not.

---

### javascript:S1439 — Only "while", "do", "for" and "switch" statements should be labelled

**Severity**: Medium

Labels allow specifying a target statement to jump to using the 
`break`
 or 
`continue`
 statements. It’s possible to assign a
label to any statement or block of statements. However, using it with any statement can create a complex control flow path, making the code harder to
understand and maintain.

---

### javascript:S3403 — Strict equality operators should not be used with dissimilar types

**Severity**: Medium

The strict equality operator in JavaScript is represented by three equal signs (
`===`
), the strict inequality with (
`!==`
).
It is used to compare two values for equality, but with an important difference from the regular equality operator (
`==`
). The strict
equality operator compares both value and type, while the regular equality operator only compares values after performing type coercion if
necessary.

---

### javascript:S3616 — Comma and logical OR operators should not be used in switch cases

**Severity**: Medium

The use of the comma operator and logical OR (||) operator within switch cases is not recommended. The switch statement is designed to evaluate a
single expression and compare it against multiple values. When you use the comma operator or logical OR operator within a case, you’re essentially
trying to match multiple values or conditions simultaneously: only the rightmost value will ever be considered with the comma operator, and the first
truthy operand will be handled with the logical OR operator.

---

### javascript:S3981 — Collection size and array length comparisons should make sense

**Severity**: Medium

The size of a collection and the length of an array are always greater than or equal to zero. Testing it doesn’t make sense, since the result is
always 
`true`
.

```

if (someSet.size >= 0) {...} // Noncompliant always true

const result = someArray.length >= 0;  // Noncompliant always true

```

Similarly testing that it is less than zero will always return 
`false`
.

```

if (someMap.size < 0) {...} // Noncompliant always false

```

Fix the code to properly check for emptiness if it was the intent, or remove the redundant code to keep the current behavior.

---

### javascript:S4619 — "in" should not be used on arrays

**Severity**: Medium

The 
`in`
 operator is used to check if a property is in an object or its 
[prototype chain](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Inheritance_and_the_prototype_chain)
.

---

### javascript:S3800 — Functions should always return the same type

**Severity**: Medium

Unlike strongly typed languages, JavaScript does not enforce a return type on a function. This means that different paths through a function can
return different types of values.

---

### javascript:S3923 — All branches in a conditional structure should not have exactly the same implementation

**Severity**: Medium

Having all branches of a 
`switch`
 or 
`if`
 chain with the same implementation indicates a problem.

---

### javascript:S6019 — Reluctant quantifiers in regular expressions should be followed by an expression that can't match the empty string

**Severity**: Medium

When a reluctant (or lazy) quantifier is followed by a pattern that can match the empty string or directly by the end of the regex, it will always
match zero times for 
`*?`
 or one time for 
`+?`
. If a reluctant quantifier is followed directly by the end anchor
(
`$`
), it behaves indistinguishably from a greedy quantifier while being less efficient.

This is likely a sign that the regex does not work as intended.

Noncompliant code example

```

str.split(/.*?x?/); // Noncompliant, this will behave just like "x?"
/^.*?$/.test(str); // Noncompliant, replace with ".*"

```

Compliant solution

```

str.split(/.*?x/);
/^.*$/.test(str);

```

---

### javascript:S6035 — Single-character alternations in regular expressions should be replaced with character classes

**Severity**: Medium

When an alternation contains multiple alternatives that consist of a single character, it can be rewritten as a character class. This should be
preferred because it is more efficient and can even help prevent stack overflows when used inside a repetition (see rule 
[S5998](https://sonarqube.internal.philips/coding_rules#rule_key=javascript%3AS5998)
).

Noncompliant code example

```

/a|b|c/; // Noncompliant

```

Compliant solution

```

/[abc]/;
// or
/[a-c]/;

```

---

### javascript:S125 — Sections of code should not be commented out

**Severity**: Medium

Commented-out code distracts the focus from the actual executed code. It creates a noise that increases maintenance code. And because it is never
executed, it quickly becomes out of date and invalid.

Commented-out code should be deleted and can be retrieved from source control history if required.

---

### javascript:S1848 — Objects should not be created to be dropped immediately without being used

**Severity**: Medium

Creating an object without assigning it to a variable or using it in any function means the object is essentially created for no reason and may be
dropped immediately without being used. Most of the time, this is due to a missing piece of code and could lead to an unexpected behavior.

---

### javascript:S4043 — Array-mutating methods should not be used misleadingly

**Severity**: Medium

In JavaScript, some 
`Array`
 methods do not mutate the existing array that the method was called on, but instead return a new array.
Other methods mutate the array, and their return value differs depending on the method.

---

### javascript:S4165 — Assignments should not be redundant

**Severity**: Medium

The transitive property says that if 
`a == b`
 and 
`b == c`
, then 
`a == c`
. In such cases, there’s no point in
assigning 
`a`
 to 
`c`
 or vice versa because they’re already equivalent.

This rule raises an issue when an assignment is useless because the assigned-to variable already holds the value on all execution paths.

Noncompliant code example

```

a = b;
c = a;
b = c; // Noncompliant: c and b are already the same

```

Compliant solution

```

a = b;
c = a;

```

---

### javascript:S5256 — Tables should have headers

**Severity**: Medium

Table headers are essential to enhance the accessibility of a table’s data, particularly for assistive technologies like screen readers. These
headers provide the necessary context to transform data into information. Without headers, users get rapidly lost in the flow of data.

**Noncompliant code example**

```javascript
<table> <!-- Noncompliant -->
  <tr>
    <td>Name</td>
    <td>Age</td>
  </tr>
  <tr>
    <td>John Doe</td>
    <td>24</td>
  </tr>
  <tr>
    <td>Alice Doe</td>
    <td>54</td>
  </tr>
</table>
```

**Compliant solution**

```javascript
<table>
  <tr>
    <th scope="col">Name</th>
    <th scope="col">Age</th>
  </tr>
  <tr>
    <td>John Doe</td>
    <td>24</td>
  </tr>
  <tr>
    <td>Alice Doe</td>
    <td>54</td>
  </tr>
</table>
```

---

### javascript:S6351 — Regular expressions with the global flag should be used with caution

**Severity**: Medium

Regular expressions in JavaScript can have a global flag (
`/g`
) that enables global searching and matching. While this flag can be
useful in certain scenarios, it should be used with caution. When a regular expression has the global flag enabled, it remembers the position of the
last match and continues searching for subsequent matches from that position. This behavior can lead to unexpected results if you’re not careful and
be a source of bugs that are tricky to debug.

---

### javascript:S4143 — Collection elements should not be replaced unconditionally

**Severity**: Medium

Storing a value inside a collection at a given key or index and then unconditionally overwriting it without reading the initial value is a case of
a "dead store".

This rule detects repeatedly adding an element at the same index or key in a collection or adding identical elements to a set.

```

fruits[1] = "banana";
fruits[1] = "apple";  // Noncompliant

myMap.set("key", 1);
myMap.set("key", 2); // Noncompliant

mySet.add(1);
mySet.add(1); // Noncompliant

```

This practice is redundant and will cause confusion for the reader. More importantly, it is often an error and not what the developer intended to
do.

---

### javascript:S4144 — Functions should not have identical implementations

**Severity**: Medium

Two functions having the same implementation are suspicious. It might be that something else was intended. Or the duplication is intentional, which
becomes a maintenance burden.

---

### javascript:S6323 — Alternation in regular expressions should not contain empty alternatives

**Severity**: Medium

Alternation is used to match a single regular expression out of several possible regular expressions. If one of the alternatives is empty it would
match any input, which is most probably a mistake.

---

### javascript:S6324 — Regular expressions should not contain control characters

**Severity**: Medium

Entries in the ASCII table below code 32 are known as control characters or non-printing characters. As they are not common in JavaScript strings,
using these invisible characters in regular expressions is most likely a mistake.

```

const pattern1 = /\x1a/;             // Noncompliant: 1a (23 base 10) is less than 32
const pattern2 = new RegExp('\x1a'); // Noncompliant: 1a (23 base 10) is less than 32

```

Instead, one should only match printable characters in regular expressions.

```

const pattern1 = /\x20/;
const pattern2 = new RegExp('\x20');

```

---

### javascript:S6326 — Regular expressions should not contain multiple spaces

**Severity**: Medium

Multiple spaces in a regular expression can make it hard to tell how many spaces should be matched. It’s more readable to use only one space and
then indicate with a quantifier how many spaces are expected.

Noncompliant code example

```

const pattern = /Hello,   world!/;

```

Compliant solution

```

const pattern = /Hello, {3}world!/;

```

---

### javascript:S6328 — Replacement strings should reference existing regular expression groups

**Severity**: Medium

In JavaScript, the 
`String.prototype.replace()`
 method is used to replace parts of a string with new substrings. It allows you to
perform simple to complex string replacements based on either a static string or a regular expression pattern.

---

### javascript:S4030 — Collection contents should be used

**Severity**: Medium

A collection is a data structure that holds multiple values, such as an array or a map. If a collection is declared and populated, but its values
are never read anywhere in the code, it can be considered unused code. This can be due to some refactoring, copy-pasting, or typing errors.

---

### javascript:S6331 — Regular expressions should not contain empty groups

**Severity**: Medium

There are several reasons to use a group in a regular expression:

---
