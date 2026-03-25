# java-code-simplifier

Java 代码优化技能，在不改变任何功能的前提下，自动检查并改进 Java 代码的清晰度、安全性和可维护性。

## 安装

```bash
npx skills add https://github.com/lltx/skills --skill java-code-simplifier
```

## 功能

覆盖 8 个维度的 Java 代码优化检查：

- **空值安全** - 检查链式调用 NPE 风险，推荐 `Optional` 用法
- **异常处理** - 识别空 catch 块、异常链丢失、过宽捕获
- **集合与 Stream** - 避免迭代时修改集合，合理选择 Stream vs for 循环
- **资源管理** - 确保 `Closeable` 资源使用 try-with-resources
- **并发安全** - 检查共享可变状态、check-then-act 竞态条件
- **Java 惯用法** - equals/hashCode 成对实现，Builder 模式，模式匹配
- **API 设计** - 布尔参数改枚举，返回 `Optional`，公共 API 输入校验
- **性能热点** - 循环内字符串拼接、正则预编译、N+1 查询

## 用法

### 直接调用（指定文件）

```bash
# 审计单个文件
/java-code-simplifier UserService.java

# 审计指定路径
/java-code-simplifier src/main/java/com/example/service/UserService.java

# 同时审计多个文件
/java-code-simplifier UserService.java OrderController.java
```

### 默认调用（无参数）

不传参数时，自动检测并审计所有**未提交的后端 Java 文件**（排除测试类）：

```bash
/java-code-simplifier
# → 等价于：git diff --name-only HEAD | grep '\.java$' | grep -v 'src/test/'
```

适合在 `git commit` 前做一次快速审查。

## 触发方式

Claude Code 也会在以下场景自动使用此技能：

- "优化这段 Java 代码"
- "简化 / 清理 / 重构 Java 代码"
- "review 一下这个类"
- 完成任何 Java 编码任务后（自动建议）

## 示例

**输入代码（有问题）：**

```java
// NPE 风险 + 资源泄露 + 吞异常
public String readFile(String path) {
    try {
        FileInputStream fis = new FileInputStream(path);
        return user.getName().toUpperCase();
    } catch (Exception e) {
        return null;
    }
}
```

**优化建议：**

```
## Java 代码优化建议：readFile

### 严重
- 第 4 行：`user.getName()` 可能为 null，建议用 Optional 保护
- 第 3 行：FileInputStream 未用 try-with-resources，存在资源泄露风险

### 改进
- catch 块吞掉了异常且返回 null，建议记录日志并抛出或返回 Optional<String>
```
