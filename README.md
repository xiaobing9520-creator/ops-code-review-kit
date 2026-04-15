# 运维代码接收审核工具包

## 这是什么

这是一套基于 Kiro（AI IDE）的代码审核工具包。运维团队在接收开发团队交付的应用系统之前，
使用本工具包对代码进行标准化审核，确保接收到的系统足够安全、稳定、可维护。

**本工具包不要求开发团队使用 Kiro 或任何特定工具。**
审核工作完全由运维团队在自己的环境中完成。

## 核心能力

- **一键批量扫描**：单条指令 `@batch-scan` 触发所有模块的完整扫描
- **每模块 2 份报告**：Reliability & Maintainability + Security
- **全局汇总报告**：合并所有模块扫描结果，整体 Pass/Fail 判定
- **严格规则对照**：每个 issue 必须映射到具体 Rule ID，不允许自行调整
- **质量门控**：基于 Critical/High/Medium(P0) 的自动 Pass/Fail 判定
- **修复优先级**：P0–P3 分级，明确修复时间要求

## 报告类型

| 报告 | 审查标准 | 覆盖范围 |
|------|---------|---------|
| Reliability & Maintainability | SonarQube Java/JavaScript 规则 | Blocker / High / Medium |
| Security | Philips Secure Coding Baseline (BSL 11.1.1.d, 230 条) | 17 个安全域 |
| Summary | 汇总所有模块 | 全局 Pass/Fail |

4 个模块一次扫描产出 **9 份报告**（4×2 + 1）。

## 前置条件

### 必须安装

1. **Kiro IDE** — 下载地址：https://kiro.dev

## 使用步骤

### 第一步：获取待审核代码

```bash
git clone <代码仓库地址> /path/to/target-project
```

### 第二步：注入审核工具包

```bash
cp -r ops-code-review-kit/.kiro /path/to/target-project/
```

### 第三步：用 Kiro 执行审核

1. 用 Kiro IDE 打开目标项目
2. 在 AI 聊天窗口中执行：

```
@codebase-reverse-engineering
```

等待完成后执行一键批量扫描：

```
@batch-scan
```

**这一条命令会自动完成：**
- 识别所有模块
- 对每个模块生成 Reliability & Maintainability 报告
- 对每个模块生成 Security 报告
- 生成全局 Summary 报告

### 第四步：查看审核结果

扫描完成后，`code-review-artifacts/` 目录下会生成所有报告：

```
code-review-artifacts/
├── reverse-engineering/                              ← 代码库理解文档
├── Module1_Reliability_Maintainability_Report_2026-04-15.md
├── Module1_Security_Report_2026-04-15.md
├── Module2_Reliability_Maintainability_Report_2026-04-15.md
├── Module2_Security_Report_2026-04-15.md
├── Module3_Reliability_Maintainability_Report_2026-04-15.md
├── Module3_Security_Report_2026-04-15.md
├── Module4_Reliability_Maintainability_Report_2026-04-15.md
├── Module4_Security_Report_2026-04-15.md
└── Summary_Report_2026-04-15.md                      ← 汇总报告
```

## 报告结构说明

### 分类报告（R&M / Security）

每份分类报告包含：

1. **报告抬头** — 仓库/模块名称、扫描日期、审查标准、规则编号格式
2. **审查概要** — 按类别统计 + 严重程度分布 + 质量门状态
3. **Issue 详情** — 每个 issue 包含：
   - 编号（如 BUG-01, SEC-01）
   - 规则编号 + 规则描述（严格对照 SonarQube / BSL 规则）
   - 严重程度（Critical / High / Medium）
   - 问题文件路径 + 代码片段
   - 问题说明（根因 + 业务影响）
   - 详尽修复建议（针对具体代码）
   - 修复优先级（P0/P1/P2/P3）
   - 不修复的业务影响
4. **修复优先级汇总**
5. **附录** — LLM 自发现的、无法映射到规则集的额外问题（不计入质量门）

