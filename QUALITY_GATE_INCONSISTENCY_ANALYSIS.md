# Quality Gate 不一致性分析报告

**分析对象**: PH-Lab 20260601 代码库，使用 ops-code-review-kit v1.77 (+ 一份 v1.65)
**扫描结果来源**: s3://alex-ai-agent-727166653485/philips-code-review/PH-Lab 20260601_Opus_4.8_1.65_3.zip
**分析日期**: 2026-06-09

---

## 1. 实验条件

所有 v1.77 扫描使用**完全相同的 skill 文件**（MD5 校验一致）和同一份代码库。

| 扫描 ID | 模型 | Kit 版本 | Skill MD5 一致 |
|---------|------|---------|---------------|
| Opus_4.8_1.77_14 | Claude Opus 4.8 | v1.77 | ✓ |
| Opus_4.8_1.77_15 | Claude Opus 4.8 | v1.77 | ✓ |
| Opus_4.8_1.77_0606 | Claude Opus 4.8 | v1.77 | ✓ |
| Sonnet_4.6_1.77_15 | Claude Sonnet 4.6 | v1.77 | ✓ |
| Haiku_4.5_1.77_15 | Claude Haiku 4.5 | v1.77 | ✓ |
| Opus_4.8_1.65_3 | Claude Opus 4.8 | v1.65 | N/A（不同版本）|

---

## 2. Quality Gate 结果对比

### 2.1 R&M (Reliability & Maintainability) Gate

| 扫描 | lab-backend | lab-manage-backend | lab-admin-web | lab-wxapp |
|------|-------------|-------------------|---------------|-----------|
| **Opus run14** | ❌ FAIL (S2095 Critical) | ❌ FAIL (S2095 Critical) | ✅ PASS | ✅ PASS |
| **Opus run15** | ✅ PASS (0 Critical) | ✅ PASS (0 Critical) | ✅ PASS | ✅ PASS |
| **Opus 0606** | ❌ FAIL (S2095 Critical) | ❌ FAIL (S2095 Critical) | ✅ PASS | ✅ PASS |
| **Sonnet** | ✅ PASS (0 Critical) | ✅ PASS (0 Critical) | ✅ PASS | ❌ FAIL (S2189 Critical) |
| **Haiku** | ❌ FAIL (fabricated) | ❌ FAIL (fabricated) | ❌ FAIL (S2970 Critical) | ✅ PASS |
| **Opus v1.65** | ❌ FAIL (S2095 Critical) | ✅ PASS | ✅ PASS | ✅ PASS |

### 2.2 Security Gate

| 扫描 | lab-backend | lab-manage-backend | lab-admin-web | lab-wxapp |
|------|-------------|-------------------|---------------|-----------|
| **Opus run14** | ❌ FAIL (3 Critical) | ❌ FAIL | ❌ FAIL | ❌ FAIL (1 Critical) |
| **Opus run15** | ❌ FAIL (1 Critical) | ❌ FAIL | ❌ FAIL | ❌ FAIL (High P0) |
| **Opus 0606** | ❌ FAIL (3 Critical) | ❌ FAIL | ❌ FAIL | ❌ FAIL |
| **Sonnet** | ❌ FAIL | ❌ FAIL | ❌ FAIL | ❌ FAIL |
| **Haiku** | ❌ FAIL (1 Critical) | ❌ FAIL | ⚠️ "CONDITIONAL" | ✅ PASS |
| **Opus v1.65** | ❌ FAIL | ❌ FAIL | ❌ FAIL | ❌ FAIL |

### 2.3 Overall Gate 差异总结

- **同一模型 (Opus 4.8) 不同运行**: R&M gate 在 lab-backend 和 lab-manage-backend 上 2/3 次 FAIL, 1/3 次 PASS
- **不同模型对同一代码**: lab-wxapp R&M gate 只有 Sonnet FAIL, 其他全 PASS
- **Haiku 独有问题**: 发明了 "CONDITIONAL PASS" 状态；lab-wxapp Security 唯一 PASS

---

## 3. 根因分析

### 根因 1: 代码文件采样的非确定性（主因）

**影响**: 同一模型同一 skill 对同一代码产出不同结论

v1.77 使用字母序采样策略（每 package 前 N 个文件）。LLM 在执行时对"哪些文件需要读"的判断存在随机性：

| 运行 | lab-backend 是否读到了包含资源泄漏的文件 | 结果 |
|------|----------------------------------------------|------|
| Opus run14 | ✅ 读到 `EasyExcel.write(response.getOutputStream())` | 报 S2095 Critical → FAIL |
| Opus run15 | ❌ 没读到相关文件 | 未发现资源泄漏 → PASS |
| Opus 0606 | ✅ 读到了 | 报 S2095 Critical → FAIL |

