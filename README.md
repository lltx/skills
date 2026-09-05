# Skills 技能库

一个可复用的自动化技能集合，覆盖 Java 开发、本地诊断和文档查询等工作流。

## 快速开始

```bash
npx skills add https://github.com/lltx/skills --skill <技能名称>
```

## 可用技能

### code-tidy

Java 代码整理工具，自动完成代码规范化工作。

**安装：**

```bash
npx skills add https://github.com/lltx/skills --skill code-tidy
```

**功能：**

- **自动添加 Javadoc 注释** - 为类和 public/protected 方法添加规范的注释
- **更新日期注释** - 自动更新 `@date` 为当前日期，更新 Copyright 年份
- **代码格式化** - 使用 spring-javaformat-maven-plugin 格式化修改过的文件

**触发方式：**

- "整理代码"
- "添加注释"
- "格式化 Java"
- "更新日期注释"

**注释规范：**

- 自动跳过 getter/setter、@Override 方法
- 不重复添加已有完整注释
- 类注释包含：功能描述、@author、@date
- 方法注释包含：功能描述、@param、@return

### java-code-simplifier

Java 代码优化工具，在不改变任何功能的前提下提升代码的清晰度、安全性和可维护性。

**安装：**

```bash
npx skills add https://github.com/lltx/skills --skill java-code-simplifier
```

**功能：**

- **空值安全** - 检查链式调用 NPE 风险，推荐 `Optional` 用法
- **异常处理** - 识别空 catch 块、异常链丢失、过宽捕获
- **集合与 Stream** - 避免迭代时修改集合，合理选择 Stream vs for 循环
- **资源管理** - 确保 `Closeable` 资源使用 try-with-resources
- **并发安全** - 检查共享可变状态、check-then-act 竞态条件
- **Java 惯用法** - equals/hashCode 成对实现，Builder 模式，模式匹配
- **API 设计** - 布尔参数改枚举，返回 `Optional`，公共 API 输入校验
- **性能热点** - 循环内字符串拼接、正则预编译、N+1 查询

**触发方式：**

- "优化这段 Java 代码"
- "简化 / 清理 / 重构 Java 代码"
- "review 一下这个类"
- 完成任何 Java 编码任务后（自动建议）

### network-doctor

本地网络诊断工具，用只读基线先定位网速慢、延迟高、DNS 慢、Wi-Fi 弱、VPN/代理异常、MTU 或后台流量问题，再按“一次只改一个变量”的方式给出可回滚建议。

**安装：**

```bash
npx skills add https://github.com/lltx/skills --skill network-doctor
```

**功能：**

- **只读基线优先** - 先采集吞吐、延迟、丢包、DNS、路由、Wi-Fi、MTU、代理/VPN 和进程信号
- **分层诊断** - 区分 ISP、Wi-Fi/LAN、DNS、VPN/代理、MTU/TCP 和后台流量原因
- **安全变更门禁** - DNS、MTU、代理、VPN、防火墙、网络位置、`sudo` 等修改必须先确认
- **前后对比验证** - 每次只改一个变量，并用同一组指标复测
- **回滚要求** - 所有修改都必须给出旧值、恢复命令或 UI 路径

**触发方式：**

- "网络慢 / 网速慢 / 网速优化"
- "网络延迟高 / packet loss"
- "Wi-Fi 慢 / DNS 慢 / MTU 问题"
- "VPN 或代理影响网速"
- "帮我安全地把网络弄快"

### audit-agents-md

审计项目或全局的技能与 `AGENTS.md`，检查触发过宽、流程过重、授权冲突、失效引用和跨技能步骤衔接，并给出有文件位置与具体场景支撑的改写建议。

**安装：**

```bash
npx skills add https://github.com/lltx/skills --skill audit-agents-md
```

**用法：**

安装后，在支持技能的 Agent 中明确给出审计范围和是否修改。以下是 Codex 的调用示例；其他客户端按其技能调用方式使用。

审计当前项目：

```text
$audit-agents-md 审计当前项目内的所有技能和 AGENTS.md，只输出问题与改写建议，暂不修改文件。
```

审计全局个人指令：

```text
$audit-agents-md 审计 ~/.agents/skills、~/.codex/skills 及全局 AGENTS.md，给出完整覆盖清单和优先处理的问题。
```

按指定范围直接整改（将路径替换为实际项目路径）：

```text
$audit-agents-md 审计并精简 /absolute/project 内的技能和 AGENTS.md，直接修复已确认的触发过宽、重复指令和失效引用，保留原有业务约束，并验证修改。
```

需要包含 `CLAUDE.md` 时，在请求中明确说明。使用自定义 `CODEX_HOME` 时，全局范围填写实际的技能和指令路径。

**交付内容：**

- 每份目标文件的覆盖状态：已审阅、仅静态扫描或无法读取。
- 问题位置、触发场景、具体后果和最小改写建议，区分已确认问题与待验证候选。
- 已要求整改时，提供实际修改、必要验证和剩余问题；只要求审计时交付报告。

内置清单脚本需要 Python 3，安装 PyYAML 后可完整解析 YAML 前言；缺少 PyYAML 时仍可扫描，并标注解析限制。脚本只建立静态清单，语义审阅由 Agent 完成；文件字数变化不代表模型性能已经改善。

[查看技能定义](skills/audit-agents-md/SKILL.md) · [方法来源](skills/audit-agents-md/references/source-notes.md)

## 贡献

欢迎提交 PR 添加新的技能！每个技能需要在 `skills/` 目录下创建独立文件夹，并包含 `SKILL.md` 定义文件。

## 许可证

MIT
