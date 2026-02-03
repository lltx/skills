---
name: code-tidy
description: 整理 Java 代码。使用场景：(1) 对新增/修改的 Java 类和方法添加 Javadoc 注释，(2) 更新代码中的日期注释（@author、@since、Copyright 年份），(3) 使用 spring-javaformat 格式化代码。当用户说"整理代码"、"添加注释"、"格式化 Java"、"更新日期注释"时触发。
argument-hint: [maven-root]
metadata:
  author: lengleng
  version: "1.2.0"
---

# Code Tidy v1.2.0

整理 Git 未提交的 Java 代码，添加 Javadoc 注释并更新日期。

## 参数说明

| 参数 | 说明 | 示例 |
|------|------|------|
| `$0` | Maven 项目根路径（包含 pom.xml 的目录） | `/code-tidy pigx/` |
| 无参数 | 自动查找最近的 pom.xml 所在目录 | `/code-tidy` |

## 工作流程

### 1. 定位 Maven 项目根目录

**如果提供了参数 `$0`**：
- 验证 `$0/pom.xml` 是否存在
- 如果不存在，报错并提示用户

**如果未提供参数**：
```bash
# 从当前目录向上查找 pom.xml
find . -maxdepth 3 -name "pom.xml" -type f | head -1 | xargs dirname
```

### 2. 获取 Git 未提交的 Java 文件

**重要**：必须先 `cd` 到 Maven 项目根目录，再执行 git 命令（因为项目可能是独立的 git 仓库）。

只处理 Git 未提交（已修改、新增、未跟踪）的 Java 文件：

```bash
# 切换到项目目录后执行
cd ${MAVEN_ROOT}

# 获取所有未提交的 Java 文件（已暂存、已修改、新增）
git status --porcelain | grep '\.java$' | awk '{print $2}'
```

**如果没有未提交的 Java 文件**：提示用户并退出。

### 3. 获取当前日期

```bash
# 获取当前日期（YYYY-MM-DD 格式）
CURRENT_DATE=$(date +"%Y-%m-%d")

# 获取当前年份
CURRENT_YEAR=$(date +"%Y")
```

### 4. 添加/更新 Javadoc 注释

对每个未提交的 Java 文件执行：

**类注释模板**（如果缺失则添加）：
```java
/**
 * 类功能描述
 *
 * @author lengleng
 * @date ${CURRENT_DATE}
 */
```

**方法注释模板**（对 public/protected 方法添加）：
```java
/**
 * 方法功能描述
 *
 * @param paramName 参数说明
 * @return 返回值说明
 */
```

### 5. 更新日期注释

| 类型 | 查找模式 | 更新为 |
|------|----------|--------|
| @date | `@date YYYY/MM/DD` 或 `@date YYYY-MM-DD` | `${CURRENT_DATE}` |
| @since | `@since X.X.X` | 保持不变 |
| Copyright | `Copyright © YYYY` 或 `Copyright YYYY` | `${CURRENT_YEAR}` |

### 6. 格式化代码

**前置条件**：检查项目是否配置了 spring-javaformat 插件：
```bash
grep -q 'spring-javaformat-maven-plugin' ${MAVEN_ROOT}/pom.xml
```

**如果已配置**：对修改的文件执行格式化：
```bash
cd ${MAVEN_ROOT} && mvn spring-javaformat:apply -Dformatter.includes="**/File1.java,**/File2.java"
```

**如果未配置**：跳过格式化，提示用户。

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
- `@Override` 注解的方法
- private 方法（除非逻辑复杂）
- 已有完整注释的类/方法

## 执行顺序

1. 定位 Maven 项目根目录
2. 获取 Git 未提交的 Java 文件列表
3. 获取当前日期
4. 逐个文件添加/更新注释
5. 执行 spring-javaformat 格式化
6. 展示修改摘要
