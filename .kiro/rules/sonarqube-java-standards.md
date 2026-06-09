# SonarQube Java Review Standards

This rule defines the SonarQube-based Java code review criteria. Apply these
standards when the target project contains Java source code. Rules are sourced
from SonarQube's Java analyzer and organized by review category.

Each rule includes its SonarQube rule key, severity, explanation, and
Noncompliant/Compliant code examples to guide pattern matching during review.

**Total: 341 rules (27 Blocker, 80 High, 234 Medium)**

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
based on the organization's risk assessment. When a rule is a Security Hotspot
type, this is noted in its description where applicable.

---

## 1. Security Rules (37 rules)

These rules detect security vulnerabilities including injection attacks, credential leaks, cryptographic weaknesses, and authentication flaws.

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

---

---

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

---

---

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

---

---

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

---

---

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

---

---

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

---

---

---

### java:S2235 — "IllegalMonitorStateException" should not be caught

**Severity**: High

error-handling

---

---

---

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

---

---

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

---

---

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

---

---

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

---

---

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

---

---

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

---

---

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

---

---

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

---

---

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

---

---

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

---

---

---

### java:S131 — "switch" statements should have "default" clauses

**Severity**: High

Loading...

---

---

---

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

---

---

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

---

---

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

---

---

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

---

---

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

---

---

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

---

---

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

---

---

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

---

---

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

---

---

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

---

---

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

---

---

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

---

---

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

---

---

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

---

---

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

---

---

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

---

---

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

---

---

---

### java:S1163 — Exceptions should not be thrown in finally blocks

**Severity**: High

error-handling

---

---

---

---

### java:S1215 — Execution of the Garbage Collector should be triggered only by the JVM

**Severity**: High

unpredictable Skip to rules filters Quality Profiles Quality Gates Clear All Filters Software quality Security Hotspots Show Security Hotspots Only Available Since Security Category Quality Profile Prioritized Rules Execution of the Garbage Collector should be triggered only by the JVM unpredictable Calling System.gc() or Runtime.getRuntime().gc() is a bad idea for a simple reason: there is no way to know exactly what will be done under the hood by the JVM because the behavior will depend on its vendor, version and options: Will the whole application be frozen during the call? Is the -XX:DisableExplicitGC option activated? Will the JVM simply ignore the call? Like for System.gc(), there is no reason to manually call runFinalization() to force the call of finalization methods of any...

---

---

---

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

---

---

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

---

---

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

---

---

---

### java:S1452 — Generic wildcard types should not be used in return types

**Severity**: High

A return type containing wildcards cannot be narrowed down in any context. This indicates that the developer’s intention was likely something else. The core problem lies in type variance. Expressions at an input position, such as arguments passed to a method, can have a more specific type than the type expected by the method, which is called covariance. Expressions at an output position, such as a variable that receives the return result from a method, can have a more general type than the method’s return type, which is called contravariance. This can be traced back to the Liskov substitution principle. In Java, type parameters of a generic type are invariant by default due to their potential occurrence in both input and output positions at the same time. A classic example of this is the...

**List<? extends Animal> getAnimals() { ... } // Noncompliant, wildcard with no use**

---

---

---

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

---

---

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

---

---

---

### java:S2696 — Instance methods should not write to "static" fields

**Severity**: High

multi-threading

---

---

---

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

---

---

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

---

---

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

---

---

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

---

---

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

---

---

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

---

---

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

---

---

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

---

---

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

---

---

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

---

---

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

---

---

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

---

---

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

---

---

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

---

---

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

---

---

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

---

---

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

---

---

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

---

---

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

---

---

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

---

---

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

---

---

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

---

---

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

---

---

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

---

---

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

---

---

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

---

---

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

---

---

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

---

---

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

---

---

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

---

---

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

---

---

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


---

# Medium-Severity Rules

The following rules are classified as **Medium** severity in the
organization's SonarQube quality profile. Medium-severity issues
MUST be assigned a fix priority (P0–P3). A Medium issue rated P0
will cause the quality gate to **Fail**.

## 10. Security Rules — Medium (19 rules)

---

---

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

---

---

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

---

---

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

---

---

---

### javabugs:S3518 — Zero should not be a possible denominator

**Severity**: High

Dataflow Bug Detection SonarAnalyzer (Java)

---

---

---

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

---

---

---

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

---

---

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

---

---

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

---

---

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

---

---

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

---

---

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

---

---

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

---

---

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

---

---

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

---

---

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

---

---

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

---

---

---

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

---

---

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

---

---

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

---

---

---

### java:S2236 — Methods "wait(...)", "notify()" and "notifyAll()" should not be called on Thread instances

**Severity**: Blocker

multi-threading

---

---

---

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

---

---

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

---

---

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

---

---

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

---

---

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

---

---

---

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

---

---

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

---

---

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

---

---

---

### java:S2187 — TestCases should contain tests

**Severity**: Blocker

Adaptability Skip to rules filters Quality Profiles Quality Gates Clear All Filters Software quality Security Hotspots Show Security Hotspots Only Available Since Security Category Quality Profile Prioritized Rules TestCases should contain tests Adaptability There’s no point in having a JUnit TestCase without any test methods. Similarly, you shouldn’t have a file in the tests directory named *Test, *Tests, or *TestCase, but no tests in the file. Doing either of these things may lead someone to think that uncovered classes have been tested. This rule raises an issue when files in the test directory are named *Test, *Tests, or *TestCase or implement TestCase but don’t contain any tests. Supported frameworks: TestClassNamePattern Test class name pattern (regular expression) Default Value:...

---

---

---

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

---

---

---

### java:S2437 — Unnecessary bit operations should not be performed

**Severity**: Blocker

Skip to rules filters Quality Profiles Quality Gates Clear All Filters Software quality Security Hotspots Show Security Hotspots Only Available Since Security Category Quality Profile Prioritized Rules Unnecessary bit operations should not be performed Certain bit operations are just silly and should not be performed because their results are predictable. Specifically, using & -1 with any value will always result in the original value, as will anyValue ^ 0 and anyValue | 0.

---

---

---

---

### java:S1144 — Unused "private" methods should be removed

**Severity**: Medium

A method that is never called is dead code, and should be removed. Cleaning out dead code decreases the size of the maintained codebase, making it
easier to understand the program and preventing bugs from being introduced.

---

---

---

---

### java:S110 — Inheritance tree of classes should not be too deep

**Severity**: Medium

Inheritance is one of the most valuable concepts in object-oriented programming. It’s a way to categorize and reuse code by creating collections of
attributes and behaviors called classes, which can be based on previously created classes.

---

---

---

---

### javabugs:S2259 — Null pointers should not be dereferenced

**Severity**: Medium

A reference to 
`null`
 should never be dereferenced/accessed. Doing so will cause a 
`NullPointerException`
 to be thrown. At
best, such an exception will cause abrupt program termination. At worst, it could expose debugging information that would be useful to an attacker, or
it could allow an attacker to bypass security measures.

**Noncompliant code example**

```java
public void method(Object input) {
  if (input == null) {
    // ...
  }
  System.out.println(input.toString()); // Noncompliant
}
```

**Compliant solution**

```java
public void method(Object input) {
  if (input == null) {
    // ...
    return;
  }
  System.out.println(input.toString());
```

---

---

---

---

### java:S2273 — "Object.wait()", "Object.notify()" and "Object.notifyAll()" should only be called from synchronized code

**Severity**: Medium

The 
`Object.wait(…​)`
, 
`Object.notify()`
 and 
`Object.notifyAll()`
 methods are used in multithreaded environments
to coordinate interdependent tasks that are performed by different threads. These methods are not thread-safe and by contract, they require the
invoking 
`Thread`
 to own the object’s monitor. If a thread invokes one of these methods without owning the object’s monitor an

`IllegalMonitorStateException`
 is thrown.

**Noncompliant code example**

```java
private void performSomeAction(Object syncValue) {
  while (!suitableCondition()){
    syncValue.wait(); // Noncompliant, not being inside a `synchronized` block, this will raise an IllegalMonitorStateException
  }
  ... // Perform some action
}
```

**Compliant solution**

```java
private void performSomeAction(Object syncValue) {
  synchronized(syncValue) {
    while (!suitableCondition()){
      syncValue.wait(); // Compliant, the `synchronized` block guarantees ownership of syncValue's monitor
    }
    ... // Perform some action
  }
}
```

---

---

---

---

### java:S2864 — "entrySet()" should be iterated when both the key and value are needed

**Severity**: Medium

`Map`
 is an object that maps keys to values. A map cannot contain duplicate keys, which means each key can map to at most one value.

---

---

---

---

### java:S6906 — Virtual threads should not run tasks that include synchronized code

**Severity**: Medium

Java virtual threads enable the JVM to optimize the use of OS threads by mounting and unmounting them as needed. This makes them more efficient
when dealing with blocking operations such as I/O or HTTP requests.

---

---

---

---

### java:S1854 — Unused assignments should be removed

**Severity**: Medium

Dead stores refer to assignments made to local variables that are subsequently never used or immediately overwritten. Such assignments are
unnecessary and don’t contribute to the functionality or clarity of the code. They may even negatively impact performance. Removing them enhances code
cleanliness and readability. Even if the unnecessary operations do not do any harm in terms of the program’s correctness, they are - at best - a waste
of computing resources.

Exceptions

This rule ignores initializations to 
`-1`
, 
`0`
, 
`1`
, 
`null`
, 
`true`
, 
`false`
 and

`""`
.

**Noncompliant code example**

```java
int foo(int y) {
  int x = 100; // Noncompliant: dead store
  x = 150;     // Noncompliant: dead store
  x = 200;
  return x + y;
}
```

**Compliant solution**

```java
int foo(int y) {
  int x = 200; // Compliant: no unnecessary assignment
  return x + y;
}
```

---

---

---

---

### java:S1844 — "Object.wait" should not be called on objects that implement "java.util.concurrent.locks.Condition"

**Severity**: Medium

The 
`java.util.concurrent.locks.Condition`
 interface provides an alternative to the 
`Object`
 monitor methods
(
`wait`
, 
`notify`
 and 
`notifyAll`
). Hence, the purpose of implementing said interface is to gain access to its more
nuanced 
`await`
 methods.

Consequently, calling the method 
`Object.wait`
 on a class implementing the 
`Condition`
 interface is contradictory and should
be avoided. Use 
`Condition.await`
 instead.

Noncompliant code example

```

void doSomething(Condition condition) {
    condition.wait(); // Noncompliant, Object.wait is called

        ...
}

```

Compliant solution

```

void doSomething(Condition condition) {
    condition.await(); // Compliant, Condition.await is called

        ...
}

```

---

---

---

---

### java:S1849 — "Iterator.hasNext()" should not call "Iterator.next()"

**Severity**: Medium

Calling 
`Iterator.hasNext()`
 is not supposed to have any side effects and hence should not change the iterator’s state.

`Iterator.next()`
 advances the iterator by one item. So calling it inside 
`Iterator.hasNext()`
 breaks the 
`hasNext()`

contract and will lead to unexpected behavior in production.

**Noncompliant code example**

```java
class MyIterator implements Iterator<Integer> {

  private Queue<Integer> elements;

    ...

  @Override
  public boolean hasNext() {
    try {
      next(); // Noncompliant, next() is called from hasNext()
      return true;
    } catch (NoSuchElementException e) {
      return false;
    }
  }

  @Override
  public Integer next() {
    return elements.remove();
  }
}
```

**Compliant solution**

```java
class MyIterator implements Iterator<Integer> {

  private Queue<Integer> elements;

    ...

  @Override
  public boolean hasNext() {
    return !elements.isEmpty(); // Compliant, no call to next()
  }

  @Override
  public Integer next() {
    return elements.remove();
  }
}
```

---

---

---

---

### java:S3034 — Raw byte values should not be used in bitwise operations in combination with shifts

**Severity**: Medium

In Java, numeric promotions happen when two operands of an arithmetic expression have different sizes. More specifically, narrower operands get
promoted to the type of wider operands. For instance, an operation between a 
`byte`
 and an 
`int`
, will trigger a promotion of
the 
`byte`
 operand, converting it into an 
`int`
.

**Noncompliant code example**

```java
public static void main(String[] args) {
    byte[] bytes12 = BigInteger.valueOf(12).toByteArray(); // This byte array will be simply [12]
    System.out.println(intFromBuffer(bytes12)); // In this case, the bytes promotion will not cause any issues, and "12" will be printed.

    // Here the bytes will be [2, -128] since 640 in binary is represented as 0b0000_0010_1000_0000
    // which is equivalent to the concatenation of 2 bytes: 0b0000_0010 = 2, and 0b1000_0000 = -128
    byte[] bytes640 = BigInteger.valueOf(640).toByteArray();

    // In this case, the shifting operation combined with the bitwise OR, will produce the wrong binary string and "-128" will be printed.
    System.out.println(intFromBuffer(bytes640));
  }

  static int intFromBuffer(byte[] bytes) {
    int originalInt = 0;
    for (int i = 0; i < bytes.length; i++) {
      // Here the right operand of the bitwise OR, which is a byte, will be promoted to an `int`
      // and if its value was negative, the added ones in front of the binary string will alter the value of the `originalInt`
      originalInt = (originalInt << 8) | bytes[i]; // Noncompliant
    }
    return originalInt;
  }
```

**Compliant solution**

```java
public static void main(String[] args) {
    byte[] bytes12 = BigInteger.valueOf(12).toByteArray(); // This byte array will be simply [12]
    System.out.println(intFromBuffer(bytes12)); // In this case, the bytes promotion will not cause any issues, and "12" will be printed.

    // Here the bytes will be [2, -128] since 640 in binary is represented as 0b0000_0010_1000_0000
    // which is equivalent to the concatenation of 2 bytes: 0b0000_0010 = 2, and 0b1000_0000 = -128
    byte[] bytes640 = BigInteger.valueOf(640).toByteArray();

    // This will correctly print "640" now.
    System.out.println(intFromBuffer(bytes640));
  }

  static int intFromBuffer(byte[] bytes) {
    int originalInt = 0;
    for (int i = 0; i < bytes.length; i++) {
      originalInt = (originalInt << 8) | Byte.toUnsignedInt(bytes[i]); // Compliant, only the relevant 8 least significant bits will affect the bitwise OR
    }
    return originalInt;
  }
```

---

---

---

---

### java:S1191 — Classes from "sun.*" packages should not be used

**Severity**: Medium

The classes in the 
`sun.*`
 packages are not part of the official Java API and are not intended for public use. They are internal
implementation details specific to the Oracle JDK (Java Development Kit). Therefore, their availability, behavior, or compatibility is not guaranteed
across different Java implementations or versions.

---

---

---

---

### java:S7482 — Don't provide an initializer for a stateless stream gatherer

**Severity**: Medium

Stateless stream gatherers, which process each element of the stream independently, don’t need an initializer function. That’s because the role of
the initializer function is to set up the gatherer’s private state object.

---

---

---

---

### java:S4030 — Collection contents should be used

**Severity**: Medium

If a collection is declared and populated but its values are never read anywhere in the code, it can be considered unused. This often arises from
incomplete refactoring, copy-pasting errors, or typos. Unused collections can lead to wasted memory and degraded application performance.
Additionally, their presence makes the code harder to read and understand.

**Noncompliant code example**

```java
int getLength(String a, String b, String c) {
  List<String> strings = new ArrayList<>();  // Noncompliant: List is declared and populated but never read.
  strings.add(a);
  strings.add(b);
  strings.add(c);

  return a.length() + b.length() + c.length();
}
```

**Compliant solution**

```java
int getLength(String a, String b, String c) {
  return a.length() + b.length() + c.length();
}
```

---

---

---

---

### java:S3063 — "StringBuilder" data should be used

**Severity**: Medium

`StringBuffer`
 and 
`StringBuilder`
 instances that are 
`append`
ed but never 
`toString`
ed needlessly
clutter the code, and worse are a drag on performance. Either they should be removed, or the missing 
`toString`
 call added.

---

---

---

---

### java:S2226 — Servlets should not have mutable instance fields

**Severity**: Medium

The 
`processHttpRequest`
 method and methods called from it can be executed by multiple threads within the same servlet instance, and
state changes to the instance caused by these methods are, therefore, not threadsafe.

**Noncompliant code example**

```java
public class MyServlet extends HttpServlet {
  String apiVersion = "0.9.1"; // Noncompliant, field changes are not thread-safe
}
```

**Compliant solution**

```java
public class MyServlet extends HttpServlet {
  final String apiVersion = "0.9.1"; // Compliant, field cannot be changed
}
```

---

---

---

---

### java:S6829 — "@Autowired" should be used when multiple constructors are provided

**Severity**: Medium

The Spring dependency injection mechanism cannot identify which constructor to use for auto-wiring when multiple constructors are present in a
class. This ambiguity can cause the application to crash at runtime, and it makes the code less clear to understand and more complex to extend and
maintain.

**Noncompliant code example**

```java
@Component
public class ExampleClass { // Noncompliant: multiple constructors present and no @Autowired annotation to specify which one to use

    private final DependencyClass1 dependency1;

    public ExampleClass() {
        throw new UnsupportedOperationException("Not supported yet.");
    }

    public ExampleClass(DependencyClass1 dependency1) {
        this.dependency1 = dependency1;
    }

    // ...
}
```

**Compliant solution**

```java
@Component
public class ExampleClass {

    private final DependencyClass1 dependency1;

    public ExampleClass() {
        throw new UnsupportedOperationException("Not supported yet.");
    }

    @Autowired
    public ExampleClass(DependencyClass1 dependency1) {
        this.dependency1 = dependency1;
    }

    // ...
}
```

---

---

---

---

### java:S2230 — Methods with Spring proxying annotations should be public

**Severity**: Medium

Marking a non-public method 
`@Async`
 or 
`@Transactional`
 is misleading because, up to version 5, Spring does not recognize
non-public methods, and so makes no provision for their proper invocation. Nor does Spring make provision for the methods invoked by the method it
called. Since Spring 6, protected and package-private methods can be handled, but the issue remains for private methods.

Therefore, marking a private method, for instance, @Transactional gives a false sense of security, and can lead to incorrect assumptions and
potential bugs.

Exceptions

The rule targets all non-public methods for project using Spring up to Spring 5, but only private methods for Spring 6 because Spring 6 takes into
account all non-private methods.

**Noncompliant code example**

```java
@Async
private Future<String> asyncMethodWithReturnType() { // Noncompliant, no proxy generated and
    return "Hellow, world!";                         // can only be invoked from same class
}
```

**Compliant solution**

```java
@Async
public Future<String> asyncMethodWithReturnType() { // Compliant
    return "Hellow, world!";
}
```

---

---

---

---

### java:S6838 — "@Bean" methods for Singleton should not be invoked in "@Configuration" when proxyBeanMethods is false

**Severity**: Medium

When setting the 
`proxyBeanMethods`
 attribute to 
`false`
 the 
`@Bean`
 methods are not proxied and this is similar
to removing the 
`@Configuration`
 stereotype. In this scenario, 
`@Bean`
 methods within the 
`@Configuration`
 annotated
class operate in 
[lite
mode](https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/context/annotation/Bean.html)
, resulting in a new bean creation each time the method is invoked.

For 
`Singleton`
 beans, this could cause unexpected outcomes as the bean is created multiple times instead of being created once and
