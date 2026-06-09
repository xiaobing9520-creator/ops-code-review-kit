# AI Code Review 方案设计最佳实践

**基于 ops-code-review-kit v1.6 → v1.8.1 七个版本迭代的经验总结**

本文档回顾了在构建 AI 驱动的代码审查系统过程中遇到的所有问题、踩过的坑、以及
最终沉淀下来的设计原则。适用于任何想用 LLM 做自动化代码审查的团队。

---

## 目录

1. [确定性是第一优先级](#1-确定性是第一优先级)
2. [先理解架构，再做扫描](#2-先理解架构再做扫描)
3. [代码采样策略决定了报告质量的上限](#3-代码采样策略决定了报告质量的上限)
4. [规则映射必须严格，LLM发现必须隔离](#4-规则映射必须严格llm发现必须隔离)
5. [Quality Gate 必须全局一致](#5-quality-gate-必须全局一致)
6. [报告格式标准化是可比较性的基础](#6-报告格式标准化是可比较性的基础)
7. [模块发现必须自动化且确定](#7-模块发现必须自动化且确定)
8. [深度追踪需要明确的停止条件](#8-深度追踪需要明确的停止条件)
9. [自校验机制比事后修复更有效](#9-自校验机制比事后修复更有效)
10. [方案必须与项目结构解耦](#10-方案必须与项目结构解耦)
11. [版本演进的节奏与策略](#11-版本演进的节奏与策略)
12. [采样是确定性的敌人——全量扫描是终极解](#12-采样是确定性的敌人全量扫描是终极解)
13. [LLM 自校验不可信——必须有外部验证](#13-llm-自校验不可信必须有外部验证)
14. [CVSS 评分需要锚定——不能完全交给 LLM 主观判断](#14-cvss-评分需要锚定不能完全交给-llm-主观判断)
15. [模型能力是方案的硬性前提——不是所有模型都能用](#15-模型能力是方案的硬性前提不是所有模型都能用)

---

## 1. 确定性是第一优先级

**教训来源**: v1.7 — 同一代码库多次运行产出不同报告

### 问题

LLM 天然具有非确定性——同样的输入可以产出不同的措辞、不同的排序、甚至不同的
发现数量。对于代码审查报告来说，这是不可接受的：
- 运维团队拿到两份不同的报告会质疑工具的可信度
- Summary Report 的 issue 计数每次不同，无法追踪修复进展
- 无法建立"同一代码 = 同一结论"的信任基础

### 设计原则

| 规则 | 含义 | 反例 |
|------|------|------|
| **排序固定** | 所有列表、表格必须有明确的排序键 | "按重要性排序"（主观） |
| **发现去重** | 同一规则同一模块只报一次，附计数 | 每个违规实例单独成条 |
| **严禁主观表达** | 只允许事实（计数、路径、版本） | "well-structured"、"notable" |
| **模板固定** | 每个字段要么填值，要么写 `Not Found` | 随意增减章节 |
| **无上下文泄漏** | 每次运行独立，不引用上一次结果 | "相比上次运行..." |
| **发现顺序固定** | 按 severity → rule ID → file path 排序 | 按"发现时间"排序 |

### 实现方式

```
D1: 文件发现必须 find | sort
D2: 文件读取有固定优先级
D3: 明确的包含/排除边界
D4: 所有表格有排序键
D5: 只允许事实性内容
D6: 模板字段不能增删
D7: 无上下文泄漏
```

**关键洞察**: 确定性不是 LLM 的自然行为。你必须通过**结构性约束**（排序规则、
固定模板、去重规则）来强制实现它，而不是靠 prompt 里写"请保持一致"。

---

## 2. 先理解架构，再做扫描

**教训来源**: v1.76 — 跳过架构理解导致拓扑错误（admin plane 被错误路由）

### 问题

直接对代码做 rule-by-rule 扫描，看似高效，实际会导致：
- 不理解请求路由 → 安全扫描漏掉整个 admin 平面
- 不理解认证机制 → 报告中的安全建议与实际架构矛盾
- 不理解模块边界 → 跨模块调用被误报为内部问题

### 设计原则

```
阶段1: 逆向工程（理解系统是什么）
  ↓
阶段2: 规则扫描（评估系统有什么问题）
  ↓
阶段3: 汇总报告（合并所有模块结论）
```

**绝不能跳过阶段1**。逆向工程的输出（架构文档、API清单、技术栈、数据流）是
下游扫描的基础数据。扫描技能需要引用这些文档来：
- 确定哪些模块用哪套规则
- 理解安全边界在哪里
- 判断某个发现是否真正有风险

### 逆向工程必须覆盖的信息

| 类别 | 为什么扫描需要它 |
|------|------------------|
| 请求路由（谁调谁） | 确定攻击面和信任边界 |
| 认证机制（用什么方式） | 判断密码存储、session 管理是否合规 |
| 技术栈（框架+版本） | 确定适用哪些规则（Java vs JS） |
| 数据流（敏感数据去哪） | 判断加密、日志脱敏是否到位 |
| 部署模型（容器/k8s/VM） | 判断基础设施安全配置 |

---

## 3. 代码采样策略决定了报告质量的上限

**教训来源**: v1.7 → v1.8 — 字母序采样导致关键文件被跳过

### 问题的演化

| 版本 | 采样策略 | 问题 |
|------|---------|------|
| v1.7 | 每 package 取字母序前 N 个文件 | `UserService` 被跳过，`AaaHelper` 被选中 |
| 研究阶段 | 考虑 fan-in 加权评分 | 连续分值在阈值附近翻转，破坏确定性 |
| v1.8 | Architecture-Role Pattern Matching | 按命名模式选文件，离散判断，理论确定性 |
| v1.8.1 | 全量扫描 | LLM 在执行 budget 规则时仍有自由裁量 → 全量读取彻底消除 |

### 采样策略的三个评估维度

```
             准确性
            /      \
           /        \
      确定性 ———————— Token效率
```

- **准确性**: 能否选中真正决定架构的文件
- **确定性**: 同一代码是否每次选同样的文件
- **Token效率**: 消耗多少上下文来完成选择

### 最佳方案: 模式匹配 + 兜底

```
Tier 1: 匹配架构角色命名模式的文件（必读）
  → *Controller, *Service, *Repository, *Config, *Entity, *Filter...

Tier 2: 字母序兜底（填充剩余预算）
  → 仅用于 Medium 规模代码库
```

**为什么不用 fan-in（import 引用计数）**:
- `StringUtils` 被 50 个文件 import → fan-in 极高 → 对架构理解毫无价值
- `OrderSagaOrchestrator` 只被 2 个文件 import → fan-in 低 → 是分布式事务核心
- 且评分是连续值，边界效应会破坏确定性

**为什么模式匹配有效**:
- 在 Java/Spring/Node 生态中，90%+ 的架构文件遵循命名约定
- 判断是离散的（匹配/不匹配），无边界翻转
- 零额外 token 消耗（只需 grep 文件名）

---

## 4. 规则映射必须严格，LLM发现必须隔离

**教训来源**: v1.65/v1.75 — LLM 编造规则 ID、混淆 severity

### 问题

LLM 在做代码审查时有三个危险倾向：
1. **编造规则 ID** — 从训练数据中"回忆"出不存在的规则编号
2. **混淆 severity** — 把 Medium 规则报成 High（因为"感觉"严重）
3. **混入主观发现** — 把自己发现的问题伪装成规则匹配结果

这三种行为会污染报告的可信度——如果审查人发现一个 rule ID 不存在，就会质疑
整份报告的所有结论。

### 设计原则

```
┌─────────────────────────────────────────────┐
│          Main Report Body                    │
│  ✓ 每条发现必须映射到标准文件中的规则 ID      │
│  ✓ Severity 必须等于标准文件中定义的值        │
│  ✓ 规则描述必须与标准文件标题匹配            │
│  ✓ 影响 Quality Gate                        │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│          Appendix (隔离区)                   │
│  ✓ LLM 发现的但无法映射的问题               │
│  ✓ 标注 "General best practices"            │
│  ✓ 不携带规则 ID                            │
│  ✓ 不影响 Quality Gate                      │
└─────────────────────────────────────────────┘
```

### 必须有的自校验步骤

| 检查项 | 含义 |
|--------|------|
| V-01 规则存在性 | 每个 rule ID 在标准文件中能 grep 到 |
| V-02 严格 severity | Blocker→Critical, High→High, Medium→Medium，不允许其他映射 |
| V-03 描述准确性 | 报告中的规则描述 = 标准文件中的规则标题 |
| V-04 Priority 完整性 | 每个 Medium 必须有 P0-P3 标签 |
| V-05 Appendix 标签 | 无效发现必须在 Appendix 且不带规则 ID |

### 已知的 LLM 高频错误

记录并维护一张"已知坑位"表，在 prompt 中明确列出：

```
| Rule ID | 真实定义 | LLM 常犯错误 |
|---------|---------|-------------|
| javascript:S106 | 不存在 | 用来报 console.log |
| java:S3305 | @Configuration factory injection | 用来报过期依赖 |
| java:S2115 | DB密码安全 (Blocker) | 报成 High |
```

---

## 5. Quality Gate 必须全局一致

**教训来源**: v1.75/v1.8 — README、steering、skills 三处 gate 定义不一致

### 问题

Quality Gate 是"通过/不通过"的最终判定。如果不同文档对 gate 的定义不同：
- 开发团队看 README 说 "0 High 就挂" → 修了所有 High
- 实际 skill 执行时 gate 是 "High+P0 才挂" → 报告说 PASS
- 双方对结果的理解不一致 → 信任崩塌

### 设计原则

**Single Source of Truth**: Quality Gate 只在一处定义（steering.md），
所有其他地方引用或复制必须完全一致。

```
Shared Quality Gate:
  FAIL if:
    - severity = Critical (any priority)
    - severity = High AND priority = P0
  PASS otherwise.
```

**检查清单**（每次修改 gate 时必须同步）:
- [ ] `steering.md`
- [ ] `README.md`
- [ ] `batch-scan/skill.md`
- [ ] `sonarqube-review/skill.md`
- [ ] `secure-coding-baseline-review/skill.md`
- [ ] `summary-report/skill.md`
- [ ] `rescan/skill.md`

### 经验法则

- **Medium 不应该 block gate** — Medium 问题太多，如果 block 则几乎所有项目都 Fail
- **High 不应该无条件 block** — 不是所有 High 都是 release blocker，P0 区分了紧迫性
- **Critical 必须无条件 block** — 没有妥协空间

---

## 6. 报告格式标准化是可比较性的基础

**教训来源**: v1.65/v1.75 — 不同模块的报告格式不一致，无法横向对比

### 问题

当 4 个模块的报告格式各不相同（有的 finding 有 CVSS，有的没有；有的按 list
格式，有的按 table 格式），Summary Report 就无法自动化合并。

### 设计原则: Unified Finding Header

所有报告类型（R&M / Security / Rescan）的每条发现必须以**完全相同的 4 行头**开始：

```
**Risk Level**: CRITICAL / HIGH / MEDIUM
**CVSS Score**: 9.8 (Critical) / N/A — non-security rule
**File**: `src/main/java/com/example/Config.java:42`
**Associated CVE**: CVE-2016-4437 pattern / N/A — code logic defect (CWE-xxx)
```

**强制规则**:
- 4 行必须是独立行，不是 list item（不加 `- ` 前缀）
- 顺序固定：Risk Level → CVSS → File → CVE
- Security 报告中 CVSS 必填，R&M 报告中写 `N/A`
- 写每条 finding 前必须自检 4 行是否齐全

### 为什么这很重要

1. **自动化合并**: Summary Report 可以 grep/parse 统一格式
2. **横向对比**: 不同模块的同类问题可以直接并排比较
3. **交付一致性**: 客户收到的所有报告"看起来"是同一个系统产出的
4. **减少遗漏**: CVSS 必填规则避免了安全报告缺少评分的问题

---

## 7. 模块发现必须自动化且确定

**教训来源**: v1.75 hardcoded manifest → v1.8 auto-discovery

### 问题的演化

| 阶段 | 方案 | 问题 |
|------|------|------|
| v1.6 | 无固定规则 | 每次运行发现的模块不同 → Summary 漂移 |
| v1.75 | 硬编码 manifest | 确定了，但锁死在一个项目上 |
| v1.8 | 自动发现 + 可选 manifest | 既确定又通用 |

### 设计原则

```
优先使用 module-manifest.md（如果存在）
  → 团队可以显式控制模块列表

否则自动检测（按优先级链）:
  Maven → Gradle → npm → Go → 目录启发式

检测结果排序后固定，整次扫描不再变化
```

**关键**: 自动发现 ≠ 不确定。只要检测逻辑是确定性的（基于固定的文件内容），
同一代码库每次检测结果就是一样的。

### 模块发现的坑

| 坑 | 解决方式 |
|----|---------|
| Maven parent 有多个 child module | 整体算一个模块，不拆分 |
| monorepo 中 `.kiro/` 被识别为模块 | 明确排除列表 |
| 开发者临时添加实验目录 | 只认有 build file 的目录 |
| npm workspace 中的 packages 太细 | 按 workspace 配置，不按目录 |

---

## 8. 深度追踪需要明确的停止条件

**教训来源**: v1.77 → v1.8 — auth 追踪无限深导致非确定性

### 问题

"Follow the call chain to the leaf implementation" 听起来明确，但实际上：
- 代码可能有 10 层抽象包装
- 不同运行中，LLM 可能追踪到不同深度
- 深层代码可能进入框架内部（Spring Security 的 200 个类）
- 追踪越深，消耗 token 越多，产出不确定性越大

### 设计原则

**任何"追踪"类指令必须有硬性停止条件**:

```
✗ "Follow to the leaf implementation"（无界）
✓ "Follow at most 3 hops from the entry point"（有界）
✓ "If not found within 3 hops, mark as Not Found"（优雅降级）
```

### 通用模板

```
追踪规则:
- 起点: [明确的入口类/方法]
- 最大深度: [N] 层调用
- 每层定义: 一次方法调用或类委托
- 超过深度时: 记录最深到达的类，标注 "Not Found — exceeded N-hop limit"
- 不追踪进: 框架内部类、第三方库源码、测试代码
```

---

## 9. 自校验机制比事后修复更有效

**教训来源**: v1.65 rm-report-validator — 报告生成后才发现规则错误

### 问题

如果校验只在报告生成后做（"先生成，再用另一个 skill 检查"），那：
- 错误已经写入文件，修复需要重新生成
- 用户可能跳过校验步骤
- 两个 skill 之间的一致性难以保证

### 设计原则

**校验逻辑必须内嵌在生成流程中（Step N: Self-Validation）**:

```
生成流程:
  Step 1: 准备（读取标准文件）
  Step 2: 扫描（逐规则检查代码）
  Step 3: 分级（分配 severity 和 priority）
  Step 4: 自校验 ← 在写报告之前
    - V-01: 每个 rule ID 存在
    - V-02: 每个 severity 匹配
    - V-03: 每个描述准确
    - V-04: 每个 Medium 有 priority
    - 不通过的 → 移到 Appendix
  Step 5: 生成报告
```

**额外保险**: 仍然提供独立的 `@rm-report-validator` skill 作为事后复核，但
主路径上校验已经完成。

### 校验清单的设计

好的校验清单是**可机械执行的**（grep、count、compare），而不是主观判断：

```
✓ "standards file 中能找到 ### java:S2095 —"（机械）
✗ "确认 severity 是否合理"（主观）

✓ "report 中的 rule description == standards file 的标题"（机械）
✗ "确认描述是否准确反映了问题"（主观）
```

---

## 10. 方案必须与项目结构解耦

**教训来源**: v1.75 → v1.8 — hardcoded manifest 导致换项目就失败

### 问题

在一个特定项目上做 PoC 时，很容易把项目特有的信息写进方案：
- 固定的模块名（`lab-backend`, `lab-admin-web`）
- 固定的模块数量（"exactly 4 modules"）
- 固定的技术栈假设（"Java + Vue"）
- 固定的报告数量（"9 reports"）

这在 PoC 阶段没问题，但方案要推广时就成了障碍。

### 设计原则

| 应该固定的 | 应该参数化的 |
|-----------|-------------|
| 报告模板格式 | 模块列表 |
| Quality Gate 规则 | 模块数量 |
| Severity 映射表 | 技术栈（自动检测） |
| 规则标准文件 | 项目名称 |
| 扫描流程步骤 | 输出路径中的变量 |
| Finding header 格式 | 日期 |

### 通用化检查表

把方案从一个项目推广前，搜索以下模式并替换为参数化：

```bash
# 搜索硬编码的项目名
grep -r "lab-backend\|lab-admin\|lab-wxapp" .kiro/

# 搜索固定数字
grep -r "exactly 4\|4 modules\|9 reports" .kiro/

# 搜索固定路径
grep -r "lab-manage-backend/" .kiro/
```

---

## 11. 版本演进的节奏与策略

**教训来源**: 7 个版本的迭代节奏回顾

### 版本拓扑

```
v1.6 (初始)
 ├── v1.65 (客户端改进: gate + validator + rule fix)
 └── v1.7  (运维团队: 确定性 D1-D7)
      │
      v1.75 (合并 v1.65 + v1.7)
      │
      v1.76 (修架构拓扑: admin plane)
      │
      v1.77 (修 auth 深度: password hash + token issuance)
      │
      v1.8  (结构性改进: pattern matching + open discovery + bug fixes)
      │
      v1.8.1 (全量扫描: 消除所有采样，彻底解决 gate 不一致)
```

### 版本类型

| 类型 | 特征 | 例子 |
|------|------|------|
| **补丁版** | 修一个具体 bug，不改结构 | v1.76, v1.77 |
| **合并版** | 将并行开发的分支合回 | v1.75 |
| **结构版** | 改变核心机制，影响多个文件 | v1.7 (确定性), v1.8 (pattern matching) |
| **简化版** | 删除复杂逻辑，用更简单的方案替代 | v1.8.1 (删除采样逻辑→全量) |

### 演进策略建议

1. **每个版本只改一件事**（v1.76 只修拓扑，v1.77 只修深度）。多件事混在一起
   出了问题难以定位。

2. **Release Notes 必须解释 WHY，不只是 WHAT**。读者需要理解：
   - 这个版本解决了什么观察到的问题
   - 根因是什么
   - 为什么选择这个修复方案

3. **兼容性声明是必需品**。每个版本必须说清楚：
   - 哪些规则/行为不变
   - 哪些输出格式不变
   - 是否需要重新运行之前的步骤

4. **Bug 不要攒着修**。v1.8 同时修了 5 个 bug，理想情况下应该在发现时就修。
   攒着修的风险是：用户在多个版本中都受 bug 影响但不知道。

---

## 12. 采样是确定性的敌人——全量扫描是终极解

**教训来源**: v1.8 → v1.8.1 — 同一模型同一代码同一 skill 产出不同 Quality Gate

### 问题

v1.8 的 Pattern Matching 在理论上是确定性的（同文件名→同选择），但在**执行层面**
存在不确定性：

```
同一个 Opus 4.8, 同一份代码, 同一个 v1.77 skill（MD5 完全一致）:

  Run 14: 读到了 ph-fss-admin 的 Excel export 方法 → 报 java:S2095 Critical → FAIL
  Run 15: 没读到这些文件 → 0 Critical → PASS
  Run 0606: 读到了 → 报 java:S2095 Critical → FAIL
```

**根因**: 即使规则写了"每 package 最多读 3 个 Tier-1 文件"，LLM 在**执行这个规则**
时的行为并不完全一致。它可能对"package 边界在哪里"、"这个文件算不算 Tier-1"
有不同的瞬时判断。

### 核心洞察

> **凡是需要 LLM 做"选择"的地方，就是不确定性的入口。**
>
> 唯一能消除选择的方式是：**不给它选择的机会——全部读取。**

### 设计原则

```
✗ "读取前 5 个文件"（LLM 可能数错）
✗ "读取匹配模式的文件"（LLM 可能漏匹配）
✗ "读取最重要的文件"（主观判断）
✓ "读取所有源文件"（零自由裁量）
```

### 代价与取舍

| 方案 | 确定性 | Token 消耗 | 适用场景 |
|------|--------|-----------|---------|
| 字母序采样 | ❌ 低 | 低 | 不推荐 |
| Pattern Matching + budget | ⚠️ 理论高/实践中等 | 中等 | 不推荐（v1.8 已证明不够） |
| 全量扫描 | ✅ 完美 | 高 | **v1.8.1 推荐** |

**结论**: 对于代码审查这种需要可复现结果的场景，token 消耗不是问题——Quality Gate
的可信度才是问题。宁可多花 token，不可让同一代码出两种结论。

---

## 13. LLM 自校验不可信——必须有外部验证

**教训来源**: v1.8.1 Quality Gate 分析 — Haiku 声称自校验通过但实际规则 ID 不存在

### 问题

Haiku 4.5 在报告末尾写道：

```
- V-01 Rule ID Verification: All 12 issues map to verified SonarQube rule IDs. ✓
- V-02 Severity Alignment: All severities match SonarQube standards file exactly. ✓
```

但实际验证发现：
- `java:S2755` — 标准文件中不存在（编造）
- `java:S116` — 标准文件中不存在（编造）
- `java:S2077` — 标准文件中不存在（编造）
- `java:S1119` — 存在但含义完全不同（张冠李戴）

**LLM 的"自校验"本质上是让同一个大脑检查自己的输出。** 如果生成时就犯了错（从
训练数据中回忆出不存在的规则），校验时它会用同样的错误记忆来"确认"。

### 设计原则

```
┌─────────────────────────────────────────────┐
│  LLM 自校验（必要但不充分）                    │
│  - 在生成流程中内嵌，减少明显错误              │
│  - 对强模型(Opus/Sonnet)有效率约 90%+         │
│  - 对弱模型(Haiku)基本无效                    │
└─────────────────────────────────────────────┘
                    +
┌─────────────────────────────────────────────┐
│  外部验证（必须有）                            │
│  - 脚本化: grep 标准文件验证每个 Rule ID       │
│  - 不用 LLM: 用确定性程序执行                  │
│  - 失败时: 自动将不合规 finding 移到 Appendix  │
└─────────────────────────────────────────────┘
```

### 实现建议

```bash
# 外部验证脚本示例 (post-generation)
for rule_id in $(grep -oP 'java:S\d+|javascript:S\d+|javabugs:S\d+' report.md); do
  if ! grep -q "### $rule_id" standards.md; then
    echo "INVALID: $rule_id not found in standards"
  fi
done
```

这类验证**必须是独立于 LLM 的程序**，而不是让 LLM 在 prompt 中"请验证"。

---

## 14. CVSS 评分需要锚定——不能完全交给 LLM 主观判断

**教训来源**: v1.8.1 分析 — 同一安全问题被评为 CRITICAL/HIGH/MEDIUM 三种 severity

### 问题

BSL Security 报告要求为每个发现计算 CVSS v3.1 分数。CVSS 有 8 个度量值
（AV/AC/PR/UI/S/C/I/A），每个都需要判断。LLM 对同一问题的判断不一致：

**案例: "认证 token 存储在微信小程序 localStorage"**

| 模型 | AV | AC | PR | UI | 评分 | Severity |
|------|----|----|----|----|------|----------|
| Sonnet | Network | Low | None | None | 9.1 | CRITICAL |
| Opus | Network | Low | Low | None | 7.5 | HIGH |
| Haiku | Local | High | Low | Required | 4.2 | MEDIUM |

分歧来源：
- **Attack Vector**: 是 Network（远程可利用）还是 Local（需要物理接触设备）？
- **Privileges Required**: 是 None（任何人）还是 Low（需要先获取某种权限）？

### 设计原则

**为高频安全模式建立 CVSS 参照表**，减少 LLM 的自由判断空间：

```markdown
### CVSS Anchor Table (Security Report 使用)

| 安全模式 | 标准 Vector | 分数 | Severity |
|----------|------------|------|----------|
| 硬编码密钥/密码在源码中 | AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H | 9.8 | CRITICAL |
| SQL 注入 (无 WAF) | AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N | 9.1 | CRITICAL |
| SQL 注入 (有 WAF/参数化部分) | AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N | 8.1 | HIGH |
| Token 明文存储在客户端 | AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N | 7.1 | HIGH |
| CORS 允许所有 origin | AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:L/A:N | 7.1 | HIGH |
| 日志中包含敏感信息 | AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N | 5.5 | MEDIUM |
| 使用弱随机数 | AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N | 5.9 | MEDIUM |
| 过期依赖（有已知 CVE） | 参照该 CVE 的官方 CVSS | — | — |
```

**规则**：
- 如果发现匹配参照表中的模式 → 使用表中预定义的 vector 和分数
- 如果不匹配 → LLM 自行评估，但必须逐字段给出理由
- 参照表优先级高于 LLM 判断

### 为什么这很重要

CVSS 分数直接影响 severity → severity 直接影响 Quality Gate。如果同一问题的
CVSS 在 6.9（Medium）和 7.0（High）之间浮动，gate 结论就会翻转。参照表消除了
这个边界问题。

---

## 15. 模型能力是方案的硬性前提——不是所有模型都能用

**教训来源**: v1.8.1 分析 — Haiku 4.5 产出的报告从规则 ID 到日期全部不可信

### 问题

Haiku 4.5 在代码审查场景中的表现：

| 能力维度 | 表现 | 证据 |
|----------|------|------|
| 规则 ID 准确性 | ❌ 编造不存在的 ID | java:S2755, java:S116, java:S2077 |
| 规则描述准确性 | ❌ 张冠李戴 | S1119="Labels"说成"Deprecated methods" |
| 自校验有效性 | ❌ 通过了不该通过的 | 声称 V-01 ✓ 但 ID 不存在 |
| Gate 规则遵守 | ❌ 发明新状态 | 创造了 "CONDITIONAL PASS" |
| 日期准确性 | ❌ 幻觉 | 2026 年运行产出 2025-01-15 |
| Severity 判断 | ❌ 严重偏差 | 同一问题评为 Medium（其他模型评 HIGH/CRITICAL）|

### 设计原则

**不是所有 LLM 都适合执行结构化代码审查。** 方案设计必须声明模型最低要求：

```
模型适用性矩阵:

| 模型 | 逆向工程 | R&M 扫描 | Security 扫描 | 生产报告 |
|------|---------|---------|--------------|---------|
| Opus 4.8+ | ✅ | ✅ | ✅ | ✅ 推荐 |
| Sonnet 4.6+ | ✅ | ✅ | ✅ | ✅ 可用 |
| Haiku 4.5 | ⚠️ 仅供测试 | ❌ | ❌ | ❌ 禁止 |
```

### 如何判断一个模型是否适用

在正式使用前，用一个**已知答案的小代码库**做验证：

1. 准备一个包含 3-5 个已知问题的小项目（手动植入 S2095 资源泄漏、S3776 复杂度超标等）
2. 运行扫描
3. 检查：
   - 所有已知问题是否被发现？
   - 报告中的 Rule ID 是否全部存在于标准文件中？
   - Severity 是否与标准文件一致？
   - 有没有编造的发现？
4. 通过率 < 90% → 该模型不适合生产使用

### 不同模型的使用策略

| 策略 | 说明 |
|------|------|
| **单模型生产** | 选定一个强模型（Opus），所有正式报告只用它 |
| **多模型交叉验证** | 用 2 个模型分别扫描，取 findings 的交集作为高置信度结果 |
| **强模型生成 + 弱模型辅助** | Opus 生成报告，Sonnet 做 adversarial review（尝试推翻每个 finding） |

---

## 总结：核心设计原则清单

| # | 原则 | 一句话 |
|---|------|--------|
| 1 | 确定性优先 | 同一代码 = 同一报告，用结构约束而非祈祷实现 |
| 2 | 理解先于评判 | 先逆向工程理解系统，再做规则扫描 |
| 3 | 全量扫描优于任何采样 | 任何"选择"都是不确定性入口，全读是终极解 |
| 4 | 规则映射严格，LLM 发现隔离 | Main body 只放规则匹配，Appendix 放 LLM 发现 |
| 5 | Gate 全局一致 | 所有文档的 Quality Gate 必须是同一份定义的副本 |
| 6 | 格式标准化 | 统一 Finding Header 让报告可合并可对比 |
| 7 | 模块发现自动化 | 自动检测 + 可选手动覆盖，不硬编码 |
| 8 | 追踪有界 | 任何"follow"指令都要有 hop limit |
| 9 | 校验内嵌 + 外部验证 | LLM 自校验不可信，必须有独立程序做规则存在性检查 |
| 10 | 与项目解耦 | 方案不应包含特定项目的名字、路径、数量 |
| 11 | 版本聚焦 | 每个版本解决一个明确问题，说清 why |
| 12 | CVSS 评分锚定 | 高频安全模式用参照表固定分数，消除边界翻转 |
| 13 | 模型有门槛 | 声明最低模型要求，弱模型（Haiku）禁止用于生产报告 |

---

## 附录：常见失败模式速查

| 失败模式 | 症状 | 根因 | 修复 |
|----------|------|------|------|
| 报告每次不同 | Summary 的 issue 数量波动 | 无排序规则或 per-instance 报告 | D1-D7 确定性规则 |
| 同一代码 gate 翻转 | 跑3次，2次FAIL 1次PASS | 文件采样不确定性 | 全量扫描（v1.8.1） |
| 架构描述错误 | Admin 被画成走 Gateway | 没读 frontend .env 和 proxy config | Step 1.7 mandatory read |
| 关键文件被跳过 | 报告中缺少核心 Service 的描述 | 字母序采样 | 全量扫描（v1.8.1） |
| 规则 ID 不存在 | Reviewer 查不到 `java:S2755` | LLM 从训练数据回忆 | 外部脚本 grep 验证 |
| 自校验失效 | 报告声称 V-01 ✓ 但 ID 实际不存在 | LLM 用同一错误记忆做"验证" | 独立程序做校验，不信 LLM |
| Severity 被篡改 | Medium 规则报成 High | LLM 觉得"严重"就升级 | V-02 strict severity mapping |
| CVSS 边界翻转 | 同一问题评为 6.9(Med) 或 7.0(Hi) | LLM 对 CVSS 维度判断波动 | CVSS 参照表锚定 |
| Gate 定义矛盾 | README 说 Fail 但报告说 Pass | 多处定义不同步 | Single source of truth |
| Gate 状态被发明 | 出现 "CONDITIONAL PASS" | 弱模型不遵守二值约束 | 明确声明只有 PASS/FAIL |
| 换项目就报错 | "Module lab-backend not found" | 硬编码 manifest | Auto-discovery + optional override |
| Auth 信息缺失 | 不知道用的 BCrypt 还是 MD5 | 只读到 realm/filter 没追到实现 | 3-hop leaf tracing |
| CVSS 分数缺失 | Security finding 没有评分 | Skill 没强制要求 | Self-check before each finding |
| 报告无法合并 | Summary 生成失败 | 模块报告格式不一致 | Cross-module format consistency policy |
| 弱模型产出垃圾 | 规则编造+日期错误+gate 状态发明 | 模型能力不足 | 设定模型最低要求，Haiku 禁用 |
| 日期幻觉 | 报告日期 2025-01-15（不可能） | Haiku 无法正确使用系统日期 | 仅用 Opus/Sonnet |

---

*本文档随版本演进持续更新。最后更新: v1.8.1 (2026-06-09)*
