# SonarQube Java Review Standards

This rule defines the SonarQube-based Java code review criteria. Apply these
standards when the target project contains Java source code. Rules are sourced
from SonarQube's Java analyzer and organized by review category.

Each rule includes its SonarQube rule key, severity, explanation, and
Noncompliant/Compliant code examples to guide pattern matching during review.

**Total: 145 rules (45 Blocker, 100 High)**

## Severity Mapping

| SonarQube Severity | Review Severity | Action |
|--------------------|----------------|--------|
| **Blocker** | Critical | Must fix before acceptance |
| **High** | High | Must fix or have documented mitigation plan |

---

## 1. Security Rules (37 rules)

These rules detect security vulnerabilities including injection attacks, credential leaks, cryptographic weaknesses, and authentication flaws.

### java:S2115 — A secure password should be used when connecting to a database

**Severity**: Blocker

| Trustworthy Which component or framework contains the issue? The following code uses an empty password to connect to a Postgres database. The vulnerability can be fixed by using a strong password retrieved from Properties. This database.password property is set during deployment. Its value should be strong and different for each database.

**Noncompliant code example**

**Compliant solution**

```java
String password = System.getProperty("database.password");
Connection conn = DriverManager.getConnection("jdbc:derby:memory:myDB;create=true", "login", password);

Pitfalls
Hard-coded passwords

It could be tempting to replace the empty password with a hard-coded one. Hard-coding passwords in the code can pose significant security risks. Here are a few reasons why it is not recommended:

Security Vulnerability: Hard-coded passwords can be easily discovered by anyone who has access to the code, such as other developers or attackers. This can lead to unauthorized access to the database and potential data breaches.
Lack of Flexibility: Hard-coded passwords make it difficult to change the password without modifying the code. If the password needs to be updated, it would require recompiling and redeploying the code, which can be time-consuming and error-prone.
Version Control Issues: Storing passwords in code can lead to version control issues. If the code is shared or stored in a version control system, the password will be visible to anyone with access to the repository, which is a security risk.

To mitigate these risks, it is recommended to use secure methods for storing and retrieving passwords, such as using environment variables, configuration files, or secure key management systems. These methods allow for better security, flexibility, and separation of sensitive information from the codebase.
```

---

### java:S2755 — XML parsers should not be vulnerable to XXE attacks

**Severity**: Blocker

Which component or framework contains the issue? The following code contains examples of XML parsers that have external entity processing enabled. As a result, the parsers are vulnerable to XXE attacks if an attacker can control the XML file that is processed.

**Noncompliant code example**

```java
import org.dom4j.io.SAXReader;

public void decode() {
```

**Compliant solution**

```java
import org.dom4j.io.SAXReader;

public void decode() {

    SAXReader xmlReader = new SAXReader();
    xmlReader.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);

}
```

---

### java:S3753 — "@Controller" classes that use "@SessionAttributes" must call "setComplete" on their "SessionStatus" objects

**Severity**: Blocker

Skip to rules filters Quality Profiles Quality Gates Clear All Filters Software quality Security Hotspots Show Security Hotspots Only Available Since Security Category Quality Profile Prioritized Rules "@Controller" classes that use "@SessionAttributes" must call "setComplete" on their "SessionStatus" objects A Spring @Controller that uses @SessionAttributes is designed to handle a stateful / multi-post form. Such @Controllers use the specified @SessionAttributes to store data on the server between requests. That data should be cleaned up when the session is over, but unless setComplete() is called on the SessionStatus object from a @RequestMapping method, neither Spring nor the JVM will know it’s time to do that. Note that the SessionStatus object must be passed to that method as a...

**Noncompliant code example**

```java
@Controller
```

**Compliant solution**

```java
@Controller
@SessionAttributes("hello")
public class HelloWorld {

  @RequestMapping("/greet", method = GET)
  public String greet(String greetee) {

    return "Hello " + greetee;
  }

  @RequestMapping("/goodbye", method = POST)
  public String goodbye(SessionStatus status) {
    //...
    status.setComplete();
  }

}
```

---

### java:S6373 — XML parsers should not allow inclusion of arbitrary files

**Severity**: Blocker

symbolic-execution | Conventional Which component or framework contains the issue? The following code is vulnerable because it explicitly enables the xinclude feature.

**Noncompliant code example**

```java
import org.dom4j.io.SAXReader;

SAXReader xmlReader = new SAXReader();
```

**Compliant solution**

```java
import org.dom4j.io.SAXReader;

SAXReader xmlReader = new SAXReader();

xmlReader.setFeature("http://apache.org/xml/features/xinclude", false);
```

---

### java:S6437 — Credentials should not be hard-coded

**Severity**: Blocker

| Trustworthy Revoke the secret Revoke any leaked secrets and remove them from the application source code. Before revoking the secret, ensure that no other applications or processes are using it. Other usages of the secret will also be impacted when the secret is revoked. Analyze recent secret use When available, analyze authentication logs to identify any unintended or malicious use of the secret since its disclosure date. Doing this will allow determining if an attacker took advantage of the leaked secret and to what extent. This operation should be part of a global incident response process. Use a secret vault A secret vault should be used to generate and store the new secret. This will ensure the secret’s security and prevent any further unexpected disclosure. Depending on the...

**Noncompliant code example**

```java
import org.h2.security.SHA256;


String inputString = "s3cr37";

byte[] key         = inputString.getBytes();
```

**Compliant solution**

```java
import org.h2.security.SHA256;


String inputString = System.getenv("SECRET");

byte[] key         = inputString.getBytes();


SHA256.getHMAC(key, message);
```

---

### javasecurity:S2076 — OS commands should not be vulnerable to command injection attacks

**Severity**: Blocker

Which component or framework contains the issue? Apache Commons Java Lang Package The following code is vulnerable to command injections because it is using untrusted inputs to set up a new process. Therefore an attacker can execute an arbitrary program that is installed on the system.

**Noncompliant code example**

```java
@Controller
public class ExampleController
{
    @GetMapping(value = "/exec")
    public void exec(@RequestParam("command") String command) throws IOException {


        CommandLine cmd = new CommandLine(command);
        DefaultExecutor executor = new DefaultExecutor();
        executor.execute(cmd);

    }
}
```

**Compliant solution**

```java
@Controller
public class ExampleController
{
    @GetMapping(value = "/exec")
    public void exec(@RequestParam("command") String command) throws IOException {


        List<String> allowedCmds = new ArrayList<String>();
        allowedCmds.add("/bin/ls");
        allowedCmds.add("/bin/cat");

        if (allowedCmds.contains(command)){
            CommandLine cmd = new CommandLine(command);
            DefaultExecutor executor = new DefaultExecutor();
            executor.execute(cmd);
        }

    }
}
```

---

### javasecurity:S2078 — LDAP queries should not be vulnerable to injection attacks

**Severity**: Blocker

Which component or framework contains the issue? Java JNDI API The following noncompliant code is vulnerable to LDAP injections because untrusted data is concatenated to an LDAP query without prior sanitization or validation.

**Noncompliant code example**

```java
import javax.naming.directory.DirContext;
import javax.naming.directory.SearchControls;

public boolean authenticate(HttpServletRequest req, DirContext ctx) throws NamingException {
  String user = req.getParameter("user");
  String pass = req.getParameter("pass");


  String filter = "(&(uid=" + user + ")(userPassword=" + pass + "))";



  NamingEnumeration<SearchResult> results = ctx.search("ou=system", filter, new SearchControls());

  return results.hasMore();
}
```

**Compliant solution**

```java
import javax.naming.directory.DirContext;
import javax.naming.directory.SearchControls;

public boolean authenticate(HttpServletRequest req, DirContext ctx) throws NamingException {
  String user = req.getParameter("user");
  String pass = req.getParameter("pass");


  String filter = "(&(uid={0})(userPassword={1}))";



  NamingEnumeration<SearchResult> results = ctx.search("ou=system", filter, new String[]{user, pass}, new SearchControls());

  return results.hasMore();
}
```

---

### javasecurity:S2083 — I/O function calls should not be vulnerable to path injection attacks

**Severity**: Blocker

Which component or framework contains the issue? Java I/O API The following code is vulnerable to path injection as it creates a path using untrusted data without validation. In this particular case, the code can be exploited with the following input to delete arbitrary files outside of the intended directory: ../../../../

**Noncompliant code example**

```java
@Controller
public class ExampleController
{

    static private String targetDirectory = "/path/to/target/directory/";


    @GetMapping(value = "/delete")
    public void delete(@RequestParam("filename") String filename) throws IOException {


        File file = new File(targetDirectory + filename);

        file.delete();
    }
}
```

**Compliant solution**

```java
@Controller
public class ExampleController
{

    private static String targetDirectory = "/path/to/target/directory/";
    private static Path targetPath        = new File(targetDirectory).toPath().normalize();


    @GetMapping(value = "/delete")
    public void delete(@RequestParam("filename") String filename) throws IOException {


        File file = new File(targetPath + filename);

        if (!file.toPath().normalize().startsWith(targetPath)) {
            throw new IOException("Entry is outside of the target directory");
        }


        file.delete();
    }
}
```

---

### javasecurity:S2091 — XPath expressions should not be vulnerable to injection attacks

**Severity**: Blocker

Which component or framework contains the issue? Apache Commons Java XML API The following noncompliant code is vulnerable to XPath injections because untrusted data is concatenated to an XPath query without prior validation.

**Noncompliant code example**

```java
public Book findBook(HttpServletRequest req, Author author) throws JXPathException {
  String name = request.getParameter("name");

  JXPathContext context = JXPathContext.newContext(author);


  return (Book)context.getValue("books[@name='" + name + "']");

}
```

**Compliant solution**

```java
public Book findBook(HttpServletRequest req, Author author) throws JXPathException {
  String name = request.getParameter("name");

  JXPathContext context = JXPathContext.newContext(author);

  context.getVariables().declareVariable("name", name);



  return (Book)context.getValue("books[@name=$name]");

}
```

---

### javasecurity:S3649 — Database queries should not be vulnerable to injection attacks

**Severity**: Blocker

Which component or framework contains the issue? Java JDBC API Spring Data Cassandra Spring Data Neo4j The following code is vulnerable to SQL++ injection because user-controlled data is inserted directly into a query string. The application assumes that incoming data always has a specific range of characters, and ignores that some characters may change the query logic to a malicious one.

**Noncompliant code example**

```java
import com.couchbase.client.java.Cluster;


@RestController
public class ApiController
{

    private final Cluster couchbaseCluster;


    @GetMapping("/find")
    public List<Person> find(@RequestParam("name") String name) {

        QueryResult result = couchbaseCluster.query("SELECT * FROM `bucket` WHERE name = '" + name + "'");
        return result.rowsAs(Person.class);

    }
}
```

**Compliant solution**

```java
org.springframework.data.couchbase.core.query.Query;


@RestController
public class ApiController
{

    private final CouchbaseTemplate couchbaseTemplate;


    @GetMapping("/find")
    public List<Person> find(@RequestParam("name") String name) {

        Query query = Query.query(QueryCriteria.where("name").eq(name));
        return couchbaseTemplate.findByQuery(Person.class).matching(query).all();

    }
}
```

---

### javasecurity:S5131 — Endpoints should not be vulnerable to reflected cross-site scripting (XSS) attacks

**Severity**: Blocker

Which component or framework contains the issue? The following code is vulnerable to cross-site scripting because JSP does not auto-escape variables. User input embedded in HTML code should be HTML-encoded to prevent the injection of additional code. This can be done with the OWASP Java Encoder or similar libraries.

**Noncompliant code example**

```java
<%@page contentType="text/html" pageEncoding="UTF-8"%>
<%@taglib prefix="e" uri="https://www.owasp.org/index.php/OWASP_Java_Encoder_Project" %>
<!doctype html>
<html>
 <body>
```

**Compliant solution**

```java
<%@page contentType="text/html" pageEncoding="UTF-8"%>
<%@taglib prefix="e" uri="https://www.owasp.org/index.php/OWASP_Java_Encoder_Project" %>
<!doctype html>
<html>
 <body>

  <h1>${e:forHtml(param.title)}</h1>

 </body>
</html>
```

---

### javasecurity:S5135 — Deserialization should not be vulnerable to injection attacks

**Severity**: Blocker

Which component or framework contains the issue? Java I/O API The following code is vulnerable to deserialization attacks because it deserializes HTTP data without validating it first.

**Noncompliant code example**

```java
public class RequestProcessor {
  protected void doGet(HttpServletRequest request, HttpServletResponse response) {
    ServletInputStream servletIS = request.getInputStream();

    ObjectInputStream  objectIS  = new ObjectInputStream(servletIS);

    Object input                 = objectIS.readObject();
  }
}
```

**Compliant solution**

```java
public class SecureObjectInputStream extends ObjectInputStream {

  @Override
  protected Class<?> resolveClass(ObjectStreamClass osc) throws IOException, ClassNotFoundException {

    List<String> approvedClasses = new ArrayList<String>();
    approvedClasses.add(AllowedClass1.class.getName());
    approvedClasses.add(AllowedClass2.class.getName());

    if (!approvedClasses.contains(osc.getName())) {
      throw new InvalidClassException("Unauthorized deserialization", osc.getName());
    }

    return super.resolveClass(osc);
  }
}


public class RequestProcessor {
  protected void doGet(HttpServletRequest request, HttpServletResponse response) {
    ServletInputStream servletIS = request.getInputStream();

    ObjectInputStream  objectIS  = new SecureObjectInputStream(servletIS);

    Object input                 = objectIS.readObject();
  }
}
```

---

### javasecurity:S5146 — HTTP request redirections should not be open to forging attacks

**Severity**: Blocker

Which component or framework contains the issue? The following noncompliant code example is vulnerable to open redirection as it constructs a URL with user-controllable data. This URL is then used to redirect the user without being first validated. An attacker can leverage this to manipulate users into performing unwanted redirects.

**Noncompliant code example**

```java
protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws IOException {
  String location = req.getParameter("url");

  resp.sendRedirect(location);

}
```

**Compliant solution**

```java
protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws IOException {
  String location = req.getParameter("url");


  List<String> allowedHosts = new ArrayList<String>();
  allowedHosts.add("https://trusted1.example.com/");
  allowedHosts.add("https://trusted2.example.com/");

  if (allowedHosts.contains(location))
    resp.sendRedirect(location);

}
```

---

### javasecurity:S5147 — NoSQL operations should not be vulnerable to injection attacks

**Severity**: Blocker

Which component or framework contains the issue? Legacy Mongo Java API Spring Data MongoDB Spring Data Redis The following code is vulnerable to NoSQL injections because untrusted data is concatenated to the $where operator. This operator indicates to the backend that the expression needs to be interpreted, resulting in code injection.

**Noncompliant code example**

```java
import com.mongodb.MongoClient;
import com.mongodb.DB;
import com.mongodb.DBCollection;
import com.mongodb.BasicDBObject;

protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws UnknownHostException
{
    String input = req.getParameter("input");

    MongoClient mongoClient = new MongoClient();
    DB database             = mongoClient.getDB("ExampleDatabase");
    DBCollection collection = database.getCollection("exampleCollection");
    BasicDBObject query     = new BasicDBObject();


    query.append("$where", "this.field == \"" + input + "\"");


    collection.find(query);
}
```

**Compliant solution**

