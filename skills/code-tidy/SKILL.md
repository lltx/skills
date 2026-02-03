---
name: code-tidy
description: 整理本地未提交的 Git Java 代码。使用场景：(1) 对新增/修改的 Java 类和方法添加 Javadoc 注释，(2) 更新代码中的日期注释（@author、@since、Copyright 年份），(3) 使用 spring-javaformat 格式化代码。当用户说"整理代码"、"添加注释"、"格式化 Java"、"更新日期注释"时触发。
metadata:
  author: lengleng
  version: "1.0.0"
---

# Code Tidy v1.0.0

整理本地未提交的 Git Java 代码，添加 Javadoc 注释并更新日期。

## 工作流程

### 1. 获取未提交的 Java 文件

```bash
git diff --name-only --diff-filter=AM HEAD | grep '\.java$'
```

如果需要包含未跟踪文件：
```bash
git status --porcelain | grep '\.java$' | awk '{print $2}'
```

### 2. 添加 Javadoc 注释

**重要**：日期值必须通过 `date +"%Y-%m-%d"` 命令动态获取，不要使用写死的日期。

对每个文件执行：

**类注释模板**（如果缺失则添加）：
```java
/**
 * 类功能描述
 *
 * @author lengleng
 * @date $(date +"%Y-%m-%d")
 */
```

注意：`$(date +"%Y-%m-%d")` 表示执行命令获取当前日期，实际写入文件时使用命令输出值（如 `2026-02-03`）。

**方法注释模板**（对 public/protected 方法添加）：
```java
/**
 * 方法功能描述
 *
 * @param paramName 参数说明
 * @return 返回值说明
 */
```

### 3. 更新日期注释

**先获取当前时间**：

```bash
# 获取当前日期（YYYY-MM-DD 格式）
date +"%Y-%m-%d"

# 获取当前年份
date +"%Y"
```

使用获取的时间更新注释：

| 类型 | 查找模式 | 更新为 |
|------|----------|--------|
| @author 日期 | `@date YYYY/MM/DD` 或 `@date YYYY-MM-DD` | `date +"%Y-%m-%d"` 的输出 |
| @since 版本 | `@since X.X.X` | 保持不变（版本号由用户指定） |
| Copyright | `Copyright © YYYY` 或 `Copyright YYYY` | `date +"%Y"` 的输出 |

**日期格式**：使用 `YYYY-MM-DD` 格式（符合项目 linter 规范）

### 4. 格式化代码（可选）

**前置条件检查**：

1. 检查是否有修改的 Java 文件：
```bash
git diff --name-only --diff-filter=AM HEAD | grep '\.java$'
```
**如果没有修改的 Java 文件**：跳过格式化，不执行任何格式化命令。

2. 检查项目是否配置了 spring-javaformat 插件：
```bash
grep -q 'spring-javaformat-maven-plugin' pom.xml
```
**如果未配置**：跳过格式化步骤，提示用户项目未配置 spring-javaformat。

**执行格式化**（仅当有修改且已配置插件时）：

使用 `-Dformatter.includes` 指定具体修改的文件：
```bash
mvn spring-javaformat:apply -Dformatter.includes="**/File1.java,**/File2.java"
```

## 注释规范

### 类注释必需元素

- 类功能描述（一句话概括）
- `@author` 作者名
- `@date` 创建/修改日期

### 方法注释必需元素

- 方法功能描述
- `@param` 每个参数说明（如有）
- `@return` 返回值说明（非 void 方法）
- `@throws` 异常说明（如有）

### 跳过注释的情况

- getter/setter 方法
- `@Override` 注解的方法（已有父类文档）
- private 方法（除非逻辑复杂）
- 已有完整注释的类/方法

## 执行顺序

1. 列出待处理的 Java 文件
2. 逐个文件添加/更新注释
3. 更新所有日期相关注释
4. 执行 spring-javaformat 格式化
5. 展示修改摘要
