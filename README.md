# Skills 技能库

一个可复用的自动化技能集合，专注于提升 Java 开发工作流效率。

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

## 贡献

欢迎提交 PR 添加新的技能！每个技能需要在 `skills/` 目录下创建独立文件夹，并包含 `SKILL.md` 定义文件。

## 许可证

MIT