```java
import com.mongodb.MongoClient;
import com.mongodb.DB;
import com.mongodb.DBCollection;
import com.mongodb.BasicDBObject;

protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws UnknownHostException
{
    String input = req.getParameter("input");

    MongoClient mongoClient = new MongoClient();
    DB database             = mongoClient.getDB("ExampleDatabase");
    DBCollection collection = database.getCollection("exampleCollection");
    BasicDBObject query     = new BasicDBObject();


    query.append("field", input);


    collection.find(query);
}
```

---

### javasecurity:S5334 — Dynamic code execution should not be vulnerable to injection attacks

**Severity**: Blocker

Which component or framework contains the issue? Commons Compiler The following code is vulnerable to arbitrary code execution because it compiles and runs HTTP data.

**Noncompliant code example**

```java
import org.codehaus.janino.ScriptEvaluator;

@Controller
public class ExampleController
{
    @GetMapping(value = "/")
    public void exec(@RequestParam("message") String message) throws IOException, InvocationTargetException {
        ScriptEvaluator se = new ScriptEvaluator();
```

**Compliant solution**

```java
import org.codehaus.janino.ScriptEvaluator;

@Controller
public class ExampleController
{
    @GetMapping(value = "/")
    public void exec(@RequestParam("message") String message) throws IOException, InvocationTargetException {
        ScriptEvaluator se = new ScriptEvaluator();

        se.setParameters(new String[] { "input" }, new Class[] { String.class });
        se.cook("System.out.println(input);");
        se.evaluate(new Object[] { message });

    }
}
```

---

### javasecurity:S5496 — Server-side templates should not be vulnerable to injection attacks

**Severity**: Blocker

Which component or framework contains the issue?

**Noncompliant code example**

```java
The following code example is vulnerable to a Server-Side Template Injection attack because it builds a template string from a user input without control or sanitation.

@GetMapping("/example")
public String example(@RequestParam("title") String title) throws CompilationFailedException, ClassNotFoundException, IOException {

    String templateString = "h1('" + title + "')";

    TemplateConfiguration config = new TemplateConfiguration();
    MarkupTemplateEngine engine = new MarkupTemplateEngine(config);
```

**Compliant solution**

```java
@GetMapping("/example")
public String example(@RequestParam("title") String title) throws CompilationFailedException, ClassNotFoundException, IOException {

    String templateString = "h1(title)";

    Map<String, Object> ctx = new HashMap<>();
    ctx.put("title", title);


    TemplateConfiguration config = new TemplateConfiguration();
    MarkupTemplateEngine engine = new MarkupTemplateEngine(config);

    Template template = engine.createTemplate(templateString);
    Writable out = template.make(ctx);

    return out.toString();
}
```

---

### javasecurity:S6096 — Extracting archives should not lead to zip slip vulnerabilities

**Severity**: Blocker

Which component or framework contains the issue? Java I/O API The following code is vulnerable to Zip Slip as it is constructing a path using an archive entry name. This path is then used to copy a file without being validated first. Therefore, it can be leveraged by an attacker to overwrite arbitrary files.

**Noncompliant code example**

```java
public class Example {

    static private String targetDirectory = "/example/directory/";

    public void ExtractEntry(ZipFile zipFile) throws IOException {

        Enumeration<? extends ZipEntry> entries = zipFile.entries();
        ZipEntry entry = entries.nextElement();
        InputStream inputStream = zipFile.getInputStream(entry);

        File file = new File(targetDirectory + entry.getName());


        Files.copy(inputStream, file.toPath(), StandardCopyOption.REPLACE_EXISTING);

    }
}
```

**Compliant solution**

```java
public class Example {

    static private String targetDirectory = "/example/directory/";

    public void ExtractEntry(ZipFile zipFile) throws IOException {

        Enumeration<? extends ZipEntry> entries = zipFile.entries();
        ZipEntry entry = entries.nextElement();
        InputStream inputStream = zipFile.getInputStream(entry);

        File file = new File(targetDirectory + entry.getName());


        String canonicalDestinationPath = file.getCanonicalPath();

        if (canonicalDestinationPath.startsWith(targetDirectory)) {
            Files.copy(inputStream, file.toPath(), StandardCopyOption.REPLACE_EXISTING, LinkOption.NOFOLLOW_LINKS);
        }

    }
}
```

---

### javasecurity:S6384 — Components should not be vulnerable to intent redirection

**Severity**: Blocker

Which component or framework contains the issue? This code is vulnerable to intent injection attacks because it starts a new activity from a user-provided intent without prior validation.

**Noncompliant code example**

```java
public class MainActivity extends AppCompatActivity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        Intent intent = getIntent();
        Intent forward = (Intent) intent.getParcelableExtra("anotherintent");

        startActivity(forward);

    }
}
```

**Compliant solution**

```java
public class MainActivity extends AppCompatActivity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        Intent intent = getIntent();
        Intent forward = (Intent) intent.getParcelableExtra("anotherintent");

        ComponentName name = forward.resolveActivity(getPackageManager());
        if (name.getPackageName().equals("safePackage") && name.getClassName().equals("safeClass")) {
            startActivity(forward);
        }

    }
}
```

---

### javasecurity:S7606 — WebViews should not be vulnerable to cross-app scripting attacks

**Severity**: Blocker

Which component or framework contains the issue?

**Noncompliant code example**

```java
public class ExampleActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        WebView aWebView = new WebView(this);
        aWebView.getSettings().setJavaScriptEnabled(true);
        setContentView(aWebView);

        String name = getIntent().getStringExtra("name");
        if (name == null) {

            name = "Guest";

        }
```

**Compliant solution**

```java
public class ExampleActivity extends AppCompatActivity {


    private static final Pattern NAME_REGEX = Pattern.compile("^[a-zA-Z ]+$");


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        WebView aWebView = new WebView(this);
        aWebView.getSettings().setJavaScriptEnabled(true);
        setContentView(aWebView);

        String name = getIntent().getStringExtra("name");
        if (name == null) {

            uname = "Guest";

        }


        if (NAME_REGEX.matcher(untrustedName).matches()) {
            aWebView.evaluateJavascript("greeting('" + name + "')";, null);
        }

    }
}
```

---

### java:S2053 — Password hashing functions should use an unpredictable salt

**Severity**: High

| Trustworthy Which component or framework contains the issue? The following code contains examples of hard-coded salts.

**Noncompliant code example**

```java
import javax.crypto.spec.PBEParameterSpec;

public void hash() {

    byte[] salt = "salty".getBytes();
```

**Compliant solution**

```java
import java.security.SecureRandom;

import javax.crypto.spec.PBEParameterSpec;

public void hash() {

    SecureRandom random = new SecureRandom();
    byte[] salt = new byte[16];
    random.nextBytes(salt);

    PBEParameterSpec cipherSpec = new PBEParameterSpec(salt, 10000);

}
```

---

### java:S2254 — "HttpServletRequest.getRequestedSessionId()" should not be used

**Severity**: High

| Trustworthy Which component or framework contains the issue? In both examples, a session ID is used to check whether a user’s session is still active. In the noncompliant example, the session ID supplied by the user is used. In the compliant example, the session ID defined by the server is used instead.

**Noncompliant code example**

**Compliant solution**

```java
if (isActiveSession(request.getSession().getId())) {

    // ...
}
```

---

### java:S3305 — Factory method injection should be used in "@Configuration" classes

**Severity**: High

When @Autowired is used, dependencies need to be resolved when the class is instantiated, which may cause early initialization of beans or lead the context to look in places it shouldn’t to find the bean. To avoid this tricky issue and optimize the way the context loads, dependencies should be requested as late as possible. That means using parameter injection instead of field injection for dependencies that are only used in a single @Bean method.

**Noncompliant code example**

```java
@Configuration
public class ​FooConfiguration {
```

**Compliant solution**

```java
@Configuration
public class ​FooConfiguration {

 @Bean
  public ​MyService myService(DataSource dataSource) {
    return new ​MyService(dataSource);
  }
}
```

---

### java:S3329 — Cipher Block Chaining IVs should be unpredictable

**Severity**: High

| Trustworthy Which component or framework contains the issue? Java Cryptography Extension

**Noncompliant code example**

```java
import java.nio.charset.StandardCharsets;
import java.security.NoSuchAlgorithmException;
import java.security.InvalidKeyException;
import java.security.InvalidAlgorithmParameterException;
import javax.crypto.Cipher;
import javax.crypto.spec.IvParameterSpec;
import javax.crypto.spec.SecretKeySpec;
import javax.crypto.NoSuchPaddingException;

public void encrypt(String key, String plainText) {


    byte[] RandomBytes = "7cVgr5cbdCZVw5WY".getBytes(StandardCharsets.UTF_8);



    IvParameterSpec iv   = new IvParameterSpec(RandomBytes);

    SecretKeySpec keySpec = new SecretKeySpec(key.getBytes(StandardCharsets.UTF_8), "AES");

    try {
        Cipher cipher = Cipher.getInstance("AES/CBC/PKCS5Padding");
        cipher.init(Cipher.ENCRYPT_MODE, keySpec, iv);

    } catch(NoSuchAlgorithmException|InvalidKeyException|
            NoSuchPaddingException|InvalidAlgorithmParameterException e) {
        // ...
    }
}
```

**Compliant solution**

```java
In this example, the code explicitly uses a number generator that is considered strong.

import java.nio.charset.StandardCharsets;

import java.security.SecureRandom;

import java.security.NoSuchAlgorithmException;
import java.security.InvalidKeyException;
import java.security.InvalidAlgorithmParameterException;
import javax.crypto.Cipher;
import javax.crypto.spec.IvParameterSpec;
import javax.crypto.spec.SecretKeySpec;
import javax.crypto.NoSuchPaddingException;

public void encrypt(String key, String plainText) {


    SecureRandom random = new SecureRandom();
    byte[] randomBytes  = new byte[128];
    random.nextBytes(randomBytes);



    IvParameterSpec iv   = new IvParameterSpec(randomBytes);

    SecretKeySpec keySpec = new SecretKeySpec(key.getBytes(StandardCharsets.UTF_8), "AES");

    try {
        Cipher cipher = Cipher.getInstance("AES/CBC/PKCS5Padding");
        cipher.init(Cipher.ENCRYPT_MODE, keySpec, iv);

    } catch(NoSuchAlgorithmException|InvalidKeyException|
            NoSuchPaddingException|InvalidAlgorithmParameterException e) {
```

---

### java:S4347 — Secure random number generators should not output predictable values

**Severity**: High

Which component or framework contains the issue? The following code uses a cryptographically strong random number generator to generate data that is not cryptographically strong.

**Noncompliant code example**

```java
SecureRandom sr = new SecureRandom();
```

**Compliant solution**

```java
SecureRandom sr = new SecureRandom();
int v = sr.next(32);


This solution is available for JDK 1.8 and higher.

SecureRandom sr = SecureRandom.getInstanceStrong();

int v = sr.next(32);
```

---

### java:S4423 — Weak SSL/TLS protocols should not be used

**Severity**: High

| Trustworthy Which component or framework contains the issue? Java Cryptography Extension

**Noncompliant code example**

```java
import javax.net.ssl.SSLContext;
import java.security.NoSuchAlgorithmException;

public static void main(String[] args) {
    try {
```

**Compliant solution**

```java
import javax.net.ssl.SSLContext;
import java.security.NoSuchAlgorithmException;

public static void main(String[] args) {
    try {

        SSLContext.getInstance("TLSv1.2");

    } catch (NoSuchAlgorithmException e) {
        // ...
    }
}
```

---

### java:S4426 — Cryptographic keys should be robust

**Severity**: High

| Trustworthy Which component or framework contains the issue? Java Cryptography Extension The following code examples either explicitly or implicitly generate keys. Note that there are differences in the size of the keys depending on the algorithm. Due to the mathematical properties of the algorithms, the security requirements for the key size vary depending on the algorithm. For example, a 256-bit ECC key provides about the same level of security as a 3072-bit RSA key and a 128-bit symmetric key.

**Noncompliant code example**

```java
Here is an example of a private key generation with RSA:

import java.security.KeyPairGenerator;
import java.security.NoSuchAlgorithmException;

public static void main(String[] args) {
    try {
        KeyPairGenerator keyPairGenerator = KeyPairGenerator.getInstance("RSA");
```

**Compliant solution**

```java
import java.security.KeyPairGenerator;
import java.security.NoSuchAlgorithmException;

public static void main(String[] args) {
    try {
        KeyPairGenerator keyPairGenerator = KeyPairGenerator.getInstance("RSA");

        keyPairGenerator.initialize(2048);


    } catch (NoSuchAlgorithmException e) {
        // ...
    }
}

import java.security.KeyPairGenerator;
import java.security.NoSuchAlgorithmException;
import java.security.InvalidAlgorithmParameterException;
import java.security.spec.ECGenParameterSpec;

public static void main(String[] args) {
    try {
        KeyPairGenerator keyPairGenerator    = KeyPairGenerator.getInstance("EC");

        ECGenParameterSpec ellipticCurveName = new ECGenParameterSpec("secp256r1");

        keyPairGenerator.initialize(ellipticCurveName);

    } catch (NoSuchAlgorithmException | InvalidAlgorithmParameterException e) {
        // ...
    }
}
```

---

### java:S4433 — LDAP connections should be authenticated

**Severity**: High

The following code indicates an anonymous LDAP authentication vulnerability because it binds to a remote server using an Anonymous Simple authentication mechanism.

**Noncompliant code example**

```java
// Set up the environment for creating the initial context
Hashtable<String, Object> env = new Hashtable<String, Object>();
env.put(Context.INITIAL_CONTEXT_FACTORY, "com.sun.jndi.ldap.LdapCtxFactory");

env.put(Context.PROVIDER_URL, "ldap://localhost:389/o=JNDITutorial");



// Use anonymous authentication
```

**Compliant solution**

```java
// Set up the environment for creating the initial context
Hashtable<String, Object> env = new Hashtable<String, Object>();
env.put(Context.INITIAL_CONTEXT_FACTORY, "com.sun.jndi.ldap.LdapCtxFactory");

env.put(Context.PROVIDER_URL, "ldap://localhost:389/o=Example");



// Use simple authentication
env.put(Context.SECURITY_AUTHENTICATION, "simple");
env.put(Context.SECURITY_PRINCIPAL, "cn=local, ou=Unit, o=Example");
env.put(Context.SECURITY_CREDENTIALS, getLDAPPassword());


// Create the initial context
DirContext ctx = new InitialDirContext(env);
```

---

### java:S4830 — Server certificates should be verified during SSL/TLS connections

**Severity**: High

| Trustworthy Which component or framework contains the issue? Java Cryptography Extension The following code contains examples of disabled certificate validation. The certificate validation gets disabled by overriding X509TrustManager with an empty implementation. It is highly recommended to use the original implementation.

**Noncompliant code example**

```java
class TrustAllManager implements X509TrustManager {

    @Override
```

---

### java:S5344 — Passwords should not be stored in plaintext or with a fast hashing algorithm

**Severity**: High

| Trustworthy Which component or framework contains the issue? Java Cryptography Extension

**Noncompliant code example**

```java
The derived key is vulnerable because the cost factor (rounds) is too low for the chosen algorithm.

private SecretKey deriveKey(String password, byte[] salt) throws Exception {
```

**Compliant solution**

