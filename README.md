# 运维代码接收审核工具包

## 这是什么

这是一套基于 Kiro（AI IDE）的代码审核工具包。运维团队在接收开发团队交付的应用系统之前，
使用本工具包对代码进行标准化审核，确保接收到的系统足够安全、稳定、可维护。

**本工具包不要求开发团队使用 Kiro 或任何特定工具。**
审核工作完全由运维团队在自己的环境中完成。

## 前置条件

### 必须安装

1. **Kiro IDE**
   - 下载地址：https://kiro.dev
   - 安装后打开，按提示完成初始化

### 建议安装（用于补充扫描，非必须）

以下工具可以提供更精确的量化数据，与 Kiro 的智能分析互补：

| 工具 | 用途 | 安装命令 |
|------|------|---------|
| Trivy | 依赖漏洞扫描 | `brew install trivy` 或参考 https://trivy.dev |
| Semgrep | 代码安全扫描 | `pip install semgrep` 或参考 https://semgrep.dev |
| Checkov | IaC 配置扫描 | `pip install checkov` 或参考 https://checkov.io |

如果不安装这些工具，Kiro 仍然可以独立完成审核，但报告中会标注"未提供工具扫描数据"。

## 使用步骤

### 第一步：获取待审核代码

从 GitLab/GitHub 克隆开发团队提交的代码到本地：

```bash
git clone <代码仓库地址> /path/to/target-project
```

### 第二步：注入审核工具包

将本工具包的 `.kiro` 目录复制到目标项目的根目录：

```bash
cp -r ops-code-review-kit/.kiro /path/to/target-project/
```

复制完成后，目标项目的目录结构应该类似：

```
target-project/
├── .kiro/                  <-- 这是你刚复制进去的审核工具包
│   ├── steering.md
│   ├── rules/
│   │   ├── security-standards.md
│   │   ├── reliability-standards.md
│   │   ├── performance-standards.md
│   │   ├── maintainability-standards.md
│   │   ├── sonarqube-java-standards.md
│   │   └── sonarqube-javascript-standards.md
│   └── skills/
│       ├── codebase-reverse-engineering/
│       ├── security-review/
│       ├── reliability-review/
│       ├── performance-review/
│       ├── maintainability-review/
│       ├── sonarqube-review/
│       └── acceptance-report/
├── src/                    <-- 开发团队的代码
├── package.json            <-- 开发团队的配置
└── ...
```

### 第三步（可选）：运行补充扫描工具

如果你安装了 Trivy、Semgrep 等工具，可以运行提供的脚本：

```bash
cp ops-code-review-kit/run-tool-scans.sh /path/to/target-project/
cd /path/to/target-project
bash run-tool-scans.sh
```

脚本会自动检测已安装的工具并运行扫描，结果保存到 `tool-reports/` 目录。
Kiro 审核时会自动读取这些报告。

### 第四步：用 Kiro 打开项目并执行审核

1. 打开 Kiro IDE
2. 选择 `File > Open Folder`，打开目标项目目录
3. Kiro 会自动加载 `.kiro/` 中的配置

然后在 Kiro 的 AI 聊天窗口中，**按顺序执行以下命令**：

#### 4.1 理解代码库（必须最先执行）

在聊天窗口输入：
```
@codebase-reverse-engineering
```

等待 Kiro 完成分析。完成后检查 `code-review-artifacts/reverse-engineering/` 目录下
的产出文件，确认 Kiro 对项目的理解是否准确。如有偏差，在聊天窗口中纠正。

#### 4.2 执行四维度审核

依次在聊天窗口输入以下命令（每次等上一个完成后再执行下一个）：

```
@security-review
```
```
@reliability-review
```
```
@performance-review
```
```
@maintainability-review
```

每个审核完成后，对应的报告会保存到 `code-review-artifacts/` 对应子目录中。

#### 4.3 执行 SonarQube 规则审核（Java/JavaScript 项目推荐）

如果待审核项目包含 Java 或 JavaScript/TypeScript 代码，**强烈建议**执行此步骤：

```
@sonarqube-review
```

此审核基于从组织 SonarQube 系统导出的 222 条 Blocker/High 级别规则（Java 145 条 + JavaScript 77 条），
覆盖以下检查领域：
- **安全漏洞**：注入攻击、XSS、硬编码凭据、加密弱点等
- **可靠性缺陷**：资源泄漏、并发问题、无限循环等
- **Spring Framework**：Spring 特定的配置和使用问题（仅 Java）
- **测试质量**：测试完整性、断言正确性等
- **代码质量**：复杂度、命名、类型安全、现代语法等

