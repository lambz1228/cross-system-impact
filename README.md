<div align="center">

# 🔍 Cross-System Impact Analysis

### 跨系统变更影响分析框架

**让微服务架构下的变更影响一目了然**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-brightgreen.svg)](skills/cross-system-impact/)
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-orange.svg)]()
[![GitHub stars](https://img.shields.io/github/stars/lambz1228/cross-system-impact?style=social)]()

---

</div>

## 🎯 这是什么？

在微服务架构中，改一个字段可能影响 5 个服务、10 个团队。

**这个 Skill 帮你回答：**

> "改了这个字段，会影响哪些服务？谁需要通知？怎么修？"

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   订单服务   │────▶│   支付服务   │────▶│   计费服务   │
│  (变更点)   │     │  (受影响)   │     │  (受影响)   │
└─────────────┘     └─────────────┘     └─────────────┘
       │
       ▼
┌─────────────┐
│    前端     │
│  (受影响)   │
└─────────────┘
```

---

## ✨ 核心能力

| 能力 | 说明 | 输出 |
|:---:|------|------|
| 🔎 | **变更识别** | 从 diff 提取变更对象、类型 |
| 🗺️ | **拓扑收集** | 结构化描述服务间数据流 |
| 🔗 | **路径追踪** | 沿拓扑图追踪所有传播路径 |
| ⚠️ | **影响评估** | Critical / High / Medium / Low 分级 |
| 📊 | **报告输出** | 标准化影响报告 + 行动建议 |

---

## 🚀 快速开始

### 1. 安装

```bash
# 克隆仓库
git clone https://github.com/lambz1228/cross-system-impact.git

# 符号链接到 Claude Code skills 目录
ln -s $(pwd)/cross-system-impact/skills/cross-system-impact ~/.claude/skills/cross-system-impact
```

### 2. 使用

在 Claude Code 中：

```
你：我改了订单服务的 order.total 字段，帮我分析影响范围

Claude：让我帮你分析这个变更的跨系统影响...
        [自动运行 cross-system-impact Skill]
```

### 3. 输出

```
【跨系统变更影响报告】

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

一、变更概况
• 变更服务：订单服务
• 变更内容：order.total → order.amount
• 变更类型：重命名

二、影响清单
┌──────────────┬────────┬─────────────────┐
│ 下游服务     │ 等级   │ 失败模式        │
├──────────────┼────────┼─────────────────┤
│ 支付服务     │ 🔴 Critical │ 扣款金额为 null    │
│ 计费服务     │ 🟠 High    │ SQL 列名错误       │
│ 前端         │ 🟢 Low     │ 显示 undefined     │
└──────────────┴────────┴─────────────────┘

三、行动建议
[紧急] 通知支付服务团队...
```

---

## 📚 文档

| 文档 | 说明 |
|------|------|
| [📋 拓扑格式](skills/cross-system-impact/references/topology-format.md) | 如何描述服务间数据流 |
| [📄 报告模板](skills/cross-system-impact/references/report-template.md) | 影响报告标准格式 |
| [🔄 常见数据流](skills/cross-system-impact/references/common-dataflows.md) | 8 种常见数据流模式 |

---

## 💡 使用案例

| 案例 | 场景 | 影响范围 | 链接 |
|------|------|---------|------|
| 🔤 | 字段重命名 | 4 个服务 | [查看](examples/field-rename.md) |
| 🔌 | API 破坏性变更 | 5 个调用方 | [查看](examples/api-breaking-change.md) |
| 📨 | 消息 Schema 变更 | 向后兼容 | [查看](examples/message-schema-change.md) |

---

## 🛠️ 自动化工具

| 工具 | 用途 |
|------|------|
| [Kafka Scanner](automation/kafka-scanner/) | 自动发现 Kafka topic 消费者 |
| [API Scanner](automation/api-scanner/) | 自动扫描 HTTP API 调用关系 |
| [Database Scanner](automation/database-scanner/) | 自动扫描数据库表读写关系 |

---

## 🔄 CI/CD 集成

在 PR 阶段自动检测潜在影响：

```yaml
# GitHub Actions 配置示例
- name: Impact Analysis
  run: python scripts/analyze-changes.py --output report.md
```

支持：GitHub Actions / GitLab CI / Jenkins

详见 [CI/CD 集成指南](cicd/README.md)

---

## 📁 项目结构

```
cross-system-impact/
│
├── 📂 skills/cross-system-impact/    # 核心 Skill
│   ├── SKILL.md                      # 主定义文件
│   └── 📂 references/                # 参考文档
│       ├── topology-format.md
│       ├── report-template.md
│       └── common-dataflows.md
│
├── 📂 examples/                      # 真实案例
│   ├── field-rename.md
│   ├── api-breaking-change.md
│   └── message-schema-change.md
│
├── 📂 automation/                    # 自动化工具
│   ├── kafka-scanner/
│   ├── api-scanner/
│   ├── database-scanner/
│   ├── requirements.txt
│   └── topology-schema.json
│
├── 📂 scripts/                       # 辅助脚本
│   ├── analyze-changes.py
│   ├── generate-report.py
│   └── convert-to-unified.py
│
├── 📂 cicd/                          # CI/CD 集成
│   └── README.md
│
├── 📂 claude-config/                 # Claude Code 配置
│   └── README.md
│
└── CHANGELOG.md                      # 版本变更记录
```

---

## ⚠️ 局限性

本 Skill 是**分析框架**，依赖用户提供拓扑信息：

| 能做到 | 做不到 |
|--------|--------|
| ✅ 基于拓扑分析影响范围 | ❌ 自动发现未文档化的依赖 |
| ✅ 识别关键传播路径 | ❌ 检测隐式字段依赖 |
| ✅ 输出标准化报告 | ❌ 访问运行时动态路由 |

**拓扑信息越完整 → 分析结果越准确**

---

## 🤝 贡献

欢迎提交 Issue 和 PR！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

---

## 📄 License

[MIT License](LICENSE)

---

<div align="center">

**如果这个项目对你有帮助，请给个 ⭐ Star 支持一下！**

</div>
