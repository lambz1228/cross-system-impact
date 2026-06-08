# 自动化发现指南

本目录包含自动化收集服务拓扑信息的工具和脚本。

## 目录结构

```
automation/
├── README.md                    # 本文件
├── kafka-scanner/               # Kafka 消费关系扫描
├── api-scanner/                 # API 依赖扫描
├── database-scanner/            # 数据库依赖扫描
└── code-scanner/                # 代码依赖扫描
```

## 可用工具

| 工具 | 用途 | 输入 | 输出 |
|------|------|------|------|
| [kafka-scanner](kafka-scanner/) | 扫描 Kafka topic 的生产者/消费者 | Kafka 配置 | 消费关系表 |
| [api-scanner](api-scanner/) | 扫描 HTTP API 调用关系 | 代码仓库 | API 依赖图 |
| [database-scanner](database-scanner/) | 扫描数据库表的读写关系 | 代码仓库 | 数据依赖表 |
| [code-scanner](code-scanner/) | 扫描代码中的字段使用 | 代码仓库 | 字段依赖表 |

## 快速开始

### 1. 扫描 Kafka 消费关系

```bash
cd kafka-scanner
./scan.sh --bootstrap-servers localhost:9092 --output kafka-topology.json
```

### 2. 扫描 API 调用关系

```bash
cd api-scanner
./scan.sh --repo-path /path/to/repo --output api-dependencies.json
```

### 3. 扫描数据库依赖

```bash
cd database-scanner
./scan.sh --repo-path /path/to/repo --output db-dependencies.json
```

### 4. 扫描代码字段依赖

```bash
cd code-scanner
./scan.sh --repo-path /path/to/repo --field "total" --output field-dependencies.json
```

## 输出格式

所有工具输出统一的 JSON 格式：

```json
{
  "scan_time": "2026-06-08T10:00:00Z",
  "scan_type": "kafka",
  "results": [
    {
      "source": "order-service",
      "target": "payment-service",
      "type": "kafka",
      "topic": "order.created",
      "fields": ["order_id", "total", "user_id"]
    }
  ]
}
```

## 与 Skill 集成

扫描结果可以直接作为 Skill 的拓扑输入：

```bash
# 1. 运行扫描
./kafka-scanner/scan.sh --output topology.json

# 2. 使用扫描结果作为 Skill 输入
# 在 Claude Code 中：
# "使用 topology.json 中的拓扑信息，分析 order.total 字段变更的影响"
```

## 局限性

自动化发现的局限性：

1. **无法发现动态路由**
   - 配置中心控制的路由
   - 运行时动态生成的 topic

2. **无法发现隐式依赖**
   - 字符串拼接的字段名
   - 动态生成的 API 路径

3. **需要代码访问权限**
   - 需要克隆所有相关仓库
   - 需要访问 Kafka 集群

4. **无法发现第三方依赖**
   - 外部 SaaS 服务
   - 第三方 API 调用

## 最佳实践

1. **定期扫描**
   - 在 CI/CD 中集成扫描
   - 每次发布后更新拓扑

2. **手动补充**
   - 自动化扫描 + 手动补充
   - 无法自动发现的部分手动描述

3. **版本控制**
   - 将拓扑信息纳入版本控制
   - 跟踪拓扑变更历史

## 贡献

欢迎贡献新的扫描工具或改进现有工具。
