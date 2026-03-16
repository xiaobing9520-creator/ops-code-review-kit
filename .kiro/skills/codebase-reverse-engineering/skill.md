---
name: codebase-reverse-engineering
description: >
  Performs comprehensive reverse engineering analysis of an existing codebase
  before code review. Use as the FIRST step before running any dimension-specific
  review. Generates architecture docs, code structure, API inventory, dependency
  map, technology stack, and code quality baseline.
---

# Codebase Reverse Engineering

You are a senior software architect performing comprehensive reverse engineering
of a codebase. Your goal is to deeply understand the system before any code
review begins, producing structured artifacts that downstream review skills
will reference.

## IMPORTANT: Run This Skill FIRST

This skill MUST be executed before any of the following review skills:
- security-review
- reliability-review
- performance-review
- maintainability-review
- acceptance-report

The artifacts generated here provide the foundation for all subsequent reviews.

## Output Directory

All artifacts are saved to `code-review-artifacts/reverse-engineering/` in the
project root.

## General Rules

- If information for a section cannot be determined or does not exist, mark it
  as **"Not Found"** with a brief reason. Never guess or fabricate content.
- Use cross-references (`See [architecture.md](architecture.md)`) instead of
  duplicating information across artifacts.
- Adapt depth of analysis to codebase scale (see Step 0).

---

## Reverse Engineering Process

### Step 0: Scale Assessment & Exploration Strategy

Before diving into analysis, assess the codebase scale and plan your approach.

#### 0.1 Quick Scale Assessment

Run a top-level scan to classify the codebase:

| Scale | File Count | Strategy |
|-------|-----------|----------|
| **Small** | < 50 source files | Full analysis — read all key files |
| **Medium** | 50-500 source files | Module-level analysis — read entry points, configs, and core logic per module; sample non-critical files |
| **Large** | > 500 source files | Skeleton analysis — focus on architecture, entry points, configs, public APIs; skip internal implementation details |

Record the assessed scale in the analysis summary. All subsequent steps should
respect this scale classification.

#### 0.2 Exploration Strategy

Follow this order to efficiently understand the codebase:

1. **Root-level scan**: List root directory contents; read top-level config files
   (package.json, pom.xml, build.gradle, go.mod, Cargo.toml, pyproject.toml,
   Makefile, docker-compose.yml, etc.)
2. **Workspace/monorepo detection**: Check for monorepo tooling (Nx, Turborepo,
   Lerna, pnpm workspaces, Bazel, Gradle multi-project, Maven multi-module).
   If present, read workspace config to discover all packages.
3. **Entry point identification**: Locate main entry files (main.*, index.*,
   app.*, handler.*, server.*) using glob patterns.
4. **Config & infra scan**: Glob for `**/Dockerfile`, `**/*.tf`, `**/template.yaml`,
   `**/.github/workflows/*`, `**/Jenkinsfile`, `**/*.pipeline.*`.
5. **API surface scan**: Glob for OpenAPI/Swagger specs, GraphQL schemas, gRPC
   proto files, Smithy models, route definitions.
6. **Targeted deep reads**: Based on discoveries above, read specific files that
   are critical for understanding architecture and business logic.

Do NOT read files sequentially or exhaustively. Use glob and grep to discover,
then read selectively.

---

### Step 1: Multi-Package Discovery

#### 1.1 Scan Workspace

- Discover ALL packages, modules, and sub-projects (not just top-level)
- Identify package relationships via config files
- Classify package types: Application, Infrastructure, Models/Shared, Clients, Tests
- **Monorepo handling**: If a monorepo tool is detected (Nx, Turborepo, Lerna,
  pnpm workspaces, Bazel, etc.), document:
  - Workspace configuration and package discovery mechanism
  - Build orchestration and task pipeline
  - Shared configuration (tsconfig, eslint, etc.)
  - Package dependency graph within the monorepo

#### 1.2 Understand Business Context

- Identify the core business domain the system implements
- Determine the business purpose of every package/module
- List business transactions/workflows implemented in the system

#### 1.3 Infrastructure Discovery

- IaC packages: CDK, Terraform (.tf), CloudFormation, Pulumi, Ansible
- Container configurations: Dockerfile, docker-compose, Kubernetes manifests
- Deployment scripts and CI/CD pipelines (.github/workflows, Jenkinsfile,
  .gitlab-ci.yml, buildspec.yml, etc.)