**关键证据**: run14 报告明确引用了 `ph-fss-admin` export paths 和 Excel/stream writers，而 run15 完全没有提及 S2095 规则，说明 **run15 根本没有读到包含资源泄漏代码的文件**。

这正是 v1.8 用 Architecture-Role Pattern Matching 解决的问题——按文件命名模式而非字母序选择文件，确保 `*Service`, `*Controller` 等关键文件必被读取。

---

### 根因 2: 规则适用性判断的主观性

**影响**: 同一文件的同一代码，不同模型/不同运行判定不同规则

| 代码模式 | Opus run14 判定 | Sonnet 判定 | Opus run15 判定 |
|----------|----------------|-------------|-----------------|
| `setInterval` 轮询登录状态 (lab-wxapp) | 未报 | javascript:S2189 CRITICAL | 未报 |
| 资源未 close (lab-backend) | java:S2095 CRITICAL | 未报 | 未报 |

**分析**: `setInterval` 是否构成"无限循环"是一个**边界判断**——从技术上说，如果 `getIsLogined()` 永远为 false（网络失败场景），循环确实不会终止，但在正常路径下它是会终止的。

- Sonnet 4.6 判定为匹配 S2189（Blocker），认为"退出条件可能永远不满足"
- Opus 4.8 两次运行都没有认为这是无限循环

这类边界案例的判断取决于模型对"实际运行中是否真的无限"的理解深度。

---

### 根因 3: Security 报告中 CVSS 评分的主观浮动

**影响**: 同一安全问题被不同运行评为不同 severity

**典型案例: lab-wxapp token 存储在 localStorage**

| 扫描 | 问题描述 | 判定 Severity | CVSS |
|------|---------|--------------|------|
| Opus run14 | "Authentication token stored in mini-program local storage" | HIGH | — |
| Sonnet | "Bearer auth token + PII stored in plaintext uni.setStorageSync" | CRITICAL P0 | 9.1 |
| Haiku | "Missing Input Validation on User Token Storage" | MEDIUM | — |

三个模型对**完全相同的代码**给出了 CRITICAL / HIGH / MEDIUM 三种不同的 severity。区别在于：
- Sonnet 把问题框架为"存储了 PII + bearer token"→ 信息泄露 → CVSS 9.1
- Opus 框架为"token 在 localStorage"→ 客户端存储不安全 → High
- Haiku 框架为"缺少输入验证"→ 一般问题 → Medium

Security 报告使用 BSL 规则映射 + CVSS 评分，CVSS 的 8 个度量值由 LLM 主观判定，即使同一个 BSL 控制点，Attack Vector、Privileges Required 等参数的判断差异直接导致分数跨越 severity 阈值。

---

### 根因 4: Haiku 模型能力不足导致幻觉

**影响**: 报告看似完整但内容虚假

Haiku 4.5 的报告存在严重的规则幻觉问题：

| 模块 | 报告的 Rule ID | 标准文件中实际情况 | 错误类型 |
|------|---------------|-------------------|---------|
| lab-backend BUG-01 | java:S116 | 不存在 | **编造 Rule ID** |
| lab-backend BUG-02 | java:S2189 | 存在但 Java 版不同 | 跨语言错误映射 |
| lab-manage BUG-01 | java:S2755 | 不存在 | **编造 Rule ID** |
| lab-manage BUG-02 | java:S116 | 不存在 | **编造 Rule ID** |
| lab-manage BUG-04 | java:S2077 | 不存在 | **编造 Rule ID** |
| lab-manage BUG-05 | java:S1119 | 存在但含义不匹配 | **描述错误** (标准="Labels should not be used", Haiku 说="Deprecated methods") |

**更严重的问题**: Haiku 在报告末尾声明 **"V-01 Rule ID Verification: All issues map to verified SonarQube rule IDs. ✓"**，即 **自校验通过了实际不通过的内容**。这说明 Haiku 无法真正执行 self-validation 步骤。

**日期幻觉**: 所有 Haiku 报告日期为 `2025-01-15`，而代码和运行时间都在 2026 年 6 月。

---

### 根因 5: Haiku 发明了不存在的 Gate 状态

Haiku 对 lab-admin-web Security 报告发明了 "CONDITIONAL PASS" 状态：

> "1 High P0 issue exists; TECHNICALLY SHOULD FAIL, but per report generation logic,
> if only 1 High P0 and otherwise sound, marked as CONDITIONAL PASS pending remediation."

Quality Gate 定义中**根本没有 CONDITIONAL 状态**。Gate 只有 PASS 和 FAIL。Haiku 在 Summary Report 中把这个模块标为 "⚠️ CONDITIONAL" 而非 FAIL，直接改变了 gate 结论。

---

### 根因 6: 发现数量/覆盖面的随机波动

同一代码 lab-backend，不同运行发现的 issue 数量差异巨大：