### 汇总报告（Summary）

- 各模块 × 各报告类型的 Pass/Fail 汇总
- 所有模块 issue 合并明细表
- 全局修复优先级分布

## 质量门判定逻辑

```
Pass 条件（全部满足）：
  - 0 个 Critical 问题
  - 0 个 High 问题
  - Medium 中没有 P0 优先级的 issue

否则：Fail
```

## 修复优先级定义

| 优先级 | 含义 | 典型场景 |
|-------|------|---------|
| **P0** | 发版前必须修复 | 影响正确性或安全性，含部分 Medium |
| **P1** | 短期修复（1-2 周） | 高风险但不阻塞当前发版 |
| **P2** | 中期修复（1 个月内） | 代码质量问题，有一定风险 |
| **P3** | 长期优化 | 低风险，技术债务 |

Medium 级别 issue 必须明确标注 P0–P3，P0 的 Medium issue 会导致质量门 Fail。

## 规则来源

### SonarQube 规则（Reliability & Maintainability 报告）

- 使用 `sonarqube_rules.json` 中的规则集
- 当前包含 222 条规则（Java 145 + JavaScript 77）
- 每个 issue 的规则编号、名称、严重程度严格对照规则定义
- 无法映射到具体 Rule ID 的问题不列入主报告

### Philips Secure Coding Baseline（Security 报告）

- 使用 BSL 11.1.1.d Version 3（2025年10月）
- 包含 230 条安全控制要求，覆盖 17 个安全域
- 每个 issue 映射到具体 BSL Control ID（如 `11.1.1_41`）

### LLM 自发现问题隔离

SonarQube / BSL 规则之外的问题不混入主报告 issue 列表，统一收录至各报告末尾的附录章节，
不影响质量门判定。

## 也可以逐步执行

如果不使用一键批量扫描，也可以逐步执行：

```
@codebase-reverse-engineering     ← 1. 理解代码库（必须最先）
@sonarqube-review                 ← 2. 对指定模块生成 R&M 报告
@secure-coding-baseline-review    ← 3. 对指定模块生成 Security 报告
@summary-report                   ← 4. 生成汇总报告
```

### 可选的补充审核（深度分析）

以下 skill 提供超出两类核心报告的补充分析：

```
@security-review          ← OWASP/CWE 安全分析
@reliability-review       ← 12-Factor App 运维就绪性
@performance-review       ← 性能效率分析
@maintainability-review   ← 技术债务/可维护性分析
@acceptance-report        ← 综合准入决策（所有维度）
```

## 常见问题

**Q: 开发团队不用 Kiro 怎么办？**
A: 不需要开发团队使用 Kiro。`.kiro/` 目录是运维团队的审核工具，不提交到开发团队的代码仓库。

**Q: 可以只扫描部分模块吗？**
A: 可以。`@batch-scan module1 module2` 指定模块名即可。也可以用 `@sonarqube-review` 和
`@secure-coding-baseline-review` 逐模块执行。

**Q: SonarQube 规则集怎么更新？**
A: 从组织的 SonarQube 系统导出最新规则配置（JSON 格式），更新
`.kiro/rules/sonarqube-java-standards.md` 和 `sonarqube_rules.json`。
当前版本包含 222 条 Blocker + High 级别规则，后续可扩展 Medium 级别规则。

**Q: 报告中的严重程度等级怎么定义的？**
A: SonarQube Blocker → Critical，High → High，Medium → Medium。
BSL 报告按安全影响分级：注入/凭据/加密失败 → Critical，访问控制/会话管理 → High，
配置/编码实践 → Medium。

**Q: 附录中的问题要不要修？**
A: 附录中的问题来自 LLM 通用最佳实践发现，不在客户指定规则集内，不影响质量门。
建议作为参考，酌情处理。

**Q: 质量门 Fail 了怎么办？**
A: 查看 Summary Report 中的 P0 issues 列表，这些是必须修复的。修复后重新执行扫描验证。