如果项目不包含 Java 或 JavaScript，可跳过此步骤。

#### 4.4 生成准入报告

所有维度审核完成后，执行：

```
@acceptance-report
```

这会生成最终的准入决策报告，保存在 `code-review-artifacts/acceptance-report.md`。

### 第五步：查看审核结果

打开 `code-review-artifacts/acceptance-report.md`，查看：

- **准入决策**：Accept（通过）/ Conditional Accept（有条件通过）/ Reject（拒绝）
- **问题清单**：按严重等级分类的所有发现
- **整改要求**：如果是有条件通过，需要开发团队修复的问题列表
- **复审条件**：整改后需要重新审核的范围

### 第六步：反馈给开发团队

将 `code-review-artifacts/` 整个目录打包发送给开发团队，其中包含：

```
code-review-artifacts/
├── reverse-engineering/         # 系统理解文档（帮助开发团队了解审核视角）
│   ├── business-overview.md
│   ├── architecture.md
│   ├── api-documentation.md
│   ├── technology-and-dependencies.md
│   └── code-quality-baseline.md
├── security-review/
│   └── security-report.md       # 安全审核详细报告
├── reliability-review/
│   └── reliability-report.md    # 可靠性审核详细报告
├── performance-review/
│   └── performance-report.md    # 性能审核详细报告
├── maintainability-review/
│   └── maintainability-report.md # 可维护性审核详细报告
├── sonarqube-review/
│   └── sonarqube-report.md      # SonarQube 规则审核报告（Java/JS 项目）
└── acceptance-report.md          # 最终准入决策报告
```

## 准入决策说明

| 决策 | 含义 | 后续动作 |
|------|------|---------|
| **Accept** | 代码质量达标，可以接收进入运维 | 进入运维交接流程 |
| **Conditional Accept** | 存在需要修复的问题，但不影响短期运行 | 开发团队在约定期限内完成整改，整改后复审 |
| **Reject** | 存在严重问题，不具备接收条件 | 开发团队完成全面整改后重新提交全量审核 |

## 审核标准概览

本工具包依据以下行业标准进行审核：

- **安全性**：OWASP Top 10、CWE Top 25、NIST SSDF
- **可靠性**：缺陷密度 < 1.0/KLOC、12-Factor App 运维就绪性
- **性能**：响应时间分级、资源利用率基线、可扩展性评估
- **可维护性**：可维护性指数、技术债务比率 < 10%、代码异味密度 < 5/KLOC
- **SonarQube 规则**：222 条 Blocker/High 级别规则（Java 145 + JavaScript 77），
  覆盖注入攻击、Spring Framework、并发安全、测试质量等

详细标准见 `standards/code-scan-standards.md` 和 `.kiro/rules/` 目录。

## 常见问题

**Q: 开发团队不用 Kiro 怎么办？**
A: 不需要开发团队使用 Kiro。`.kiro/` 目录是运维团队的审核工具，不需要提交到开发团队的代码仓库。

**Q: 审核需要多长时间？**
A: 取决于代码库规模。每个 skill 执行通常需要几分钟，整套流程（6 个 skill）需要依次执行。

**Q: 可以只跑部分审核吗？**
A: 可以，但 `@codebase-reverse-engineering` 必须最先执行（后续审核依赖它的产出）。
四个维度审核可以选择性执行，但建议全部执行以获得完整的准入决策。
`@sonarqube-review` 是可选的，仅适用于 Java/JavaScript 项目。

**Q: SonarQube 规则审核和现有四维度审核有什么区别？**
A: 四维度审核是基于通用行业标准（OWASP、CWE、12-Factor 等）的审核，侧重架构和设计层面。
SonarQube 规则审核是基于组织现有 SonarQube 质量配置导出的语言特定编码规则，侧重具体代码模式和
最佳实践。两者互补，SonarQube 审核的发现会自动纳入最终准入决策评分。

**Q: 整改后需要全部重新审核吗？**
A: 如果是 Conditional Accept，可以只针对问题相关的维度重新执行对应的 review skill，
然后重新执行 `@acceptance-report`。如果是 Reject，建议全量重审。

**Q: 如何更新审核标准？**
A: 修改 `.kiro/rules/` 目录下的对应规则文件即可。建议每季度审查一次行业标准更新。

**Q: 如何更新 SonarQube 规则？**
A: 从组织的 SonarQube 系统导出最新的规则配置（JSON 格式），然后更新
`.kiro/rules/sonarqube-java-standards.md` 和 `.kiro/rules/sonarqube-javascript-standards.md`
中的规则列表。当前版本包含 222 条规则（Blocker + High 级别）。
