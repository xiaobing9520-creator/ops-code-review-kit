---
name: codebase-reverse-engineering
description: >
  Performs deterministic reverse engineering analysis of an existing codebase
  before code review. Use as the FIRST step before running any review skill.
  Generates architecture docs, API inventory, dependency map, technology stack,
  and code quality baseline. Designed for reproducible output: same code + same
  skill + same model = same architecture output.
---

# Codebase Reverse Engineering (v1.7 — Deterministic)

You are a senior software architect performing comprehensive reverse engineering
of a codebase. Your goal is to deeply understand the system before any code
review begins, producing structured artifacts that downstream review skills
will reference.

## IMPORTANT: Run This Skill FIRST

This skill MUST be executed before any of the following review skills:
- security-review
- secure-coding-baseline-review
- sonarqube-review
- batch-scan
- acceptance-report

The artifacts generated here provide the foundation for all subsequent reviews.

## Output Directory

All artifacts are saved to `code-review-artifacts/reverse-engineering/` in the
project root.

---

## DETERMINISM RULES (v1.7)

These rules ensure that running this skill on the SAME codebase produces the
SAME output regardless of when or how many times it is run.

### D1: Canonical File Discovery Order

All file discovery MUST use explicit, sorted listings:
- Use `find . -type f | sort` (or language equivalent) for all directory scans
- NEVER rely on raw filesystem order (readdir, glob without sort)
- When listing directories: always `ls -1 | sort` or equivalent
- Result: every file list in every artifact is alphabetically sorted

### D2: Deterministic Read Order

Files MUST be read in the following fixed priority order:
1. Build config files (pom.xml, build.gradle, package.json, go.mod, Cargo.toml,
   pyproject.toml) — sorted alphabetically by path
2. Entry points (main.*, index.*, app.*, Application.*, server.*, handler.*) —
   sorted alphabetically by path