#### 1.4 Build System Discovery

- Identify build systems: Maven, Gradle, npm/yarn/pnpm, pip/poetry, Go modules,
  Cargo, Bazel, Make, etc.
- Map config files and build-system declarations
- Trace build dependencies between packages

#### 1.5 Service Architecture Discovery

- **Serverless functions**: AWS Lambda, Azure Functions, GCP Cloud Functions,
  Cloudflare Workers, etc.
- **Container services**: Docker/ECS/Kubernetes/Cloud Run, etc.
- **API definitions**: OpenAPI/Swagger, GraphQL, gRPC/Protobuf, Smithy, REST
  route definitions
- **Data stores**: Relational DBs, NoSQL, caches (Redis/Memcached), object
  storage (S3/GCS/Azure Blob)
- **Message & event systems**: Kafka, RabbitMQ, SQS/SNS, EventBridge, NATS,
  Pub/Sub, etc.

#### 1.6 Code Metrics Baseline

- Count lines of code per language (KLOC)
- Count files per package/module
- Identify programming languages and frameworks
- Note test coverage indicators (coverage config, reports if present)
- Note linting/formatting configurations

---

### Step 2: Generate Business Overview

Create `code-review-artifacts/reverse-engineering/business-overview.md`:

```markdown
# Business Overview

## Business Context
- **System Purpose**: [Overall description of what the system does]
- **Business Domain**: [Domain area]
- **Codebase Scale**: Small / Medium / Large ([N] source files)

## Business Transactions
| # | Transaction | Description | Components Involved |
|---|------------|-------------|---------------------|
| 1 | [name]     | [description] | [list]            |

## Business Dictionary
| Term   | Meaning      |
|--------|-------------|
| [term] | [definition] |
```

---

### Step 3: Generate Architecture Documentation

Create `code-review-artifacts/reverse-engineering/architecture.md`:

This is the **single source of truth** for component descriptions, data flow,
and integration points. Other artifacts should reference this file instead of
repeating architectural details.

```markdown
# System Architecture

## System Overview
[High-level description of the system]

## Architecture Diagram
[Describe the architecture in text form: components, connections, data flow.
Use a Mermaid diagram if the structure is complex enough to warrant one.]

## Component Catalog
### [Package/Component Name]
- **Purpose**: [What it does]
- **Responsibilities**: [Key responsibilities]
- **Type**: Application / Infrastructure / Model / Client / Test
- **Internal Dependencies**: [Other components in this codebase it depends on]
- **External Dependencies**: [Third-party services or libraries it depends on]

## Data Flow
[Describe key data flows through the system]

## Integration Points
- **External APIs**: [List with purposes]
- **Databases**: [List with purposes and types]
- **Third-party Services**: [List with purposes]
- **Message Queues/Events**: [List with purposes]

## Infrastructure
- **IaC Approach**: [CDK/Terraform/CloudFormation/Pulumi/None]
- **Deployment Model**: [Containers, Serverless, VMs, Hybrid, etc.]
- **CI/CD**: [Pipeline tool and config location]
- **Networking**: [VPC, subnets, security groups if applicable]
```

---

### Step 4: Generate API & Interface Documentation

Create `code-review-artifacts/reverse-engineering/api-documentation.md`:

```markdown
# API & Interface Documentation

## External APIs (REST / GraphQL / gRPC)
### [Endpoint or Service Name]
- **Protocol**: REST / GraphQL / gRPC
- **Method/Operation**: GET /path | Query name | RPC name
- **Purpose**: [What it does]
- **Request**: [Request format/body summary]
- **Response**: [Response format/body summary]
- **Authentication**: [Auth method]

## Event Contracts
### [Event Name]
- **Source**: [Producer component - see [architecture.md](architecture.md)]
- **Consumers**: [List]
- **Payload Schema**: [Summary or reference]

## Key Data Models
### [Model Name]
- **Fields**: [Field descriptions with types]
- **Relationships**: [Related models]
- **Validation**: [Validation rules]

## Internal Interfaces
[Document only interfaces that cross package boundaries.]
### [Interface Name]
- **Package**: [Where defined]
- **Consumed by**: [Which packages use it]
- **Key Methods**: [Signatures]
```

---

### Step 5: Generate Technology & Dependency Documentation

Create `code-review-artifacts/reverse-engineering/technology-and-dependencies.md`:

