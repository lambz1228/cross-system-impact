# Kafka Scanner

扫描 Kafka topic 的生产者和消费者关系。

## 功能

- 列出所有 topic
- 列出每个 topic 的生产者
- 列出每个 topic 的消费者组
- 导出为 JSON 格式

## 使用方法

### 前置条件

- Python 3.8+
- kafka-python 包
- 访问 Kafka 集群的权限

### 安装依赖

```bash
pip install kafka-python
```

### 运行扫描

```bash
python scan.py \
  --bootstrap-servers localhost:9092 \
  --output kafka-topology.json
```

### 参数说明

| 参数 | 说明 | 必填 |
|------|------|------|
| --bootstrap-servers | Kafka 集群地址 | 是 |
| --output | 输出文件路径 | 否 |
| --group-filter | 消费者组过滤（正则） | 否 |
| --topic-filter | Topic 过滤（正则） | 否 |

## 输出格式

```json
{
  "scan_time": "2026-06-08T10:00:00Z",
  "cluster": "localhost:9092",
  "topics": [
    {
      "name": "order.created",
      "partitions": 3,
      "consumer_groups": [
        {
          "group_id": "payment-service",
          "members": ["consumer-1", "consumer-2"]
        },
        {
          "group_id": "billing-service",
          "members": ["consumer-1"]
        }
      ]
    }
  ]
}
```

## 示例输出

```json
{
  "scan_time": "2026-06-08T10:00:00Z",
  "cluster": "localhost:9092",
  "topics": [
    {
      "name": "order.created",
      "partitions": 3,
      "consumer_groups": [
        {
          "group_id": "payment-service",
          "members": ["consumer-1", "consumer-2"]
        },
        {
          "group_id": "billing-service",
          "members": ["consumer-1"]
        }
      ]
    },
    {
      "name": "payment.completed",
      "partitions": 3,
      "consumer_groups": [
        {
          "group_id": "billing-service",
          "members": ["consumer-1"]
        },
        {
          "group_id": "notification-service",
          "members": ["consumer-1"]
        }
      ]
    }
  ]
}
```

## 局限性

1. **无法确定生产者**
   - Kafka 不记录谁生产了消息
   - 需要通过代码扫描或配置推断

2. **无法获取消息 schema**
   - 需要配合 Schema Registry 或代码扫描

3. **需要集群访问权限**
   - 某些环境可能限制访问

## 与 Skill 集成

扫描结果可以作为 Skill 的拓扑输入：

```bash
# 1. 运行扫描
python scan.py --bootstrap-servers localhost:9092 --output kafka-topology.json

# 2. 在 Claude Code 中使用
# "使用 kafka-topology.json 中的信息，分析 order.created 事件变更的影响"
```