cached.

The rule raises an issue when the 
`proxyBeanMethods`
 attribute is set to 
`false`
 and the 
`@Bean`
 method of a

`Singleton`
 bean is directly invoked in the 
`@Configuration`
 annotated class code.

**Noncompliant code example**

```java
@Configuration(proxyBeanMethods = false)
class ConfigurationExample {
  @Bean
  public SingletonBean singletonBean() {
    return new SingletonBean();
  }

  @Bean
  @Scope("prototype")
  public PrototypeBean prototypeBean() {
    return new PrototypeBean(singletonBean()); // Noncompliant: a "singletonBean" is created every time a prototypeBean is created
  }

  class SingletonBean {
    // ...
  }

  class PrototypeBean {
    // ...

    public PrototypeBean(SingletonBean singletonBean) {
      // ...
    }

    // ...
  }
}
```

**Compliant solution**

```java
@Configuration(proxyBeanMethods = false)
class ConfigurationExample {
  @Bean
  public SingletonBean singletonBean() {
    return new SingletonBean();
  }

  @Bean
  @Scope("prototype")
  public PrototypeBean prototypeBean(SingletonBean singletonBean) { // Compliant, the singletonBean is injected in the context and used by every prototypeBean
    return new PrototypeBean(singletonBean);
  }

  class SingletonBean {
    // ...
  }

  class PrototypeBean {
    // ...

    public PrototypeBean(SingletonBean singletonBean) {
      // ...
    }

    // ...
  }
}
```

---

---

---

---

### java:S7180 — "@Cache*" annotations should only be applied on concrete classes

**Severity**: Medium

Annotating interfaces or interface methods with 
`@Cache*`
 annotations is not recommended by the official Spring documentation:

**Noncompliant code example**

```java
public interface ExampleService {

    @Cacheable("exampleCache") // Noncompliant: interface method is annotated with @Cacheable
    String getData(String id);
}
```

**Compliant solution**

```java
public interface Zoo {
    @Cacheable("popAnimal") //non compliant, interface method is annotated with @Cacheable
    Animal getMostPopularAnimal();
}

public class SanDiegoZoo implements Zoo {
    @Override
    public Animal getMostPopularAnimal() {
        return new Lion();
    }
}

public class RomeBioparc implements Zoo {
    @Override
    public Animal getMostPopularAnimal() {
        return new Pantegana();
    }
}
```

---

---

---

---

### java:S1217 — "Thread.run()" should not be called directly

**Severity**: Medium

The likely intention of a user calling 
`Thread.run()`
 is to start the execution of code within a new thread. This, however, is not what
happens when this method is called.

The purpose of 
`Thread.run()`
 is to provide a method that users can overwrite to specify the code to be executed. The actual thread is
then started by calling 
`Thread.start()`
. When 
`Thread.run()`
 is called directly, it will be executed as a regular method within
the current thread.

**Noncompliant code example**

```java
Thread myThread = new Thread(runnable);
myThread.run(); // Noncompliant, does not start a thread
```

**Compliant solution**

```java
Thread myThread = new Thread(runnable);
myThread.start(); // Compliant
```

---

---

---

---

### java:S2885 — Non-thread-safe fields should not be static

**Severity**: Medium

When an object is marked as 
`static`
, it means that it belongs to the class rather than any class instance. This means there is only one
copy of the static object in memory, regardless of how many class instances are created. Static objects are shared among all instances of the class
and can be accessed using the class name rather than an instance of the class.

**Noncompliant code example**

```java
public class MyClass {
  private static Calendar calendar = Calendar.getInstance();  // Noncompliant
  private static SimpleDateFormat format = new SimpleDateFormat("HH-mm-ss");  // Noncompliant
}
```

**Compliant solution**

```java
public class MyClass {
  private Calendar calendar = Calendar.getInstance();
  private SimpleDateFormat format = new SimpleDateFormat("HH-mm-ss");
}
```

---

---

---

---

### java:S2886 — Getters and setters should be synchronized in pairs

**Severity**: Medium

A synchronized method is a method marked with the 
`synchronized`
 keyword, meaning it can only be accessed by one thread at a time. If
multiple threads try to access the synchronized method simultaneously, they will be blocked until the method is available.

**Noncompliant code example**

```java
public class Person {
  String name;
  int age;

  public synchronized void setName(String name) {
    this.name = name;
  }

  public String getName() {  // Noncompliant
    return this.name;
  }

  public void setAge(int age) {  // Noncompliant
    this.age = age;
  }

  public int getAge() {
    synchronized (this) {
      return this.age;
    }
  }
}
```

**Compliant solution**

```java
public class Person {
  String name;
  int age;

  public synchronized void setName(String name) {
    this.name = name;
  }

  public synchronized String getName() {
    return this.name;
  }

  public void setAge(int age) {
    synchronized (this) {
      this.age = age;
   }
  }

  public int getAge() {
    synchronized (this) {
      return this.age;
    }
  }
}
```

---

---

---

---

### java:S6856 — "@PathVariable" annotation should be present if a path variable is used

**Severity**: Medium

The 
`@PathVariable`
 annotation in Spring extracts values from the URI path and binds them to method parameters in a Spring MVC
controller. It is commonly used with 
`@GetMapping`
, 
`@PostMapping`
, 
`@PutMapping`
, and 
`@DeleteMapping`
 to
capture path variables from the URI. These annotations map HTTP requests to specific handler methods in a controller. They are part of the Spring Web
module and are commonly used to define the routes for different HTTP operations in a RESTful API.

**Noncompliant code example**

```java
@GetMapping("/api/resource/{id}")
public ResponseEntity<String> getResourceById(Long id) { // Noncompliant - The 'id' parameter will not be automatically populated with the path variable value
  return ResponseEntity.ok("Fetching resource with ID: " + id);
}

@GetMapping("/api/asset/")
public ResponseEntity<String> getAssetById(@PathVariable Long id) { // Noncompliant - The 'id' parameter does not have a corresponding placeholder
  return ResponseEntity.ok("Fetching asset with ID: " + id);
}
```

**Compliant solution**

```java
@GetMapping("/api/resource/{id}")
public ResponseEntity<String> getResourceById(@PathVariable Long id) { // Compliant
  return ResponseEntity.ok("Fetching resource with ID: " + id);
}

@GetMapping("/api/asset/{id}")
public ResponseEntity<String> getAssetById(@PathVariable Long id) {
  return ResponseEntity.ok("Fetching asset with ID: " + id);
}
```

---

---

---

---

### java:S7177 — Use appropriate @DirtiesContext modes

**Severity**: Medium

In a Spring application, the 
`@DirtiesContext`
 annotation marks the ApplicationContext as dirty and indicates that it should be cleared
and recreated. This is important in tests that modify the context, such as altering the state of singleton beans or databases.

Misconfiguring 
`@DirtiesContext`
 by setting the 
`methodMode`
 at the class level or the 
`classMode`
 at the method
level will make the annotation have no effect.

This rule will raise an issue when the incorrect mode is configured on a @DirtiesContext annotation targeting a different scope.

**Noncompliant code example**

```java
@ContextConfiguration
@DirtiesContext(methodMode = MethodMode.AFTER_METHOD) // Noncompliant, for class-level control, use classMode instead.
public class TestClass {
  @DirtiesContext(classMode = DirtiesContext.ClassMode.AFTER_CLASS) // Non compliant, for method-level control use methodMode instead
  public void test() {...}
}
```

**Compliant solution**

```java
@ContextConfiguration
@DirtiesContext(classMode = DirtiesContext.ClassMode.AFTER_CLASS)
public class TestClass {
  @DirtiesContext(methodMode = MethodMode.AFTER_METHOD)
  public void test() {...}
}
```

---

---

---

---

### java:S7179 — @Cacheable and @CachePut should not be combined

**Severity**: Medium

`@Cacheable`
 annotation is used to store the result of a method and avoid executing it for the same inputs. 
`@CachePut`

instead is used to force the execution of a method and store the result in the cache. Annotating a method with both will produce unreliable behavior,
except for specific corner-cases when their 
`condition()`
 or 
`unless()`
 expressions are mutually exclusive. Hence this pattern
is strongly discouraged and an issue will be raised on such cases.

**Noncompliant code example**

```java
@Cacheable
@CachePut
void getBook(String isbn){ // Non compliant, methods annotated with both @Cacheable and @CachePut will not behave as intended
    ...
}
```

**Compliant solution**

```java
@Cacheable
void getBook(String isbn){
    ...
}
```

---

---

---

---

### java:S7183 — @InitBinder methods should have void return type

**Severity**: Medium

Spring provides the 
`@InitBinder`
 annotation to initialize a 
`WebDataBinder`
 instance for controllers. This is useful to bind
request parameters to a model object, and to plug converters and formatters into this process.

Methods annotated with 
`@InitBinder`
 must not have a return value, otherwise the controller containing them will throw an exception when
invoked.

This rule raises an issue when a method annotated with 
`@InitBinder`
 does not have a 
`void`
 return type

**Noncompliant code example**

```java
@Controller
public class MyController {

	@InitBinder
	public String initBinder(WebDataBinder binder) { // Non compliant, make the @InitBinder method return void
		SimpleDateFormat dateFormat = new SimpleDateFormat("yyyy-MM-dd");
		dateFormat.setLenient(false);
		binder.registerCustomEditor(Date.class, new CustomDateEditor(dateFormat, false));
        return "OK";
	}

	// ...
}
```

**Compliant solution**

```java
@Controller
public class MyController {

	@InitBinder
	public void initBinder(WebDataBinder binder) {
		SimpleDateFormat dateFormat = new SimpleDateFormat("yyyy-MM-dd");
		dateFormat.setLenient(false);
		binder.registerCustomEditor(Date.class, new CustomDateEditor(dateFormat, false));
	}

	// ...
}
```

---

---

---

---

### java:S6830 — Bean names should adhere to the naming conventions

**Severity**: Medium

Consistent naming of beans is important for the readability and maintainability of the code. More precisely, according to the Spring
documentation:

**Noncompliant code example**

```java
@Bean(name = "MyBean") // Noncompliant, the first letter of the name should be lowercase
public MyBean myBean() {
    ...
```

**Compliant solution**

```java
@Bean(name = "myBean") // Compliant
public MyBean myBean() {
    ...
```

---

---

---

---

### java:S6837 — Superfluous "@ResponseBody" annotations should be removed

**Severity**: Medium

The Spring framework’s 
`@RestController`
 annotation is equivalent to using the 
`@Controller`
 and 
`@ResponseBody`

annotations together. As such, it is redundant to add a 
`@ResponseBody`
 annotation when the class is already annotated with

`@RestController`
.

**Noncompliant code example**

```java
@RestController
public class MyController {
  @ResponseBody // Noncompliant, the @RestController annotation already implies @ResponseBody
  @RequestMapping("/hello")
  public String hello() {
    return "Hello World!";
  }
}
```

**Compliant solution**

```java
@RestController
public class MyController {
  @RequestMapping("/hello")
  public String hello() {
    return "Hello World!";
  }
}
```

---

---

---

---

### java:S6863 — Set appropriate Status Codes on HTTP responses

**Severity**: Medium

The request handler function in a 
`Controller`
 should set the appropriate HTTP status code based on the operation’s success or failure.
This is done by returning a 
`Response`
 object with the appropriate status code.

If an exception is thrown during the execution of the handler, the status code should be in the range of 4xx or 5xx. Examples of such codes are

`BAD_REQUEST`
, 
`UNAUTHORIZED`
, 
`FORBIDDEN`
, 
`NOT_FOUND`
, 
`INTERNAL_SERVER_ERROR`
,

`BAD_GATEWAY`
, 
`SERVICE_UNAVAILABLE`
, etc.

The status code should be 1xx, 2xx, or 3xx if no exception is thrown and the operation is considered successful. Such codes include

`OK`
, 
`CREATED`
, 
`MOVED_PERMANENTLY`
, 
`FOUND`
, etc.

**Noncompliant code example**

```java
@Controller
public class UserController {
    public ResponseEntity<User> getUserById(Long userId) {
        try {
            User user = userService.getUserById(userId);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(user); // Noncompliant: Setting 500 for a successful operation
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.OK).build(); // Noncompliant: Setting 200 for exception
        }
    }
}
```

**Compliant solution**

```java
@Controller
public class UserController {
    public ResponseEntity<User> getUserById(Long userId) {
        try {
            User user = userService.getUserById(userId);
            return ResponseEntity.ok(user); // Compliant: Setting 200 for a successful operation
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build(); // Compliant: Setting 500 for exception
        }
    }
}
```

---

---

---

---

### java:S6878 — Use record pattern instead of explicit field access

**Severity**: Medium

Java 21 enhances Pattern Matching, introduced in Java 16, with a 
record pattern
 that decomposes records into local variables. This form
should be used when all fields of a record are accessed within a block for improved readability. Nested record patterns are also allowed and should be
used when a record field is another record, and all its fields are accessed.

Exceptions

This rule does not apply when not all record fields are accessed. This prevents the creation of unused local variables in the decomposed record
structure.

**Noncompliant code example**

```java
record Point(Float x, Float y, Float z) {}

void print(Object obj) {
    if (obj instanceof Point p) { // Noncompliant, because all three fields x, y, z are accessed
        Float x = p.x;
        Float y = p.y();
        System.out.println(x + y + p.z);
    }
}
```

**Compliant solution**

```java
record Point(Float x, Float y, Float z) {}

void print(Object obj) {
    if (obj instanceof Point(Float x, Float y, Float z)) { // Compliant
        System.out.println(x + y + z);
    }
}
```

---

---

---

---

### java:S6909 — Constant parameters in a "PreparedStatement" should not be set more than once

**Severity**: Medium

The 
`PreparedStatement`
 is frequently used in loops because it allows to conveniently set parameters. A small optimization is possible
by setting constant parameters outside the loop or hard-coding them in the query whenever possible.

What is the potential impact?

 
Performance
: the unnecessary calls to the setter methods bring overhead. 

 
Sustainability
: the extra overhead has a negative impact on the environment.

**Noncompliant code example**

```java
public class DatabaseExample {

    public record Order(String id, BigDecimal price) {}

    public void updateTodayOrders(Connection connection, List<Order> orders) {
            Date today = java.sql.Date.valueOf(LocalDate.now());
            String insertQuery = "INSERT INTO Order (id, price, executionDate) VALUES (?, ?, ?)";
            PreparedStatement preparedStatement = connection.prepareStatement(insertQuery);

            for(Order order: orders) {
                preparedStatement.setString(1, order.id());
                preparedStatement.setString(2, order.price());
                preparedStatement.setDate(3, today); // Noncompliant
                preparedStatement.executeUpdate();
            }
    }
}
```

**Compliant solution**

```java
public class DatabaseExample {

    public record Order(String id, BigDecimal price) {}

    public void updateTodayOrders(Connection connection, List<Order> orders) {
            Date today = java.sql.Date.valueOf(LocalDate.now());
            String insertQuery = "INSERT INTO Order (id, price, executionDate) VALUES (?, ?, ?)";
            PreparedStatement preparedStatement = connection.prepareStatement(insertQuery);

            preparedStatement.setDate(3, today); // Compliant
            for(Order order: orders) {
                preparedStatement.setString(1, order.id());
                preparedStatement.setString(2, order.price());
                preparedStatement.executeUpdate();
            }
    }
}
```

---

---

---

---

### java:S6905 — SQL queries should retrieve only necessary fields

**Severity**: Medium

A common reason for a poorly performant query is because it’s processing more data than required.

Querying unnecessary data demands extra work on the server, adds network overhead, and consumes memory and CPU resources on the application server.
The effect is amplified when the query includes multiple 
joins
.

The rule flags an issue when a 
`SELECT *`
 query is provided as an argument to methods in 
`java.sql.Connection`
 and

`java.sql.Statement`
.

What is the potential impact?

 
Performance
: the unnecessary extra data being processed brings overhead. 

 
Sustainability
: the extra resources used have a negative impact on the environment.

**Noncompliant code example**

```java
public class OrderRepository {

    public record OrderSummary(String name, String orderId, BigDecimal price) { }

    public List<OrderSummary> queryOrderSummaries(Connection conn) {
            String sql = "SELECT * " +                                                         // Noncompliant
                          "FROM Orders JOIN Customers ON Orders.customerId = Customers.id ";

            Statement stmt = conn.createStatement();
            ResultSet rs = stmt.executeQuery(sql);

            return convertResultToOrderSummaryList(rs);
    }
}
```

**Compliant solution**

```java
public class OrderRepository {

    public record OrderSummary(String name, String orderId, BigDecimal price) { }

    public List<OrderSummary> queryOrderSummaries(Connection conn) {
            String sql = "SELECT Customers.name, Orders.id, Orders.price " +                   // Compliant
                          "FROM Orders JOIN Customers ON Orders.customerId = Customers.id ";

            Statement stmt = conn.createStatement();
            ResultSet rs = stmt.executeQuery(sql);

            return convertResultToOrderSummaryList(rs);
    }
}
```

---

---

---

---

### java:S6912 — Use batch Processing in JDBC

**Severity**: Medium

Executing a batch of SQL queries instead of individual queries improves performance by reducing communication overhead with the database.

Batching SQL statements is beneficial in common situations where a SQL statement is executed within a loop. In such cases, adding the statement to
a batch and subsequently executing it reduces the number of interactions with the database. This results in improved efficiency and faster execution
times.

The rule raises an issue when it detects a 
`java.sql.Statement`
 being executed within a loop instruction, such as 
`for`
,

`while`
 or the 
`forEach`
 method of 
`java.lang.Iterable`
, 
`java.util.Map`
 and

`java.util.stream.Stream`
.

**Noncompliant code example**

```java
public void execute(Connection connection) {
  try {
    Statement statement = connection.createStatement();

    for (int i = 0; i < 10; i++) {
      statement.execute("INSERT INTO myTable (column1, column2) VALUES (" + i + ", 'value" + i + "')"); // Noncompliant
    }

    statement.close();
    connection.close();
  } catch (SQLException e) {
    e.printStackTrace();
  }
}
```

**Compliant solution**

```java
public void execute(Connection connection) {
  try {
    Statement statement = connection.createStatement();

    for (int i = 0; i < 10; i++) {
      statement.addBatch("INSERT INTO myTable (column1, column2) VALUES (" + i + ", 'value" + i + "')"); // Compliant
    }
    statement.executeBatch();

    statement.close();
    connection.close();
  } catch (SQLException e) {
    e.printStackTrace();
  }
}
```

---

---

---

---

### java:S6485 — Hash-based collections with known capacity should be initialized with the proper related static method.

**Severity**: Medium

When creating an instance of HashMap or HashSet, the developer can pick a constructor with known capacity. However, the requested capacity is not
fully allocated by default. Indeed, when the collection reaches the load factor of the collection (default: 0.75), the collection is resized on the
fly, leading to unexpected performance issues.

**Noncompliant code example**

```java
private static final int KNOWN_CAPACITY = 1_000_000;

public static Map<String, Integer> buildAMap() {
    return new HashMap<>(KNOWN_CAPACITY); // Noncompliant
}

public static Set<String> buildASet() {
    return new HashSet<>(KNOWN_CAPACITY); // Noncompliant
}
```

**Compliant solution**