```java
private SecretKey deriveKey(String password, byte[] salt) throws Exception {

    PBEKeySpec keySpec = new PBEKeySpec(password.toCharArray(), salt, 210000, 256);

    SecretKeyFactory secretKeyFactory = SecretKeyFactory.getInstance("PBKDF2withHmacSHA512");
    return secretKeyFactory.generateSecret(keySpec);
}
```

---

### java:S5445 — Insecure temporary file creation methods should not be used

**Severity**: High

The following code example is vulnerable to a race condition attack because it creates a temporary file using an unsafe API function.

**Noncompliant code example**

```java
import java.io.File;

import java.io.IOException;

protected void Example() throws IOException {

    File tempDir;
    tempDir = File.createTempFile("", ".");
    tempDir.delete();
```

**Compliant solution**

```java
import java.io.IOException;

import java.nio.file.Files;
import java.nio.file.Path;


protected void Example() throws IOException {

    Path tempPath = Files.createTempDirectory("");
    File tempDir = tempPath.toFile();

}
```

---

### java:S5527 — Server hostnames should be verified during SSL/TLS connections

**Severity**: High

Which component or framework contains the issue? Apache Commons Email The following code contains examples of disabled hostname validation. The hostname validation gets disabled because setSSLCheckServerIdentity is omitted. To enable validation, set it to true.

**Noncompliant code example**

```java
import org.apache.commons.mail.DefaultAuthenticator;
import org.apache.commons.mail.Email;
import org.apache.commons.mail.SimpleEmail;

public void sendMail(String message) {
    Email email = new SimpleEmail();

    email.setMsg(message);
    email.setSmtpPort(465);
    email.setAuthenticator(new DefaultAuthenticator(username, password));
```

**Compliant solution**

```java
import org.apache.commons.mail.DefaultAuthenticator;
import org.apache.commons.mail.Email;
import org.apache.commons.mail.SimpleEmail;

public void sendMail(String message) {
    Email email = new SimpleEmail();

    email.setMsg(message);
    email.setSmtpPort(465);
    email.setAuthenticator(new DefaultAuthenticator(username, password));

    email.setSSLCheckServerIdentity(true);
    email.setSSLOnConnect(true);


    email.send();
}
```

---

### java:S5542 — Encryption algorithms should be used with secure mode and padding scheme

**Severity**: High

| Trustworthy Which component or framework contains the issue? Java Cryptography Extension

**Noncompliant code example**

```java
Example with a symmetric cipher, AES:

import javax.crypto.Cipher;
import java.security.NoSuchAlgorithmException;
import javax.crypto.NoSuchPaddingException;

public static void main(String[] args) {
    try {
```

**Compliant solution**

```java
For the AES symmetric cipher, use the GCM mode:

import javax.crypto.Cipher;
import java.security.NoSuchAlgorithmException;
import javax.crypto.NoSuchPaddingException;

public static void main(String[] args) {
    try {

        Cipher.getInstance("AES/GCM/NoPadding");

    } catch(NoSuchAlgorithmException|NoSuchPaddingException e) {
        // ...
    }
}


For the RSA asymmetric cipher, use the Optimal Asymmetric Encryption Padding (OAEP):

import javax.crypto.Cipher;
import java.security.NoSuchAlgorithmException;
import javax.crypto.NoSuchPaddingException;

public static void main(String[] args) {
    try {

        Cipher.getInstance("RSA/ECB/OAEPWITHSHA-256ANDMGF1PADDING");

    } catch(NoSuchAlgorithmException|NoSuchPaddingException e) {
        // ...
    }
}
```

---

### java:S5547 — Cipher algorithms should be robust

**Severity**: High

| Trustworthy Which component or framework contains the issue? Java Cryptography Extension The following code contains examples of algorithms that are not considered highly resistant to cryptanalysis and thus should be avoided.

**Noncompliant code example**

```java
import javax.crypto.Cipher;
import java.security.NoSuchAlgorithmException;
import javax.crypto.NoSuchPaddingException;

public static void main(String[] args) {
    try {
```

**Compliant solution**

```java
import javax.crypto.Cipher;
import java.security.NoSuchAlgorithmException;
import javax.crypto.NoSuchPaddingException;

public static void main(String[] args) {
    try {

        Cipher aes = Cipher.getInstance("AES/GCM/NoPadding");

    } catch(NoSuchAlgorithmException|NoSuchPaddingException e) {
        // ...
    }
}
```

---

### java:S5659 — JWT should be signed and verified with strong cipher algorithms

**Severity**: High

| Trustworthy Which component or framework contains the issue? The following code contains examples of JWT encoding and decoding without a strong cipher algorithm.

**Noncompliant code example**

```java
import com.auth0.jwt.JWT;

public void encode() {
    JWT.create()
        .withSubject(SUBJECT)
```

**Compliant solution**

```java
import com.auth0.jwt.JWT;

public void encode() {
    JWT.create()
        .withSubject(SUBJECT)

        .sign(Algorithm.HMAC256(SECRET_KEY));

}

import com.auth0.jwt.JWT;

public void decode() {

    JWTVerifier verifier = JWT.require(Algorithm.HMAC256(SECRET_KEY))

        .withSubject(LOGIN)
        .build();
}
```

---

### java:S5876 — A new session should be created during user authentication

**Severity**: High

Skip to rules filters Quality Profiles Quality Gates Clear All Filters Software quality Security Hotspots Show Security Hotspots Only Available Since Security Category Quality Profile Prioritized Rules

Skip to rules filters

---

### javasecurity:S2631 — Regular expressions should not be vulnerable to Denial of Service attacks

**Severity**: High

Which component or framework contains the issue? Java Regex API The following noncompliant code is vulnerable to Regex Denial of Service because untrusted data is used as a regex to scan a string without prior sanitization or validation.

**Noncompliant code example**

```java
public boolean validate(HttpServletRequest request) {
  String regex = request.getParameter("regex");
  String input = request.getParameter("input");


  return input.matches(regex);

}
```

**Compliant solution**

```java
import java.util.regex.Pattern;


public boolean validate(HttpServletRequest request) {
  String regex = request.getParameter("regex");
  String input = request.getParameter("input");


  return input.matches(Pattern.quote(regex));

}
```

---

### javasecurity:S6390 — Thread suspensions should not be vulnerable to Denial of Service attacks

**Severity**: High

Which component or framework contains the issue? Java Lang Package This code is vulnerable to a Denial of Service because it sets a thread’s suspension time from user input without prior validation or sanitation.

**Noncompliant code example**

```java
protected void doGet(HttpServletRequest req, HttpServletResponse resp) {
  Long time = Long.parseLong(req.getParameter("time"));
  try {
```

**Compliant solution**

```java
protected void doGet(HttpServletRequest req, HttpServletResponse resp) {
  Long time = Long.parseLong(req.getParameter("time"));
  try {

    Thread.sleep(Math.min(time, 1000));

  } catch (InterruptedException e) {
    resp.sendError(500);
  }
}
```

---

## 2. Reliability & Bug Prevention Rules (28 rules)

These rules detect patterns that cause runtime errors, resource leaks, concurrency issues, and control flow defects.

### java:S2095 — Resources should be closed

**Severity**: Blocker

Connections, streams, files, and other classes that implement the `Closeable` interface or its super-interface `AutoCloseable`, need to be closed after use. Further, that close call must be made in a `finally` block otherwise an exception could keep the close call from being made. Failing to properly close resources will result in a resource leak which could bring first the application and then the box it runs on to their knees.

**Noncompliant code example**

```java
private void readTheFile() throws IOException {
  Path path = Paths.get(this.fileName);
  BufferedReader reader = Files.newBufferedReader(path, this.charset);
  // ...
  reader.close();  // Noncompliant
  // ...
  Files.lines("input.txt").forEach(System.out::println); // Noncompliant
}
```

**Compliant solution**

```java
private void readTheFile(String fileName) throws IOException {
    Path path = Paths.get(fileName);
    try (BufferedReader reader = Files.newBufferedReader(path, StandardCharsets.UTF_8)) {
      reader.readLine();
      // ...
    }
    try (Stream<String> input = Files.lines("input.txt")) {
      input.forEach(System.out::println);
    }
}
```

---

### java:S2168 — Double-checked locking should not be used

**Severity**: Blocker

Given significant performance improvements of synchronized methods in recent JVM versions, synchronized methods are now preferred over the less robust double-checked locking. If marking the entire method as synchronized is not an option, consider using an inner static class to hold the reference instead. Inner static classes are guaranteed to be initialized lazily.

**Noncompliant code example**

```java
public class ResourceFactory {
    private static Resource resource;


    public static Resource getInstance() {
        if (resource == null) {
```

**Compliant solution**

```java
public class ResourceFactory {
    private static Resource resource;


    public static synchronized Resource getInstance() { // Compliant, the entire method is synchronized and hence thread-safe
        if (resource == null)
            resource = new Resource();

        return resource;
    }
}
```

---

### java:S2189 — Loops should not be infinite

**Severity**: Blocker

symbolic-execution

An infinite loop will never end while the program runs, meaning you have to kill the program to get out of the loop. Every loop should have an end condition, whether by meeting the loop's termination condition or via a break statement.

**Noncompliant code example:**

```java
for (;;) {  // Noncompliant; end condition omitted
  // ...
}

int j;
while (true) { // Noncompliant; end condition omitted
  j++;
}

int k;
boolean b = true;
while (b) { // Noncompliant; b never written to in loop
  k++;
}
```

**Compliant solution:**

```java
int j;
while (true) { // reachable end condition added
  j++;
  if (j == Integer.MIN_VALUE) {  // true at Integer.MAX_VALUE +1
    break;
  }
}

int k;
boolean b = true;
while (b) {
  k++;
  b = k < Integer.MAX_VALUE;
}
```

---

### java:S2236 — Methods "wait(...)", "notify()" and "notifyAll()" should not be called on Thread instances

**Severity**: Blocker

multi-threading

---

### java:S2276 — "wait(...)" should be used instead of "Thread.sleep(...)" when a lock is held

**Severity**: Blocker

Call wait(…​) on the monitor object instead of using Thread.sleep(…​). While wait(…​) is executed, the lock is temporarily released and hence other threads can run in the meantime.

**Noncompliant code example**

```java
public void doSomething(){
  synchronized(monitor) {
    while(notReady()){
```

**Compliant solution**

```java
public void doSomething(){
  synchronized(monitor) {
    while(notReady()){

      monitor.wait(200); // Compliant, the current monitor is released.

    }
    process();
  }
  ...
}
```

---

### java:S3014 — "ThreadGroup" should not be used

**Severity**: Blocker

| Conventional Instead, use implementations of java.util.concurrent.ExecutorService to safely manage groups of threads.

**Noncompliant code example**

```java
class NetworkHandler {
```

**Compliant solution**

```java
class NetworkHandler {

  void handleThreadsProperly() {
    ThreadFactory threadFactory = Executors.defaultThreadFactory();
    ThreadPoolExecutor executorPool = new ThreadPoolExecutor(3, 10, 5, TimeUnit.SECONDS, new ArrayBlockingQueue<Runnable>(2), threadFactory);
    for (int i = 0; i < 10; i++) {
      executorPool.execute(new Thread("Job: " + i));
    }
    executorPool.shutdown();
  }

}
```

---

### java:S3046 — "wait" should not be called when multiple locks are held

**Severity**: Blocker

multi-threading Skip to rules filters Quality Profiles Quality Gates Clear All Filters Software quality Security Hotspots Show Security Hotspots Only Available Since Security Category Quality Profile Prioritized Rules "wait" should not be called when multiple locks are held multi-threading When two locks are held simultaneously, a wait call only releases one of them. The other will be held until some other thread requests a lock on the awaited object. If no unrelated code tries to lock on that object, then all other threads will be locked out, resulting in a deadlock.

**Noncompliant code example**

```java
synchronized (this.mon1) {  // threadB can't enter this block to request this.mon2 lock & release threadA
	synchronized (this.mon2) {
```

---

### java:S3516 — Methods returns should not be invariant

**Severity**: Blocker

symbolic-execution Skip to rules filters Quality Profiles Quality Gates Clear All Filters Software quality Security Hotspots Show Security Hotspots Only Available Since Security Category Quality Profile Prioritized Rules Methods returns should not be invariant symbolic-execution When a method is designed to return an invariant value, it may be poor design, but it shouldn’t adversely affect the outcome of your program. However, when it happens on all paths through the logic, it is surely a bug. This rule raises an issue when a method contains several return statements that all return the same value.

**Noncompliant code example**

```java
int foo(int a) {
  int b = 12;
  if (a == 1) {
    return b;
  }
```

---

### javabugs:S2190 — Recursion should not be infinite

**Severity**: Blocker

Dataflow Bug Detection SonarAnalyzer (Java) To correctly implement recursion, you must ensure that the following conditions are met: On every recursive call, the input to the call needs to become smaller, meaning it needs to be brought closer to the base case. For instance, if you are operating on a list, you can split it into smaller segments. If the input is numerical, you can ensure that you only make recursive calls on numbers that are strictly smaller. The recursive method must contain a termination condition that checks whether the base case has been reached. If so, it must not perform another recursive call. For example, a base case can be that the input is an empty list. You need to ensure that your process for splitting the input into smaller instances will actually lead to the...

**Noncompliant code example**

```java
int myPow(int num, int exponent) {
```

**Compliant solution**

```java
int myPow(int num, int exponent) {

  if (exponent == 0) { // <- termination condition
    return 1;
  }

  if (exponent < 0) {
    throw new IllegalArgumentException("Negative exponents are not supported.");
  }

  num = num * myPow(num, exponent - 1);
  return num;

}
```

---

### java:S1143 — Jump statements should not occur in "finally" blocks

**Severity**: High

Using return, break, throw, and so on from a finally block suppresses the propagation of any unhandled Throwable which was thrown in the try or catch block. This rule raises an issue when a jump statement (break, continue, return, throw, and goto) would force control flow to leave a finally block.

**Noncompliant code example:**

```java
public static void main(String[] args) {
  try {
    doSomethingWhichThrowsException();
    System.out.println("OK");   // incorrect "OK" message is printed
  } catch (RuntimeException e) {
    System.out.println("ERROR");  // this message is not shown
  }
}

public static void doSomethingWhichThrowsException() {
  try {
    throw new RuntimeException();
  } finally {
    for (int i = 0; i < 10; i ++) {
      //...
      if (q == i) {
        break; // ignored
      }
    }

    /* ... */
```

**Compliant solution:**

```java
public static void main(String[] args) {
  try {
    doSomethingWhichThrowsException();
    System.out.println("OK");
  } catch (RuntimeException e) {
    System.out.println("ERROR");  // "ERROR" is printed as expected
  }
}

public static void doSomethingWhichThrowsException() {
  try {
    throw new RuntimeException();
  } finally {
    for (int i = 0; i < 10; i ++) {
      //...
      if (q == i) {
        break; // ignored
      }
    }

    /* ... */
  }
}

```

---

### java:S1163 — Exceptions should not be thrown in finally blocks

**Severity**: High

error-handling

---

### java:S2093 — Try-with-resources should be used

**Severity**: High