3. Configuration files (application.yml, .env.example, config/*) — sorted
   alphabetically by path
4. API definitions (OpenAPI, GraphQL schemas, proto files, route files) —
   sorted alphabetically by path
5. Infrastructure files (Dockerfile, *.tf, docker-compose.yml, CI configs) —
   sorted alphabetically by path
6. Source files by module — modules sorted alphabetically, files within each
   module sorted alphabetically by path

Within each priority group, always process files in **alphabetical path order**.

### D3: Explicit Scope Boundaries

**ALWAYS include** (if they exist):
- All files matching the build config patterns above
- All files in `src/main/` or equivalent source root
- All files defining public APIs (controllers, routes, handlers, resolvers)
- All configuration and property files

**NEVER include** (even if present):
- `node_modules/`, `vendor/`, `.gradle/`, `target/`, `build/`, `dist/`, `out/`
- `.git/` contents
- Binary files (images, compiled artifacts, archives)
- Lock files contents (package-lock.json, yarn.lock, pnpm-lock.yaml, go.sum) —
  note their EXISTENCE but do not parse contents
- Generated code directories (if clearly marked as generated)
- Test fixture data files (large JSON/XML test data)

### D4: Deterministic Table Ordering

ALL tables in ALL output artifacts MUST be sorted by a defined key:

| Table Type | Sort Key | Direction |
|-----------|----------|-----------|
| Component Catalog | Component/package name | A→Z |
| Dependency tables | Dependency name | A→Z |
| Framework/library tables | Library name | A→Z |
| API endpoint tables | HTTP method + path (REST), operation name (GraphQL/gRPC) | A→Z |
| Infrastructure services | Service name | A→Z |
| Business transactions | Transaction name | A→Z |
| Design patterns | Pattern name | A→Z |
| Metrics tables | Metric name | A→Z |

### D5: Factual Content Only — No Subjective Assessments

**PROHIBITED in output artifacts**:
- Subjective quality judgments ("well-structured", "could be improved", "notable")
- Ranked "key findings" or "top observations" (ordering is subjective)
- Recommendations or suggestions (that's for review skills, not reverse engineering)
- Comparative statements ("more than expected", "unusual amount of")
- Future-looking statements ("should consider", "would benefit from")

**REQUIRED instead**:
- State facts: counts, names, versions, paths, relationships
- Use "Present / Absent / Not Found" — not quality adjectives
- List ALL findings in sorted order rather than selecting "top N"

### D6: Fixed Template Completion Rules

For every template field:
- If the information EXISTS in the code: extract it verbatim or compute it
  deterministically (counts, sorted lists)
- If the information DOES NOT EXIST: write exactly `Not Found — [reason]`
- NEVER paraphrase differently across runs — use the exact field labels from
  the templates below
- NEVER add extra sections beyond what the template defines
- NEVER omit template sections — mark as "Not Found" or "N/A" if empty

### D7: No Context Leakage

- Do NOT reference previous runs, prior artifacts, or cached results
- Do NOT let conversation context influence output — only the source code matters
- If `code-review-artifacts/reverse-engineering/` already exists, overwrite it
  completely (do not merge with previous output)
- Each run is independent and self-contained

---

## General Rules

- If information for a section cannot be determined or does not exist, mark it
  as **"Not Found — [specific reason]"**. Never guess or fabricate content.
- Use cross-references (`See [architecture.md](architecture.md)`) instead of
  duplicating information across artifacts.
- Adapt depth of analysis to codebase scale (see Step 0), but apply the same
  DETERMINISM RULES at every scale.

---

## Reverse Engineering Process

### Step 0: Scale Assessment & Scope Definition

#### 0.1 Scale Assessment (Deterministic)

Run a file count to classify the codebase:

```bash
# Count source files (exclude node_modules, vendor, .git, build, dist, target, out)
find . -type f \
  -not -path '*/node_modules/*' \
  -not -path '*/vendor/*' \
  -not -path '*/.git/*' \
  -not -path '*/build/*' \
  -not -path '*/dist/*' \
  -not -path '*/target/*' \
  -not -path '*/out/*' \
  -not -path '*/.gradle/*' \
  -name '*.java' -o -name '*.js' -o -name '*.ts' -o -name '*.jsx' -o \
  -name '*.tsx' -o -name '*.py' -o -name '*.go' -o -name '*.rs' -o \
  -name '*.kt' -o -name '*.scala' -o -name '*.rb' -o -name '*.cs' -o \
  -name '*.php' -o -name '*.swift' -o -name '*.c' -o -name '*.cpp' -o \
  -name '*.h' | sort | wc -l
```

| Scale | File Count | Scope |
|-------|-----------|-------|
| **Small** | < 50 source files | Read ALL source files |
| **Medium** | 50–500 source files | Read all files in priority groups D2.1–D2.5, plus all public API source files; sample internal implementation (first file alphabetically per package) |
| **Large** | > 500 source files | Read all files in priority groups D2.1–D2.5; for source (D2.6), read only entry points, controllers, service layer entry classes (first 3 files alphabetically per package) |

The scale classification determines which files are read, NOT how they are
reported. Output artifact structure is identical at all scales.

#### 0.2 File Manifest (Required)

Before any analysis, produce a sorted file manifest:

```bash
find . -type f \
  -not -path '*/node_modules/*' \
  -not -path '*/vendor/*' \
  -not -path '*/.git/*' \
  -not -path '*/build/*' \
  -not -path '*/dist/*' \
  -not -path '*/target/*' \
  -not -path '*/out/*' \
  -not -path '*/.gradle/*' \
  | sort
```

This manifest is the CANONICAL source for all file references in the output.
Only files in this manifest may appear in the artifacts.

#### 0.3 Module Discovery (Deterministic)

Detect modules using this fixed priority chain (stop at first match):

1. **Maven**: Parse `<modules>` in root `pom.xml` → sort alphabetically
2. **Gradle**: Parse `include` in `settings.gradle(.kts)` → sort alphabetically
3. **npm/pnpm/yarn workspaces**: Parse `workspaces` in root `package.json` → sort alphabetically
4. **Nx/Turborepo/Lerna**: Parse workspace config → sort alphabetically
5. **Go workspace**: Parse `go.work` → sort alphabetically
6. **Directory heuristic**: Subdirectories with their own build file → sort alphabetically

The module list is FIXED after this step. All subsequent per-module processing
uses this exact sorted list.

---

### Step 1: Structured Discovery (Fixed Order)

Process the following in EXACT sequence. Do not skip steps. Do not reorder.

#### 1.1 Build System Identification

For each module (in alphabetical order):
1. Read the build config file (pom.xml / build.gradle / package.json / etc.)
2. Extract: group/artifact ID, version, declared dependencies, plugins
3. Record build system type and version

#### 1.2 Language & Framework Detection

From build configs and file extensions (using the sorted file manifest):
1. Count files per extension → determine primary/secondary languages
2. Extract framework declarations from dependencies (Spring Boot, Express,
   React, Django, FastAPI, Gin, etc.)
3. Extract framework versions from config/lock files

#### 1.3 Entry Point Identification

Search in this fixed order:
1. `**/src/main/**/Application.java` or `**/*Application.java`
2. `**/src/main/**/Main.java` or `**/main.go` or `**/cmd/*/main.go`
3. `**/index.ts` or `**/index.js` or `**/main.ts` or `**/main.js`
4. `**/app.py` or `**/main.py` or `**/manage.py`
5. `**/src/main.rs` or `**/src/lib.rs`
6. Custom entry points declared in build configs (`mainClass`, `entry`, `bin`)

Sort results alphabetically. These are the confirmed entry points.

#### 1.4 API Surface Discovery

Search in this fixed order (sort results alphabetically):
1. OpenAPI/Swagger: `**/*swagger*`, `**/*openapi*`, `**/api-docs*`
2. GraphQL: `**/*.graphql`, `**/*.gql`, `**/schema.*`
3. gRPC/Protobuf: `**/*.proto`
4. REST Controllers: `**/*Controller.*`, `**/*Resource.*`, `**/routes/*`,
   `**/router.*`, `**/*Handler.*`
5. Route registrations: grep for `@RequestMapping`, `@GetMapping`,
   `@PostMapping`, `router.get`, `app.get`, `@app.route`, etc.

#### 1.5 Infrastructure Discovery

Search in this fixed order (sort results alphabetically):
1. Containers: `**/Dockerfile*`, `**/docker-compose*`
2. IaC: `**/*.tf`, `**/cdk.json`, `**/template.yaml`, `**/serverless.yml`
3. CI/CD: `**/.github/workflows/*`, `**/Jenkinsfile`, `**/.gitlab-ci.yml`,
   `**/buildspec.yml`, `**/*.pipeline.*`
4. K8s: `**/k8s/**`, `**/kubernetes/**`, `**/helm/**`, `**/*deployment*`,
   `**/*service.yaml`

#### 1.6 Data Store & Integration Discovery

Search in this fixed order (sort results alphabetically):
1. Database configs: connection strings, ORM configs, migration directories
2. Cache configs: Redis, Memcached, Hazelcast configurations
3. Message systems: Kafka, RabbitMQ, SQS/SNS, EventBridge configs
4. External service clients: HTTP clients, SDK initializations, API keys

---

### Step 2: Generate Business Overview

Create `code-review-artifacts/reverse-engineering/business-overview.md`:

```markdown
# Business Overview

**Generated by**: @codebase-reverse-engineering v1.7
**Codebase Scale**: [Small / Medium / Large] ([N] source files)

## System Purpose

[Single paragraph: what this system does. Derived from README, build config
descriptions, and entry point analysis. State only what the code proves.]

## Modules

| # | Module Name | Path | Type | Primary Language |
|---|-------------|------|------|-----------------|
| 1 | [name] | [path] | [Application/Library/Infrastructure/Shared] | [lang] |

(Sorted alphabetically by Module Name)

## Business Transactions

| # | Transaction Name | Description | Entry Point | Modules Involved |
|---|-----------------|-------------|-------------|-----------------|
| 1 | [name] | [what it does] | [file:class/function] | [module list] |

(Sorted alphabetically by Transaction Name)

## Domain Terminology

| Term | Definition | Source |
|------|-----------|--------|
| [term] | [definition] | [file where found] |

(Sorted alphabetically by Term)
```

---

### Step 3: Generate Architecture Documentation

Create `code-review-artifacts/reverse-engineering/architecture.md`:

```markdown
# System Architecture

**Generated by**: @codebase-reverse-engineering v1.7

## System Overview

[1–3 factual sentences describing the system type and deployment model.
No quality judgments.]

## Architecture Pattern

**Pattern**: [Monolith / Microservices / Serverless / Modular Monolith / Hybrid]
**Evidence**: [file path(s) proving this classification]

## Component Catalog

(Sorted alphabetically by Component Name)

### [Component Name]

- **Path**: `[exact path]`
- **Type**: Application / Infrastructure / Library / Shared / Test
- **Purpose**: [1 sentence — what it does]
- **Primary Language**: [language]
- **Framework**: [framework and version, or "None"]
- **Entry Point**: `[file path]`
- **Internal Dependencies**: [sorted list of other components, or "None"]
- **External Dependencies**: [sorted list of external services consumed, or "None"]

## Data Flow

(For each data flow, sorted alphabetically by flow name)

### [Flow Name]

```
[Component A] → [protocol/mechanism] → [Component B] → ... → [Component N]
```

- **Trigger**: [what initiates this flow]
- **Data**: [what data moves]

## Integration Points

### External APIs Consumed

| Service Name | Protocol | Config Location |
|-------------|----------|----------------|
| [name] | [REST/gRPC/SOAP/SDK] | [file path] |

(Sorted alphabetically by Service Name)

### Databases

| Name/Identifier | Type | Config Location |
|----------------|------|----------------|
| [name] | [PostgreSQL/MySQL/MongoDB/DynamoDB/...] | [file path] |

(Sorted alphabetically by Name)

### Message Systems

| Name/Identifier | Type | Config Location | Role |
|----------------|------|----------------|------|
| [name] | [Kafka/RabbitMQ/SQS/...] | [file path] | [Producer/Consumer/Both] |

(Sorted alphabetically by Name)

### Cache Systems

| Name/Identifier | Type | Config Location |
|----------------|------|----------------|
| [name] | [Redis/Memcached/...] | [file path] |

(Sorted alphabetically by Name)

## Infrastructure

- **IaC Approach**: [CDK / Terraform / CloudFormation / Pulumi / None]
- **IaC Location**: `[path]`
- **Deployment Model**: [Containers / Serverless / VMs / Hybrid]
- **Container Runtime**: [Docker / Podman / None]
- **Orchestrator**: [Kubernetes / ECS / Cloud Run / None]
- **CI/CD Tool**: [GitHub Actions / Jenkins / GitLab CI / None]
- **CI/CD Config**: `[path]`
```

#### Architecture Diagrams in Markdown

The `architecture.md` file MUST include Mermaid diagrams in fenced code blocks.
Include the following diagrams (as applicable):

1. **System Overview** — `graph LR` showing all modules/components and their
   connections to shared infrastructure
2. **Microservices Detail** (if applicable) — `graph LR` showing internal
   services grouped by domain
3. **Authentication Flows** (if applicable) — `sequenceDiagram` showing how
   users authenticate and how tokens are validated

Mermaid diagram rules:
- Use `graph LR` for architecture diagrams (left-to-right flow)
- Use `sequenceDiagram` for interaction flows
- Use `subgraph` to group related components
- Label all edges with protocol/mechanism
- Keep node labels concise (component name + 1-line role)
- Sort nodes alphabetically within each subgraph
- Do NOT use emoji characters in Mermaid node labels (breaks some renderers)

---

### Step 3b: Generate Architecture HTML (Diagram Preview)

Create `code-review-artifacts/reverse-engineering/architecture-preview.html`:

This file renders the same Mermaid diagrams from `architecture.md` as visual
graphics in a browser. Users can open it in any browser, then copy/paste or
print-to-PDF for Word documents.

**Template**:

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>[Project Name] — System Architecture</title>
<style>
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    max-width: 1200px;
    margin: 0 auto;
    padding: 40px 20px;
    background: #fff;
    color: #1a1a1a;
    line-height: 1.6;
  }
  h1 { border-bottom: 2px solid #333; padding-bottom: 10px; }
  h2 { border-bottom: 1px solid #ddd; padding-bottom: 6px; margin-top: 40px; }
  h3 { margin-top: 30px; }
  .diagram-container {
    margin: 24px 0;
    padding: 20px;
    background: #fafafa;
    border: 1px solid #e0e0e0;
    border-radius: 6px;
    overflow-x: auto;
  }
  table { border-collapse: collapse; width: 100%; margin: 16px 0; }
  th, td { border: 1px solid #ddd; padding: 8px 12px; text-align: left; }
  th { background: #f5f5f5; }
  code { background: #f0f0f0; padding: 2px 5px; border-radius: 3px; font-size: 0.9em; }
  .export-instructions {
    background: #e8f4fd;
    border: 1px solid #b3d9f2;
    border-radius: 6px;
    padding: 16px;
    margin-bottom: 30px;
  }
  @media print {
    .export-instructions { display: none; }
    body { padding: 0; }
    .diagram-container { break-inside: avoid; }
  }
</style>
</head>
<body>

<div class="export-instructions">
  <strong>Export to Word:</strong> Open in browser → Ctrl+A → Copy → Paste into Word.
  Or use Print → Save as PDF. Diagrams render as images that paste cleanly.
</div>

<h1>[Project Name] — System Architecture</h1>

<!-- Repeat for each diagram in architecture.md -->
<h3>[Diagram Title]</h3>
<p>[Diagram description]</p>
<div class="diagram-container">
<pre class="mermaid">
[Mermaid code from architecture.md — IDENTICAL content]
</pre>
</div>

<!-- Include Component Catalog, Data Flow, Integration Points as HTML -->
<!-- Mirror the content from architecture.md in HTML format -->

<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<script>
  mermaid.initialize({
    startOnLoad: true,
    theme: 'default',
    flowchart: { useMaxWidth: true, htmlLabels: true },
    sequence: { useMaxWidth: true }
  });
</script>
</body>
</html>
```

**Generation rules**:
- The Mermaid code in the HTML MUST be identical to the code in `architecture.md`
  (single source of truth — copy verbatim)
- Convert all other sections from `architecture.md` to semantic HTML (tables,
  lists, headings) so the full architecture document is viewable in the browser
- The HTML file is self-contained except for the Mermaid JS CDN reference
- If the review environment is offline, add a comment noting the user should
  download `mermaid.min.js` locally

---

### Step 4: Generate API & Interface Documentation

Create `code-review-artifacts/reverse-engineering/api-documentation.md`:

```markdown
# API & Interface Documentation

**Generated by**: @codebase-reverse-engineering v1.7

## REST APIs

(Sorted by: HTTP Method alphabetically, then Path alphabetically)

| Method | Path | Handler | Module | Auth Required |
|--------|------|---------|--------|--------------|
| [GET/POST/...] | [/path] | [Class.method or file:function] | [module] | [Yes/No/Unknown] |

## GraphQL Operations

(Sorted alphabetically by Operation Name)

| Type | Operation Name | Resolver Location |
|------|---------------|-------------------|
| [Query/Mutation/Subscription] | [name] | [file:line] |

## gRPC Services

(Sorted alphabetically by Service Name)

| Service | Method | Proto File | Implementation |
|---------|--------|-----------|----------------|
| [service] | [method] | [file path] | [file path] |

## Event Contracts

(Sorted alphabetically by Event Name)

| Event Name | Producer | Consumer(s) | Payload Location |
|-----------|----------|-------------|-----------------|
| [name] | [component] | [component list] | [schema file or class] |

## Key Data Models

(Sorted alphabetically by Model Name)

### [Model Name]

- **Location**: `[file path]`
- **Fields**: [field list with types]
- **Relationships**: [related models]
- **Used By**: [sorted list of modules/components]

## Internal Interfaces (Cross-Module)

(Sorted alphabetically by Interface Name)

| Interface/Class | Defined In | Consumed By |
|----------------|-----------|-------------|
| [name] | [module/path] | [sorted module list] |
```

---

### Step 5: Generate Technology & Dependency Documentation

Create `code-review-artifacts/reverse-engineering/technology-and-dependencies.md`:

```markdown
# Technology & Dependencies

**Generated by**: @codebase-reverse-engineering v1.7

## Programming Languages

(Sorted alphabetically by Language)

| Language | Version | File Count | KLOC | Modules Using |
|----------|---------|-----------|------|---------------|
| [lang] | [ver or "Not specified"] | [n] | [n] | [sorted list] |

## Frameworks & Libraries (Key)

(Sorted alphabetically by Name. Include only: frameworks, major libraries
declared in build configs. Do NOT list transitive dependencies.)

| Name | Version | Category | Modules Using |
|------|---------|----------|---------------|
| [name] | [ver] | [Web/ORM/Security/Testing/Messaging/Logging/...] | [sorted list] |

## Infrastructure Services

(Sorted alphabetically by Service Name)

| Service | Type | Version/Tier | Config Location |
|---------|------|-------------|----------------|
| [name] | [Database/Cache/Queue/Storage/...] | [ver or "Not specified"] | [path] |

## Build Tools

(Sorted alphabetically by Tool Name)

| Tool | Version | Config File |
|------|---------|------------|
| [name] | [ver] | [path] |

## Internal Dependency Graph

(Sorted alphabetically by source module)

| Source Module | Depends On | Dependency Type |
|--------------|-----------|----------------|
| [module A] | [module B] | [Compile / Runtime / Test] |

## External Dependency Count

| Module | Direct Dependencies | Dev Dependencies |
|--------|-------------------|-----------------|
| [module] | [n] | [n] |

(Sorted alphabetically by Module)
```

---

### Step 6: Generate Code Quality Baseline

Create `code-review-artifacts/reverse-engineering/code-quality-baseline.md`:

```markdown
# Code Quality Baseline

**Generated by**: @codebase-reverse-engineering v1.7

## File Metrics

| Metric | Value |
|--------|-------|
| Total source files | [n] |
| Total KLOC (source only) | [n] |
| Total test files | [n] |
| Total config files | [n] |
| Languages | [sorted comma-separated list] |

## Source Files by Language

(Sorted alphabetically by Language)

| Language | Source Files | Test Files | KLOC |
|----------|------------|-----------|------|
| [lang] | [n] | [n] | [n] |

## Source Files by Module

(Sorted alphabetically by Module)

| Module | Source Files | Test Files | KLOC | Primary Language |
|--------|------------|-----------|------|-----------------|
| [module] | [n] | [n] | [n] | [lang] |

## Testing Infrastructure

| Aspect | Status | Details |
|--------|--------|---------|
| Unit test framework | Present / Not Found | [framework name and config path] |
| Integration tests | Present / Not Found | [directory or config path] |
| E2E tests | Present / Not Found | [directory or config path] |
| Coverage config | Present / Not Found | [config file path] |
| Coverage reports | Present / Not Found | [report location] |

## Code Quality Tooling

| Tool Type | Status | Tool Name | Config Path |
|-----------|--------|-----------|------------|
| Linting | Present / Not Found | [name] | [path] |
| Formatting | Present / Not Found | [name] | [path] |
| Type checking | Present / Not Found | [name] | [path] |
| Static analysis | Present / Not Found | [name] | [path] |
| Dependency scanning | Present / Not Found | [name] | [path] |

## Design Patterns Identified

(Sorted alphabetically by Pattern Name. Only list patterns with concrete evidence.)

| Pattern | Location(s) | Evidence |
|---------|------------|----------|
| [pattern name] | [sorted file paths] | [specific class/annotation/structure proving it] |
```

---

### Step 7: Generate Analysis Summary

Create `code-review-artifacts/reverse-engineering/analysis-summary.md`:

```markdown
# Reverse Engineering Analysis Summary

**Generated by**: @codebase-reverse-engineering v1.7
**Analysis Date**: [YYYY-MM-DD]
**Workspace**: [project root path]
**Codebase Scale**: [Small / Medium / Large] ([N] source files)

## Artifacts Generated

- [x] business-overview.md
- [x] architecture.md
- [x] architecture-preview.html (diagrams rendered in browser)
- [x] api-documentation.md
- [x] technology-and-dependencies.md
- [x] code-quality-baseline.md

## Codebase Facts

| Fact | Value |
|------|-------|
| Modules | [n] |
| Total source files | [n] |
| Total KLOC | [n] |
| Primary language | [lang] |
| Primary framework | [framework] |
| Architecture pattern | [pattern] |
| Deployment model | [model] |
| API endpoints (total) | [n] |
| External integrations | [n] |
| Database systems | [n] |

## Review Scope Indicators

(These facts help downstream review skills determine what to focus on.
Sorted alphabetically by category.)

| Category | Applicable | Evidence |
|----------|-----------|----------|
| Authentication present | Yes / No | [file path or "Not Found"] |
| Cryptography used | Yes / No | [file path or "Not Found"] |
| Database access present | Yes / No | [file path or "Not Found"] |
| File upload handling | Yes / No | [file path or "Not Found"] |
| External API calls | Yes / No | [file path or "Not Found"] |
| Message queue usage | Yes / No | [file path or "Not Found"] |
| Session management | Yes / No | [file path or "Not Found"] |
| User input handling | Yes / No | [file path or "Not Found"] |

## Modules for Scan

The following modules should be scanned by @batch-scan (alphabetical order):

| # | Module | Path | Language | Applicable Standards |
|---|--------|------|----------|---------------------|
| 1 | [name] | [path] | [lang] | [SonarQube Java / SonarQube JS / BSL / All] |
```

---

### Step 8: Self-Validation Checklist

Before saving artifacts, verify ALL of the following:

- [ ] All tables are sorted by their defined sort key (Rule D4)
- [ ] All file paths reference files that exist in the file manifest (Rule D2)
- [ ] No subjective quality judgments in any artifact (Rule D5)
- [ ] No extra sections beyond what templates define (Rule D6)
- [ ] No "Not Found" sections that should have content (re-check source)
- [ ] Every module from Step 0.3 appears in architecture.md Component Catalog
- [ ] Cross-references between artifacts use correct filenames
- [ ] No content from previous runs influences current output (Rule D7)
- [ ] architecture-preview.html contains the SAME Mermaid code as architecture.md
- [ ] architecture-preview.html renders correctly (valid HTML structure)

---

## Completion Message

After generating all artifacts:

```
Reverse engineering analysis complete (v1.7 — deterministic mode).

Artifacts saved to: code-review-artifacts/reverse-engineering/
  - business-overview.md
  - architecture.md
  - architecture-preview.html  ← Open in browser for diagrams
  - api-documentation.md
  - technology-and-dependencies.md
  - code-quality-baseline.md
  - analysis-summary.md

Codebase: [N] source files, [N] modules, [primary language]
Scale: [Small / Medium / Large]

Architecture diagrams: Open architecture-preview.html in a browser to view
rendered diagrams. To export to Word: Ctrl+A → Copy → Paste into Word document.

Proceed with: @batch-scan
```