```java
private static final int KNOWN_CAPACITY = 1_000_000;

public static Map<String, Integer> buildABetterMap() {
    return HashMap.newHashMap(KNOWN_CAPACITY);
}

public static Set<String> buildABetterSet() {
    return HashSet.newHashSet(KNOWN_CAPACITY);
}

public static Set<String> buildABetterSet(float customLoadFactor) {
    return new HashSet<>(KNOWN_CAPACITY, customLoadFactor);
}
```

---

---

---

---

### java:S6889 — Proper Sensor Resource Management

**Severity**: Medium

Optimizing resource usage and preventing unnecessary battery drain are critical considerations in Android development. Failing to release sensor
resources when they are no longer needed can lead to prolonged device activity, negatively impacting battery life. Common Android sensors, such as
cameras, GPS, and microphones, provide a method to release resources after they are not in use anymore.

**Noncompliant code example**

```java
public void method() {
  PowerManager powerManager = (PowerManager) getSystemService(POWER_SERVICE);
  PowerManager.WakeLock wakeLock = powerManager.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, "My Wake Lock");
  wakeLock.acquire(); // Noncompliant
  // do some work...
}
```

**Compliant solution**

```java
public void method() {
  PowerManager powerManager = (PowerManager) getSystemService(POWER_SERVICE);
  PowerManager.WakeLock wakeLock = powerManager.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, "My Wake Lock");
  wakeLock.acquire(); // Compliant
  // do some work...
  wakeLock.release();
}
```

---

---

---

---

### java:S1751 — Loops with at most one iteration should be refactored

**Severity**: Medium

A loop with at most one iteration is equivalent to an 
`if`
 statement. This can confuse developers and make the code less readable since
loops are not meant to replace 
`if`
 statements.

If the intention was to conditionally execute the block only once, an 
`if`
 statement should be used instead. Otherwise, the loop should
be fixed so the loop block can be executed multiple times.

A loop statement with at most one iteration can happen when a statement that unconditionally transfers control, such as a jump or throw statement,
is misplaced inside the loop block.

This rule arises when the following statements are misplaced:

 
`break`
 

 
`return`
 

 
`throw`

**Noncompliant code example**

```java
int i = 0;
while(i < 10) { // Noncompliant; loop only executes once
  System.out.println("i is " + i);
  i++;
  break;
}
```

**Compliant solution**

```java
for (int i = 0; i < 10; i++) { // Noncompliant; loop only executes once
  if (i == x) {
    break;
  } else {
    System.out.println("i is " + i);
    return;
  }
}
```

---

---

---

---

### java:S3981 — Collection sizes and array length comparisons should make sense

**Severity**: Medium

The size of a collection and the length of an array are always greater than or equal to zero. Testing it doesn’t make sense, since the result is
always 
`true`
.

```

if (myList.size() >= 0) {...} // Noncompliant: always true

boolean result = myArray.length >= 0; // Noncompliant: true

```

Similarly testing that it is less than zero will always return 
`false`
.

```

if (myList.size() < 0) {...} // Noncompliant: always false

```

Fix the code to properly check for emptiness if it was the intent, or remove the redundant code to keep the current behavior.

---

---

---

---

### java:S6813 — Field dependency injection should be avoided

**Severity**: Medium

Dependency injection frameworks such as Spring, Quarkus, and others support dependency injection by using annotations such as 
`@Inject`

**Noncompliant code example**

```java
public class SomeService {
    @Autowired
    private SomeDependency someDependency; // Noncompliant

    private String name = someDependency.getName(); // Will throw a NullPointerException
}
```

**Compliant solution**

```java
public class SomeService {
    private final SomeDependency someDependency;
    private final String name;

    @Autowired
    public SomeService(SomeDependency someDependency) {
        this.someDependency = someDependency;
        name = someDependency.getName();
    }
}
```

---

---

---

---

### java:S2159 — Unnecessary equality checks should not be made

**Severity**: Medium

Comparisons of dissimilar types will always return false. The comparison and all its dependent code can simply be removed. This includes:

---

---

---

---

### java:S2154 — Dissimilar primitive wrappers should not be used with the ternary operator without explicit casting

**Severity**: Medium

Using boxed values in a ternary operator does not simply return one operand or the other based on the condition. Instead, the values are unboxed
and coerced to a common type, which can result in a loss of precision when converting one operand from 
`int`
 to 
`float`
 or from

`long`
 to 
`double`
.

While this behavior is expected for arithmetic operations, it may be unexpected for the ternary operator. To avoid confusion or unexpected
behavior, cast to a compatible type explicitly.

**Noncompliant code example**

```java
Integer i = 123456789;
Float f = 1.0f;
Number n1 = condition ? i : f;  // Noncompliant, unexpected precision loss, n1 = 1.23456792E8
```

**Compliant solution**

```java
Integer i = 123456789;
Float f = 1.0f;
Number n1 = condition ? (Number) i : f; // Compliant, cast to Number prevents unboxing
Number n2 = condition ? i : (Number) f; // Compliant, cast to Number prevents unboxing
```

---

---

---

---

### java:S2133 — Objects should not be created only to invoke "getClass"

**Severity**: Medium

Creating an object for the sole purpose of calling 
`getClass`
 on it is a waste of memory and cycles. Instead, simply use the class’s

`.class`
 property.

Noncompliant code example

```

MyObject myOb = new MyObject();  // Noncompliant
Class c = myOb.getClass();

```

Compliant solution

```

Class c = MyObject.class;

```

---

---

---

---

### java:S1656 — Variables should not be self-assigned

**Severity**: Medium

There is no reason to re-assign a variable to itself. Either this statement is redundant and should be removed, or the re-assignment is a mistake
and some other value or variable was intended for the assignment instead.

Noncompliant code example

```

public void setName(String name) {
  name = name;
}

```

Compliant solution

```

public void setName(String name) {
  this.name = name;
}

```

---

---

---

---

### java:S1871 — Two branches in a conditional structure should not have exactly the same implementation

**Severity**: Medium

When the same code is duplicated in two or more separate branches of a conditional, it can make the code harder to understand, maintain, and can
potentially introduce bugs if one instance of the code is changed but others are not.

---

---

---

---

### java:S1872 — Classes should not be compared by name

**Severity**: Medium

There is no requirement that class names be unique, only that they be unique within a package. Therefore trying to determine an object’s type based
on its class name is an exercise fraught with danger. One of those dangers is that a malicious user will send objects of the same name as the trusted
class and thereby gain trusted access.

---

---

---

---

### java:S1862 — Related "if/else if" statements should not have the same condition

**Severity**: Medium

A chain of 
`if`
/
`else if`
 statements is evaluated from top to bottom. At most, only one branch will be executed: the first
one with a condition that evaluates to 
`true`
.

Therefore, duplicating a condition automatically leads to dead code. Usually, this is due to a copy/paste error. At best, it’s simply dead code and
at worst, it’s a bug that is likely to induce further bugs as the code is maintained, and obviously it could lead to unexpected behavior.

Noncompliant code example

```

if (param == 1)
  openWindow();
else if (param == 2)
  closeWindow();
else if (param == 1)  // Noncompliant
  moveWindowToTheBackground();
}

```

Compliant solution

```

if (param == 1)
  openWindow();
else if (param == 2)
  closeWindow();
else if (param == 3)
  moveWindowToTheBackground();
}

```

---

---

---

---

### java:S2185 — Do not perform unnecessary mathematical operations

**Severity**: Medium

Some mathematical operations are unnecessary and should not be performed because their results are predictable.

**Noncompliant code example**

```java
public void doMath(int a) {
  double res1 = Math.floor((double)a); // Noncompliant, the result will always be equal to '(double) a'
  double res2 = Math.ceil(4.2);        // Noncompliant, the result will always be 5.0
  double res3 = Math.atan(0.0);        // Noncompliant, the result will always be 0.0
}
```

**Compliant solution**

```java
public void doMath(int a) {
  double res1 = a;    // Compliant
  double res2 = 5.0;  // Compliant
  double res3 = 0.0;  // Compliant
}
```

---

---

---

---

### javabugs:S6417 — Collections should not be modified while they are iterated

**Severity**: Medium

Iterating over a collection using a 
`for-each`
 loop in Java relies on iterators.

---

---

---

---

### java:S2225 — "toString()" and "clone()" methods should not return null

**Severity**: Medium

Calling 
`toString()`
 or 
`clone()`
 on an object should always return a string or an object. Returning 
`null`

instead contravenes the method’s implicit contract.

Noncompliant code example

```

public String toString () {
  if (this.collection.isEmpty()) {
    return null; // Noncompliant
  } else {
    // ...

```

Compliant solution

```

public String toString () {
  if (this.collection.isEmpty()) {
    return "";
  } else {
    // ...

```

---

---

---

---

### java:S2589 — Boolean expressions should not be gratuitous

**Severity**: Medium

Control flow constructs like 
`if`
-statements allow the programmer to direct the flow of a program depending on a boolean expression.
However, if the condition is always true or always false, only one of the branches will ever be executed. In that case, the control flow construct and
the condition no longer serve a purpose; they become 
gratuitous
.

**Noncompliant code example**

```java
public class MyClass {
    public void doThings(boolean b, boolean c) {
        a = true;
        if (a) {                // Noncompliant
          doSomething();
        }

        if (b && a) {           // Noncompliant; "a" is always "true"
          doSomething();
        }

        if (c || !a) {          // Noncompliant; "!a" is always "false"
          doSomething();
        }

        if (c || (!c && b)) {   // Noncompliant; c || (!c && b) is equal to c || b
          doSomething();
        }
    }
}
```

**Compliant solution**

```java
public class MyClass {
    public void doThings(boolean b, boolean c) {
        a = true;
        if (foo(a)) {
          doSomething();
        }

        if (b) {
          doSomething();
        }

        if (c) {
          doSomething();
        }

        if (c || b) {
          doSomething();
        }
    }
}
```

---

---

---

---

### java:S3436 — Value-based classes should not be used for locking

**Severity**: Medium

According to the documentation,

---

---

---

---

### java:S5854 — Regexes containing characters subject to normalization should use the CANON_EQ flag

**Severity**: Medium

Characters like 
`'é'`
 can be expressed either as a single code point or as a cluster of the letter 
`'e'`
 and a combining
accent mark. Without the 
`CANON_EQ`
 flag, a regex will only match a string in which the characters are expressed in the same way.

Noncompliant code example

```

String s = "e\u0300";
Pattern p = Pattern.compile("é|ë|è"); // Noncompliant
System.out.println(p.matcher(s).replaceAll("e")); // print 'è'

```

Compliant solution

```

String s = "e\u0300";
Pattern p = Pattern.compile("é|ë|è", Pattern.CANON_EQ);
System.out.println(p.matcher(s).replaceAll("e")); // print 'e'

```

---

---

---

---

### java:S1134 — Track uses of "FIXME" tags

**Severity**: Medium

`FIXME`
 tags are commonly used to mark places where a bug is suspected, but which the developer wants to deal with later.

Sometimes the developer will not have the time or will simply forget to get back to that tag.

This rule is meant to track those tags and to ensure that they do not go unnoticed.

```

int divide(int numerator, int denominator) {
  return numerator / denominator;              // FIXME denominator value might be  0
}

```

---

---

---

---

### java:S5855 — Regex alternatives should not be redundant

**Severity**: Medium

If an alternative in a regular expression only matches things that are already matched by another alternative, that alternative is redundant and
serves no purpose.

In the best case this means that the offending subpattern is merely redundant and should be removed. In the worst case it’s a sign that this regex
does not match what it was intended to match and should be reworked.

Noncompliant code example

```

"[ab]|a"   // Noncompliant: the "|a" is redundant because "[ab]" already matches "a"
".*|a"     // Noncompliant: .* matches everything, so any other alternative is redundant

```

Compliant solution

```

"[ab]"
".*"

```

---

---

---

---

### java:S5976 — Similar tests should be grouped in a single Parameterized test

**Severity**: Medium

When multiple tests differ only by a few hardcoded values they should be refactored as a single "parameterized" test. This reduces the chances of
adding a bug and makes them more readable. Parameterized tests exist in most test frameworks (JUnit, TestNG, etc…​).

---

---

---

---

### java:S5850 — Alternatives in regular expressions should be grouped when used with anchors

**Severity**: Medium

In regular expressions, anchors (
`^`
, 
`$`
, 
`\A`
, 
`\Z`
 and 
`\z`
) have higher precedence than
the 
`|`
 operator. So in a regular expression like 
`^alt1|alt2|alt3$`
, 
`alt1`
 would be anchored to the beginning,

---

---

---

---

### java:S2109 — Reflection should not be used to check non-runtime annotations

**Severity**: Medium

Denoted by the "@" symbol, annotations are metadata that can be added to classes, methods, and variables for various purposes such as
documentation, code analysis, and runtime processing.

---

---

---

---

### java:S2583 — Conditionally executed code should be reachable

**Severity**: Medium

Conditional expressions which are always 
`true`
 or 
`false`
 can lead to 