| Conventional Use the try-with-resources syntax by moving the Closable variable declarations after the try keyword surrounded by parentheses and separated by ;: try (/* resources declarations */) { // resources usage ...

**Noncompliant code example**

```java
FileReader fr = null;
BufferedReader br = null;
```

**Compliant solution**

```java
try ( // Compliant, all resources are instantiated within a try-with-resources statement and hence automatically closed after use
    FileReader fr = new FileReader(fileName);
    BufferedReader br = new BufferedReader(fr)
  ) {

  return br.readLine();
}

catch (...) {}
```

---

### java:S2122 — "ScheduledThreadPoolExecutor" should not have 0 core threads

**Severity**: High

ThreadPoolExecutor is an object that efficiently manages and controls the execution of multiple tasks in a thread pool. A thread pool is a collection of pre-initialized threads ready to execute tasks. Instead of creating a new thread for each task, which can be costly in terms of system resources, a thread pool reuses existing threads. java.util.concurrent.ScheduledThreadPoolExecutor is an extension of ThreadPoolExecutor that can additionally schedule commands to run after a given delay or to execute periodically. ScheduledThreadPoolExecutor 's pool is sized with corePoolSize, so setting corePoolSize to zero means the executor will have no threads and run nothing. corePoolSize should have a value greater than zero and valid for your tasks. This rule detects instances where corePoolSize is set to zero via its setter or the object constructor.

**Noncompliant code example:**

```java
public void do(){

  int poolSize = 5; // value greater than 0
```

---

### java:S2222 — Locks should be released on all paths

**Severity**: High

If a lock is acquired and released within a method, then it must be released along all execution paths of that method. Failing to do so will expose the conditional locking logic to the method's callers and hence be deadlock-prone.

**Noncompliant code example:**

```java
public class MyClass {
  public void doSomething() {
    Lock lock = new Lock();
    lock.lock(); // Noncompliant
    if (isInitialized()) {
      // ...
      lock.unlock();
    }
  }
}
```

**Compliant solution:**

```java
public class MyClass {
  public void doSomething() {
    Lock lock = new Lock();
    if (isInitialized()) {
      lock.lock();
      // ...
      lock.unlock();
    }
  }
}
```

---

### java:S2235 — "IllegalMonitorStateException" should not be caught

**Severity**: High

error-handling

---

### java:S2274 — "Object.wait(...)" and "Condition.await(...)" should be called inside a "while" loop

**Severity**: High

multi-threading Make sure that the desired condition is actually true after being awakened. This can be accomplished by calling the wait or await methods inside a loop that checks said condition.

**Noncompliant code example**

```java
synchronized (obj) {

  if (!suitableCondition()){
```

**Compliant solution**

```java
synchronized (obj) {

  while (!suitableCondition()){
    obj.wait(timeout); // Compliant, the condition is checked in a loop, so the action below will only occur if the condition is true

  }
   ... // Perform some logic that is appropriate for when the condition is true
}
```

---

### java:S2447 — "null" should not be returned from a "Boolean" method

**Severity**: High

Callers of a Boolean method may be expecting to receive true or false in response. But Boolean objects can take null as a possible value. Boolean methods should not return null unless the code is annotated appropriately. With the proper annotation, the caller is aware that the returned value could be null.

**Noncompliant code example**

```java
public Boolean isUsable() {
  // ...
```

**Compliant solution**

```java
@javax.annotation.Nullable
public Boolean isUsable() {
  // ...
  return null;
}

@javax.annotation.CheckForNull
public Boolean isUsable() {
  // ...
  return null;
}

public void caller() {
  if (Boolean.True.equals(isUsable())) { // This caller knows to check and avoid ambiguity
    // ...
  }
}
```

---

### java:S2692 — "indexOf" checks should not be for positive numbers

**Severity**: High

Skip to rules filters Quality Profiles Quality Gates Clear All Filters Software quality Security Hotspots Show Security Hotspots Only Available Since Security Category Quality Profile Prioritized Rules "indexOf" checks should not be for positive numbers Most checks against an indexOf value compare it with -1 because 0 is a valid index. Checking against > 0 ignores the first element, which is likely a bug. String name = "ishmael";

**if (name.indexOf("ish") > 0) { // Noncompliant**

```java
// ...
}


Moreover, if the intent is merely to check the inclusion of a value in a String or a List, consider using the contains method instead.

String name = "ishmael";

if (name.contains("ish") {
  // ...
}


If the intent is really to skip the first element, comparing it with >=1 will make it more straightforward.

String name = "ishmael";

if (name.indexOf("ish") >= 1) {
  // ...
}


This rule raises an issue when an indexOf value retrieved from a String or a List is tested against > 0.
```

---

### java:S4454 — "equals" method parameters should not be marked "@Nonnull"

**Severity**: High

| Conventional Skip to rules filters Quality Profiles Quality Gates Clear All Filters Software quality Security Hotspots Show Security Hotspots Only Available Since Security Category Quality Profile Prioritized Rules "equals" method parameters should not be marked "@Nonnull" | Conventional By contract, the equals(Object) method, from java.lang.Object, should accept a null argument. Among all the other cases, the null case is even explicitly detailed in the Object.equals(...) Javadoc, stating "For any non-null reference value x, x.equals(null) should return false." Assuming that the argument to equals is always non-null, and enforcing that assumption with an annotation is not only a fundamental violation of the contract of equals, but it is also likely to cause problems in the future as...

**Noncompliant code example**

**Compliant solution**

```java
public boolean equals(Object obj) {
  if (obj == null) {
    return false;
  }
  // ...
}
```

---

### java:S4970 — Derived exceptions should not hide their parents' catch blocks

**Severity**: High

Skip to rules filters Quality Profiles Quality Gates Clear All Filters Software quality Security Hotspots Show Security Hotspots Only Available Since Security Category Quality Profile Prioritized Rules Derived exceptions should not hide their parents' catch blocks The catch block of a checked exception "E" may be hidden because the corresponding try block only throws exceptions derived from E. These derived exceptions are handled in dedicated catch blocks prior to the catch block of the base exception E. The catch block of E is unreachable and should be considered dead code. It should be removed, or the entire try-catch structure should be refactored. It is also possible that a single exception type in a multi-catch block may be hidden while the catch block itself is still reachable. In...

**Noncompliant code example**

```java
public class HiddenCatchBlock {

  public static class CustomException extends Exception {
  }

  public static class CustomDerivedException extends CustomException {
  }

  public static void main(String[] args) {
    try {
      throwCustomDerivedException();
    } catch(CustomDerivedException e) {
      // ...
```

**Compliant solution**

```java
public class HiddenCatchBlock {

  public static class CustomException extends Exception {
  }

  public static class CustomDerivedException extends CustomException {
  }

  public static void main(String[] args) {
    try {
      throwCustomDerivedException();
    } catch(CustomDerivedException e) { // Compliant; try-catch block is "catching" only the Exception that can be thrown in the "try"
      //...
    }
  }
}
```

---

### java:S5996 — Regex boundaries should not be used in a way that can never be matched

**Severity**: High

Skip to rules filters Quality Profiles Quality Gates Clear All Filters Software quality Security Hotspots Show Security Hotspots Only Available Since Security Category Quality Profile Prioritized Rules Regex boundaries should not be used in a way that can never be matched In regular expressions the boundaries ^ and \A can only match at the beginning of the input (or, in case of ^ in combination with the MULTILINE flag, the beginning of the line) and $, \Z and \z only at the end. These patterns can be misused, by accidentally switching ^ and $ for example, to create a pattern that can never match.

**Noncompliant code example**

```java
// This can never match because $ and ^ have been switched around
```

**Compliant solution**

```java
Pattern.compile("^[a-z]+$");
```

---

### java:S6104 — Map "computeIfAbsent()" and "computeIfPresent()" should not be used to add "null" values.

**Severity**: High

Map computeIfAbsent and computeIfPresent methods are convenient to avoid the cumbersome process to check if a key exists or not, followed by the addition of the entry. However, when the function used to compute the value returns null, the entry key->null will not be added to the Map. Furthermore, in the case of computeIfPresent, if the key is present the entry will be removed. These methods should therefore not be used to conditionally add an entry with a null value. The traditional way should be used instead. This rule raises an issue when computeIfAbsent or computeIfPresent is used with a lambda always returning null.

**Noncompliant code example:**

```java

```

**Compliant solution:**

```java
if (!map.containsKey(key)) {
    map.put(key, null);
}
if (map.containsKey(key)) {
    map.put(key, null);
}

```

---

### java:S6816 — Nullable injected fields and parameters should provide a default value

**Severity**: High

Add a default value to the @Value annotation. A default value can be supplied by using the colon (:) operator. As the field is nullable, the default value should most likely be #{null}.

**Noncompliant code example**

```java
@Nullable
```

**Compliant solution**

```java
@Nullable

@Value("${my.property:#{null}}") // Compliant, a default value is provided

private String myProperty;
```

---

### java:S6881 — Virtual threads should be used for tasks that include heavy blocking operations

**Severity**: High

multi-threading Replace platform thread instances or platform thread pools with virtual threads, if their task involves blocking operations.

**Noncompliant code example**

```java
The following example creates a platform thread to handle a blocking operation, here denoted by Thread.sleep(1000). The overhead for instantiating a platform thread is higher than for a virtual thread. Further, instantiating too many platform threads can lead to problems if the number of instantiated threads exceeds the maximum number of platform threads allowed by the OS.

new Thread(() -> {

    try {
```

**Compliant solution**

```java
Using virtual threads allows the developer to abstract from any pooling logic as they are much lighter than platform threads, and the number of virtual threads that can be instantiated is only limited by the available memory. In this example, the execution of 10000 requests would take just over ~1 second without any risk of exceeding the allowed number of platform threads.

Thread.ofVirtual().start(() -> {

    try {

        Thread.sleep(1000); // Compliant

    } catch (InterruptedException e) {
        throw new RuntimeException(e);
    }
});
```

---

### javabugs:S3518 — Zero should not be a possible denominator

**Severity**: High

Dataflow Bug Detection SonarAnalyzer (Java)

---

### javabugs:S6320 — Cast operations should not trigger a ClassCastException

**Severity**: High

Dataflow Bug Detection SonarAnalyzer (Java) When an object is cast, the code makes assumptions about the type of the object. A ClassCastException indicates that this assumption has been broken. If the assumption is reasonable, then some prior logic should ensure that only objects of a compatible type can be cast. You should try to identify the code responsible for these checks and fix it.

**Noncompliant code example**

```java
private String hexString(Object o) {
```

**Compliant solution**

```java
One possible solution is to change hexString to only accept integers and adapt call sites.

private String hexString(Integer i) {
  return Integer.toHexString(i);
}


Another one is to return a default value for types that are not Integer. Here, the if statement with the condition relying on instanceof prevents references to objects with an incompatible type from making it to the cast operation.

private String hexString(Object o) {
  if (o instanceof Integer) {
    return Integer.toHexString((Integer) o);
  }
  return "0x0";
}


The solution to adopt depends on which part of the code should be responsible to handle non-Integer types.

Going the extra mile

Casting is considered an anti-pattern in object-oriented programming. It is sometimes necessary, but there often is a better alternative. Consider:

Polymorphism
The visitor design pattern
Pattern matching

They come with some guarantees from the compiler, making your code more reliable.
```

---

### javabugs:S6416 — Calls to methods should not trigger an exception

**Severity**: High

Dataflow Bug Detection SonarAnalyzer (Java)

**Noncompliant code example**

```java
/**
 * Set the oven temperature
 * @param temp the temperature in Celsius, between 0 and 250 (inclusive)
 * @throws IllegalArgumentException if the temperature is outside of the supported range
 */
private void setOvenTemperature(int temp) {
  if (temp < 0 || temp > 250) {
    throw new IllegalArgumentException();
  }
  // ...
}

void finishCooking() {
```

**Compliant solution**

```java
/**
 * Set the oven temperature
 * @param temp the temperature in Celsius, between 0 and 250 (inclusive)
 * @throws IllegalArgumentException if the temperature is outside of the supported range
 */
private void setOvenTemperature(int temp) {
  if (temp < 0 || temp > 250) {
    throw new IllegalArgumentException();
  }
  // ...
}

void finishCooking() {

  setOvenTemperature(0);

}
```

---

### javabugs:S6466 — Accessing an array element should not trigger an ArrayIndexOutOfBoundsException

**Severity**: High

Dataflow Bug Detection SonarAnalyzer (Java) The following examples contain out-of-bounds accesses to arrays, resulting in ArrayIndexOutOfBounds exceptions. These situations can be avoided by carefully considering the range of valid index values, or even better, by comparing indices against the size of a sequence. In this first example, the array arr contains three elements. Since the first element of a list has index 0, the last valid index is 2. Therefore, an ArrayIndexOutOfBoundsException is thrown when accessing arr at index 3.

**Noncompliant code example**

```java
void fun() {
    int[] arr = {1, 2, 3};
```

**Compliant solution**

```java
void fun() {
    int[] arr = {1, 2, 3};


    int x = arr[0];

  }


Accessing an array with its size as the index is never correct:
```

---

## 3. Spring Framework Rules (11 rules)

Apply these ONLY when the project uses Spring/Spring Boot. These rules detect Spring-specific misconfigurations and anti-patterns.

### java:S4602 — "@SpringBootApplication" and "@ComponentScan" should not be used in the default package

**Severity**: Blocker

Skip to rules filters Quality Profiles Quality Gates Clear All Filters Software quality Security Hotspots Show Security Hotspots Only Available Since Security Category Quality Profile Prioritized Rules "@SpringBootApplication" and "@ComponentScan" should not be used in the default package @ComponentScan is used to determine which Spring Beans are available in the application context. The packages to scan can be configured thanks to the basePackageClasses or basePackages (or its alias value) parameters. If neither parameter is configured, @ComponentScan will consider only the package of the class annotated with it. When @ComponentScan is used on a class belonging to the default package, the entire classpath will be scanned. This will slow-down the start-up of the application and it is...

**Noncompliant code example**

```java
import org.springframework.boot.SpringApplication;
```

**Compliant solution**

```java
package hello;

import org.springframework.boot.SpringApplication;

@SpringBootApplication // Compliant; RootBootApp belongs to the "hello" package
public class RootBootApp {
...
}
```

---

### java:S4684 — Persistent entities should not be used as arguments of "@RequestMapping" methods

**Severity**: High

| Conventional Which component or framework contains the issue? The following code is vulnerable to a mass assignment attack because it allows modifying the User persistent entities thanks to maliciously forged Wish object properties.

**Noncompliant code example**

```java
import javax.persistence.Entity;

@Entity
public class Wish {

  Long productId;
  Long quantity;

  Client client;

}


@Entity
public class Client {
  String clientId;
  String name;
  String password;
}


import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;

@Controller
public class PurchaseOrderController {

  @RequestMapping(path = "/saveForLater", method = RequestMethod.POST)
```

**Compliant solution**

```java
public class WishDTO {

  Long productId;
  Long quantity;

  Long clientId;

}

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;

@Controller
public class PurchaseOrderController {

  @RequestMapping(path = "/saveForLater", method = RequestMethod.POST)

  public String saveForLater(WishDTO wish) {
    Wish persistentWish = new Wish();
    persistentWish.productId = wish.productId
    persistentWish.quantity = wish.quantity
    persistentWish.client = getClientById(with.clientId)
    session.save(persistentWish);

  }
}
```

---

### java:S6809 — Methods with Spring proxy should not be called via "this"

**Severity**: High

| Conventional Replace calls to @Async, @Cacheable or @Transactional methods via this with calls on an instance that was injected by Spring (@Autowired, @Resource or @Inject). The injected instance is a proxy on which the methods can be invoked safely.

**Noncompliant code example**

```java
@Service
public class AsyncNotificationProcessor implements NotificationProcessor {

  @Override
  public void process(Notification notification) {
```

**Compliant solution**

```java
@Service
public class AsyncNotificationProcessor implements NotificationProcessor {


  @Resource
  private AsyncNotificationProcessor asyncNotificationProcessor;


  @Override
  public void process(Notification notification) {

    asyncNotificationProcessor.processAsync(notification); // Compliant, call via injected proxy
    asyncNotificationProcessor.retrieveNotification(notification.id); // Compliant, the call will be cached

  }

  @Async
  public processAsync(Notification notification) {
    // ...
  }

  @Cacheable
  public Notification retrieveNotification(Long id) {
    // ...
  }
}
```

---

### java:S6817 — Use of the "@Async" annotation on methods declared within a "@Configuration" class in Spring Boot

**Severity**: High

Don’t use @Async annotations on methods of @Configuration classes.

**Noncompliant code example**

```java
@EnableAsync
@Configuration
public class MyConfiguration {
```

**Compliant solution**

```java
@EnableAsync
@Configuration
public class MyConfiguration {


  public void method() {

    // ...
  }
}
```

---

### java:S6818 — "@Autowired" should only be used on a single constructor

**Severity**: High

To maintain code clarity and ensure that the Spring context can create beans correctly, have only one constructor annotated with @Autowired within a Spring component or set required = false.

**Noncompliant code example**

```java
@Component
public class MyComponent {
  private final MyService myService;

  @Autowired
  public MyComponent(MyService myService) {
    this.myService = myService;
    // ...
  }
```

**Compliant solution**

```java
@Component
public class MyComponent {
  private final MyService myService;

  @Autowired
  public MyComponent(MyService myService) {
    this.myService = myService;
    // ...
  }

  public MyComponent(MyService myService, Integer i) {
    this.myService = myService;
    // ...
  }

  public MyComponent(MyService myService, Integer i, String s) {
    this.myService = myService;
    // ...
  }
}
```

---

### java:S6857 — SpEL expression should have a valid syntax

**Severity**: High

| Conventional Correct the syntax error in the SpEL expression.

**Noncompliant code example**

**Compliant solution**

```java
@Value("#{systemProperties['user.region']}") // Compliant

private String region;

@Value("#{'${listOfValues}'.split(',')}") // Compliant

private List<String> valuesList;

@Value("#{T(java.lang.Math).random() * 100.0}") // Compliant

private Double randPercent;

@Query("SELECT u FROM User u WHERE u.status = :#{#status+42}") // Compliant

List<User> findUsersByStatus(@Param("status") String status);

@Value("${myapp.prop}") // Compliant

private String myProperty;

@Value("${my.property:#{1*1}}") // Compliant

private Integer myValue;
```

---

### java:S7178 — Injecting data into static fields is not supported by Spring

**Severity**: High

Either use an instance field instead of a static field or remove the @Value, @Inject, or @Autowired annotation and initialize the field.

**Noncompliant code example**

```java
@Component
public class MyComponent {

    @Value("${my.app.prop}")

    private static SomeDependency dependency; // non compliant, @Value will be ignored and no value will be injected

    // ...
}
```

**Compliant solution**

```java
@Component
public class MyComponent {

    @Value("${my.app.prop}")

    private final SomeDependency dependency;

    // ...
}
```

---

### java:S7184 — "@Scheduled" annotation should only be applied to no-arg methods

**Severity**: High

Transform method annotated with @Scheduled into a no-arg method.

**Noncompliant code example**

```java
public class ExampleService {

    @Scheduled(fixedRate = 5000)

    public void scheduledTask(String param) { // non compliant, method has an argument. It will raise a runtime error.

        // Task implementation
    }
}
```

**Compliant solution**

```java
public class ExampleService {

    @Scheduled(fixedRate = 5000)

    public void scheduledTask() { // compliant, no-arg method

        // Task implementation
    }
}
```

---

### java:S7185 — @EventListener methods should have one parameter at most

**Severity**: High

**Noncompliant code example**

```java
@EventListener
void handleEvent(CustomerEvent customerEvent, ExceptionalEvent exceptionalEvent) { // Non compliant, this will cause a runtime error

    //... some event handling
}
```

**Compliant solution**

```java
@EventListener(classes = {CustomerEvent.class, ExceptionalEvent.class})
void handleEvent(ApplicationEvent event) { // Only one parameter, of the super type `ApplicationEvent`

    //... some event handling
}
```

---

### java:S7186 — Methods returning "Page" or "Slice" must take "Pageable" as an input parameter

**Severity**: High

| Conventional Ensure that query methods returning a Page or Slice include a Pageable parameter in their method signature.

**Noncompliant code example**

```java
interface ItemRepository extends JpaRepository<Item, Long> {

    Page<Item> findItems(); //non compliant, no Pageable parameter

}
```

**Compliant solution**

```java
interface ItemRepository extends JpaRepository<Item, Long> {

    Page<Item> findItems(Pageable pageable);

}
```

---

### java:S7190 — Methods annotated with "@BeforeTransaction" or "@AfterTransaction" must respect the contract

**Severity**: High

Ensure that methods annotated with @BeforeTransaction or @AfterTransaction have a void return type and do not accept any arguments.

**Noncompliant code example**

```java
@Transactional
public class TransactionalTest {

    @BeforeTransaction

    public String setupTransaction(int x) { // non-compliant, method should be void and have no argument

        // Setup logic
    }

    @AfterTransaction

    public int cleanupTransaction(int x) { // non-compliant, method should be void and have no argument

        // Cleanup logic
    }
}
```

**Compliant solution**

```java
@Transactional
public class TransactionalTest {

    @BeforeTransaction

    public void setupTransaction() {

        // Setup logic
    }

    @AfterTransaction

    public void cleanupTransaction() {

        // Cleanup logic
    }
}
```

---

## 4. Testing Quality Rules (14 rules)

These rules ensure test correctness and completeness.

### java:S2187 — TestCases should contain tests

**Severity**: Blocker

Adaptability Skip to rules filters Quality Profiles Quality Gates Clear All Filters Software quality Security Hotspots Show Security Hotspots Only Available Since Security Category Quality Profile Prioritized Rules TestCases should contain tests Adaptability There’s no point in having a JUnit TestCase without any test methods. Similarly, you shouldn’t have a file in the tests directory named *Test, *Tests, or *TestCase, but no tests in the file. Doing either of these things may lead someone to think that uncovered classes have been tested. This rule raises an issue when files in the test directory are named *Test, *Tests, or *TestCase or implement TestCase but don’t contain any tests. Supported frameworks: TestClassNamePattern Test class name pattern (regular expression) Default Value:...

---

### java:S2188 — JUnit test cases should call super methods

**Severity**: Blocker

Add an explicit call to super.setUp() and super.tearDown() in the overriding methods.

**Noncompliant code example**

```java
public class MyClassTest extends MyAbstractTestCase {

  private MyClass myClass;

  @Override
```

**Compliant solution**

```java
public class MyClassTest extends MyAbstractTestCase {

  private MyClass myClass;

  @Override

  protected void setUp() throws Exception {
    super.setUp();

    myClass = new MyClass();
  }
}
```

---

### java:S2699 — Tests should include assertions

**Severity**: Blocker

Adaptability Skip to rules filters Quality Profiles Quality Gates Clear All Filters Software quality Security Hotspots Show Security Hotspots Only Available Since Security Category Quality Profile Prioritized Rules Tests should include assertions Adaptability A test case without assertions ensures only that no exceptions are thrown. Beyond basic runnability, it ensures nothing about the behavior of the code under test. This rule raises an exception when no assertions from any of the following known frameworks are found in a test: Eclipse Vert.x Fest 1.x and 2.x Rest-assured 2.x, 3.x and 4.x RxJava 1.x and 2.x Spring’s org.springframework.test.web.servlet.ResultActions.andExpect() and org.springframework.test.web.servlet.ResultActions.andExpectAll() Truth Framework Furthermore, as new or...

**Noncompliant code example**

```java
@Test
```

**Compliant solution**

```java
Example when com.company.CompareToTester#compare* is used as parameter to the rule.

import com.company.CompareToTester;

@Test
public void testDoSomething() {
  MyClass myClass = new MyClass();
  assertNull(myClass.doSomething());  // JUnit assertion
  assertThat(myClass.doSomething()).isNull();  // Fest assertion
}

@Test
public void testDoSomethingElse() {
  MyClass myClass = new MyClass();
  new CompareToTester().compareWith(myClass);  // Compliant - custom assertion method defined as rule parameter
  CompareToTester.compareStatic(myClass);  // Compliant
}

Parameters
customAssertionMethods	
Comma-separated list of fully qualified method symbols that should be considered as assertion methods. The wildcard character can be used at the end of the method name.
```

---

### java:S2970 — Assertions should be complete

**Severity**: Blocker

Adaptability Skip to rules filters Quality Profiles Quality Gates Clear All Filters Software quality Security Hotspots Show Security Hotspots Only Available Since Security Category Quality Profile Prioritized Rules Assertions should be complete Adaptability It is very easy to write incomplete assertions when using some test frameworks. This rule enforces complete assertions in the following cases: Fest: assertThat is not followed by an assertion invocation AssertJ: assertThat is not followed by an assertion invocation Mockito: verify is not followed by a method invocation Truth: assertXXX is not followed by an assertion invocation In such cases, what is intended to be a test doesn’t actually verify anything

**Noncompliant code example**

```java
// Fest
boolean result = performAction();
// let's now check that result value is true
```

**Compliant solution**

```java
// Fest
boolean result = performAction();
// let's now check that result value is true
assertThat(result).isTrue();

// Mockito
List mockedList = Mockito.mock(List.class);
mockedList.add("one");
mockedList.clear();
// let's check that "add" and "clear" methods are actually called
Mockito.verify(mockedList).add("one");
Mockito.verify(mockedList).clear();
```

---

### java:S2186 — JUnit assertions should not be used in "run" methods

**Severity**: High

Assertions in Runnable tasks should be extracted or executed by the main thread to make the whole test fail.

**Noncompliant code example**

```java
class RunnableWithAnAssertion extends Thread {
  @Override
  public void run() {
```

**Compliant solution**

```java
class RunnableWithAnAssertion extends Thread {
  @Override
  public void run() {
```

---

### java:S5779 — Assertion methods should not be used within the try block of a try-catch catching an Error

**Severity**: High

Assertion methods are throwing a "java.lang.AssertionError". If this call is done within the try block of a try-catch cathing a similar error, you should make sure to test some properties of the exception. Otherwise, the assertion will never fail.

**Noncompliant code example:**

```java
@Test
public void should_throw_assertion_error() {
  try {
    throwAssertionError();
```

**Compliant solution:**

```java
assertThrows(AssertionError.class, () -> throwAssertionError());

try {
   throwAssertionError();
```

---

### java:S5783 — Only one method invocation is expected when testing checked exceptions

**Severity**: High

Skip to rules filters Quality Profiles Quality Gates Clear All Filters Software quality Security Hotspots Show Security Hotspots Only Available Since Security Category Quality Profile Prioritized Rules Only one method invocation is expected when testing checked exceptions When verifying that code raises an exception, a good practice is to avoid having multiple method calls inside the tested code, to be explicit about what is exactly tested. When two of the methods can raise the same checked exception, not respecting this good practice is a bug, since it is not possible to know what is really tested. You should make sure that only one method can raise the expected checked exception in the tested code.

**Noncompliant code example**

```java
@Test
public void testG() {
  // Do you expect g() or f() throwing the exception?
```

**Compliant solution**

```java
@Test
public void testG() {
  int y = f(1);
  // It is explicit that we expect an exception from g() and not f()
  assertThrows(IOException.class, () -> g(y) );
}

@Test
public void testGTryCatchIdiom() {
  int y = f(1);
  try {
    g(y);
    Assert.fail("Expected an IOException to be thrown");
  } catch (IOException e) {
    // Test exception message...
  }
}
```

---

### java:S5790 — JUnit5 inner test classes should be annotated with @Nested

**Severity**: High

Adaptability Skip to rules filters Quality Profiles Quality Gates Clear All Filters Software quality Security Hotspots Show Security Hotspots Only Available Since Security Category Quality Profile Prioritized Rules JUnit5 inner test classes should be annotated with @Nested Adaptability If not annotated with @Nested, an inner class containing some tests will never be executed during tests execution. While you could still be able to manually run its tests in an IDE, it won’t be the case during the build. By contrast, a static nested class containing some tests should not be annotated with @Nested, JUnit5 will not share setup and state with an instance of its enclosing class. This rule raises an issue on inner classes and static nested classes containing JUnit5 test methods which has a wrong...

**Noncompliant code example**

```java
import org.junit.jupiter.api.Test;

class MyJunit5Test {
  @Test
  void test() { /* ... */ }
```

**Compliant solution**

```java
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Nested;

class MyJunit5Test {
  @Test
  void test() { /* ... */ }

  @Nested
  class InnerClassTest {
    @Test
    void test() { /* ... */ }
  }

  static class StaticNestedClassTest {
    @Test
    void test() { /* ... */ }
  }
}
```

---

### java:S5803 — Class members annotated with "@VisibleForTesting" should not be accessed from production code

**Severity**: High

| Conventional Skip to rules filters Quality Profiles Quality Gates Clear All Filters Software quality Security Hotspots Show Security Hotspots Only Available Since Security Category Quality Profile Prioritized Rules Class members annotated with "@VisibleForTesting" should not be accessed from production code | Conventional @VisibleForTesting can be used to mark methods, fields and classes whose visibility restrictions have been relaxed more than necessary for the API to allow for easier unit testing. Access to such methods, fields and classes only possible thanks to this relaxed visibility is fine for test code, but it should be avoided in production code. In production code these methods should be treated as if they are private. Supported framework: Guava:...

**Noncompliant code example**

```java
/** src/main/java/MyObject.java */

@VisibleForTesting String foo;

/** src/main/java/Service.java */
```

**Compliant solution**

```java
/** src/main/java/MyObject.java */

@VisibleForTesting String foo;

/** src/test/java/MyObjectTest.java */

new MyObject().foo; // Compliant, foo is accessed from test code
```

---

### java:S5826 — Methods setUp() and tearDown() should be correctly annotated starting with JUnit4

**Severity**: High

| Conventional Skip to rules filters Quality Profiles Quality Gates Clear All Filters Software quality Security Hotspots Show Security Hotspots Only Available Since Security Category Quality Profile Prioritized Rules Methods setUp() and tearDown() should be correctly annotated starting with JUnit4 | Conventional The setUp() and tearDown() methods (initially introduced with JUnit3 to execute a block of code before and after each test) need to be correctly annotated with the equivalent annotation in order to preserve the same behavior when migrating from JUnit3 to JUnit4 or JUnit5. This rule consequently raise issues on setUp() and tearDown() methods which are not annotated in test classes.

**Noncompliant code example**

```java
JUnit4:
```

**Compliant solution**

```java
JUnit4:
@Before
public void setUp() { ... }

@After
public void tearDown() { ... }

JUnit5:
@BeforeEach
void setUp() { ... }

@AfterEach
void tearDown() { ... }
```

---

### java:S5845 — Assertions comparing incompatible types should not be made

**Severity**: High

Assertions comparing incompatible types always fail, and negative assertions always pass. At best, negative assertions are useless. At worst, the developer loses time trying to fix his code logic before noticing wrong assertions. Dissimilar types are: comparing a primitive with null comparing an object with an unrelated primitive (E.G. a string with an int) comparing unrelated classes comparing an array to a non-array comparing two arrays of dissimilar types This rule also raises issues for unrelated class and interface or unrelated interface types in negative assertions. Because except in some corner cases, those types are more likely to be dissimilar. And inside a negative assertion, there is no test failure to inform the developer about this unusual comparison. Supported test frameworks: JUnit4 JUnit5 AssertJ

**Noncompliant code example:**

```java
interface KitchenTool {}
interface Plant {}
class Spatula implements KitchenTool {}
class Tree implements Plant {}

void assertValues(int size,
                  Spatula spatula, KitchenTool tool,  KitchenTool[] tools,
                  Tree    tree,    Plant       plant, Tree[]        trees) {

  // Whatever the given values, those negative assertions will always pass due to dissimilar types:
```

---

### java:S5846 — Empty lines should not be tested with regex MULTILINE flag

**Severity**: High

Skip to rules filters Quality Profiles Quality Gates Clear All Filters Software quality Security Hotspots Show Security Hotspots Only Available Since Security Category Quality Profile Prioritized Rules Empty lines should not be tested with regex MULTILINE flag One way to test for empty lines is to use the regex "^$", which can be extremely handy when filtering out empty lines from collections of Strings, for instance. With regard to this, the Javadoc for Pattern (Line Terminators) states the following: By default, the regular expressions ^ and $ ignore line terminators and only match at the beginning and the end, respectively, of the entire input sequence. If MULTILINE mode is activated then ^ matches at the beginning of input and after any line terminator except at the end of input. When...

**Noncompliant code example**

**Compliant solution**

```java
static final Pattern p = Pattern.compile("^$", Pattern.MULTILINE);

boolean containsEmptyLines(String str) {
    return p.matcher(str).find() || str.isEmpty();
}

// ...
System.out.println(containsEmptyLines("a\n\nb")); // correctly prints 'true'
System.out.println(containsEmptyLines("")); // also correctly prints 'true'
```

---

### java:S5969 — Mocking all non-private methods of a class should be avoided

**Severity**: High

Adaptability Skip to rules filters Quality Profiles Quality Gates Clear All Filters Software quality Security Hotspots Show Security Hotspots Only Available Since Security Category Quality Profile Prioritized Rules Mocking all non-private methods of a class should be avoided Adaptability If you end up mocking every non-private method of a class in order to write tests, it is a strong sign that your test became too complex, or that you misunderstood the way you are supposed to use the mocking mechanism. You should either refactor the test code into multiple units, or consider using the class itself, by either directly instantiating it, or creating a new one inheriting from it, with the expected behavior. This rule reports an issue when every member of a given class are mocked.

**Noncompliant code example**

```java
@Test
void test_requiring_MyClass() {
```

**Compliant solution**

```java
@Test
void test_requiring_MyClass() {
  MyClass myClass = new MyClassForTest();
  //...
}

class MyClassForTest extends MyClass {

  @Override
  int f() {
    return 1;
  }

  @Override
  int g() {
    return 2;
  }
}


or

@Test
void test_requiring_f() {
  MyClass myClassMock = mock(MyClass.class);
  when(myClassMock.f()).thenReturn(1);
  //...
}

@Test
void test_requiring_g() {
  MyClass myClassMock = mock(MyClass.class);
  when(myClassMock.g()).thenReturn(2);
  //...
```

---

### java:S6002 — Regex lookahead assertions should not be contradictory

**Severity**: High

Skip to rules filters Quality Profiles Quality Gates Clear All Filters Software quality Security Hotspots Show Security Hotspots Only Available Since Security Category Quality Profile Prioritized Rules Regex lookahead assertions should not be contradictory This rule raises an issue when a regex lookahead contradicts the rest of the regex. Lookahead assertions are a regex feature that makes it possible to look ahead in the input without consuming it. It is often used at the end of regular expressions to make sure that substrings only match when they are followed by a specific pattern. For example, the following pattern will match an "a" only if it is directly followed by a "b". This does not consume the "b" in the process: Pattern.compile("a(?=b)"); However, lookaheads can also be used in...

**Noncompliant code example**

**Compliant solution**

```java
Pattern.compile("(?<=a)b");
Pattern.compile("a(?=b)");
```

---

## 5. Code Quality & Maintainability Rules (55 rules)

These rules detect complexity, naming, structural, and design anti-patterns that increase maintenance cost.

### java:S1190 — Future keywords should not be used as names

**Severity**: Blocker

| Conventional Rename the _ identifiers.

**Noncompliant code example**

```java
public class MyClass {
```

**Compliant solution**

```java
public class MyClass {

    String s = "";            // Compliant

}
```

---

### java:S1219 — "switch" statements should not contain non-case labels

**Severity**: Blocker

Even if it is legal, mixing case and non-case labels in the body of a switch statement is very confusing and can even be the result of a typing error.

**Noncompliant code example**

```java
switch (day) {
  case MONDAY:
  case TUESDAY:
```

**Compliant solution**

```java
switch (day) {
  case MONDAY:
  case TUESDAY:
  case WEDNESDAY:
    doSomething();
    break;
  ...
}

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

### java:S128 — Switch cases should end with an unconditional "break" statement

**Severity**: Blocker

When the execution is not explicitly terminated at the end of a switch case, it continues to execute the statements of the following case. While this is sometimes intentional, it often is a mistake which leads to unexpected behavior.

**Noncompliant code example**

```java
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

```java
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

### java:S1845 — Methods and field names should not be the same or differ only by capitalization

**Severity**: Blocker

| Identifiable Skip to rules filters Quality Profiles Quality Gates Clear All Filters Software quality Security Hotspots Show Security Hotspots Only Available Since Security Category Quality Profile Prioritized Rules Methods and field names should not be the same or differ only by capitalization | Identifiable This rule raises an issue when there is a method and a field in a class with names that differ only by capitalization. Looking at the set of methods in a class, including superclass methods, and finding two methods or fields that differ only by capitalization is confusing to users of the class. It is similarly confusing to have a method and a field which differ only in capitalization or a method and a field with exactly the same name and visibility. In the case of methods, it may...

**Noncompliant code example**

```java
public class Car{


  public DriveTrain drive;


  public void tearDown(){...}
```

**Compliant solution**

```java
public class Car{


  private DriveTrain drive;


  public void tearDown(){...}


  public void drive() {...}  // field visibility reduced

}

public class MyCar extends Car{

  @Override
  public void tearDown(){...}


  public void drivefast(){...}


  public void driveReallyFast(){...}


}
```

---

### java:S2178 — Short-circuit logic should be used in boolean contexts

**Severity**: Blocker

The use of non-short-circuit logic in a boolean context is likely a mistake - one that could cause serious program errors as conditions are evaluated under the wrong circumstances.

**Noncompliant code example:**

```java

```

**Compliant solution:**

```java
if(getTrue() || getFalse()) { ... } // true short-circuit logic

```

---

### java:S2229 — Methods should not call same-class methods with incompatible "@Transactional" values

**Severity**: Blocker

| Conventional Change the corresponding functions into a compatible propagation type.

**Noncompliant code example**

```java
public void doTheThing() {
  // ...
```

**Compliant solution**

```java
@Transactional

public void doTheThing() {
  // ...

  actuallyDoTheThing(); // Compliant

}

@Transactional
public void actuallyDoTheThing() {
  // ...
}
```

---

### java:S2275 — Printf-style format strings should not lead to unexpected behavior at runtime

**Severity**: Blocker

Skip to rules filters Quality Profiles Quality Gates Clear All Filters Software quality Security Hotspots Show Security Hotspots Only Available Since Security Category Quality Profile Prioritized Rules Printf-style format strings should not lead to unexpected behavior at runtime Because printf-style format strings are interpreted at runtime, rather than validated by the Java compiler, they can contain errors that lead to unexpected behavior or runtime errors. This rule statically validates the good behavior of printf-style formats when calling the format(...) methods of java.util.Formatter, java.lang.String, java.io.PrintStream, MessageFormat, and java.io.PrintWriter classes and the printf(...) methods of java.io.PrintStream or java.io.PrintWriter classes.

**Noncompliant code example**

**Compliant solution**

```java
String.format("The value of my integer is %d", 3);
String.format("Duke's Birthday year is %tY", c);
String.format("Display %1$d and then %d", 1);
String.format("Not enough arguments %d and %d", 1, 2);
String.format("%d is equals to %<", 2);

MessageFormat.format("Result {0}.", value);
MessageFormat.format("Result {0} & {1}.", value, value);
MessageFormat.format("Result {0}.", myObject);

java.util.logging.Logger logger;
logger.log(java.util.logging.Level.SEVERE, "Result {1},{2}!", 14, 2);

org.slf4j.Logger slf4jLog;
org.slf4j.Marker marker;

slf4jLog.debug(marker, "message {}", 1);

org.apache.logging.log4j.Logger log4jLog;
log4jLog.debug("message {}", 1);
```

---

### java:S2387 — Child class fields should not shadow parent class fields

**Severity**: Blocker

Having a variable with the same name in two unrelated classes is fine, but do the same thing within a class hierarchy and you’ll get confusion at best, chaos at worst.

**Noncompliant code example**

```java
public class Fruit {
  protected Season ripe;
  protected Color flesh;

  // ...
}

public class Raspberry extends Fruit {
```

**Compliant solution**

```java
public class Fruit {
  protected Season ripe;
  protected Color flesh;

  // ...
}

public class Raspberry extends Fruit {
  private boolean ripened;
  private static Color FLESH_COLOR;

}
```

---

### java:S2437 — Unnecessary bit operations should not be performed

**Severity**: Blocker

Skip to rules filters Quality Profiles Quality Gates Clear All Filters Software quality Security Hotspots Show Security Hotspots Only Available Since Security Category Quality Profile Prioritized Rules Unnecessary bit operations should not be performed Certain bit operations are just silly and should not be performed because their results are predictable. Specifically, using & -1 with any value will always result in the original value, as will anyValue ^ 0 and anyValue | 0.

---

### java:S2689 — Files opened in append mode should not be used with "ObjectOutputStream"

**Severity**: Blocker

serialization Open the file to use the default action (writes stream header).

**Noncompliant code example**

```java
FileOutputStream fos = new FileOutputStream(fileName , true);  // fos opened in append mode
```

**Compliant solution**

```java
FileOutputStream fos = new FileOutputStream(fileName);
ObjectOutputStream out = new ObjectOutputStream(fos);
```

---

### java:S2695 — "PreparedStatement" and "ResultSet" methods should be called with valid indices

**Severity**: Blocker

Ensure the index passed to the PreparedStatement and ResultSet methods is valid.

**Noncompliant code example**

```java
PreparedStatement ps = con.prepareStatement("SELECT fname, lname FROM employees where hireDate > ? and salary < ?");
```

**Compliant solution**

```java
PreparedStatement ps = con.prepareStatement("SELECT fname, lname FROM employees where hireDate > ? and salary < ?");

ps.setDate(1, date);
ps.setDouble(2, salary);


ResultSet rs = ps.executeQuery();
while (rs.next()) {

  String fname = rs.getString(1);

  // ...
}
```

---

### java:S2975 — "clone" should not be overridden

**Severity**: Blocker

| Conventional A copy constructor, copy factory or a custom copy function are suitable alternatives to the Object.clone / java.lang.Cloneable mechanism. Consider the following example:

**class Entity implements Cloneable { // Noncompliant, using `Cloneable`**

```java
public int value;
  public List<Entity> children; // deep copy wanted

  Entity() {
    EntityManager.register(this); // invariant
  }


  @Override
  public Entity clone() {
    try {
      Entity copy = (Entity) super.clone(); // invariant not enforced, because no constructor is caled
      copy.children = children.stream().map(Entity::clone).toList();
      return copy;
    } catch (CloneNotSupportedException e) { // this will not happen due to behavioral contract
      throw new AssertionError();
    }

  }
}


The Cloneable / Object.clone mechanism could easily be replaced by copy constructor:

class Entity { // Compliant


  public int value;
  public List<Entity> children; // deep copy wanted

  Entity() {
    EntityManager.register(this); // invariant
```

---

### java:S1113 — The "Object.finalize()" method should not be overridden

**Severity**: High

unpredictable

Before it reclaims storage from an object that is no longer referenced, the garbage collector calls finalize() on the object. But there is no guarantee that this method will be called as soon as the last references to the object are removed. It can be few microseconds to few minutes later. For this reason relying on overriding the finalize() method to release resources or to update the state of the program is highly discouraged. What is the potential impact? More unexpected issues can be caused by relying on the finalize() method to perform important operations on the application state: The JVM might terminate without ever calling this method on a particular object, leaving an unexpected or incomplete state of the program Uncaught exceptions will be ignored inside this method, making it harder to detect issues that could have been logged otherwise Finalizer methods can also be invoked concurrently, even on single-threaded applications, making it hard to maintain desired program invariants

**Noncompliant code example:**

```java
public class MyClass {

  @Override
```

---

### java:S115 — Constant names should comply with a naming convention

**Severity**: High

| Identifiable First, familiarize yourself with the particular naming convention of the project in question. Then, update the name of the constant to match the convention, as well as all usages of the name. For many IDEs, you can use built-in renaming and refactoring features to update all usages of a constant at once.

**Noncompliant code example**

```java
The following example assumes that constant names should match the default regular expression ^[A-Z][A-Z0-9]*(_[A-Z0-9]+)*$:

public class MyClass {
```

**Compliant solution**

```java
public class MyClass {

  public static final float PI = 3.14159f;


  void myMethod() {

    System.out.println(PI);

  }
}

public enum MyEnum {

  OPTION_ONE,
  OPTION_TWO;

}
```

---

### java:S1174 — "Object.finalize()" should remain protected (versus public) when overriding

**Severity**: High

Adaptability

The contract of the Object.finalize() method is clear: only the Garbage Collector is supposed to call this method. Making this method public is misleading, because it implies that any caller can use it.

**Noncompliant code example:**

```java
public class MyClass {

  @Override
```

---

### java:S1175 — The signature of "finalize()" should match that of "Object.finalize()"

**Severity**: High

Object.finalize() is called by the Garbage Collector at some point after the object becomes unreferenced. In general, overloading Object.finalize() is a bad idea because: The overload may not be called by the Garbage Collector. Users are not expected to call Object.finalize() and will get confused. But beyond that it’s a terrible idea to name a method "finalize" if it doesn’t actually override Object.finalize().

**Noncompliant code example**

**Compliant solution**

```java
public int someBetterName(int someParameter) {  // Compliant
  /* ... */
}
```

---

### java:S1186 — Methods should not be empty

**Severity**: High

To fix this issue, either make the method do something, throw an exception, or add a comment to explain why it is empty.

**Noncompliant code example**

**Compliant solution**

```java
public void doSomething() {
  doSomething();

}


public void notImplemented() {
  throw new UnsupportedOperationException("notImplemented() cannot be performed because ...");

}

@Override

public void emptyOnPurpose() {
  // comment explaining why the method is empty

}
```

---

### java:S1192 — String literals should not be duplicated

**Severity**: High

Adaptability Use constants to replace the duplicated string literals. Constants can be referenced from many places, but only need to be updated in a single place.

**Noncompliant code example**

```java
With the default threshold of 3:

public void run() {
```

**Compliant solution**

```java
private static final String ACTION_1 = "action1";  // Compliant


public void run() {

  prepare(ACTION_1);                               // Compliant
  execute(ACTION_1);
  release(ACTION_1);

}

Parameters
threshold	
Number of times a literal must be duplicated to trigger an issue
Default Value:
3
```

---

### java:S1214 — Interfaces should not solely consist of constants

**Severity**: High

bad-practice Adaptability If the concrete value of the constants is not essential, and they serve as mere identifiers, replace the interface with an enum like in the following example:

**public interface Status { // Noncompliant, enum should be used**

```java
int OPEN = 1;
  int CLOSED = 2;

}

public enum Status {      // Compliant
  OPEN,
  CLOSED

}


In some cases, enums are not a suitable option because the concrete constant value is important. Then you should check whether it is appropriate to move them to a specific existing class, for example, if that class is the primary user of the constants:
```

---

### java:S1215 — Execution of the Garbage Collector should be triggered only by the JVM

**Severity**: High

unpredictable Skip to rules filters Quality Profiles Quality Gates Clear All Filters Software quality Security Hotspots Show Security Hotspots Only Available Since Security Category Quality Profile Prioritized Rules Execution of the Garbage Collector should be triggered only by the JVM unpredictable Calling System.gc() or Runtime.getRuntime().gc() is a bad idea for a simple reason: there is no way to know exactly what will be done under the hood by the JVM because the behavior will depend on its vendor, version and options: Will the whole application be frozen during the call? Is the -XX:DisableExplicitGC option activated? Will the JVM simply ignore the call? Like for System.gc(), there is no reason to manually call runFinalization() to force the call of finalization methods of any...

---

### java:S131 — "switch" statements should have "default" clauses

**Severity**: High

Loading...

---

### java:S1452 — Generic wildcard types should not be used in return types

**Severity**: High

A return type containing wildcards cannot be narrowed down in any context. This indicates that the developer’s intention was likely something else. The core problem lies in type variance. Expressions at an input position, such as arguments passed to a method, can have a more specific type than the type expected by the method, which is called covariance. Expressions at an output position, such as a variable that receives the return result from a method, can have a more general type than the method’s return type, which is called contravariance. This can be traced back to the Liskov substitution principle. In Java, type parameters of a generic type are invariant by default due to their potential occurrence in both input and output positions at the same time. A classic example of this is the...

**List<? extends Animal> getAnimals() { ... } // Noncompliant, wildcard with no use**

---

### java:S1598 — Package declaration should match source file directory

**Severity**: High

| Conventional Either move the source file so that the relative file path within the source directory matches the package name, or change the package name so that it matches the relative file path.

**Noncompliant code example**

```java
// file: src/main/foo/Fubar.java

package com.foo.bar;

class Fubar {
}
```

**Compliant solution**

```java
// file: src/main/com/foo/bar/Fubar.java

package com.foo.bar;

class Fubar {
}

// file: src/main/foo/Fubar.java
package foo;

class Fubar {
}
```

---

### java:S1948 — Fields in a "Serializable" class should either be transient or serializable

**Severity**: High

Consider the following scenario. public class Address { public class Person implements Serializable { private static final long serialVersionUID = 1905122041950251207L; private String name;

**  private Address address;  // Noncompliant, Address is not serializable**

```java
}


How to fix this issue depends on the application’s needs. If the field’s value should be preserved during serialization and deserialization, you may want to make the field’s value serializable.

public class Address implements Serializable {
  private static final long serialVersionUID = 2405172041950251807L;


    ...
}

public class Person implements Serializable {
  private static final long serialVersionUID = 1905122041950251207L;

  private String name;

  private Address address; // Compliant, Address is serializable

}


If the field’s value does not need to be preserved during serialization and deserialization, mark it as transient. The field will be ignored when the object is serialized. After deserialization, the field will be set to the default value corresponding to its type (e.g., null for object references).

public class Address {
    ...
}

public class Person implements Serializable {
  private static final long serialVersionUID = 1905122041950251207L;

  private String name;
  private transient Address address; // Compliant, the field is transient
```

---

### java:S1994 — "for" loop increment clauses should modify the loops' counters

**Severity**: High

The counter of a for loop should be updated in the loop’s increment clause. The purpose of a for loop is to iterate over a range using a counter variable. It should not be used for other purposes, and alternative loops should be used in those cases. If the counter is not updated, the loop will be infinite with a constant counter variable. If this is intentional, use a while or do while loop instead of a for loop. If the counter variable is updated within the loop’s body, try to move it to the increment clause. If this is impossible due to certain conditions, replace the for loop with a while or do while loop.

**Noncompliant code example**

```java
Move the counter variable update to the loop’s increment clause.
```

**Compliant solution**

```java
for (i = 0; i < 10; i++) { // Compliant

  // ...
}

int sum = 0

for (int i = 0; i < 10; i++) { // Compliant

  // ...

  sum++;

}
```

---

### java:S2062 — "readResolve" methods should be inheritable

**Severity**: High

Developers may want to add some logic to handle deserialized objects before they are returned to the caller. This can be achieved by implementing the readResolve method. Non-final classes implementing readResolve should not set its visibility to private as this would make it unavailable to child classes. Instead, mark readResolve as protected, allowing it to be inherited.

**Noncompliant code example:**

```java
public class Fruit implements Serializable {
  private static final long serialVersionUID = 1;
```

**Compliant solution:**

```java
public class Fruit implements Serializable {
  private static final long serialVersionUID = 1;
```

---

### java:S2119 — "Random" objects should be reused

**Severity**: High

Define and reuse the Random object.

**Noncompliant code example**

```java
class MyClass {

    public void doSomethingCommon() {
```

**Compliant solution**

```java
class MyClass {

    private Random random = new Random();  // Compliant


    public void doSomethingCommon() {

      int rValue = this.random.nextInt();

    }
}
```

---

### java:S2151 — "runFinalizersOnExit" should not be called

**Severity**: High

| Conventional

Enabling runFinalizersOnExit is unsafe as it might result in erratic behavior and deadlocks on application exit. Indeed, finalizers might be force-called on live objects while other threads are concurrently manipulating them. Instead, if you want to execute something when the virtual machine begins its shutdown sequence, you should attach a shutdown hook.

**Noncompliant code example:**

```java
public static void main(String [] args) {
```

**Compliant solution:**

```java
public static void main(String [] args) {

  Thread myThread = new Thread( () -> { doShutdownOperations(); });
  Runtime.getRuntime().addShutdownHook(myThread);

}

```

---

### java:S2157 — "Cloneables" should implement "clone"

**Severity**: High

This rule raises an issue when a class implements the interface java.lang.Cloneable, but does not override the Object.clone() method. Cloneable is a marker interface that defines the contract of the Object.clone method, which is to create a consistent copy of the instance. The clone method is not defined by the interface though, but by class Objects. The general problem with marker interfaces is that their definitions cannot be enforced by the compiler because they have no own API. When a class implements Cloneable but does not override Object.clone, it is highly likely that it violates the contract for Cloneable. Consider the following example:

**class Foo implements Cloneable { // Noncompliant, override `clone` method**

```java
public int value;
}


Override the clone method in class Foo. By convention, it must call super.clone(). At this point, we know that:

By behavioral contract, Object.clone will not throw a CloneNotSupportedException, because Foo implements Cloneable.
The returned object is an instance of class Foo

We can narrow down the return type of clone to Foo and handle the CloneNotSupportedException inside the function instead of throwing it:

class Foo implements Cloneable { // Compliant


  public int value;


  @Override
  public Foo clone() {
    try {
      return (Foo) super.clone();
    } catch (CloneNotSupportedException e) {
      throw new AssertionError();
    }
  }

}


Be aware that super.clone() returns a one-by-one copy of the fields of the original instance. This means that in our example, the Foo.value field is not required to be explicitly copied in the overridden function.

If you require another copy behavior for some or all of the fields, for example, deep copy or certain invariants that need to be true for a field, these fields must be patched after super.clone():
```

---

### java:S2176 — Class names should not shadow interfaces or superclasses

**Severity**: High

Two classes can have the same simple name if they are in two different packages. package org.foo.domain; public class User { package org.foo.presentation; public class User { However, this becomes an issue when a class has the same name as the superclass it extends or the interfaces it implements, also known as class name shadowing. It is problematic because it can be unclear which class is being referred to in the code, leading to ambiguity and potential bugs. Therefore, it is recommended to use unique and descriptive class names that do not conflict with the names of the superclass or interfaces. This rule raises an issue when a class name shadows its superclass or interface names. Rename the class using a more descriptive name.

**Noncompliant code example**

```java
package org.foo.presentation;
```

**Compliant solution**

```java
package org.foo.presentation;


import org.foo.domain.User;

public class UserView implements User { // Compliant

  // ...
}
```

---

### java:S2390 — Classes should not access their own subclasses during class initialization

**Severity**: High

Adaptability

Referencing a static member of a subclass from its parent during class initialization, makes the code more fragile and prone to future bugs. The execution of the program will rely heavily on the order of initialization of classes and their static members. What is the potential impact? This could create what is known as an "initialization cycle", or even a deadlock in some extreme cases. Additionally, if the order of the static class members is changed, the behavior of the program might change. These issues can be very hard to diagnose so it is highly recommended to avoid creating this kind of dependencies.

**Noncompliant code example:**

```java
class Parent {
```

---

### java:S2479 — Whitespace and control characters in literals should be explicit

**Severity**: High

Non-encoded control characters and whitespace characters are often injected in the source code because of a bad manipulation. They are either invisible or difficult to recognize, which can result in bugs when the string is not what the developer expects. If you actually need to use a control character use their encoded version (ex: ASCII \n,\t,…​ or Unicode U+000D, U+0009,…​). This rule raises an issue when the following characters are seen in a literal string: ASCII control character. (character index < 32 or = 127) Unicode whitespace characters. Unicode C0 control characters Unicode characters U+200B, U+200C, U+200D, U+2060, U+FEFF, U+2028, U+2029 No issue will be raised on the simple space character. Unicode U+0020, ASCII 32.

**Noncompliant code example**

**Compliant solution**

```java
String tabInside = "A\tB";  // Compliant, uses escaped value
String zeroWidthSpaceInside = "foo\u200Bbar";  // Compliant, uses escaped value
char tab = '\t';

Parameters
allowTabsInTextBlocks	
Allow tabs in text blocks
Default Value:
false
```

---

### java:S2638 — Method overrides should not change contracts

**Severity**: High

This rule raises an issue when an overriding method changes a contract defined in a superclass. Because a subclass instance may be cast to and treated as an instance of the superclass, overriding methods should uphold the aspects of the superclass contract that relate to the Liskov Substitution Principle. Specifically, if the parameters or return type of the superclass method are marked with any of the following: @Nullable, @CheckForNull, @NotNull, @NonNull, and @Nonnull, then subclass parameters are not allowed to tighten the contract, and return values are not allowed to loosen it.

**Noncompliant code example:**

```java
public class Fruit {

  private Season ripe;
  private String color;

  public void setRipe(@Nullable Season ripe) {
    this.ripe = ripe;
  }

  public @NotNull Integer getProtein() {
    return 12;
  }
}

public class Raspberry extends Fruit {
```

**Compliant solution:**

```java
public class Fruit {

  private Season ripe;
  private String color;

  public void setRipe(@Nullable Season ripe) {
    this.ripe = ripe;
  }

  public @NotNull Integer getProtein() {
    return 12;
  }
}

public class Raspberry extends Fruit {


  public void setRipe(@Nullable Season ripe) {

    this.ripe = ripe;
  }


  public @NotNull Integer getProtein() {
    return 12;

  }
}

```

---

### java:S2696 — Instance methods should not write to "static" fields

**Severity**: High

multi-threading

---

### java:S3252 — "static" base class members should not be accessed via derived types

**Severity**: High

In object-oriented programming, inappropriately accessing static members of a base class via derived types is considered a code smell. Static members are associated with the class itself, not with any specific instance of the class or its children classes. Accessing through the wrong type suggests a misunderstanding of the ownership and role of this member. This can make the maintenance of the code more complicated. Therefore, the access should be done directly through the base class to maintain clarity and avoid potential misunderstandings.

**Noncompliant code example**

```java
class Parent {
  public static int counter;
}

class Child extends Parent {
  public Child() {
```

**Compliant solution**

```java
class Parent {
  public static int counter;
}

class Child extends Parent {
  public Child() {

    Parent.counter++;

  }
}
```

---

### java:S3776 — Cognitive Complexity of methods should not be too high

**Severity**: High

brain-overload Adaptability Reducing cognitive complexity can be challenging. Here are a few suggestions: Extract complex conditions in a new function. Mixed operators in condition will increase complexity. Extracting the condition in a new function with an appropriate name will reduce cognitive load. Break down large functions. Large functions can be hard to understand and maintain. If a function is doing too many things, consider breaking it down into smaller, more manageable functions. Each function should have a single responsibility. Avoid deep nesting by returning early. To avoid the nesting of conditions, process exceptional cases first and return early. Extraction of a complex condition in a new function.

**Noncompliant code example**

```java
The code is using a complex condition and has a cognitive cost of 3.

double calculateFinalPrice(User user, Cart cart) {
  double total = calculateTotal(cart);

  if (user.hasMembership()                            // +1 (if)
    && user.ordersCount() > 10                        // +1 (more than one condition)
    && user.isAccountActive()
    && !user.hasDiscount()
    || user.ordersCount() == 1) {                    // +1 (change of operator in condition)

    total = applyDiscount(user, total);
  }
  return total;
}
```

**Compliant solution**

```java
Even if the cognitive complexity of the whole program did not change, it is easier for a reader to understand the code of the calculateFinalPrice function, which now only has a cognitive cost of 1.

double calculateFinalPrice(User user, Cart cart) {
  double total = calculateTotal(cart);

  if (isEligibleForDiscount(user)) {                  // +1 (if)

    total = applyDiscount(user, total);
  }
  return total;
}


boolean isEligibleForDiscount(User user) {
  return user.hasMembership()
    && user.ordersCount() > 10                        // +1 (more than one condition)
    && user.isAccountActive()
    && !user.hasDiscount()
    || user.ordersCount() == 1;                       // +1 (change of operator in condition)
}


Break down large functions.
```

---

### java:S3972 — Conditionals should start on new lines

**Severity**: High

Skip to rules filters Quality Profiles Quality Gates Clear All Filters Software quality Security Hotspots Show Security Hotspots Only Available Since Security Category Quality Profile Prioritized Rules Conditionals should start on new lines Placing an if statement on the same line as the closing } from a preceding if, else, or else if block can lead to confusion and potential errors. It may indicate a missing else statement or create ambiguity for maintainers who might fail to understand that the two statements are unconnected. The following code snippet is confusing: if (condition1) {

**} if (condition2) {  // Noncompliant**

```java
//...
}


Either the two conditions are unrelated and they should be visually separated:

if (condition1) {
  // ...

}

if (condition2) {

  //...
}


Or they were supposed to be exclusive and you should use else if instead:

if (condition1) {
  // ...
} else if (condition2) {
  //...
}
```

---

### java:S3973 — A conditionally executed single line should be denoted by indentation

**Severity**: High

Skip to rules filters Quality Profiles Quality Gates Clear All Filters Software quality Security Hotspots Show Security Hotspots Only Available Since Security Category Quality Profile Prioritized Rules A conditionally executed single line should be denoted by indentation When the line immediately after a conditional has neither curly braces nor indentation, the intent of the code is unclear and perhaps not what is executed. Additionally, such code is confusing to maintainers.

**if (condition)  // Noncompliant**

```java
doTheThing();
doTheOtherThing(); // Was the intent to call this function unconditionally?


It becomes even more confusing and bug-prone if lines get commented out.
```

---

### java:S4275 — Getters and setters should access the expected fields

**Severity**: High

Getters and setters provide a way to enforce encapsulation by providing public methods that give controlled access to private fields. However, in classes with multiple fields, it is not unusual that copy and paste is used to quickly create the needed getters and setters, which can result in the wrong field being accessed by a getter or setter. This rule raises an issue in any of these cases: A setter does not update the field with the corresponding name. A getter does not access the field with the corresponding name.

**Noncompliant code example**

```java
class A {
  private int x;
  private int y;
```

**Compliant solution**

```java
class A {
  private int x;
  private int y;

  public void setX(int val) {
    this.x = val;
  }

  public int getY() {
    return this.y;
  }
}
```

---

### java:S4524 — "default" clauses should be last

**Severity**: High

Skip to rules filters Quality Profiles Quality Gates Clear All Filters Software quality Security Hotspots Show Security Hotspots Only Available Since Security Category Quality Profile Prioritized Rules "default" clauses should be last switch can contain a default clause for various reasons: to handle unexpected values, to show that all the cases were properly considered, etc. For readability purposes, to help a developer quickly spot the default behavior of a switch statement, it is recommended to put the default clause at the end of the switch statement. This rule raises an issue if the default clause is not the last one of the switch's cases. switch (param) { doSomething();

**  default: // Noncompliant: default clause should be the last one**

```java
error();
    break;
  case 1:
    doSomethingElse();
    break;
}
```

---

### java:S4601 — "HttpSecurity" URL patterns should be correctly ordered

**Severity**: High

| Conventional Which component or framework contains the issue? The following code is vulnerable because it defines access control configuration in the wrong order.

**Noncompliant code example**

```java
protected void configure(HttpSecurity http) throws Exception {
    http.authorizeRequests()
      .antMatchers("/resources/**", "/signup", "/about").permitAll()
      .antMatchers("/admin/**").hasRole("ADMIN")
```

**Compliant solution**

```java
protected void configure(HttpSecurity http) throws Exception {
    http.authorizeRequests()
      .antMatchers("/resources/**", "/signup", "/about").permitAll()

      .antMatchers("/admin/login").permitAll()

      .antMatchers("/admin/**").hasRole("ADMIN")

      .antMatchers("/db/**").access("hasRole('ADMIN') and hasRole('DBA')")

      .antMatchers("/**", "/home").permitAll()
      .and().formLogin().loginPage("/login").permitAll().and().logout().permitAll();
  }
```

---

### java:S4635 — String offset-based methods should be preferred for finding substrings from offsets

**Severity**: High

Looking for a given substring starting from a specified offset can be achieved by such code: str.substring(beginIndex).indexOf(char1). This works well, but it creates a new String for each call to the substring method. When this is done in a loop, a lot of Strings are created for nothing, which can lead to performance problems if str is large. To avoid performance problems, String.substring(beginIndex) should not be chained with the following methods: indexOf(int ch) indexOf(String str) lastIndexOf(int ch) lastIndexOf(String str) startsWith(String prefix) For each of these methods, another method with an additional parameter is available to specify an offset. Using these methods will avoid the creation of additional String instances. For indexOf methods, adjust the returned value by subtracting the substring index parameter to obtain the same result.

**Noncompliant code example:**

```java

```

**Compliant solution:**

```java
str.indexOf(char1, beginIndex) - beginIndex; // index for char1 not found is (-1-beginIndex)

```

---

### java:S5361 — "String#replace" should be preferred to "String#replaceAll"

**Severity**: High

The underlying implementation of String::replaceAll calls the java.util.regex.Pattern.compile() method each time it is called even if the first argument is not a regular expression. This has a significant performance cost and therefore should be used with care. When String::replaceAll is used, the first argument should be a real regular expression. If it’s not the case, String::replace does exactly the same thing as String::replaceAll without the performance drawback of the regex. This rule raises an issue for each String::replaceAll used with a String as first parameter which doesn’t contains special regex character or pattern.

**Noncompliant code example:**

```java
String init = "Bob is a Bird... Bob is a Plane... Bob is Superman!";
```

**Compliant solution:**

```java
String init = "Bob is a Bird... Bob is a Plane... Bob is Superman!";
String changed = init.replace("Bob is", "It's");
changed = changed.replace("...", ";");


Or, with a regex:

String init = "Bob is a Bird... Bob is a Plane... Bob is Superman!";
String changed = init.replaceAll("\\w*\\sis", "It's");
changed = changed.replaceAll("\\.{3}", ";");

```

---

### java:S5856 — Regular expressions should be syntactically valid

**Severity**: High

Skip to rules filters Quality Profiles Quality Gates Clear All Filters Software quality Security Hotspots Show Security Hotspots Only Available Since Security Category Quality Profile Prioritized Rules Regular expressions should be syntactically valid Regular expressions have their own syntax that is understood by regular expression engines. Those engines will throw an exception at runtime if they are given a regular expression that does not conform to that syntax. To avoid syntax errors, special characters should be escaped with backslashes when they are intended to be matched literally and references to capturing groups should use the correctly spelled name or number of the group. To match a literal string instead of a regular expression, either all special characters should be escaped,...

**Noncompliant code example**

```java
Pattern.compile("([");
str.matches("([");
str.replaceAll("([", "{");
str.matches("(\\w+-(\\d+)");
```

**Compliant solution**

```java
Pattern.compile("\\(\\[");
Pattern.compile("([", Pattern.LITERAL);
str.equals("([");
str.replace("([", "{");
str.matches("(\\w+)-(\\d+)");
```

---

### java:S5994 — Regex patterns following a possessive quantifier should not always fail

**Severity**: High

Skip to rules filters Quality Profiles Quality Gates Clear All Filters Software quality Security Hotspots Show Security Hotspots Only Available Since Security Category Quality Profile Prioritized Rules Regex patterns following a possessive quantifier should not always fail Possessive quantifiers in Regex patterns like below improve performance by eliminating needless backtracking: ?+ , *+ , ++ , {n}+ , {n,}+ , {n,m}+ But because possessive quantifiers do not keep backtracking positions and never give back, the following sub-patterns should not match only similar characters. Otherwise, possessive quantifiers consume all characters that could have matched the following sub-patterns and nothing remains for the following sub-patterns.

**Noncompliant code example**

**Compliant solution**

```java
Pattern pattern1 = Pattern.compile("aa++bc");            // Compliant, for example it can match "aaaabc"
Pattern pattern2 = Pattern.compile("\\d*+(?<=[02468])"); // Compliant, for example it can match an even number like "1234"
```

---

### java:S6001 — Back references in regular expressions should only refer to capturing groups that are matched before the reference

**Severity**: High

Skip to rules filters Quality Profiles Quality Gates Clear All Filters Software quality Security Hotspots Show Security Hotspots Only Available Since Security Category Quality Profile Prioritized Rules Back references in regular expressions should only refer to capturing groups that are matched before the reference When a back reference in a regex refers to a capturing group that hasn’t been defined yet (or at all), it can never be matched. Named back references throw a PatternSyntaxException in that case; numeric back references fail silently when they can’t match, simply making the match fail. When the group is defined before the back reference but on a different control path (like in (.)|\1 for example), this also leads to a situation where the back reference can never match.

**Noncompliant code example**

**Compliant solution**

```java
Pattern.compile("(.)\\1");
Pattern.compile("(?<x>.)\\k<x>");
```

---

### java:S6209 — Members ignored during record serialization should not be used

**Severity**: High

In Records, serialization is not done the same way as for ordinary serializable or externalizable classes. The serialized representation of a record object will be a sequence of values (record components). During the deserialization of records, the stream of components is read and components are constructed. Then the record object is recreated by invoking the record’s canonical constructor with the component values serving as arguments (or default values for absent arguments). This process cannot be customized, so any class-specific writeObject, readObject, readObjectNoData, writeExternal, and readExternal methods or serialPersistentFields fields in record classes are ignored during serialization and deserialization. However, there is a way to substitute serialized/deserialized objects in writeReplace and readResolve. This rule raises an issue when any of writeObject, readObject, readObjectNoData, writeExternal, readExternal or serialPersistentFields are present as members in a Record class.

**Noncompliant code example:**

```java
record Record() implements Serializable {
  @Serial
```

**Compliant solution:**

```java
record Record() implements Serializable {}

record Record() implements Serializable {
  private Object writeReplace() throws ObjectStreamException {
    ...
  }
  private Object readResolve() throws ObjectStreamException {
    ...
  }
}

```

---

### java:S6432 — Counter Mode initialization vectors should not be reused

**Severity**: High

Which component or framework contains the issue? BouncyCastle Java Cryptography Extension The example uses a hardcoded IV as a nonce, which causes AES-CCM to be insecure. To fix it, a nonce is randomly generated instead.

**Noncompliant code example**

```java
public void encrypt(byte[] key, byte[] ptxt) {

    byte[] nonce = "7cVgr5cbdCZV".getBytes(StandardCharsets.UTF_8);


    BlockCipher engine = new AESEngine();
    AEADParameters params = new AEADParameters(new KeyParameter(key), 128, nonce);
    CCMBlockCipher cipher = new CCMBlockCipher(engine);
```

**Compliant solution**

```java
public void encrypt(byte[] key, byte[] ptxt) {

    SecureRandom random = new SecureRandom();
    byte[] nonce = new byte[12];
    random.nextBytes(nonce);


    BlockCipher engine = new AESEngine();
    AEADParameters params = new AEADParameters(new KeyParameter(key), 128, nonce);
    CCMBlockCipher cipher = new CCMBlockCipher(engine);


    cipher.init(true, params);

}
```

---

### java:S6814 — Optional REST parameters should have an object type

**Severity**: High

| Conventional Replace primitive types, such as boolean, char, int, with the corresponding wrapper type, such as Boolean, Character, Integer. Alternatively, you might choose to remove required = false from the annotation and use an Optional<T> type for the parameter, such as Optional<Boolean> or Optional<String>, which automatically makes the REST parameter optional. This is the preferred approach because it enforces the proper handling of null in the method implementation.

**Noncompliant code example**

```java
@RequestMapping(value = {"/article", "/article/{id}"})
```

**Compliant solution**

```java
@RequestMapping(value = {"/article", "/article/{id}"})

public Article getArticle(@PathVariable(required = false) Integer articleId) { // Compliant

   //...
}
```

---

### java:S6876 — Reverse iteration should utilize reversed view

**Severity**: High

| Conventional Replace the reported statement with a forward-iteration over the reversed view of the collection.

**Noncompliant code example**

```java
void printLastToFirst(List<String> list) {

  for (var it = list.listIterator(list.size()); it.hasPrevious();) {
    var element = it.previous();

    System.out.println(element);
  }
}
```

**Compliant solution**

```java
void printLastToFirst(List<String> list) {

  for (var element: list.reversed()) {

    System.out.println(element);
  }
}
```

---

### java:S6877 — Reverse view should be used instead of reverse copy in read-only cases

**Severity**: High

| Conventional Remove Collections.reverse(list); and replace list with list.reversed() after.

**Noncompliant code example**

```java
void foo() {
  var list = new ArrayList<String>();
  list.add("A");
  list.add("B");
```

**Compliant solution**

```java
void foo() {
  var list = new ArrayList<String>();
  list.add("A");
  list.add("B");

  for (var e : list.reversed()) {  // Compliant

    // ...
  }
}
```

---

### javaarchitecture:S7788 — Relationships should align with the intended architecture

**Severity**: High

Sonar Architecture (Java) architecture Adaptability Remove or refactor the deviating dependency. This may involve replacing the dependency with an allowed one, moving code to appropriate classes or packages, or introducing new abstractions. The exact solution depends on your project’s specific situation and the code deviating the intended architecture.

**Noncompliant code example**

```java
If the intended architecture prohibits classes in package com.example.panels to depend on classes in com.example.repo, then the following code example is noncompliant:

package com.example.panels;


import com.example.repos.CustomerRepo;


class ShowCustomersPanel extends Panel {


    CustomerRepo customerRepo = ...;



    List<Customer> customers = customerRepo.findAll();

}
```

**Compliant solution**

```java
A solution could be to call into the service layer instead.

package com.example.panels;


import com.example.services.CustomerService;


class ShowCustomersPanel extends Panel {


    CustomerService customerService = ...;



    List<Customer> customers = customerService.getAllCustomers();

}
```

---

### javaarchitecture:S7789 — Classes should be located according to the intended architecture

**Severity**: High

Sonar Architecture (Java) architecture Adaptability Move the relevant class to its intended location or rename the relevant package as intended.

**Noncompliant code example**

```java
If the intended architecture declares developers should use the package name com.example.panel, not com.example.panels, then the following code example is noncompliant:

package com.example.panels;


class ShowCustomersPanel extends Panel {
  // ...
}
```

**Compliant solution**

```java
The solution is to move the class to its appropriate package, or respectively, to rename the package panels to panel.

package com.example.panel;



import com.example.services.CustomerService;


class ShowCustomersPanel extends Panel {
  // ...
}
```

---

### javaarchitecture:S8134 — Forbidden relationships should be removed to solve tangles as directed by the project's architect

**Severity**: High

Sonar Architecture (Java) architecture Adaptability Remove or refactor the problematic dependency. This may involve replacing the dependency with an allowed one, moving code to appropriate classes or packages, or introducing new abstractions. The exact solution depends on your project’s specific situation.

**Noncompliant code example**

```java
The following code contains two cycles: Order → Customer → Order, and Order → Product → Order. Furthermore, both cycles are connected to each other via class Order. This is called a tangle consisting of two cycles.

class Order {
    public Customer customer;
    public List<Product> products;
}

class Customer {
    public List<Order> orders;

}

class Product {
    public List<Order> orders;
}
```

**Compliant solution**

```java
The issue can be resolved by changing the structure. Two service functions can replace the dependencies Customer → Order and Product → Order.

class Order {
    public Customer customer;
    public List<Product> products;
}

class Customer { }
class Product { }
interface OrderService {
  List<Order> getOrdersByCustomer(Customer customer);
  List<Order> getOrdersByProduct(Product product);

}
```

---

### javabugs:S6322 — Unsupported methods should not be called on some collection implementations

**Severity**: High

Dataflow Bug Detection SonarAnalyzer (Java) When calling a method labeled as optional, you should make sure that the implementation class on which the call is made indeed supports this method.

**Noncompliant code example**

```java
List<String> list = Collections.emptyList(); // The list implementation returned here is unmodifiable.
if (someCondition) {
```

**Compliant solution**

```java
List<String> list = new ArrayList<>();
if (someCondition) {
  list.add("hello");
}
return list;


or

if (someCondition) {
  return Collections.singletonList("hello");
}
return Collections.emptyList();
```

---