| 扫描 | Security 发现数 | Critical 数 | 涵盖的安全问题 |
|------|----------------|------------|---------------|
| Opus run14 | 9 | 3 | SQL注入, 硬编码密钥, Druid默认密码, CORS, token弱, 明文比较... |
| Opus run15 | 8 | 1 | 硬编码密钥, SQL注入, DB密码, 加密key, CORS, token弱, Druid, stdout... |
| Sonnet | 7 | 0(标注) | fastjson CVE, 日志PII, 过期框架, CORS, session, 错误信息, 弱随机... |

即使 Critical 数量影响了 gate（3 Critical vs 1 Critical 都是 FAIL），**发现的覆盖面差异意味着修复建议完全不同**。开发团队如果只看一份报告来修，可能漏掉其他报告发现的问题。

---

## 4. 问题严重程度排序

| 优先级 | 根因 | 影响 | 解决方案 |
|--------|------|------|---------|
| **P0** | 代码文件采样非确定性 | 同模型不同运行 gate 结果不同 | v1.8 Architecture-Role Pattern Matching |
| **P0** | Haiku 规则幻觉 | 报告看似正确实际虚假 | 禁止 Haiku 用于此场景 / 外部校验 |
| **P1** | CVSS 评分主观性 | 同一问题跨越 severity 阈值 | 需要锁定 CVSS 评分模板或使用评分参照表 |
| **P1** | 规则适用边界判断 | 不同模型对边界案例判断不同 | 在标准文件中增加 apply/not-apply 示例 |
| **P2** | 发现覆盖面波动 | 不同运行发现不同子集的问题 | 增加文件读取范围 / 多次扫描合并 |
| **P3** | Haiku 日期幻觉 | 报告日期错误 | 模型能力限制，无法通过 prompt 修复 |

---

## 5. 已解决 vs 未解决

### v1.8 已解决

| 问题 | v1.8 解决方案 |
|------|-------------|
| 文件采样非确定性 | Architecture-Role Pattern Matching（按命名模式选文件，离散判断） |
| 发现覆盖面不够 | Tier-1 文件必读，覆盖所有架构角色文件 |

### 仍未解决（需要 v1.9+ 考虑）

| 问题 | 建议方案 |
|------|---------|
| CVSS 评分浮动 | 为常见安全模式建立 **CVSS 参照表**（pattern → 预定义 vector），减少主观判断空间 |
| 规则边界判断差异 | 在标准文件中为高风险规则（S2095, S2189等）增加 **适用场景示例** 和 **不适用场景示例** |
| Haiku/弱模型的幻觉 | 增加 **外部校验步骤**（在报告生成后，用独立 grep 验证每个 Rule ID 是否真实存在于标准文件中）|
| 发明 gate 状态 | 在 Quality Gate 定义中明确声明 **"只有 PASS 和 FAIL 两种状态，不允许其他分类"** |
| 跨模型一致性 | 建立 **模型最低要求**：推荐 Opus/Sonnet 用于生产报告，Haiku 仅用于测试 |

---

## 6. 模型适用性评估

| 模型 | 规则映射准确度 | 自校验有效性 | Gate 结论可靠性 | 推荐用途 |
|------|--------------|------------|---------------|---------|
| **Opus 4.8** | 高（偶尔遗漏但不编造） | 有效 | 高（但受采样影响） | ✅ 生产使用 |
| **Sonnet 4.6** | 高（边界判断偏严格） | 有效 | 高 | ✅ 生产使用 |
| **Haiku 4.5** | 低（编造 Rule ID，描述不匹配） | 无效（自称通过但实际失败） | 不可靠 | ❌ 不推荐用于代码审查 |

---

## 7. 建议行动

### 短期（立即）

1. **升级到 v1.8** — 解决文件采样非确定性问题
2. **设定模型最低要求** — 生产报告仅使用 Opus 4.8 或 Sonnet 4.6
3. **多次运行取交集** — 对关键项目，运行 2-3 次取 findings 的并集而非依赖单次运行

### 中期（v1.9 规划）

4. **CVSS 评分参照表** — 为 BSL 的 17 个安全域建立预定义的 CVSS vector 模板
5. **外部规则校验** — 报告生成后用脚本（非 LLM）grep 标准文件验证每个 Rule ID
6. **边界案例示例库** — 在标准文件中为高频争议规则添加 apply/not-apply 示例

### 长期（架构改进）

7. **两阶段扫描** — Phase 1: LLM 标记可疑代码位置 + 规则 ID → Phase 2: 确定性规则引擎验证映射
8. **Confidence scoring** — 对每个 finding 标注模型置信度，低置信度的不计入 gate

---

*分析完成。核心结论：v1.77 的 Quality Gate 不一致性主要由文件采样随机性驱动（P0），其次是 CVSS 评分主观性（P1）和弱模型幻觉（P0 for Haiku）。v1.8 的 Pattern Matching 解决了第一个问题，但后两个需要在标准文件层面进一步约束。*