[unreachable code](https://en.wikipedia.org/wiki/Unreachable_code)
.

Noncompliant code example

```

a = false;
if (a) { // Noncompliant
  doSomething(); // never executed
}

if (!a || b) { // Noncompliant; "!a" is always "true", "b" is never evaluated
  doSomething();
} else {
  doSomethingElse(); // never executed
}

```

Exceptions

This rule will not raise an issue in either of these cases:

 When the condition is a single 
`final boolean`
 

```

final boolean debug = false;
//...
if (debug) {
  // Print something
}

```

 When the condition is literally 
`true`
 or 
`false`
. 

```

if (true) {
  // do something
}

```

In these cases it is obvious the code is as intended.

---

---

---

---

### java:S3551 — Overrides should match their parent class methods in synchronization

**Severity**: Medium

When 
`@Overrides`
 of 
`synchronized`
 methods are not themselves 
`synchronized`
, the result can be improper
synchronization as callers rely on the thread-safety promised by the parent class.

Noncompliant code example

```

public class Parent {

  synchronized void foo() {
    //...
  }
}

public class Child extends Parent {

 @Override
  public void foo () {  // Noncompliant
    // ...
    super.foo();
  }
}

```

Compliant solution

```

public class Parent {

  synchronized void foo() {
    //...
  }
}

public class Child extends Parent {

  @Override
  synchronized void foo () {
    // ...
    super.foo();
  }
}

```

---

---

---

---

### java:S5973 — Tests should be stable

**Severity**: Medium

Unstable / flaky tests are tests which sometimes pass and sometimes fail, without any code change. Obviously, they slow down developments when
developers have to rerun failed tests. However, the real problem is that you can’t completely trust these tests, they might fail for many different
reasons and you don’t know if any of them will happen in production.

---

---

---

---

### java:S2116 — "hashCode" and "toString" should not be called on array instances

**Severity**: Medium

The purpose of the 
`hashCode`
 method is to return a hash code based on the contents of the object. Similarly, the purpose of the

`toString`
 method is to provide a textual representation of the object’s contents.

Calling 
`hashCode()`
 and 
`toString()`
 directly on array instances should be avoided because the default implementations
provided by the 
`Object`
 class do not provide meaningful results for arrays. 
`hashCode()`
 returns the array’s "identity hash
code", and 
`toString()`
 returns nearly the same value. Neither method’s output reflects the array’s contents.

**Noncompliant code example**

```java
public static void main(String[] args) {
    String argStr = args.toString();       // Noncompliant
    int argHash = args.hashCode();         // Noncompliant
}
```

**Compliant solution**

```java
public static void main(String[] args) {
    String argStr = Arrays.toString(args); // Compliant
    int argHash = Arrays.hashCode(args);   // Compliant
}
```

---

---

---

---

### java:S5738 — "@Deprecated" code marked for removal should never be used

**Severity**: Medium

With the introduction of Java 9, the standard annotation class 
`java.lang.Deprecated`
 has been updated with new parameters. Notably, a
boolean parameter 
`forRemoval`
 has been added to clearly signify whether the deprecated code is intended to be removed in the future. This
is indicated with 
`forRemoval=true`
. The javadoc of the annotation explicitly mentions the following:

**Noncompliant code example**

```java
/**
 * @deprecated As of release 1.3, replaced by {@link #Fee}. Will be dropped with release 1.4.
 */
@Deprecated(forRemoval=true)
public class Foo { ... }

public class Bar {
  /**
   * @deprecated  As of release 1.7, replaced by {@link #doTheThingBetter()}
   */
  @Deprecated(forRemoval=true)
  public void doTheThing() { ... }

  public void doTheThingBetter() { ... }

  /**
   * @deprecated As of release 1.14 due to poor performances.
   */
  @Deprecated(forRemoval=false)
  public void doTheOtherThing() { ... }
}

public class Qix extends Bar {
  @Override
  public void doTheThing() { ... } // Noncompliant; don't override a deprecated method marked for removal
}

public class Bar extends Foo {  // Noncompliant; Foo is deprecated and will be removed

  public void myMethod() {
// ...
```

---

---

---

---

### java:S6832 — Non-singleton Spring beans should not be injected into singleton beans

**Severity**: Medium

In Spring, singleton beans and their dependencies are initialized when the application context is created.

**Noncompliant code example**

```java
@Component
@Scope(value = WebApplicationContext.SCOPE_REQUEST, proxyMode = ScopedProxyMode.TARGET_CLASS)
public class RequestBean {
    //...
}

public class SingletonBean {
    @Autowired
    private final RequestBean requestBean; // Noncompliant, the same instance of RequestBean is used for each HTTP request.

    public RequestBean getRequestBean() {
        return requestBean;
    }
}
```

**Compliant solution**

```java
@Component
@Scope(value = WebApplicationContext.SCOPE_REQUEST, proxyMode = ScopedProxyMode.TARGET_CLASS)
public class RequestBean {
    //...
}

public class SingletonBean {
    private final ObjectFactory<RequestBean> requestBeanFactory;

    @Autowired
    public SingletonBean(ObjectFactory<RequestBean> requestBeanFactory) {
        this.requestBeanFactory = requestBeanFactory;
    }

    public RequestBean getRequestBean() {
        return requestBeanFactory.getObject();
    }
}
```

---

---

---

---

### java:S6833 — "@Controller" should be replaced with "@RestController"

**Severity**: Medium

Classes annotated as 
`@Controller`
 in Spring are responsible for handling incoming web requests. When annotating methods or the entire
controller with 
`@ResponseBody`
, the return value of said methods will be serialized and set as the response body. In other words, it tells
the Spring framework that this method does not produce a view. This mechanism is commonly used to create API endpoints.

**Noncompliant code example**

```java
@Controller
@ResponseBody
public class MyController {
    @GetMapping("/hello")
    public String hello() {
        return "Hello World!";
    }
}
```

**Compliant solution**

```java
@RestController
public class MyController {
    @GetMapping("/hello")
    public String hello() {
        return "Hello World!";
    }
}
```

---

---

---

---

### java:S2234 — Parameters should be passed in the correct order

**Severity**: Medium

When the names of parameters in a method call match the names of the method arguments, it contributes to clearer, more readable code. However, when
the names match, but are passed in a different order than the method arguments, it indicates a mistake in the parameter order which will likely lead
to unexpected results.

---

---

---

---

### java:S2111 — "BigDecimal(double)" should not be used

**Severity**: Medium

The 
`BigDecimal`
 is used to represents immutable, arbitrary-precision signed decimal numbers.

Differently from the 
`BigDecimal`
, the 
`double`
 primitive type and the 
`Double`
 type have limited precision due to
the use of double-precision 64-bit IEEE 754 floating point. Because of floating point imprecision, the 
`BigDecimal(double)`
 constructor can
be somewhat unpredictable.

For example writing 
`new BigDecimal(0.1)`
 doesn’t create a BigDecimal which is exactly equal to 0.1, but it is equal to
0.1000000000000000055511151231257827021181583404541015625. This is because 0.1 cannot be represented exactly as a double (or, for that matter, as a
binary fraction of any finite length).

**Noncompliant code example**

```java
double d = 1.1;

BigDecimal bd1 = new BigDecimal(d);   // Noncompliant
BigDecimal bd2 = new BigDecimal(1.1); // Noncompliant
```

**Compliant solution**

```java
double d = 1.1;

BigDecimal bd1 = BigDecimal.valueOf(d); // Compliant
BigDecimal bd2 = new BigDecimal("1.1"); // Compliant
```

---

---

---

---

### java:S2112 — "URL.hashCode" and "URL.equals" should be avoided

**Severity**: Medium

The 
`equals`
 and 
`hashCode`
 methods of 
`java.net.URL`
 may trigger a name service lookup (typically DNS) to resolve
the hostname or IP address. Depending on the configuration, and network status, this lookup can be time-consuming.

**Noncompliant code example**

```java
public void checkUrl(URL url) {
  Set<URL> sites = new HashSet<URL>();               // Noncompliant

  URL homepage = new URL("http://sonarsource.com");  // Compliant
  if (homepage.equals(url)) {                        // Noncompliant
    // ...
  }
}
```

**Compliant solution**

```java
public void checkUrl(URL url) {
  Set<URI> sites = new HashSet<URI>();               // Compliant

  URI homepage = new URI("http://sonarsource.com");  // Compliant
  URI uri = url.toURI();
  if (homepage.equals(uri)) {                        // Compliant
    // ...
  }
}
```

---

---

---

---

### java:S2114 — Collections should not be passed as arguments to their own methods

**Severity**: Medium

Passing a collection as an argument to the collection’s own method is either an error - some other argument was intended - or simply nonsensical
code.

Further, because some methods require that the argument remain unmodified during the execution, passing a collection to itself can result in
undefined behavior.

Noncompliant code example

```

List <Object> objs = new ArrayList<Object>();
objs.add("Hello");

objs.add(objs); // Noncompliant; StackOverflowException if objs.hashCode() called
objs.addAll(objs); // Noncompliant; behavior undefined
objs.containsAll(objs); // Noncompliant; always true
objs.removeAll(objs); // Noncompliant; confusing. Use clear() instead
objs.retainAll(objs); // Noncompliant; NOOP

```

---

---

---

---

### java:S2232 — "ResultSet.isLast()" should not be used

**Severity**: Medium

There are several reasons to avoid using this method:

 It is optionally available only for result sets of type 
`ResultSet.TYPE_FORWARD_ONLY`
. Database drivers will throw an exception if
  not supported. 

 The method can be expensive to execute as the database driver may need to fetch ahead one row to determine whether the current row is the last
  in the result set. The documentation of the method explicitly mentions this fact. 

 What "the cursor is on the last row" means for an empty 
`ResultSet`
 is unclear. Database drivers may return 
`true`
 or
  
`false`
 in this case . 

`ResultSet.next()`
 is a good alternative to 
`ResultSet.isLast()`
 as it does not have the mentioned issues. It is always
supported and, as per specification, returns 
`false`
 for empty result sets.

**Noncompliant code example**

```java
ResultSet results = stmt.executeQuery("SELECT name, address FROM PERSON");
StringBuilder sb = new StringBuilder();
while (results.next() && !results.isLast()) { // Noncompliant
  sb.append(results.getString("name") + ", ");
}
sb.append(results.getString("name"));
String formattedNames = sb.toString();
```

**Compliant solution**

```java
ResultSet results = stmt.executeQuery("SELECT name, address FROM PERSON");
List<String> names = new ArrayList<>();
while (results.next()) { // Compliant, and program logic refactored
  names.add(results.getString("name"));
}
String formattedNames =  names.stream().collect(Collectors.joining(", "));
```

---

---

---

---

### java:S5860 — Names of regular expressions named groups should be used

**Severity**: Medium

Why use named groups only to never use any of them later on in the code?

---

---

---

---

### java:S5866 — Case insensitive Unicode regular expressions should enable the "UNICODE_CASE" flag

**Severity**: Medium

By default case insensitivity only affects letters in the ASCII range. This can be changed by either passing 
`Pattern.UNICODE_CASE`
 or

---

---

---

---

### java:S1141 — Try-catch blocks should not be nested

**Severity**: Medium

Nesting 
`try`
/
`catch`
 blocks severely impacts the readability of source code because it makes it too difficult to understand
which block will catch which exception.

---

---

---

---

### java:S1149 — Synchronized classes "Vector", "Hashtable", "Stack" and "StringBuffer" should not be used

**Severity**: Medium

Early classes of the Java API, such as 
`Vector`
, 
`Hashtable`
 and 
`StringBuffer`
, were synchronized to make them
thread-safe. However, synchronization has a significant negative impact on performance, even when using these collections from a single thread.

---

---

---

---

### java:S2110 — Invalid "Date" values should not be used

**Severity**: Medium

Whether the valid value ranges for 
`Date`
 fields start with 0 or 1 varies by field. For instance, month starts at 0, and day of month
starts at 1. Enter a date value that goes past the end of the valid range, and the date will roll without error or exception. For instance, enter 12
for month, and you’ll get January of the following year.

---

---

---

---

### java:S2118 — "writeObject" argument must implement "Serializable"

**Severity**: Medium

Serialization is a platform-independent mechanism for writing the state of an object into a byte-stream. For serializing the object, we call the

`writeObject()`
 method of 
`java.io.ObjectOutputStream`
 class. Only classes that implement 
`Serializable`
 or extend a
class that does it can successfully be serialized (or de-serialized).

Attempting to write a class with the 
`writeObject`
 method of the 
`ObjectOutputStream`
 class that does not implement

`Serializable`
 or extends a class that implements it, will throw an 
`IOException`
.

**Noncompliant code example**

```java
public class Vegetable {
  // ...
}

public class Menu {
  public void meal(ObjectOutputStream oos) throws IOException {
    Vegetable veg = new Vegetable();
    oos.writeObject(veg);  // Noncompliant
  }
}
```

**Compliant solution**

```java
public class Vegetable implements Serializable {
  // ...
}

public class Menu {
  public void meal(ObjectOutputStream oos) throws IOException {
    Vegetable veg = new Vegetable();
    oos.writeObject(veg);
  }
}
```

---

---

---

---

### java:S2445 — Blocks should be synchronized on "private final" fields

**Severity**: Medium

Synchronizing on a class field synchronizes not on the field itself, but on the object assigned to it. So synchronizing on a non-
`final`

---

---

---

---

### java:S3655 — Optional value should only be accessed after calling isPresent()

**Severity**: Medium

`Optional`
 value can hold either a value or not. The value held in the 
`Optional`
 can be accessed using the

---

---

---

---

### java:S5863 — Assertions should not compare an object to itself

**Severity**: Medium

Assertions comparing an object to itself are more likely to be bugs due to developer’s carelessness.

---

---

---

---

### java:S5868 — Unicode Grapheme Clusters should be avoided inside regex character classes

**Severity**: Medium

When placing Unicode 
[Grapheme Clusters](https://unicode.org/glossary/#grapheme_cluster)
 (characters which require to be encoded in
multiple 
[Code Points](https://unicode.org/glossary/#code_point)
) inside a character class of a regular expression, this will likely lead
to unintended behavior.

---

---

---

---

### java:S5869 — Character classes in regular expressions should not contain the same character twice

**Severity**: Medium

Character classes in regular expressions are a convenient way to match one of several possible characters by listing the allowed characters or
ranges of characters. If the same character is listed twice in the same character class or if the character class contains overlapping ranges, this
has no effect.

---

---

---

---

### java:S6831 — "@Qualifier" should not be used on "@Bean" methods

**Severity**: Medium

In Spring Framework, the 
`@Qualifier`
 annotation is typically used to disambiguate between multiple beans of the same type when
auto-wiring dependencies. It is not necessary to use 
`@Qualifier`
 when defining a bean using the 
`@Bean`
 annotation because the
bean’s name can be explicitly specified using the 
`name`
 attribute or derived from the method name. Using 
`@Qualifier`
 on

---

---

---

---

### java:S2204 — ".equals()" should not be used to test the values of "Atomic" classes

**Severity**: Medium

The 
`equals`
 method in 
`AtomicInteger`
 and 
`AtomicLong`
 returns 
`true`
 only if two instances are
identical, not if they represent the same number value.

This is because 
`equals`
 is not part of the API contract of these classes, and they do not override the method inherited from

`java.lang.Object`
. Although both classes implement the 
`Number`
 interface, assertions about 
`equals`
 comparing
number values are not part of that interface either. Only the API contract of implementing classes like 
`Integer`
, 
`Long`
,

`Float`
, 
`BigInteger`
, etc., provides such assertions.

**Noncompliant code example**

```java
Boolean isSameNumberValue(AtomicLong a, AtomicLong b) {
  return a.equals(b); // Noncompliant, this is true only if a == b
}

Boolean isSameReference(AtomicLong a, AtomicLong b) {
  return a.equals(b); // Noncompliant, because misleading
}
```

**Compliant solution**

```java
Boolean isSameNumberValue(AtomicLong a, AtomicLong b) {
  return a.get() == b.get(); // Compliant
}

Boolean isSameReference(AtomicLong a, AtomicLong b) {
  return a == b; // Compliant
}
```

---

---

---

---

### java:S2446 — "notifyAll()" should be preferred over "notify()"

**Severity**: Medium

`notify`
 and 
`notifyAll`
 both wake up sleeping threads waiting on the object’s monitor, but 
`notify`
 only wakes up
one single thread, while 
`notifyAll`
 wakes them all up. Unless you do not care which specific thread is woken up, 
`notifyAll`

should be used instead.

Noncompliant code example

```

class MyThread implements Runnable {
  Object lock = new Object();

  @Override
  public void run() {
    synchronized(lock) {
      // ...
      lock.notify();  // Noncompliant
    }
  }
}

```

Compliant solution

```

class MyThread implements Runnable {
  Object lock = new Object();

  @Override
  public void run() {
    synchronized(lock) {
      // ...
      lock.notifyAll();
    }
  }
}

```

---

---

---

---

### java:S1110 — Redundant pairs of parentheses should be removed

**Severity**: Medium

Parentheses can disambiguate the order of operations in complex expressions and make the code easier to understand.

```

a = (b * c) + (d * e); // Compliant: the intent is clear.

```

Redundant parentheses are parenthesis that do not change the behavior of the code, and do not clarify the intent. They can mislead and complexify
the code. They should be removed.

Noncompliant code example

```

int x = ((y / 2 + 1)); // Noncompliant

if (a && ((x + y > 0))) { // Noncompliant
  return ((x + 1)); // Noncompliant
}

```

Compliant solution

```

int x = (y / 2 + 1);

if (a && (x + y > 0)) {
  return (x + 1);
}

```

---

---

---

---

### java:S1111 — The "Object.finalize()" method should not be called

**Severity**: Medium

Before it reclaims storage from an object that is no longer referenced, the garbage collector calls 
`finalize()`
 on the object.

---

---

---

---

### java:S2201 — Return values from functions without side effects should not be ignored

**Severity**: Medium

When the call to a function doesn’t have any side effects, what is the point of making the call if the results are ignored? In such case, either
the function call is useless and should be dropped or the source code doesn’t behave as expected.

---

---

---

---

### java:S2440 — Classes with only "static" methods should not be instantiated

**Severity**: Medium

`static`
 methods can be accessed without an instance of the enclosing class, so there’s no reason to instantiate a class that has only

---

---

---

---

### java:S2441 — Non-serializable objects should not be stored in "javax.servlet.http.HttpSession" instances

**Severity**: Medium

`HttpSession`
 s are managed by web servers and can be serialized and stored on disk as the server manages its memory use in a process
called "passivation" (and later restored during "activation").

Even though 
`HttpSession`
 does not extend 
`Serializable`
, you must nonetheless assume that it will be serialized. If
non-serializable objects are stored in the session, serialization might fail.

Noncompliant code example

```

public class Address {
  //...
}

HttpSession session = request.getSession();
session.setAttribute("address", new Address());  // Noncompliant; Address isn't serializable

```

Compliant solution

```

public class Address implements Serializable {
  //...
}

HttpSession session = request.getSession();
session.setAttribute("address", new Address());

```

---

---

---

---

### java:S2442 — Synchronizing on a "Lock" object should be avoided

**Severity**: Medium

`java.util.concurrent.locks.Lock`
 offers far more powerful and flexible locking operations than are available with

`synchronized`
 blocks. So synchronizing on a 
`Lock`
 instance throws away the power of the object, as it overrides its better
locking mechanisms. Instead, such objects should be locked and unlocked using one of their 
`lock`
 and 
`unlock`
 method
variants.

Noncompliant code example

```

Lock lock = new MyLockImpl();
synchronized(lock) {  // Noncompliant
  // ...
}

```

Compliant solution

```

Lock lock = new MyLockImpl();
if (lock.tryLock()) {
  try {
    // ...
  } finally {
    lock.unlock();
  }
}

```

---

---

---

---

### java:S2681 — Multiline blocks should be enclosed in curly braces

**Severity**: Medium

Having inconsistent indentation and omitting curly braces from a control structure, such as an 
`if`
 statement or 
`for`
 loop,
is misleading and can induce bugs.

---

---

---

---

### java:S5831 — AssertJ configuration should be applied

**Severity**: Medium

A 
`org.assertj.core.configuration.Configuration`
 will be effective only once you call 
`Configuration.apply()`
 or

`Configuration.applyAndDisplay()`
.

This rule raises an issue when configurations are set without the appropriate call to apply them.

Noncompliant code example

```

Configuration configuration = new Configuration(); // Noncompliant, this configuration will not be applied.
configuration.setComparingPrivateFields(true);

```

Compliant solution

```

Configuration configuration = new Configuration();
configuration.setComparingPrivateFields(true);
configuration.applyAndDisplay();
// Alternatively: configuration.apply();

```

---

---

---

---

### java:S5833 — AssertJ methods setting the assertion context should come before an assertion

**Severity**: Medium

Describing, setting error message or adding a comparator in 
[AssertJ](https://assertj.github.io/doc/)
 must be done before calling the
assertion, otherwise, settings will not be taken into account.

---

---

---

---

### java:S1118 — Utility classes should not have public constructors

**Severity**: Medium

Whenever there are portions of code that are duplicated and do not depend on the state of their container class, they can be centralized inside a
"utility class". A utility class is a class that only has static members, hence it should not be instantiated.

Exceptions

When a class contains 
`public static void main(String[] args)`
 method it is not considered as a utility class and will be ignored by
this rule.

**Noncompliant code example**

```java
class StringUtils { // Noncompliant

  public static String concatenate(String s1, String s2) {
    return s1 + s2;
  }

}
```

**Compliant solution**

```java
class StringUtils { // Compliant

  private StringUtils() {
    throw new IllegalStateException("Utility class");
  }

  public static String concatenate(String s1, String s2) {
    return s1 + s2;
  }

}
```

---

---

---

---

### java:S1119 — Labels should not be used

**Severity**: Medium

Labels are not commonly used in Java, and many developers do not understand how they work. Moreover, their usage makes the control flow harder to
follow, which reduces the code’s readability.

---

---

---

---

### java:S2209 — "static" members should be accessed statically

**Severity**: Medium

While it is 
possible
 to access 
`static`
 members from a class instance, it’s bad form, and considered by most to be misleading
because it implies to the readers of your code that there’s an instance of the member per class instance.

---

---

---

---

### java:S6804 — "@Value" annotation should inject property or SpEL expression

**Severity**: Medium

The purpose of the 
`@Value`
 annotation in 
`org.springframework.beans.factory.annotation`
 is to inject a value into a field or
method based on the Spring context after it has been established.

**Noncompliant code example**

```java
@Value("catalog.name") // Noncompliant, this will not inject the property
String catalog;
```

**Compliant solution**

```java
@Value("${catalog.name}") // Compliant
String catalog;
```

---

---

---

---

### java:S1117 — Local variables should not shadow class fields

**Severity**: Medium

Shadowing occurs when a local variable has the same name as a variable or a field in an outer scope.

---

---

---

---

### java:S2326 — Unused type parameters should be removed

**Severity**: Medium

Type parameters that aren’t used are dead code, which can only distract and possibly confuse developers during maintenance. Therefore, unused type
parameters should be removed.

Noncompliant code example

```

int <T> Add(int a, int b) // Noncompliant; <T> is ignored
{
  return a + b;
}

```

Compliant solution

```

int Add(int a, int b)
{
  return a + b;
}

```

---

---

---

---

### java:S3415 — Assertion arguments should be passed in the correct order

**Severity**: Medium

The standard assertions library methods such as 
`org.junit.Assert.assertEquals`
, and 
`org.junit.Assert.assertSame`
 expect the
first argument to be the expected value and the second argument to be the actual value. For AssertJ instead, the argument of

`org.assertj.core.api.Assertions.assertThat`
 is the actual value, and the subsequent calls contain the expected values.

What is the potential impact?

Having the expected value and the actual value in the wrong order will not alter the outcome of tests, (succeed/fail when it should) but the error
messages will contain misleading information.

This rule raises an issue when the actual argument to an assertions library method is a hard-coded value and the expected argument is not.

**Noncompliant code example**

```java
org.junit.Assert.assertEquals(runner.exitCode(), 0, "Unexpected exit code");  // Noncompliant; Yields error message like: Expected:<-1>. Actual:<0>.
org.assertj.core.api.Assertions.assertThat(0).isEqualTo(runner.exitCode()); // Noncompliant
```

**Compliant solution**

```java
org.junit.Assert.assertEquals(0, runner.exitCode(), "Unexpected exit code");
org.assertj.core.api.Assertions.assertThat(runner.exitCode()).isEqualTo(0);
```

---

---

---

---

### java:S1479 — "switch" statements should not have too many "case" clauses

**Severity**: Medium

When 
`switch`
 statements have large sets of 
`case`
 clauses, it is usually an attempt to map two sets of data. A real map
structure would be more readable and maintainable, and should be used instead.

Exceptions

This rule ignores 
`switch`
es over 
`Enum`
s and empty, fall-through cases.

---

---

---

---

### java:S5843 — Regular expressions should not be too complicated

**Severity**: Medium

Overly complicated regular expressions are hard to read and to maintain and can easily cause hard-to-find bugs. If a regex is too complicated, you
should consider replacing it or parts of it with regular code or splitting it apart into multiple patterns at least.

---

---

---

---

### java:S5958 — AssertJ "assertThatThrownBy" should not be used alone

**Severity**: Medium

Unlike similar AssertJ methods testing exceptions (
`assertThatCode()`
, 
`assertThatExceptionOfType()`
, …​), the

---

---

---

---

### java:S6806 — Model attributes should follow the Java identifier naming convention

**Severity**: Medium

Spring Expression Language (SpEL) is an expression language used in the Spring Framework for evaluating and manipulating objects, properties, and
conditions within Spring-based applications.

**Noncompliant code example**

```java
model.addAttribute(" a", 100); // Noncompliant (starts with a space)
model.addAttribute("a-b", 7);  // Noncompliant (contains a hyphen)
model.addAttribute("1c", 42);  // Noncompliant (starts with a digit)
```

**Compliant solution**

```java
model.addAttribute("a", 100);
model.addAttribute("b", 42);
model.addAttribute("_c", 7);
model.addAttribute("$d", 8);
```

---

---

---

---

### java:S6810 — Async methods should return void or Future

**Severity**: Medium

The Spring framework provides the annotation 
`Async`
 to mark a method (or all methods of a type) as a candidate for asynchronous
execution.

Asynchronous methods do not necessarily, by their nature, return the result of their calculation immediately. Hence, it is unexpected and in clear
breach of the 
`Async`
 contract for such methods to have a return type that is neither 
`void`
 nor a 
`Future`
 type.

**Noncompliant code example**

```java
@Async
public String asyncMethod() {
  ...
}
```

**Compliant solution**

```java
@Async
public Future<String> asyncMethod() {
  ...
}
```

---

---

---

---

### java:S1123 — Deprecated elements should have both the annotation and the Javadoc tag

**Severity**: Medium

Deprecation should be marked with both the 
`@Deprecated`
 annotation and @deprecated Javadoc tag. The annotation enables tools such as
IDEs to warn about referencing deprecated elements, and the tag can be used to explain when it was deprecated, why, and how references should be
refactored.

---

---

---

---

### java:S5960 — Assertions should not be used in production code

**Severity**: Medium

Assertions are intended to be used in 
test
 code, but not in 
production
 code. It is confusing, and might lead to

`ClassNotFoundException`
 when the build tools only provide the required dependency in test scope.

In addition, assertions will throw a sub-class of 
`Error`
: 
`AssertionError`
, which should be avoided in production code.

This rule raises an issue when any assertion intended to be used in test is used in production code.

Supported frameworks:

 JUnit 

 FestAssert 

 AssertJ 

Note: this does not apply for 
`assert`
 from Java itself or if the source code package name is related to tests (contains:

`test`
 or 
`assert`
 or 
`junit`
).

---

---

---

---

### java:S1121 — Assignments should not be made from within sub-expressions

**Severity**: Medium

A common code smell that can hinder the clarity of source code is making assignments within sub-expressions. This practice involves assigning a
value to a variable inside a larger expression, such as within a loop or a conditional statement.

**Noncompliant code example**

```java
String str;
if (!(str = cont.substring(pos1, pos2)).isEmpty()) {  // Noncompliant
  // do something with "str"
}
```

**Compliant solution**

```java
String str = cont.substring(pos1, pos2);
if (!str.isEmpty()) {
  // do something with "str"
}
```

---

---

---

---

### java:S5961 — Test methods should not contain too many assertions

**Severity**: Medium

A common good practice is to write test methods targeting only one logical concept, that can only fail for one reason.

While it might make sense to have more than one assertion to test one concept, having too many is a sign that a test became too complex and should
be refactored to multiples ones.

This rule will report any test method containing more than a given number of assertion.

Noncompliant code example

With a parameter of 2.

```

@Test
void test() { // Refactor this method.
  assertEquals(1, f(1));
  assertEquals(2, f(2));
  assertEquals(3, g(1));
}

```

Compliant solution

```

void test_f() {
  assertEquals(1, f(1));
  assertEquals(2, f(2));
}
void test_g() {
  assertEquals(3, g(1));
}

```

---

---

---

---

### java:S5967 — Tests method should not be annotated with competing annotations

**Severity**: Medium

Annotating unit tests with more than one test-related annotation is not only useless but could also result in unexpected behavior like failing
tests or unwanted side-effects.

---

---

---

---

### java:S2388 — Inner class calls to super class methods should be unambiguous

**Severity**: Medium

An inner class that extends another type can call methods from both the outer class and parent type directly, without prepending

`super.`
 or 
`Outer.this.`
.

When both the outer and parent classes contain a method with the same name, the compiler will resolve an unqualified call to the parent type’s
implementation. The maintainer or a future reader may confuse the method call as calling the outer class’s implementation, even though it really calls
the super type’s.

To make matters worse, the maintainer sees the outer class’s implementation in the same file as the call in the inner class, while the parent type
is often declared in another file. The maintainer may not even be aware of the ambiguity present, as they do not see the parent’s implementation.

**Noncompliant code example**

```java
public class Parent {
  public void foo() { ... }
}

public class Outer {
  public void foo() { ... }

  public class Inner extends Parent {
    public void doSomething() {
      foo();  // Noncompliant, it is not explicit if Outer#foo or Parent#foo is the intended implementation to be called.
      // ...
    }
  }
}
```

**Compliant solution**

```java
public class Parent {
  public void foo() { ... }
}

public class Outer {
  public void foo() { ... }

  public class Inner extends Parent {
    public void doSomething() {
      super.foo(); // Compliant, it is explicit that Parent#foo is the desired implementation to be called.
      // ...
    }
  }
}
```

---

---

---

---

### java:S3358 — Ternary operators should not be nested

**Severity**: Medium

Nested ternaries are hard to read and can make the order of operations complex to understand.

```

public String getReadableStatus(Job j) {
  return j.isRunning() ? "Running" : j.hasErrors() ? "Failed" : "Succeeded";  // Noncompliant
}

```

Instead, use another line to express the nested operation in a separate statement.

```

public String getReadableStatus(Job j) {
  if (j.isRunning()) {
    return "Running";
  }
  return j.hasErrors() ? "Failed" : "Succeeded";
}

```

---

---

---

---

### java:S4517 — InputSteam.read() implementation should not return a signed byte

**Severity**: Medium

According to the Java documentation, any implementation of the 
`InputSteam.read()`
 method is supposed to read the next byte of data from
the input stream. The value byte must be an 
`int`
 in the range 0 to 255. If no byte is available because the end of the stream has been
reached, the value -1 is returned.

---

---

---

---

### java:S5413 — 'List.remove()' should not be used in ascending 'for' loops

**Severity**: Medium

When 
`List.remove()`
 is called, the list shrinks, and the indices of all elements following the removed element are decremented by one.
If this operation is performed within a loop that iterates through the elements in ascending order, it will cause the loop to skip the element
immediately following the removed element.

**Noncompliant code example**

```java
void removeFrom(List<String> list) {
  // expected: iterate over all list elements
  for (int i = 0; i < list.size(); i++) {
    if (list.get(i).isEmpty()) {
      list.remove(i); // Noncompliant, next element is skipped
    }
  }
}
```

**Compliant solution**

```java
void removeFrom(List<String> list) {
  list.removeIf(String::isEmpty); // Compliant
}
```

---

---

---

---

### java:S5776 — Exception testing via JUnit ExpectedException rule should not be mixed with other assertions

**Severity**: Medium

When testing exception via 
`org.junit.rules.ExpectedException`
 any code after the raised exception will not be executed, so adding
subsequent assertions is wrong and misleading. This rule raises an issue when an assertion is done after the "expect(…​)" invocation, only the code
throwing the expected exception should be after "expect(…​)".

---

---

---

---

### java:S5778 — Only one method invocation is expected when testing runtime exceptions

**Severity**: Medium

When verifying that code raises a runtime exception, a good practice is to avoid having multiple method calls inside the tested code, to be
explicit about which method call is expected to raise the exception.

---

---

---

---

### java:S6862 — Beans in "@Configuration" class should have different names

**Severity**: Medium

Naming conventions play a crucial role in maintaining code clarity and readability. The uniqueness of bean names in Spring configurations is vital
to the clarity and readability of the code. When two beans share the same name within a configuration, it is not obvious to the reader which bean is
being referred to. This leads to potential misunderstandings and errors.

**Noncompliant code example**

```java
@Configuration
class Config {
  @Bean
  public User user() {
    return currentUser();
  }
  @Bean
  public User user(AuthService auth) { // Noncompliant
    return auth.user();
  }
}
```

**Compliant solution**

```java
@Configuration
class Config {
  @Bean
  public User user() {
    return currentUser();
  }
  @Bean
  public User userFromAuth(AuthService auth) {
    return auth.user();
  }
}
```

---

---

---

---

### java:S1172 — Unused method parameters should be removed

**Severity**: Medium

A typical code smell known as unused function parameters refers to parameters declared in a function but not used anywhere within the function’s
body. While this might seem harmless at first glance, it can lead to confusion and potential errors in your code. Disregarding the values passed to
such parameters, the function’s behavior will be the same, but the programmer’s intention won’t be clearly expressed anymore. Therefore, removing
function parameters that are not being utilized is considered best practice.

**Noncompliant code example**

```java
void doSomething(int a, int b) { // Noncompliant, "b" is unused
  compute(a);
}
```

**Compliant solution**

```java
void doSomething(int a) {
  compute(a);
}
```

---

---

---

---

### java:S2142 — "InterruptedException" and "ThreadDeath" should not be ignored

**Severity**: Medium

If an 
`InterruptedException`
 or a 
`ThreadDeath`
 error is not handled properly, the information that the thread was
interrupted will be lost. Handling this exception means either to re-throw it or manually re-interrupt the current thread by calling

---

---

---

---

### java:S4449 — Nullness of parameters should be guaranteed

**Severity**: Medium

When using null-related annotations at global scope level, for instance using 
`javax.annotation.ParametersAreNonnullByDefault`
 (from
JSR-305) at package level, it means that all the parameters to all the methods included in the package will, or should, be considered
Non-
`null`
. It is equivalent to annotating every parameter in every method with non-null annotations (such as 
`@Nonnull`
).

---

---

---

---

### java:S1171 — Only static class initializers should be used

**Severity**: Medium

Non-static initializers, also known as instance initializers, are blocks of code within a class that are executed when an instance of the class is
created. They are executed when an object of the class is created just before the constructor is called. Non-static initializers are useful when you
want to perform some common initialization logic for all objects of a class. They allow you to initialize instance variables in a concise and
centralized manner, without having to repeat the same initialization code in each constructor.

While non-static initializers may have some limited use cases, they are rarely used and can be confusing for most developers because they only run
when new class instances are created.

**Noncompliant code example**

```java
class MyClass {
  private static final Map<String, String> MY_MAP = new HashMap<String, String>() {
    {
      put("a", "b");
    }
  }; // Noncompliant - HashMap should be extended only to add behavior, not for initialization
}
```

**Compliant solution**

```java
class MyClass {
  private static final Map<String, String> MY_MAP = new HashMap<>();

  static {
    MY_MAP.put("a", "b");  // Compliant
  }
}
```

---

---

---

---

### java:S5669 — Vararg method arguments should not be confusing

**Severity**: Medium

Passing single 
`null`
 or primitive array argument to the variable arity method may not work as expected. In the case of

---

---

---

---

### java:S1068 — Unused "private" fields should be removed

**Severity**: Medium

If a 
`private`
 field is declared but not used locally, its limited visibility makes it dead code.

---

---

---

---

### java:S1065 — Unused labels should be removed

**Severity**: Medium

If a label is declared but not used in the program, it can be considered as dead code and should therefore be removed.

This will improve maintainability as developers will not wonder what this label is used for.

Noncompliant code example

```

void foo() {
  outer: //label is not used.
  for(int i = 0; i<10; i++) {
    break;
  }
}

```

Compliant solution

```

void foo() {
  for(int i = 0; i<10; i++) {
    break;
  }
}

```

---

---

---

---

### java:S1066 — Mergeable "if" statements should be combined

**Severity**: Medium

Nested code - blocks of code inside blocks of code - is eventually necessary, but increases complexity. This is why keeping the code as flat as
possible, by avoiding unnecessary nesting, is considered a good practice.

Merging 
`if`
 statements when possible will decrease the nesting of the code and improve its readability.

Code like

```

if (condition1) {
  if (condition2) {             // Noncompliant
    /* ... */
  }
}

```

Will be more readable as

```

if (condition1 && condition2) { // Compliant
  /* ... */
}

```

**Noncompliant code example**

```java
if (file != null) {
  if (file.isFile() || file.isDirectory()) {  // Noncompliant
    /* ... */
  }
}
```

**Compliant solution**

```java
if (file != null && isFileOrDirectory(file)) { // Compliant
  /* ... */
}

private static boolean isFileOrDirectory(File file) {
  return file.isFile() || file.isDirectory();
}
```

---

---

---

---

### java:S5664 — Whitespace for text block indent should be consistent

**Severity**: Medium

Either use only spaces or only tabs for the indentation of a text block. Mixing white space will lead to a result with irregular indentation.

Noncompliant code example

```

String textBlock = """
        this is
<tab>text block!
        !!!!
      """;

```

Compliant solution

```

String textBlock = """
        this is
        text block!
        !!!!
      """;

```

---

---

---

---

### java:S5785 — JUnit assertTrue/assertFalse should be simplified to the corresponding dedicated assertion

**Severity**: Medium

Testing equality or nullness with JUnit’s 
`assertTrue()`
 or 
`assertFalse()`
 should be simplified to the corresponding
dedicated assertion.

Noncompliant code example

```

Assert.assertTrue(a.equals(b));
Assert.assertTrue(a == b);
Assert.assertTrue(a == null);
Assert.assertTrue(a != null);
Assert.assertFalse(a.equals(b));

```

Compliant solution

```

Assert.assertEquals(a, b);
Assert.assertSame(a, b);
Assert.assertNull(a);
Assert.assertNotNull(a);
Assert.assertNotEquals(a, b);

```

---

---

---

---

### java:S1181 — Throwable and Error should not be caught

**Severity**: Medium

`Throwable`
 is the superclass of all errors and exceptions in Java. 
`Error`
 is the superclass of all errors, which are not
meant to be caught by applications.

Catching either 
`Throwable`
 or 
`Error`
 will also catch 
`OutOfMemoryError`
 and 
`InternalError`
, from
which an application should not attempt to recover.

Noncompliant code example

```

try { /* ... */ } catch (Throwable t) { /* ... */ }
try { /* ... */ } catch (Error e) { /* ... */ }

```

Compliant solution

```

try { /* ... */ } catch (RuntimeException e) { /* ... */ }
try { /* ... */ } catch (MyException e) { /* ... */ }

```

---

---

---

---

### java:S3457 — Format strings should be used correctly

**Severity**: Medium

A 
`printf-`
-style format string is a string that contains placeholders, usually represented by special characters such as "%s" or "{}",
depending on the technology in use. These placeholders are replaced by values when the string is printed or logged.

**Noncompliant code example**

```java
void logging(org.slf4j.Logger slf4jLog, java.util.logging.Logger logger) {
    String.format("Too many arguments %d and %d", 1, 2, 3); // Noncompliant - the third argument '3' is unused
    String.format("First {0} and then {1}", "foo", "bar");  //Noncompliant - it appears there is confusion with the use of "java.text.MessageFormat" - parameters "foo" and "bar" will be ignored here

    slf4jLog.debug("The number: ", 1); // Noncompliant - String contains no format specifiers.

    logger.log(level, "Can't load library \"{0}\"!", "foo"); // Noncompliant - the single quote ' must be escaped
}
```

**Compliant solution**

```java
void logging(org.slf4j.Logger slf4jLog, java.util.logging.Logger logger) {
    String.format("Too many arguments %d and %d", 1, 2);
    String.format("First %s and then %s", "foo", "bar");

    slf4jLog.debug("The number: {}", 1);

    logger.log(level, "Can''t load library \"{0}\"!", "foo");
}
```

---

---

---

---

### java:S2123 — Values should not be uselessly incremented

**Severity**: Medium

A value that is incremented or decremented and then not stored is at best wasted code and at worst a bug.

Noncompliant code example

```

public int pickNumber() {
  int i = 0;
  int j = 0;

  i = i++; // Noncompliant; i is still zero

  return j++; // Noncompliant; 0 returned
}

```

Compliant solution

```

public int pickNumber() {
  int i = 0;
  int j = 0;

  i++;
  return ++j;
}

```

---

---

---

---

### java:S2127 — "Double.longBitsToDouble" should take "long" as argument

**Severity**: Medium

`Double.longBitsToDouble`
 converts the bit pattern into its corresponding floating-point representation. The method expects a 64-bit
long argument to interpret the bits as a double value correctly.

When the argument is a smaller data type, the cast to 
`long`
 may lead to a different value than expected due to the interpretation of
the most significant bit, which, in turn, results in 
`Double.longBitsToDouble`
 returning an incorrect value.

Noncompliant code example

```

int i = 0x80003800;
Double.longBitsToDouble(i);   // Noncompliant - NaN

```

Compliant solution

```

long i = 0x80003800L;
Double.longBitsToDouble(i);   // Compliant - 1.0610049784E-314

```

---

---

---

---

### java:S4425 — "Integer.toHexString" should not be used to build hexadecimal strings

**Severity**: Medium

Using 
`Integer.toHexString`
 is a common mistake when converting sequences of bytes into hexadecimal string representations. The problem
is that the method trims leading zeroes, which can lead to wrong conversions. For instance a two bytes value of 
`0x4508`
 would be converted
into 
`45`
 and 
`8`
 which once concatenated would give 
`0x458`
.

---

---

---

---

### java:S5993 — Constructors of an "abstract" class should not be declared "public"

**Severity**: Medium

Abstract classes should not have public constructors. Constructors of abstract classes can only be called in constructors of their subclasses. So
there is no point in making them public. The 
`protected`
 modifier should be enough.

Noncompliant code example

```

public abstract class AbstractClass1 {
    public AbstractClass1 () { // Noncompliant, has public modifier
        // do something here
    }
}

```

Compliant solution

```

public abstract class AbstractClass2 {
    protected AbstractClass2 () {
        // do something here
    }
}

```

---

---

---

---

### java:S5998 — Regular expressions should not overflow the stack

**Severity**: Medium

The Java regex engine uses recursive method calls to implement backtracking. Therefore when a repetition inside a regular expression contains
multiple paths (i.e. the body of the repetition contains an alternation (
`|`
), an optional element or another repetition), trying to match
the regular expression can cause a stack overflow on large inputs. This does not happen when using a possessive quantifier (such as 
`*+`

---

---

---

---

### java:S1150 — "Enumeration" should not be implemented

**Severity**: Medium

As documented in 
`Enumeration`
 's Javadoc, you should favor the 
`Iterator`
 interface over 
`Enumeration`
.

`Iterator`
 offers a similar contract to 
`Enumeration`
 with the addition of a method for removal and shorter method names.

Noncompliant code example

```

public class MyClass implements Enumeration {  // Noncompliant
  /* ... */
}

```

Compliant solution

```

public class MyClass implements Iterator {     // Compliant
  /* ... */
}

```

---

---

---

---

### java:S1168 — Empty arrays and collections should be returned instead of null

**Severity**: Medium

Returning 
`null`
 instead of an actual array, collection or map forces callers of the method to explicitly test for nullity, making them
more complex and less readable.

---

---

---

---

### java:S2121 — String operations with predictable outcomes should be avoided

**Severity**: Medium

Operations performed on a string with predictable outcomes should be avoided. For example:

 checking if a string contains itself 

 comparing a string with itself 

 matching a string against itself 

 creating a substring from 0 to the end of the string 

 creating a substring from the end of the string 

 replacing a string with itself 

 replacing a substring with the exact substring

**Noncompliant code example**

```java
String speech = "SonarQube is the best static code analysis tool."

String s1 = speech.substring(0); // Noncompliant - yields the whole string
String s2 = speech.substring(speech.length()); // Noncompliant - yields "";
String s3 = speech.substring(5, speech.length()); // Noncompliant - use the 1-arg version instead

if (speech.contains(speech)) { // Noncompliant - always true
    // ...
}
```

**Compliant solution**

```java
String speech = "SonarQube is the best static code analysis tool."

String s1 = speech;
String s2 = "";
String s3 = speech.substring(5);

// ...
```

---

---

---

---

### java:S2129 — Constructors should not be used to instantiate "String", "BigInteger", "BigDecimal" and primitive-wrapper classes

**Severity**: Medium

Calling constructors for 
`String`
, 
`BigInteger`
, 
`BigDecimal`
 and the objects used to wrap primitives is less
efficient and less clear than relying on autoboxing or 
`valueOf`
.

---

---

---

---

### java:S2134 — Classes extending java.lang.Thread should provide a specific "run" behavior

**Severity**: Medium

The default implementation of 
`java.lang.Thread`
 's 
`run`
 will only perform a task passed as a 
`Runnable`
. If no

`Runnable`
 has been provided at construction time, then the thread will not perform any action.

When extending 
`java.lang.Thread`
, you should override the 
`run`
 method or pass a 
`Runnable`
 target to the
constructor of 
`java.lang.Thread`
.

Noncompliant code example

```

public class MyThread extends Thread { // Noncompliant
  public void doSomething() {
    System.out.println("Hello, World!");
  }
}

```

**Noncompliant code example**

```java
public class MyThread extends Thread {
  @Override
  public void run() {
    System.out.println("Hello, World!");
  }
}
```

**Compliant solution**

```java
public class MyRunnable implements Runnable {
  @Override
  public void run() {
    System.out.println("Hello, World!");
  }
}
public class MyThread extends Thread {
  public MyThread(Runnable runnable) {
    super(runnable);
  }
}

public class Main() {
  public static void main(String [] args) {
    Runnable runnable = new MyRunnable();
    Thread customThread = new MyThread(runnable);
    Thread regularThread = new Thread(runnable);
  }
}
```

---

---

---

---

### java:S3346 — Expressions used in "assert" should not produce side effects

**Severity**: Medium

Since 
`assert`
 statements aren’t executed by default (they must be enabled with JVM flags) developers should never rely on their
execution the evaluation of any logic required for correct program function.

Noncompliant code example

```

assert myList.remove(myList.get(0));  // Noncompliant

```

Compliant solution

```

boolean removed = myList.remove(myList.get(0));
assert removed;

```

---

---

---

---

### java:S2252 — Loop conditions should be true at least once

**Severity**: Medium

A 
[for](https://docs.oracle.com/javase/tutorial/java/nutsandbolts/for.html)
 loop is a fundamental programming construct
used to execute a block of code repeatedly. However, if the loop’s condition is false before the first iteration, the loop will never execute.

```

for (int i = 0; i < 0; i++) {  // Noncompliant: the condition is always false, and the loop will never execute
    // ...
}

```

Rewrite the loop to ensure the condition evaluates to 
`true`
 at least once.

```

for (int i = 0; i < 10; i++) {  // Compliant: the condition is true at least once, the loop will execute
    // ...
}

```

This bug has the potential to cause unexpected outcomes as the loop might contain critical code that needs to be executed.

---

---

---

---

### java:S2139 — Exceptions should be either logged or rethrown but not both

**Severity**: Medium

In applications where the accepted practice is to log an 
`Exception`
 and then rethrow it, you end up with miles-long logs that contain
multiple instances of the same exception. In multi-threaded applications debugging this type of log can be particularly hellish because messages from
other threads will be interwoven with the repetitions of the logged-and-thrown 
`Exception`
. Instead, exceptions should be either logged or
rethrown, not both.

---

---

---

---

### java:S1161 — "@Override" should be used on overriding and implementing methods

**Severity**: Medium

While not mandatory, using the 
`@Override`
 annotation on compliant methods improves readability by making it explicit that methods are
overridden.

A compliant method either overrides a parent method or implements an interface or abstract method.

Noncompliant code example

```

class ParentClass {
  public boolean doSomething(){/*...*/}
}
class FirstChildClass extends ParentClass {
  public boolean doSomething(){/*...*/}  // Noncompliant
}

```

Compliant solution

```

class ParentClass {
  public boolean doSomething(){/*...*/}
}
class FirstChildClass extends ParentClass {
  @Override
  public boolean doSomething(){/*...*/}  // Compliant
}

```

Exceptions

This rule does not raise issues when overriding methods from 
`Object`
 (eg: 
`equals()`
, 
`hashCode()`
,

`toString()`
, …​).

---

---

---

---

### java:S2251 — A "for" loop update clause should move the counter in the right direction

**Severity**: Medium

A 
`for`
 loop with a counter moving away from the end of the specified range is likely a programming mistake.

If the intention is to iterate over the specified range, this differs from what the loop does because the counter moves in the wrong direction.

If the intention is to have an infinite loop or a loop terminated only by a break statement, there are two problems:

 The loop condition is not infinite because the counter variable will eventually overflow and fulfill the condition. This can take a long time,
  depending on the data type of the counter. 

 An infinite loop terminated by a 
`break`
 statement should be implemented using a 
`while`
 or 
`do`

`while`
 loop to make the developer’s intention clear to the reader.

**Noncompliant code example**

```java
for (int i = 10; i > 0; i++) { // Noncompliant, wrong direction
  System.out.println("Hello, world!") // executed ca. 2 billion times
}
```

**Compliant solution**

```java
public void doSomething(String [] strings) {
  for (int i = 0; i < strings.length; i--) { // Noncompliant, wrong direction
    String string = strings[i];  // ArrayIndexOutOfBoundsException when i reaches -1
    // ...
  }
}
```

---

---

---

---

### java:S2629 — "Preconditions" and logging arguments should not require evaluation

**Severity**: Medium

Some method calls can effectively be "no-ops", meaning that the invoked method does nothing, based on the application’s configuration (eg: debug
logs in production). However, even if the method effectively does nothing, its arguments may still need to evaluated before the method is called.

---

---

---

---

### java:S3958 — Intermediate Stream methods should not be left unused

**Severity**: Medium

There are two types of stream operations: intermediate operations, which return another stream, and terminal operations, which return something
other than a stream. Intermediate operations are lazy, meaning they aren’t actually executed until and unless a terminal stream operation is performed
on their results. Consequently, if the result of an intermediate stream operation is not fed to a terminal operation, it serves no purpose, which is
almost certainly an error.

---

---

---

---

### java:S3959 — Consumed Stream pipelines should not be reused

**Severity**: Medium

Stream operations are divided into intermediate and terminal operations, and are combined to form stream pipelines. After the terminal operation is
performed, the stream pipeline is considered consumed, and cannot be used again. Such a reuse will yield unexpected results.

Noncompliant code example

```

Stream<Widget> pipeline = widgets.stream().filter(b -> b.getColor() == RED);
int sum1 = pipeline.sum();
int sum2 = pipeline.mapToInt(b -> b.getWeight()).sum(); // Noncompliant

```

---

---

---

---

### java:S2639 — Inappropriate regular expressions should not be used

**Severity**: Medium

Regular expressions are powerful but tricky, and even those long used to using them can make mistakes.

---

---

---

---

### java:S2757 — Non-existent operators like "=+" should not be used

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

int target = -5;
int num = 3;

target =- num;  // Noncompliant: target = -3. Is that the intended behavior?
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

int target = -5;
int num = 3;

target -= num;  // target = -8

```

Or fix the spacing to avoid confusion

```

int target = -5;
int num = 3;

target = -num;  // target = -3

```

---

---

---

---

### java:S4925 — "Class.forName()" should not load JDBC 4.0+ drivers

**Severity**: Medium

In the past, it was required to load a JDBC driver before creating a 
`java.sql.Connection`
. Nowadays, when using JDBC 4.0 drivers, this
is no longer required and 
`Class.forName()`
 can be safely removed because JDBC 4.0 (JDK 6) drivers available in the classpath are
automatically loaded.

---

---

---

---

### java:S1764 — Identical expressions should not be used on both sides of a binary operator

**Severity**: Medium

Using the same value on both sides of a binary operator is a code defect. In the case of logical operators, it is either a copy/paste error and,
therefore, a bug, or it is simply duplicated code and should be simplified. In the case of bitwise operators and most binary mathematical operators,
having the same value on both sides of an operator yields predictable results and should be simplified as well.

---

---

---

---

### java:S3824 — "Map.get" and value test should be replaced with single method call

**Severity**: Medium

It’s a common pattern to test the result of a 
`java.util.Map.get()`
 against 
`null`
 or calling

---

---

---

---

### java:S3631 — "Arrays.stream" should be used for primitive arrays

**Severity**: Medium

For arrays of objects, 
`Arrays.asList(T ... a).stream()`
 and 
`Arrays.stream(array)`
 are basically equivalent in terms of
performance. However, for arrays of primitives, using 
`Arrays.asList`
 will force the construction of a list of boxed types, and then use

---

---

---

---

### java:S5810 — JUnit5 test classes and methods should not be silently ignored

**Severity**: Medium

JUnit5 is more tolerant regarding the visibilities of Test classes and methods than JUnit4, which required everything to be public. JUnit5 supports
default package, public and protected visibility, even if it is recommended to use the default package visibility, which improves the readability of
code.

---

---

---

---

### java:S6901 — "setDaemon", "setPriority" and "getThreadGroup" should not be invoked on virtual threads

**Severity**: Medium

The 
`Thread`
 class has some methods that are used to monitor and manage its execution. With the introduction of virtual threads in Java
21, there are three of these methods that behave differently between the standard platform threads and the virtual ones.

---

---

---

---

### java:S3751 — "@RequestMapping" methods should not be "private"

**Severity**: Medium

A method with a 
`@RequestMapping`
 annotation part of a class annotated with 
`@Controller`
 (directly or indirectly through a
meta annotation - 
`@RestController`
 from Spring Boot is a good example) will be called to handle matching web requests. That will happen
even if the method is 
`private`
, because Spring invokes such methods via reflection, without checking visibility.

---

## 13. Testing Quality Rules — Medium (21 rules)

---

---

---

### java:S2789 — "null" should not be used with "Optional"

**Severity**: Medium

`Optional`
 acts as a container object that may or may not contain a non-null value. It is introduced in Java 8 to help avoid

`NullPointerException`
. It provides methods to check if a value is present and retrieve the value if it is present.

`Optional`
 is used instead of 
`null`
 values to make the code more readable and avoid potential errors.

It is a bad practice to use 
`null`
 with 
`Optional`
 because it is unclear whether a value is present or not, leading to
confusion and potential 
`NullPointerException`
 errors.

**Noncompliant code example**

```java
public void doSomething () {
  Optional<String> optional = getOptional();
  if (optional != null) {  // Noncompliant
    // do something with optional...
  }
  Optional<String> text = null; // Noncompliant, a variable whose type is Optional should never itself be null
  // ...
}

@Nullable // Noncompliant
public Optional<String> getOptional() {
  // ...
  return null;  // Noncompliant
}
```

**Compliant solution**

```java
public void doSomething () {
  Optional<String> optional = getOptional();
  optional.ifPresent(
    // do something with optional...
  );
  Optional<String> text = Optional.empty();
  // ...
}

public Optional<String> getOptional() {
  // ...
  return Optional.empty();
}
```

---

---

---

---

### java:S1221 — Methods should not be named "tostring", "hashcode" or "equal"

**Severity**: Medium

Due to the similar name with the methods 
`Object.toString`
, 
`Object.hashCode`
 and 
`Object.equals`
, there is a
significant likelihood that a developer intended to override one of these methods but made a spelling error.

Even if no such error exists and the naming was done on purpose, these method names can be misleading. Readers might not notice the difference, or
if they do, they may falsely assume that the developer made a mistake.

**Noncompliant code example**

```java
public int hashcode() { /* ... */ }             // Noncompliant

public String tostring() { /* ... */ }          // Noncompliant

public boolean equal(Object obj) { /* ... */ }  // Noncompliant
```

**Compliant solution**

```java
@Override
public int hashCode() { /* ... */ }             // Compliant

@Override
public String toString() { /* ... */ }          // Compliant

@Override
public boolean equals(Object obj) { /* ... */ } // Compliant
```

---

---

---

---

### java:S1223 — Non-constructor methods should not have the same name as the enclosing class

**Severity**: Medium

Having a class and some of its methods sharing the same name is misleading, and leaves others to wonder whether it was done that way on purpose, or
was the methods supposed to be a constructor.

Noncompliant code example

```

public class Foo {
   public Foo() {...}
   public void Foo(String label) {...}  // Noncompliant
}

```

Compliant solution

```

public class Foo {
   public Foo() {...}
   public void foo(String label) {...}  // Compliant
}

```

---

---

---

---

### java:S2438 — "Thread" should not be used where a "Runnable" argument is expected

**Severity**: Medium

The semantics of 
`Thread`
 and 
`Runnable`
 are different, and while it is technically correct to use 
`Thread`
 where
a 
`Runnable`
 is expected, it is a bad practice to do so.

---

---

---

---

### java:S2675 — "readObject" should not be "synchronized"

**Severity**: Medium

The 
`readObject`
 method is implemented when a 
`Serializable`
 object requires special handling to be reconstructed from a
file. The object created by 
`readObject`
 is accessed only by the thread that called the method, thus using the 
`synchronized`

keyword in this context is unnecessary and causes confusion.

Noncompliant code example

```

private synchronized void readObject(java.io.ObjectInputStream in)
     throws IOException, ClassNotFoundException { // Noncompliant
  //...
}

```

Compliant solution

```

private void readObject(java.io.ObjectInputStream in)
     throws IOException, ClassNotFoundException { // Compliant
  //...
}

```

---

---

---

---

### java:S2677 — "read" and "readLine" return values should be used

**Severity**: Medium

The 
`Reader.read()`
 and the 
`BufferedReader.readLine()`
 are used for reading data from a data source. The return value of
these methods is the data read from the data source, or 
`null`
 when the end of the data source is reached. If the return value is ignored,
the data read from the source is thrown away and may indicate a bug.

---

---

---

---

### java:S4973 — Strings and Boxed types should be compared using "equals()"

**Severity**: Medium

It’s almost always a mistake to compare two instances of 
`java.lang.String`
 or boxed types like 
`java.lang.Integer`
 using
reference equality 
`==`
 or 
`!=`
, because it is not comparing actual value but locations in memory.

Noncompliant code example

```

String firstName = getFirstName(); // String overrides equals
String lastName = getLastName();

if (firstName == lastName) { ... }; // Non-compliant; false even if the strings have the same value

```

Compliant solution

```

String firstName = getFirstName();
String lastName = getLastName();

if (firstName != null && firstName.equals(lastName)) { ... };

```

---

---

---

---

### java:S4738 — Java features should be preferred to Guava

**Severity**: Medium

Some Guava features were really useful for Java 7 application because Guava was bringing APIs missing in the JDK. Java 8 fixed some of these
limitations. When migrating an application to Java 8 or even when starting a new one, it’s recommended to prefer Java 8 APIs over Guava ones to ease
its maintenance: developers don’t need to learn how to use two APIs and can stick to the standard one.

---

---

---

---

### java:S6913 — "Math.clamp" should be used with correct ranges

**Severity**: Medium

Java 21 introduces the new method 
`Math.clamp(value, min, max)`
 that fits a value within a specified interval. Before Java 21, this
behavior required explicit calls to the 
`Math.min`
 and 
`Math.max`
 methods, as in 
`Math.min(max, Math.max(value,
min))`
.

If 
`min > max`
, 
`Math.clamp`
 throws an 
`IllegalArgumentException`
, indicating an invalid interval. This can
occur if the 
`min`
 and 
`max`
 arguments are mistakenly reversed.

Note that 
`Math.clamp`
 is not a general substitute for 
`Math.min`
 or 
`Math.max`
, but for the combination of both.
If 
`value`
 is the same as 
`min`
 or 
`max`
, using 
`Math.clamp`
 is unnecessary and 
`Math.min`
 or

`Math.max`
 should be used instead.

**Noncompliant code example**

```java
Math.clamp(red, 255, 0); // Noncompliant, [255,0] is not a valid range
```

**Compliant solution**

```java
Math.clamp(red, 0, 255); // Compliant
```

---

---

---

---

### java:S6915 — "String.indexOf" should be used with correct ranges

**Severity**: Medium

Java 21 adds new 
`String.indexOf`
 methods that accept ranges (
`beginIndex`
, to 
`endIndex`
) rather than just a
start index. A 
`StringIndexOutOfBounds`
 can be thrown when indicating an invalid range, namely when:

 
`beginIndex > endIndex`
 (eg: 
`beginIndex`
 and 
`endIndex`
 arguments are mistakenly reversed) 

 
`beginIndex < 0`
 (eg: because the older 
`String.indexOf(what, fromIndex)`
 accepts negative values)

**Noncompliant code example**

```java
String hello = "Hello, world!";
int index = hello.indexOf('o', 11, 7); // Noncompliant, 11..7 is not a valid range
```

**Compliant solution**

```java
String hello = "Hello, world!";
int index = hello.indexOf('o', 7, 11); // Compliant
```

---

---

---

---

### java:S6916 — Use when instead of a single if inside a pattern match body

**Severity**: Medium

Java 21 has introduced enhancements to switch statements and expressions, allowing them to operate on any type, not just specific ones, as in
previous versions. Furthermore, case labels have been upgraded to support patterns, providing an alternative to the previous restriction of only
accepting constants.

**Noncompliant code example**

```java
void testObject(Object response) {
    switch (response) {
        case String s -> {
            if(s.length() > 80) { // Noncompliant; use the "when" keyword
                System.out.println("This string is too long");
            }
        }
        case Integer i -> {
            if(i > 80) { // Noncompliant; use the "when" keyword
                System.out.println("This integer is too big");
            }
        }
        default -> System.out.println("Unknown type");
    }
}
```

**Compliant solution**

```java
void testObject(Object response) {
    switch (response) {
        case String s when s.length() > 80 -> {
            System.out.println("This string is too long");
        }
        case Integer i when i > 80 -> {
            System.out.println("This integer is too big");
        }
        default -> System.out.println("Unknown type");
    }
}
```

---

---

---

---

### java:S1317 — "StringBuilder" and "StringBuffer" should not be instantiated with a character

**Severity**: Medium

When a developer uses the 
`StringBuilder`
 or 
`StringBuffer`
 constructor with a single character as an argument, the likely
intention is to create an instance with the character as the initial string value.

**Noncompliant code example**

```java
StringBuffer foo = new StringBuffer('x'); // Noncompliant, replace with String
```

**Compliant solution**

```java
StringBuffer foo = new StringBuffer("x"); // Compliant
```

---

---

---

---

### java:S2761 — Unary prefix operators should not be repeated

**Severity**: Medium

The repetition of a unary operator is usually a typo. The second operator invalidates the first one in most cases:

---

---

---

---

### java:S5917 — DateTimeFormatters should not use mismatched year and week numbers

**Severity**: Medium

When creating a 
`DateTimeFormatter`
 using the 
`WeekFields.weekBasedYear()`
 temporal field, the resulting year number may be
off by 1 at the beginning of a new year (when the date to format is in a week that is shared by two consecutive years).

---

---

---

---

### java:S1201 — "equals" method overrides should accept "Object" parameters

**Severity**: Medium

In Java, the 
`Object.equals()`
 method is used for object comparison, and it is typically overridden in classes to provide a custom
equality check based on your criteria for equality.

The default implementation of 
`equals()`
 provided by the 
`Object`
 class compares the memory references of the two objects,
that means it checks if the objects are actually the same instance in memory.

The "equals" as a method name should be used exclusively to override 
`Object.equals(Object)`
 to prevent confusion.

It is important to note that when you override 
`equals()`
, you should also override the 
`hashCode()`
 method to maintain the
contract between 
`equals()`
 and 
`hashCode()`
.

**Noncompliant code example**

```java
class MyClass {
  private int foo = 1;

  public boolean equals(MyClass o) {  // Noncompliant; does not override Object.equals(Object)
    return o != null && o.foo == this.foo;
  }

  public static void main(String[] args) {
    MyClass o1 = new MyClass();
    Object o2 = new MyClass();
    System.out.println(o1.equals(o2));  // Prints "false" because o2 an Object not a MyClass
  }
}
```

**Compliant solution**

```java
class MyClass {
  private int foo = 1;

  @Override
  public boolean equals(Object o) {  // Compliant
    if (this == o) {
        return true;
    }

    if (o == null || getClass() != o.getClass()) {
      return false;
    }

    MyClass other = (MyClass)o;
    return this.foo == other.foo;
  }
}
```

---

---

---

---

### java:S3864 — "Stream.peek" should be used with caution

**Severity**: Medium

According to its JavaDocs, the intermediate Stream operation 
`java.util.Stream.peek()`
 “exists mainly to support debugging”
purposes.

---

---

---

---

### java:S3984 — Exceptions should not be created without being thrown

**Severity**: Medium

Creating a new 
`Throwable`
 without actually throwing it is useless and is probably due to a mistake.

Noncompliant code example

```

if (x < 0)
  new IllegalArgumentException("x must be nonnegative");

```

Compliant solution

```

if (x < 0)
  throw new IllegalArgumentException("x must be nonnegative");

```

---

---

---

---

### java:S3985 — Unused "private" classes should be removed

**Severity**: Medium

`private`
 classes that are never used are dead code: unnecessary, inoperative code that should be removed. Cleaning out dead code
decreases the size of the maintained codebase, making it easier to understand the program and preventing bugs from being introduced.

Noncompliant code example

```

public class TopLevel
{
  private class Nested {...} // Noncompliant: Nested is never used
}

```

Compliant solution

```

public class TopLevel
{
  void doSomething() {
    Nested a = new Nested();
    ...
  }
  private class Nested {...}
}

```

---

---

---

---

### java:S3986 — Week Year ("YYYY") should not be used for date formatting

**Severity**: Medium

Few developers are aware of the difference between 
`Y`
 for "Week year" and 
`y`
 for Year when formatting and parsing a date
with 
`SimpleDateFormat`
 or 
`DateTimeFormatter`
. That’s likely because for most dates, Week year and Year are the same, so
testing at any time other than the first or last week of the year will yield the same value for both 
`y`
 and 
`Y`
. But in the
last week of December and the first week of January, you may get unexpected results.

---

---

---

---

### java:S3740 — Raw types should not be used

**Severity**: Medium

A generic type is a generic class or interface that is parameterized over types. For example, 
`java.util.List`
 has one type parameter:
the type of its elements.

**Noncompliant code example**

```java
// List is supposed to store integers only
List integers = new ArrayList<>();

// Yet, we can add strings, because we did not give
// this information to the compiler
integers.add("Hello World!");

// Type is checked during runtime and will throw a ClassCastException
Integer a = (Integer) integers.get(0);
```

**Compliant solution**

```java
// List is supposed to store integers, and we let the compiler know
List<Integer> integers = new ArrayList<>();

// Now we can add only integers.
// Adding a string results in a compile time error.
integers.add(42);

// No cast required anymore, and no possible ClassCastException
Integer a = integers.get(0);
```

---

---

---

---

### java:S1700 — A field should not duplicate the name of its containing class

**Severity**: Medium

It’s confusing to have a class member with the same name (case differences aside) as its enclosing class. This is particularly so when you consider
the common practice of naming a class instance for the class itself.

---

---

---

---

### java:S6395 — Non-capturing groups without quantifier should not be used

**Severity**: Medium

Sub-patterns can be wrapped by parentheses to build a group. This enables to restrict alternations, back reference the group or apply quantifier to
the sub-pattern.

If this group should not be part of the match result or if no reference to this group is required, a non-capturing group can be created by adding

`?:`
 behind the opening parenthesis.

However, if this non-capturing group does not have a quantifier, or does not wrap an alternation, then imaging this group is redundant.

Noncompliant code example

```

"(?:number)\\d{2}"

```

Compliant solution

```

"number\\d{2}"      	// it is anyway required
"(?:number)?\\d{2}"  	// it is in fact optional

```

Exceptions

This rule does not report an issue if the non-capturing group is an alternation.

```

"(?:number|string)"

```

---

---

---

---

### java:S6396 — Superfluous curly brace quantifiers should be avoided

**Severity**: Medium

Curly brace quantifiers in regular expressions can be used to have a more fine-grained control over how many times the character or the
sub-expression preceeding them should occur. They can be used to match an expression exactly n times with 
`{n}`
, between n and m times with

---

---

---

---

### java:S6035 — Single-character alternations in regular expressions should be replaced with character classes

**Severity**: Medium

When an alternation contains multiple alternatives that consist of a single character, it can be rewritten as a character class. This should be
preferred because it is more efficient and can even help prevent stack overflows when used inside a repetition (see rule 
[S5998](https://sonarqube.internal.philips/coding_rules#rule_key=java%3AS5998)
).

Noncompliant code example

```

Pattern.compile("a|b|c"); // Noncompliant

```

Compliant solution

```

Pattern.compile("[abc]");
// or
Pattern.compile("[a-c]");

```

---

---

---

---

### java:S6126 — String multiline concatenation should be replaced with Text Blocks

**Severity**: Medium

In Java 15 Text Blocks are now official and can be used. The most common pattern for multiline strings in Java < 15 was to write String
concatenation. Now it’s possible to do it in a more natural way using Text Blocks.

Noncompliant code example

```

String textBlock =
               "<html>\n" +
               "    <body>\n" +
               "        <tag>\n" +
               "        </tag>\n" +
               "    </body>\n" +
               "</html>";

```

Compliant solution

```

String textBlock = """
        <html>
            <body>
                <tag>
                </tag>
            </body>
        </html>""";

```

---

---

---

---

### java:S6397 — Character classes in regular expressions should not contain only one character

**Severity**: Medium

Character classes in regular expressions are a convenient way to match one of several possible characters by listing the allowed characters or
ranges of characters. If a character class contains only one character, the effect is the same as just writing the character without a character
class.

Thus, having only one character in a character class is usually a simple oversight that remained after removing other characters of the class.

Noncompliant code example

```

"a[b]c"
"[\\^]"

```

Compliant solution

```

"abc"
"\\^"
"a[*]c" // Compliant, see Exceptions

```

Exceptions

This rule does not raise when the character inside the class is a metacharacter. This notation is sometimes used to avoid escaping (e.g.,

`[.]{3}`
 to match three dots).

---

---

---

---

### java:S6241 — Region should be set explicitly when creating a new "AwsClient"

**Severity**: Medium

If the region is not specified when creating a new AwsClient with an 
[AwsClientBuilder](https://sdk.amazonaws.com/java/api/latest/software/amazon/awssdk/awscore/client/builder/AwsClientBuilder.html)
, the AWS SDK
will execute some logic to identify the endpoint automatically.

---

---

---

---

### java:S6242 — Credentials Provider should be set explicitly when creating a new "AwsClient"

**Severity**: Medium

If the credentials provider is not specified when creating a new AwsClient with an 
[AwsClientBuilder](https://sdk.amazonaws.com/java/api/latest/software/amazon/awssdk/awscore/client/builder/AwsClientBuilder.html)
, the AWS SDK
will execute some logic to identify it automatically.

---

---

---

---

### java:S6019 — Reluctant quantifiers in regular expressions should be followed by an expression that can't match the empty string

**Severity**: Medium

When a reluctant quantifier (such as 
`*?`
 or 
`+?`
) is followed by a pattern that can match the empty string or directly by
the end of the regex, it will always match the empty string when used with methods that find partial matches (such as 
`find`
,

---

---

---

---

### java:S6243 — Reusable resources should be initialized at construction time of Lambda functions

**Severity**: Medium

Resources that can be reused across multiple invocations of the Lambda function should be initialized at construction time. For example in the
constructor of the class, or in field initializers. This way, when the same container is reused for multiple function invocations, the existing
instance can be reused, along with all resources stored in its fields. It is a good practice to reuse SDK clients and database connections by
initializing them at class construction time, to avoid recreating them on every lambda invocation. Failing to do so can lead to performance
degradation, and when not closed properly, even out of memory errors.

---

---

---

---

### java:S5164 — "ThreadLocal" variables should be cleaned up when no longer used

**Severity**: Medium

`ThreadLocal`
 variables are supposed to be garbage collected once the holding thread is no longer alive. Memory leaks can occur when
holding threads are re-used which is the case on application servers using pool of threads.

---

---

---

---

### java:S1860 — Synchronization should not be done on instances of value-based classes

**Severity**: Medium

In Java, value-based classes are those for which instances are final and immutable, like 
`String`
, 
`Integer`
 and so on, and
their identity relies on their value and not their reference. When a variable of one of these types is instantiated, the JVM caches its value, and the
variable is just a reference to that value. For example, multiple 
`String`
 variables with the same value "Hello world!" will refer to the
same cached string literal in memory.

**Noncompliant code example**

```java
private static final Boolean bLock = Boolean.FALSE;
private static final Integer iLock = Integer.valueOf(0);
private static final String sLock = "LOCK";
private static final List<String> listLock = List.of("a", "b", "c", "d");

public void doSomething() {

  synchronized(bLock) {  // Noncompliant
      ...
  }
  synchronized(iLock) {  // Noncompliant
      ...
  }
  synchronized(sLock) {  // Noncompliant
      ...
  }
  synchronized(listLock) {  // Noncompliant
      ...
  }
```

**Compliant solution**

```java
private static final Object lock1 = new Object();
private static final Integer iLock = new Integer(42);
private static final String sLock = new String("A brand new string in memory!");
private static final List<String> listLock = new ArrayList<>();

public void doSomething() {

  synchronized(lock1) { // Compliant
      ...
  }
  synchronized(iLock) { // Compliant
      ...
  }
  synchronized(sLock) { // Compliant
      ...
  }
  synchronized(listLock) { // Compliant
      ...
  }
```

---

---

---

---

### java:S2718 — "DateUtils.truncate" from Apache Commons Lang library should not be used

**Severity**: Medium

The 
`ZonedDateTime`
 is an immutable representation of a date-time with a time-zone, introduced in Java 8. This class stores all date and
time fields, to a precision of nanoseconds, and a time zone, with a zone offset used to handle ambiguous local date times.

---

---

---

---

### java:S3923 — All branches in a conditional structure should not have exactly the same implementation

**Severity**: Medium

Having all branches of a 
`switch`
 or 
`if`
 chain with the same implementation indicates a problem.

---

---

---

---

### java:S6070 — The regex escape sequence \cX should only be used with characters in the @-_ range

**Severity**: Medium

In regular expressions the escape sequence 
`\cX`
, where the X stands for any character that’s either 
`@`
, any capital ASCII
letter, 
`[`
, 
`\`
, 
`]`
, 
`^`
 or 
`_`
, represents the control character that "corresponds" to the
character following 
`\c`
, meaning the control character that comes 64 bytes before the given character in the ASCII encoding.

---

---

---

---

### java:S125 — Sections of code should not be commented out

**Severity**: Medium

Commented-out code distracts the focus from the actual executed code. It creates a noise that increases maintenance code. And because it is never
executed, it quickly becomes out of date and invalid.

Commented-out code should be deleted and can be retrieved from source control history if required.

---

---

---

---

### java:S127 — "for" loop stop conditions should be invariant

**Severity**: Medium

A 
`for`
 loop termination condition should test the loop counter against an invariant value that does not change during the execution of
the loop. Invariant termination conditions make the program logic easier to understand and maintain.

This rule tracks three types of non-invariant termination conditions:

 When the loop counters are updated in the body of the 
`for`
 loop 

 When the termination condition depends on a method call 

 When the termination condition depends on an object property since such properties could change during the execution of the loop.

**Noncompliant code example**

```java
for (int i = 0; i < foo(); i++) { // Noncompliant, "foo()" is not an invariant
  // ...
}
```

**Compliant solution**

```java
int end = foo();
for (int i = 0; i < end; i++) { // Compliant, "end" does not change during loop execution
  // ...
}
```

---

---

---

---

### java:S2925 — "Thread.sleep" should not be used in tests

**Severity**: Medium

In asynchronous testing, the test code is written in a way that allows it to wait for the asynchronous operation to complete before continuing with
the test.

---

---

---

---

### java:S1604 — Anonymous inner classes containing only one method should become lambdas

**Severity**: Medium

Before Java 8, the only way to partially support closures in Java was by using anonymous inner classes. Java 8 introduced lambdas, which are
significantly more readable and should be used instead.

---

---

---

---

### java:S1607 — JUnit4 @Ignored and JUnit5 @Disabled annotations should be used to disable tests and should provide a rationale

**Severity**: Medium

When a test fails due, for example, to infrastructure issues, you might want to ignore it temporarily. But without some kind of notation about why
the test is being ignored, it may never be reactivated. Such tests are difficult to address without comprehensive knowledge of the project, and end up
polluting their projects.

---

---

---

---

### java:S3039 — Indexes to passed to "String" operations should be within the string's bounds

**Severity**: Medium

There are various 
`String`
 operations that take one or more character indexes as arguments and return a portion of the original string.
Indexing in this context is zero-based, meaning that the first character’s index is 
`0`
. As a result, given a string 
`myString`
,
its last character is at index 
`myString.length() - 1`
.

**Noncompliant code example**

```java
String speech = "Lorem ipsum dolor sit amet";

String substr1 = speech.substring(-1, speech.length()); // Noncompliant, -1 is out of bounds
String substr2 = speech.substring(speech.length(), 0);  // Noncompliant, the beginIndex must be smaller than or equal to the endIndex
char ch = speech.charAt(speech.length());               // Noncompliant, speech.length() is out of bounds
```

**Compliant solution**

```java
String speech = "Lorem ipsum dolor sit amet";

String substr1 = speech;                                         // Compliant, no string operation used
String substr2 = new StringBuilder(speech).reverse().toString(); // Compliant, the string can be reversed using StringBuilder::reverse()
char ch = speech.charAt(speech.length() - 1);                    // Compliant, speech.length() - 1 is in bounds.
```

---

---

---

---

### java:S112 — Generic exceptions should never be thrown

**Severity**: Medium

Throwing generic exceptions such as 
`Error`
, 
`RuntimeException`
, 
`Throwable`
, and 
`Exception`
 will have
a negative impact on any code trying to catch these exceptions.

**Noncompliant code example**

```java
void checkValue(int value) throws Throwable { // Noncompliant: signature is too broad
    if (value == 42) {
        throw new RuntimeException("Value is 42"); // Noncompliant: This will be difficult for consumers to handle
    }
}
```

**Compliant solution**

```java
void checkValue(int value) {
    if (value == 42) {
        throw new IllegalArgumentException("Value is 42"); // Compliant
    }
}
```

---

---

---

---

### java:S2061 — Custom serialization methods should have required signatures

**Severity**: Medium

Java offers a built-in serialization mechanism for classes that implement the 
`Serializable`
 interface. The developer can either rely on
Java’s default serialization and deserialization logic or implement custom methods for these tasks. The JVM will use methods such as

**Noncompliant code example**

```java
public class Watermelon implements Serializable {

  void writeObject(java.io.ObjectOutputStream out)         // Noncompliant, "writeObject" needs to be private, which it is not here
        throws IOException
  {...}

  static Object readResolve() throws ObjectStreamException // Noncompliant, "readResolve" should not be static
  {...}

  Watermelon writeReplace() throws ObjectStreamException   // Noncompliant, "writeReplace" must return "java.lang.Object"
  {...}
}
```

**Compliant solution**

```java
public class Watermelon implements Serializable {

  private void writeObject(java.io.ObjectOutputStream out)    // Compliant, method declared as private
        throws IOException
  {...}

  protected Object readResolve() throws ObjectStreamException // Compliant, method is not static
  {...}

  private Object writeReplace() throws ObjectStreamException  // Compliant, method returns "java.lang.Object"
  {...}
}
```

---

---

---

---

### java:S106 — Standard outputs should not be used directly to log anything

**Severity**: Medium

In software development, logs serve as a record of events within an application, providing crucial insights for debugging. When logging, it is
essential to ensure that the logs are:

---

---

---

---

### java:S107 — Methods should not have too many parameters

**Severity**: Medium

Methods with a long parameter list are difficult to use because maintainers must figure out the role of each parameter and keep track of their
position.

---

---

---

---

### java:S108 — Nested blocks of code should not be left empty

**Severity**: Medium

An empty code block is confusing. It will require some effort from maintainers to determine if it is intentional or indicates the implementation is
incomplete.

```

for (int i = 0; i < 42; i++){}  // Noncompliant: is the block empty on purpose, or is code missing?

```

Removing or filling the empty code blocks takes away ambiguity and generally results in a more straightforward and less surprising code.

Exceptions

The rule ignores code blocks that contain comments unless they are 
`synchronized`
 blocks because these can affect program flow.

---

---

---

---

### java:S2060 — "Externalizable" classes should have no-arguments constructors

**Severity**: Medium

A class that implements 
`java.io.Externalizable`
 is a class that provides a way to customize the serialization and deserialization,
allowing greater control over how the object’s state is written or read.

**Noncompliant code example**

```java
public class Tomato implements Externalizable {

  public Color color;

  // Noncompliant; because of this constructor there is no implicit no-argument constructor,
  // deserialization will fail
  public Tomato(Color color) {
    this.color = color;
  }

  @Override
  public void writeExternal(ObjectOutput out) throws IOException {
    out.writeUTF(color.name());
  }

  @Override
  public void readExternal(ObjectInput in) throws IOException {
    color = Color.valueOf(in.readUTF());
  }
}
```

**Compliant solution**

```java
public class Tomato implements Externalizable {

  public Color color;

  // Compliant; deserialization will invoke this public no-argument constructor
  public Tomato() {
    this.color = Color.UNKNOWN;
  }

  public Tomato(Color color) {
    this.color = color;
  }

  @Override
  public void writeExternal(ObjectOutput out) throws IOException {
    out.writeUTF(color.name());
  }

  @Override
  public void readExternal(ObjectInput in) throws IOException {
    color = Color.valueOf(in.readUTF());
  }
}
```

---

---

---

---

### java:S3042 — "writeObject" should not be the only "synchronized" code in a class

**Severity**: Medium

Synchronization is a mechanism used when multithreading in Java to ensure that only one thread executes a given block of code at a time. This is
done to avoid bugs that can occur when multiple threads share a given state and try to manipulate simultaneously.

Object serialization is not thread-safe by default. In a multithreaded environment, one option is to mark 
`writeObject`
 with

`synchronized`
 to improve thread safety. It is highly suspicious, however, if 
`writeObject`
 is the only

`synchronized`
 method in a class. It may indicate that serialization is not required, as multithreading is not used. Alternatively, it
could also suggest that other methods in the same class have been forgotten to be made thread-safe.

**Noncompliant code example**

```java
public class RubberBall implements Serializable {

  private Color color;
  private int diameter;

  public RubberBall(Color color, int diameter) {
    // ...
  }

  public void bounce(float angle, float velocity) {
    // ...
  }

  private synchronized void writeObject(ObjectOutputStream stream) throws IOException { // Noncompliant, "writeObject" is the only synchronized method in this class
    // ...
  }
}
```

**Compliant solution**

```java
public class RubberBall implements Serializable {

  private Color color;
  private int diameter;

  public RubberBall(Color color, int diameter) {
    // ...
  }

  public void bounce(float angle, float velocity) {
    // ...
  }

  private void writeObject(ObjectOutputStream stream) throws IOException { // Compliant, no methods in this class are synchronized
    // ...
  }
}
```

---

---

---

---

### java:S2166 — Classes named like "Exception" should extend "Exception" or a subclass

**Severity**: Medium

Clear, communicative naming is important in code. It helps maintainers and API users understand the intentions for and uses of a unit of code.
Using "exception" in the name of a class that does not extend 
`Exception`
 or one of its subclasses is a clear violation of the expectation
that a class' name will indicate what it is and/or does.

---

---

---

---

### java:S4348 — "iterator" should not return "this"

**Severity**: Medium

An 
`Iterable`
 should not implement the 
`Iterator`
 interface or return 
`this`
 as an 
`Iterator`
. The
reason is that 
`Iterator`
 represents the iteration process itself, while 
`Iterable`
 represents the object we want to iterate
over.

**Noncompliant code example**

```java
class FooIterator implements Iterator<Foo>, Iterable<Foo> {
  private Foo[] seq;
  private int idx = 0;

  public boolean hasNext() {
    return idx < seq.length;
  }

  public Foo next() {
    return seq[idx++];
  }

  public Iterator<Foo> iterator() {
    return this; // Noncompliant
  }
  // ...
}
```

**Compliant solution**

```java
class FooSequence implements Iterable<Foo> {
  private Foo[] seq;

  public Iterator<Foo> iterator() {
    return new Iterator<Foo>() { // Compliant
      private int idx = 0;

      public boolean hasNext() {
        return idx < seq.length;
      }

      public Foo next() {
        return seq[idx++];
      }
    };
  }
  // ...
}
```

---

---

---

---

### java:S3011 — Reflection should not be used to increase accessibility of classes, methods, or fields

**Severity**: Medium

Altering or bypassing the accessibility of classes, methods, or fields through reflection violates the encapsulation principle. This can break the
internal contracts of the accessed target and lead to maintainability issues and runtime errors.

This rule raises an issue when reflection is used to change the visibility of a class, method or field, and when it is used to directly update a
field value.

```

public void makeItPublic(String methodName) throws NoSuchMethodException {

  this.getClass().getMethod(methodName).setAccessible(true); // Noncompliant
}

public void setItAnyway(String fieldName, int value) {
  this.getClass().getDeclaredField(fieldName).setInt(this, value); // Noncompliant; bypasses controls in setter
}

```

---

---

---

---

### java:S6885 — Use built-in "Math.clamp" methods

**Severity**: Medium

In Java 21 the 
`java.lang.Math`
 class was updated with the static method 
`Math.clamp`
, to clamp a numerical value between a
min and a max value.

Using this built-in method is now the preferred way to restrict to a given interval, as it is more readable and less error-prone.

**Noncompliant code example**

```java
int clampedValue = value > max ? max : value < min ? min : value; // Noncompliant; Replace with "Math.clamp"
```

**Compliant solution**

```java
int clampedValue = Math.max(min, Math.min(max, value)); // Noncompliant; Replace with "Math.clamp"
```

---

---

---

---

### java:S3010 — Static fields should not be updated in constructors

**Severity**: Medium

Assigning a value to a 
`static`
 field in a constructor could cause unreliable behavior at runtime since it will change the value for all
instances of the class.

Instead remove the field’s 
`static`
 modifier, or initialize it statically.

Noncompliant code example

```

public class Person {
  static Date dateOfBirth;
  static int expectedFingers;

  public Person(date birthday) {
    dateOfBirth = birthday;  // Noncompliant; now everyone has this birthday
    expectedFingers = 10;  // Noncompliant
  }
}

```

Compliant solution

```

public class Person {
  Date dateOfBirth;
  static int expectedFingers = 10;

  public Person(date birthday) {
    dateOfBirth = birthday;
  }
}

```

---

---

---

---

### java:S6880 — Use switch instead of if-else chain to compare a variable against multiple cases

**Severity**: Medium

Comparing a variable to multiple cases is a frequent operation. This can be done using a sequence of if-else statements. However, for many cases
like enums or simple value comparisons, a 
`switch`
 statement is the better alternative. With Java 21, the 
`switch`
 statement has
been significantly improved to support pattern matching and record pattern.

Using a 
`switch`
 statement instead of an if-else chain provides benefits like clearer code, certainty of covering all cases, and may
even improve performance.

This rule raises an issue when an if-else chain should be replaced by a 
`switch`
 statement.

**Noncompliant code example**

```java
sealed interface Expression {}
record Plus(Expression left, Expression right) implements Expression {}
record Minus(Expression left, Expression right) implements Expression {}
record Div(Expression left, Expression right) implements Expression {}

int eval(Expression expr){
  if(expr instanceof Plus plus){ // Noncompliant; should be replaced by a switch expression
    return eval(plus.left) + eval(plus.right);
  }else if(expr instanceof Div div){
    return eval(div.left) / eval(div.right);
  }else if(expr instanceof Minus minus){
    return eval(minus.left) - eval(minus.right);
  } else {
    throw new IllegalArgumentException("Unknown expression");
  }
}
```

**Compliant solution**

```java
enum Color{RED,GREEN,YELLOW}

String name(Color c){
  if(c == Color.RED){ // Noncompliant; should be replaced by a switch expression
    return "red";
  }else if(c == Color.GREEN){
    return "green";
  }else if(c == Color.YELLOW){
    return "yellow";
  }else{
    throw new IllegalArgumentException("Unknown color");
  }
}
```

---

---

---

---

### java:S1193 — Exception types should not be tested using "instanceof" in catch blocks

**Severity**: Medium

A 
`try-catch`
 block is used to handle exceptions or errors that may occur during the execution of a block of code. It allows you to
catch and handle exceptions gracefully, preventing your program from terminating abruptly.

The code that may throw an exception is enclosed within the 
`try`
 block, while each 
`catch`
 block specifies the type of
exception it can handle. The corresponding catch block is executed if the exception matches the type specified in any catch block. It is unnecessary
to manually check the types using 
`instanceof`
 because Java automatically matches the exception type to the appropriate catch block based
on the declared exception type in the catch clauses.

**Noncompliant code example**

```java
try {
  /* ... */
} catch (Exception e) {
  if(e instanceof IOException) { /* ... */ }         // Noncompliant
  if(e instanceof NullPointerException{ /* ... */ }  // Noncompliant
}
```

**Compliant solution**

```java
try {
  /* ... */
} catch (IOException e) { /* ... */ }                // Compliant
} catch (NullPointerException e) { /* ... */ }       // Compliant
```

---

---

---

---

### java:S2177 — Child class methods named for parent class methods should be overrides

**Severity**: Medium

When a method in a child class has the same signature as a method in a parent class, it is assumed to be an override. However, that’s not the case
when:

---

---

---

---

### java:S2175 — Inappropriate "Collection" calls should not be made

**Severity**: Medium

The 
`java.util.Collection`
 type and its subtypes provide methods to access and modify collections such as 
`Collection.remove(Object
o)`
 and 
`Collection.contains(Object o)`
. Some of these methods accept arguments of type 
`java.lang.Object`
 and will
compare said argument with objects already in the collection.

**Noncompliant code example**

```java
void removeFromMap(Map<Integer, Object> map, String strKey) {
  map.remove(strKey); // Noncompliant, this call will remove nothing and always return 'null' because 'map' is handling only Integer keys and String cannot be cast to Integer.
}

void listContains(List<String> list, Integer integer) {
  if (list.contains(integer)) { // Noncompliant; always false as the list only contains Strings, not integers.
    // ...
  }
}
```

**Compliant solution**

```java
void removeFromMap(Map<Integer, Object> map, String strKey) {
  map.remove(Integer.parseInt(strKey)); // Compliant, strKey is parsed into an Integer before trying to remove it from the map.
}

void listContains(List<String> list, Integer integer) {
  if (list.contains(integer.toString())) { // Compliant, 'integer' is converted to a String before checking if the list contains it.
    // ...
  }
}
```

---

---

---

---

### java:S5329 — Collection constructors should not be used as java.util.function.Function

**Severity**: Medium

It is very common to pass a collection constructor reference as an argument, for example 
`Collectors.toCollection(ArrayList::new)`
 takes
the 
`ArrayList::new`
 constructor. When the method expects a 
`java.util.function.Supplier`
 it is perfectly fine. However when the
method argument type is 
`java.util.function.Function`
 it means that an argument will be passed to the constructor.

---

---

---

---

### java:S4351 — "compareTo" should not be overloaded

**Severity**: Medium

When implementing the 
`Comparable<T>.compareTo`
 method, the parameter’s type has to match the type used in the

---

---

---

---

### java:S3078 — "volatile" variables should not be used with compound operators

**Severity**: Medium

Using compound operators as well as increments and decrements (and toggling, in the case of 
`boolean`
s) on primitive fields are not
atomic operations. That is, they don’t happen in a single step. For instance, when a 
`volatile`
 primitive field is incremented or
decremented you run the risk of data loss if threads interleave in the steps of the update. Instead, use a guaranteed-atomic class such as

---

---

---

---

### java:S4042 — "java.nio.Files#delete" should be preferred

**Severity**: Medium

When 
`java.io.File#delete`
 fails, this 
`boolean`
 method simply returns 
`false`
 with no indication of the cause. On
the other hand, when 
`java.nio.file.Files#delete`
 fails, this 
`void`
 method returns one of a series of exception types to better
indicate the cause of the failure. And since more information is generally better in a debugging situation, 
`java.nio.file.Files#delete`
 is
the preferred option.

Noncompliant code example

```

public void cleanUp(Path path) {
  File file = new File(path);
  if (!file.delete()) {  // Noncompliant
    //...
  }
}

```

Compliant solution

```

public void cleanUp(Path path) throws NoSuchFileException, DirectoryNotEmptyException, IOException {
  Files.delete(path);
}

```

---

---

---

---

### java:S4165 — Assignments should not be redundant

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

---

---

---

### java:S6103 — AssertJ assertions with "Consumer" arguments should contain assertion inside consumers

**Severity**: Medium

AssertJ assertions taking 
`Consumer`
 objects as arguments are expected to contain "requirements", which should themselves be expressed
as assertions. This concerns the following methods: 
[allSatisfy](http://joel-costigliola.github.io/assertj/core-8/api/org/assertj/core/api/AbstractIterableAssert.html#allSatisfy-java.util.function.Consumer-)
,

---

---

---

---

### java:S6355 — Deprecated annotations should include explanations

**Severity**: Medium

Since Java 9, 
`@Deprecated`
 has two additional arguments to the annotation:

 
`since`
 allows you to describe when the deprecation took place 

 
`forRemoval`
, indicates whether the deprecated element will be removed at some future date 

In order to ease the maintainers work, it is recommended to always add one or both of these arguments.

This rule reports an issue when 
`@Deprecated`
 is used without any argument.

Noncompliant code example

```

@Deprecated

```

Compliant solution

```

@Deprecated(since="4.2", forRemoval=true)

```

Exceptions

The members and methods of a deprecated class or interface are ignored by this rule. The classes and interfaces themselves are still subject to
it.

---

---

---

---

### java:S4144 — Methods should not have identical implementations

**Severity**: Medium

Two methods having the same implementation are suspicious. It might be that something else was intended. Or the duplication is intentional, which
becomes a maintenance burden.

---

---

---

---

### java:S5261 — "else" statements should be clearly matched with an "if"

**Severity**: Medium

The dangling 
`else`
 problem appears when nested 
`if`
/
`else`
 statements are written without curly braces. In
this case, 
`else`
 is associated with the nearest 
`if`
 but that is not always obvious and sometimes the indentation can also
be misleading.

---

---

---

---

### java:S6202 — Operator "instanceof" should be used instead of "A.class.isInstance()"

**Severity**: Medium

The 
`instanceof`
 construction is a preferred way to check whether a variable can be cast to some type statically because a compile-time
error will occur in case of incompatible types. The method 
[isInstance()](https://docs.oracle.com/javase/8/docs/api/java/lang/Class.html#isInstance-java.lang.Object-)
 from 
`java.lang.Class`

---

---

---

---

### java:S6206 — Records should be used instead of ordinary classes when representing immutable data structure

**Severity**: Medium

In Java 16 
`records`
 are finalized and can be safely used in production code. 
`Records`
 represent immutable read-only data
structure and should be used instead of creating immutable classes. Immutability of records is guaranteed by the Java language itself, while
implementing immutable classes on your own might lead to some bugs.

---

---

---

---

### java:S6207 — Redundant constructors/methods should be avoided in records

**Severity**: Medium

In Java 16 records represent a brief notation for immutable data structures. Records have autogenerated implementations for constructors with all
parameters, 
`getters`
, 
`equals`
, 
`hashcode`
 and 
`toString`
. Although these methods can still be overridden
inside records, there is no use to do so if no special logic is required.

---

---

---

---

### java:S6326 — Regular expressions should not contain multiple spaces

**Severity**: Medium

Multiple spaces in a regular expression can make it hard to tell how many spaces should be matched. It’s more readable to use only one space and
then indicate with a quantifier how many spaces are expected.

Noncompliant code example

```

Pattern.compile("hello   world");

```

Compliant solution

```

Pattern.compile("hello {3}world");

```

Exceptions

In 
[free-spacing mode](https://www.regular-expressions.info/freespacing.html)
 (
`Pattern.COMMENTS`
 flag, or with embedded flag
expression 
`(?x)`
), whitespaces are ignored. In this case no issue should be triggered, because the whitespaces may be intended to improve
readability.

---

---

---

---

### java:S6204 — "Stream.toList()" method should be used instead of "collectors" when unmodifiable list needed

**Severity**: Medium

In Java 8 
`Streams`
 were introduced to support chaining of operations over collections in a functional style. The most common way to
save a result of such chains is to save them to some collection (usually 
`List`
). To do so there is a terminal method 
`collect`

---

---

---

---

### java:S4143 — Map values should not be replaced unconditionally

**Severity**: Medium

Storing a value inside a collection at a given key or index and then unconditionally overwriting it without reading the initial value is a case of
a "dead store".

```

letters.put("a", "Apple");
letters.put("a", "Boy");  // Noncompliant

towns[i] = "London";
towns[i] = "Chicago";  // Noncompliant

```

This practice is redundant and will cause confusion for the reader. More importantly, it is often an error and not what the developer intended to
do.

---

---

---

---

### java:S6213 — Restricted Identifiers should not be used as Identifiers

**Severity**: Medium

Even if it is technically possible, 
[Restricted Identifiers](https://docs.oracle.com/javase/specs/jls/se16/html/jls-3.html#jls-3.8)

---

---

---

---

### java:S6216 — Reflection should not be used to increase accessibility of records' fields

**Severity**: Medium

In general, altering or bypassing the accessibility of classes, methods, or fields violates the encapsulation principle and could lead to runtime
errors. For records the case is even trickier: you cannot change the visibility of records’s fields and trying to update the existing value will lead
to 
`IllegalAccessException`
 at runtime.

This rule raises an issue when reflection is used to change the visibility of a record’s field, and when it is used to directly update a record’s
field value.

Noncompliant code example

```

record Person(String name, int age) {}

Person person = new Person("A", 26);
Field field = Person.class.getDeclaredField("name");
field.setAccessible(true); // secondary
field.set(person, "B"); // Noncompliant

```

---

## 11. Reliability & Bug Prevention Rules — Medium (30 rules)

---

---

---

### java:S6218 — Equals method should be overridden in records containing array fields

**Severity**: Medium

In records, the default behavior of the 
`equals()`
 method is to check the equality by field values. This works well for primitive fields
or fields, whose type overrides 
`equals()`
, but this behavior doesn’t work as expected for array fields.

---

---

---

---

### java:S3064 — Assignment of lazy-initialized members should be the last step with double-checked locking

**Severity**: Medium

Double-checked locking can be used for lazy initialization of 
`volatile`
 fields, but only if field assignment is the last step in the

---

## 12. Spring Framework Rules — Medium (17 rules)

---

---

---

### java:S3065 — Min and max used in combination should not always return the same value

**Severity**: Medium

When using 
`Math.min()`
 and 
`Math.max()`
 together for bounds checking, it’s important to feed the right operands to each
method. 
`Math.min()`
 should be used with the 
upper
 end of the range being checked, and 
`Math.max()`
 should be
used with the 
lower
 end of the range. Get it backwards, and the result will always be the same end of the range.

---

---

---

---

### java:S3067 — "getClass" should not be used for synchronization

**Severity**: Medium

`getClass`
 should not be used for synchronization in non-
`final`
 classes because child classes will synchronize on a
different object than the parent or each other, allowing multiple threads into the code block at once, despite the 
`synchronized`

keyword.

Instead, hard code the name of the class on which to synchronize or make the class 
`final`
.

Noncompliant code example

```

public class MyClass {
  public void doSomethingSynchronized(){
    synchronized (this.getClass()) {  // Noncompliant
      // ...
    }
  }

```

Compliant solution

```

public class MyClass {
  public void doSomethingSynchronized(){
    synchronized (MyClass.class) {
      // ...
    }
  }

```

---

---

---

---

### java:S4274 — Asserts should not be used to check the parameters of a public method

**Severity**: Medium

An 
`assert`
 is inappropriate for parameter validation because assertions can be disabled at runtime in the JVM, meaning that a bad
operational setting would completely eliminate the intended checks. Further, 
`assert`
s that fail throw 
`AssertionError`
s, rather
than throwing some type of 
`Exception`
. Throwing 
`Error`
s is completely outside of the normal realm of expected

---

## 14. Code Quality & Maintainability Rules — Medium (160 rules)

---

---

---

### java:S6331 — Regular expressions should not contain empty groups

**Severity**: Medium

There are several reasons to use a group in a regular expression:

 to change the precedence (e.g. 
`do(g|or)`
 will match 'dog' and 'door') 

 to remember parenthesised part of the match in the case of capturing group 

 to improve readability 

In any case, having an empty group is most probably a mistake. Either it is a leftover after refactoring and should be removed, or the actual
parentheses were intended and were not escaped.

Noncompliant code example

```

"foo()"  // Noncompliant, will match only 'foo'

```

Compliant solution

```

"foo\\(\\)"  // Matches 'foo()'

```

---

---

---

---
