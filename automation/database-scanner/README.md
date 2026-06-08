# Database Scanner

扫描代码中的数据库表读写关系。

## 功能

- 扫描 SQL 查询语句
- 扫描 ORM 模型定义
- 识别表的读写来源
- 导出为 JSON 格式

## 使用方法

### 前置条件

- Python 3.8+

### 运行扫描

```bash
python scan.py \
  --repo-path /path/to/repo \
  --output db-dependencies.json
```

### 参数说明

| 参数 | 说明 | 必填 |
|------|------|------|
| --repo-path | 代码仓库路径 | 是 |
| --output | 输出文件路径 | 否 |

## 输出格式

```json
{
  "scan_time": "2026-06-08T10:00:00Z",
  "repo_path": "/path/to/repo",
  "database_operations": [
    {
      "file": "src/models/order.ts",
      "line": 42,
      "table": "orders",
      "operation": "read",
      "fields": ["id", "total", "status"]
    }
  ]
}
```

## 支持的 ORM/查询方式

- SQL 原生查询
- Sequelize (Node.js)
- TypeORM (Node.js)
- Prisma (Node.js)
- SQLAlchemy (Python)
- Django ORM (Python)
- ActiveRecord (Ruby)
- MyBatis (Java)
- JPA/Hibernate (Java)

## 与 Skill 集成

扫描结果可以作为 Skill 的拓扑输入：

```bash
# 1. 运行扫描
python scan.py --repo-path /path/to/repo --output db-dependencies.json

# 2. 在 Claude Code 中使用
# "使用 db-dependencies.json 中的信息，分析 orders 表字段变更的影响"
```
