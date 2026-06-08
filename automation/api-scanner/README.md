# API Scanner

扫描代码中的 HTTP API 调用关系。

## 功能

- 扫描代码中的 HTTP 客户端调用（fetch、axios、requests 等）
- 识别 API 调用的目标服务
- 导出为 JSON 格式

## 使用方法

### 前置条件

- Python 3.8+

### 运行扫描

```bash
python scan.py \
  --repo-path /path/to/repo \
  --output api-dependencies.json
```

### 参数说明

| 参数 | 说明 | 必填 |
|------|------|------|
| --repo-path | 代码仓库路径 | 是 |
| --output | 输出文件路径 | 否 |
| --include | 包含的文件模式（glob） | 否 |
| --exclude | 排除的文件模式（glob） | 否 |

## 输出格式

```json
{
  "scan_time": "2026-06-08T10:00:00Z",
  "repo_path": "/path/to/repo",
  "api_calls": [
    {
      "file": "src/services/order.service.ts",
      "line": 42,
      "method": "GET",
      "url": "http://payment-service/api/payments",
      "target_service": "payment-service"
    }
  ]
}
```

## 示例输出

```json
{
  "scan_time": "2026-06-08T10:00:00Z",
  "repo_path": "/path/to/order-service",
  "api_calls": [
    {
      "file": "src/services/order.service.ts",
      "line": 42,
      "method": "POST",
      "url": "http://payment-service/api/payments",
      "target_service": "payment-service"
    },
    {
      "file": "src/services/order.service.ts",
      "line": 58,
      "method": "GET",
      "url": "http://user-service/api/users/${userId}",
      "target_service": "user-service"
    }
  ]
}
```

## 支持的 HTTP 客户端

- fetch (JavaScript/TypeScript)
- axios (JavaScript/TypeScript)
- got (JavaScript/TypeScript)
- request (Node.js)
- requests (Python)
- httpx (Python)
- urllib (Python)
- RestTemplate (Java)
- WebClient (Java)
- HttpClient (Java)
- Go net/http

## 局限性

1. **无法识别动态 URL**
   - URL 由变量拼接
   - 配置中心管理的地址

2. **无法识别消息队列**
   - 需要配合 kafka-scanner

3. **无法识别数据库连接**
   - 需要配合 database-scanner

## 与 Skill 集成

扫描结果可以作为 Skill 的拓扑输入：

```bash
# 1. 运行扫描
python scan.py --repo-path /path/to/repo --output api-dependencies.json

# 2. 在 Claude Code 中使用
# "使用 api-dependencies.json 中的信息，分析 payment-service 接口变更的影响"
```