```markdown
# Technology & Dependencies

## Programming Languages
| Language | Version | Usage Area | KLOC |
|----------|---------|-----------|------|
| [lang]   | [ver]   | [usage]   | [kloc] |

## Frameworks & Libraries
| Name | Version | Purpose | Package(s) Using It |
|------|---------|---------|---------------------|
| [name] | [ver] | [purpose] | [packages] |

## Infrastructure Services
| Service | Purpose | Config Location |
|---------|---------|----------------|
| [name]  | [purpose] | [path]      |

## Build & CI/CD
| Tool | Version | Purpose |
|------|---------|---------|
| [name] | [ver] | [purpose] |

## Internal Dependency Graph
[Describe or diagram how packages depend on each other within the codebase.]

### [Package A] -> [Package B]
- **Type**: Compile / Runtime / Test
- **Reason**: [Why dependency exists]

## External Dependency Inventory
| Dependency | Version (Locked) | License | Used By |
|-----------|-----------------|---------|---------|
| [name]    | [version]       | [license] | [packages] |

> **Note**: Version-freshness analysis and CVE scanning require network access
> or dedicated tooling (Trivy, Snyk). If tool-reports/ contains SCA results,
> they will be referenced in the security review.
```

---

### Step 6: Generate Code Quality Baseline

Create `code-review-artifacts/reverse-engineering/code-quality-baseline.md`:

```markdown
# Code Quality Baseline

## Metrics Summary
| Metric | Value |
|--------|-------|
| Total Source Files | [number] |
| Total KLOC | [number] |
| Languages | [list] |
| Test Files | [count] |
| Config Files | [count] |

## Test Coverage
- **Unit Tests**: Present / Absent - [details]
- **Integration Tests**: Present / Absent - [details]
- **E2E Tests**: Present / Absent - [details]
- **Coverage Config/Reports**: [tool and config location, or "Not Found"]

## Code Quality Tooling
- **Linting**: [tool name and config path, or "Not Found"]
- **Formatting**: [tool name and config path, or "Not Found"]
- **Type Checking**: [tool name and config path, or "Not Found"]
- **Static Analysis**: [tool name and config path, or "Not Found"]

## Documentation Status
- **README**: Present / Absent - [quality assessment]
- **API Docs**: Present / Absent - [quality assessment]
- **Inline Comments**: Adequate / Sparse / Excessive
- **Architecture Docs**: Present / Absent

## Design Patterns Identified
### [Pattern Name]
- **Location**: [Where used - reference file paths]
- **Purpose**: [Why used]

## Initial Observations
[List notable patterns, anti-patterns, or concerns spotted during analysis.]
```

---

### Step 7: Self-Check & Generate Analysis Summary

Before producing the final summary, perform a self-check:

- [ ] Every package/module discovered in Step 1 appears in architecture.md
- [ ] All entry points and API surfaces are documented
- [ ] No section contains fabricated information
- [ ] Cross-references between artifacts are valid
- [ ] Analysis depth matches the assessed codebase scale

Then create `code-review-artifacts/reverse-engineering/analysis-summary.md`:

```markdown
# Reverse Engineering Analysis Summary

**Analysis Date**: [date]
**Workspace**: [project name/path]
**Codebase Scale**: Small / Medium / Large
**Total Source Files**: [number]
**Total KLOC**: [number]

## Artifacts Generated
- [x] business-overview.md
- [x] architecture.md
- [x] api-documentation.md
- [x] technology-and-dependencies.md
- [x] code-quality-baseline.md

## Key Findings
1. [Most important finding]
2. [Second most important finding]
3. [Third most important finding]

## Recommended Review Focus Areas
- **Security**: [specific areas]
- **Reliability**: [specific areas]
- **Performance**: [specific areas]
- **Maintainability**: [specific areas]

## Next Steps
1. @security-review
2. @reliability-review
3. @performance-review
4. @maintainability-review
5. @acceptance-report
```

---

## Completion Message

After generating all artifacts, present:

```
Reverse engineering analysis complete.

Artifacts saved to: code-review-artifacts/reverse-engineering/

Please review the artifacts, especially:
- business-overview.md - Does the business context look correct?
- architecture.md - Is the architecture accurately captured?
- analysis-summary.md - Do the key findings and focus areas make sense?

When ready, proceed with: @security-review
```
