# Cross-System Impact Analysis

跨系统变更影响分析框架 — 用于 Claude Code 的 Skill。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-blue)](skills/cross-system-impact/)

## 适用场景

当你的代码变更涉及以下内容时，使用本 Skill 系统化识别下游影响：

- **API 字段变更** — 修改 REST/GraphQL/gRPC 接口的请求或响应字段
- **数据库 Schema 变更** — 字段重命名、类型修改、删除列
- **消息队列事件变更** — Kafka/RabbitMQ 消息体字段修改
- **共享库/SDK 变更** — 内部包的接口变动
- **缓存结构变更** — Redis key/value 格式调整

## 核心能力

| 能力 | 说明 |
|------|------|
| 变更识别 | 从 diff 中提取变更对象、类型、范围 |
| 拓扑收集 | 结构化描述服务间数据流关系 |
| 路径追踪 | 沿拓扑图追踪所有传播路径 |
| 影响评估 | 按 Critical/High/Medium/Low 分级 |
| 报告输出 | 标准化影响报告 + 行动建议 |

## 安装

将 `skills/cross-system-impact` 目录复制到你的 Claude Code skills 目录：

```bash
# 方式 1：直接复制
cp -r skills/cross-system-impact ~/.claude/skills/

# 方式 2：符号链接（推荐）
ln -s $(pwd)/skills/cross-system-impact ~/.claude/skills/cross-system-impact
```

## 使用方法

### 1. 提供拓扑信息

在使用 Skill 前，先描述你的服务拓扑：

```md
## 服务拓扑

### 服务列表
| 服务名 | 技术栈 | 仓库位置 | 负责团队 |
| --- | --- | --- | --- |
| 订单服务 | Node.js | git@xxx/order-service | 交易组 |
| 支付服务 | Java | git@xxx/payment-service | 支付组 |

### 数据流
#### 订单服务 -> 支付服务
- 方式：Kafka
- Topic：order.created
- 关键字段：order_id, total, user_id
```

详细格式见 [topology-format.md](skills/cross-system-impact/references/topology-format.md)。

### 2. 触发分析

告诉 Claude：

> "我改了订单服务的 order.total 字段，帮我分析影响范围"

或

> "分析这个变更的跨系统影响：[粘贴 diff]"

### 3. 获取报告

输出包含：
- 影响拓扑图
- 影响清单（按严重程度排序）
- 风险分析
- 行动建议
- 灰度/回滚建议

## 报告示例

```
【跨系统变更影响报告】

一、变更概况
- 变更服务：订单服务
- 变更内容：order.total -> order.amount
- 变更类型：重命名

二、影响拓扑
[订单服务] --[Kafka: order.created]--> [支付服务]
                |
                +--[Kafka]--> [计费服务]
                |
                +--[HTTP]--> [前端]

三、影响清单
| 下游服务 | 影响等级 | 失败模式 |
|---------|---------|---------|
| 支付服务 | Critical | 扣款金额为 null |
| 计费服务 | High | SQL 列名错误 |
| 前端 | Low | 显示 undefined |

四、行动建议
[紧急] 通知支付服务团队...
```

## 使用案例

| 案例 | 变更类型 | 影响范围 | 复杂度 |
|------|---------|---------|--------|
| [字段重命名](examples/field-rename.md) | 数据库字段重命名 | 4 个服务 | 中等 |
| [API 接口变更](examples/api-breaking-change.md) | REST API 破坏性变更 | 6 个服务 | 高 |
| [消息 Schema 变更](examples/message-schema-change.md) | Kafka 消息体字段修改 | 3 个服务 | 低 |

## 自动化工具

| 工具 | 用途 | 说明 |
|------|------|------|
| [Kafka Scanner](automation/kafka-scanner/) | 扫描 Kafka 消费关系 | 自动发现 topic 消费者 |
| [API Scanner](automation/api-scanner/) | 扫描 API 调用关系 | 自动发现 HTTP 依赖 |
| [Database Scanner](automation/database-scanner/) | 扫描数据库依赖 | 自动发现表读写关系 |

## CI/CD 集成

将影响分析集成到 CI/CD 流程，在 PR 阶段自动检测潜在影响。

详细配置见 [CI/CD 集成指南](cicd/README.md)。

## 项目结构

```
cross-system-impact/
├── README.md                          # 本文件
├── LICENSE                            # MIT 协议
├── .gitignore
├── skills/
│   └── cross-system-impact/
│       ├── SKILL.md                   # Skill 主定义
│       └── references/
│           ├── topology-format.md     # 拓扑描述格式
│           ├── report-template.md     # 报告模板
│           └── common-dataflows.md    # 常见数据流模式
├── examples/                          # 使用案例
│   ├── README.md
│   ├── field-rename.md
│   ├── api-breaking-change.md
│   └── message-schema-change.md
├── automation/                        # 自动化工具
│   ├── README.md
│   ├── kafka-scanner/
│   └── api-scanner/
└── cicd/                              # CI/CD 集成
    └── README.md
```

## 局限性

本 Skill 是**分析框架**，依赖用户提供拓扑信息。它不能：

- 自动发现未文档化的服务依赖
- 检测隐式的字段依赖（如字符串拼接字段名）
- 访问运行时动态路由的服务

**拓扑信息越完整，分析结果越准确。**

## 贡献

欢迎提交 Issue 和 PR。

## License

[MIT](LICENSE)
