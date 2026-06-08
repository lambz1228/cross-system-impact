#!/usr/bin/env python3
"""
convert-to-unified.py - 将各扫描器输出转换为统一拓扑格式
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def load_json(file_path):
    """加载 JSON 文件"""
    try:
        return json.loads(Path(file_path).read_text(encoding="utf-8"))
    except Exception as e:
        print(f"错误: 无法加载 {file_path} - {e}", file=sys.stderr)
        return None


def convert_kafka_scan(data):
    """转换 Kafka 扫描结果"""
    services = set()
    dependencies = []

    for topic in data.get("topics", []):
        topic_name = topic.get("name", "")

        for group in topic.get("consumer_groups", []):
            group_id = group.get("group_id", "")
            services.add(group_id)

            dependencies.append({
                "source": f"producer-of-{topic_name}",
                "target": group_id,
                "type": "kafka",
                "details": {
                    "topic": topic_name
                },
                "fields": [],
                "direction": "read"
            })

    return {
        "services": [{"name": s, "type": "unknown"} for s in services],
        "dependencies": dependencies
    }


def convert_api_scan(data):
    """转换 API 扫描结果"""
    services = set()
    dependencies = []

    for call in data.get("api_calls", []):
        target = call.get("target_service", "")
        if target:
            services.add(target)

            dependencies.append({
                "source": call.get("file", "unknown"),
                "target": target,
                "type": "http",
                "details": {
                    "url": call.get("url", ""),
                    "method": call.get("method", "")
                },
                "fields": [],
                "direction": "read"
            })

    return {
        "services": [{"name": s, "type": "unknown"} for s in services],
        "dependencies": dependencies
    }


def convert_database_scan(data):
    """转换数据库扫描结果"""
    tables = set()
    dependencies = []

    for op in data.get("database_operations", []):
        table = op.get("table", "")
        if table:
            tables.add(table)

            dependencies.append({
                "source": op.get("file", "unknown"),
                "target": f"table:{table}",
                "type": "database",
                "details": {
                    "table": table
                },
                "fields": op.get("fields", []),
                "direction": op.get("operation", "read")
            })

    return {
        "services": [{"name": f"table:{t}", "type": "database"} for t in tables],
        "dependencies": dependencies
    }


def merge_results(results_list):
    """合并多个扫描结果"""
    all_services = {}
    all_dependencies = []

    for result in results_list:
        if not result:
            continue

        # 合并服务
        for service in result.get("services", []):
            name = service.get("name", "")
            if name and name not in all_services:
                all_services[name] = service

        # 合并依赖
        all_dependencies.extend(result.get("dependencies", []))

    return {
        "scan_time": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0",
        "services": list(all_services.values()),
        "dependencies": all_dependencies
    }


def main():
    parser = argparse.ArgumentParser(description="转换扫描结果为统一拓扑格式")
    parser.add_argument("--kafka", help="Kafka 扫描结果 JSON")
    parser.add_argument("--api", help="API 扫描结果 JSON")
    parser.add_argument("--database", help="数据库扫描结果 JSON")
    parser.add_argument("--output", required=True, help="输出文件路径")

    args = parser.parse_args()

    results = []

    # 加载并转换各扫描结果
    if args.kafka:
        data = load_json(args.kafka)
        if data:
            results.append(convert_kafka_scan(data))

    if args.api:
        data = load_json(args.api)
        if data:
            results.append(convert_api_scan(data))

    if args.database:
        data = load_json(args.database)
        if data:
            results.append(convert_database_scan(data))

    if not results:
        print("错误: 没有有效的扫描结果", file=sys.stderr)
        sys.exit(1)

    # 合并结果
    unified = merge_results(results)

    # 保存
    output_json = json.dumps(unified, indent=2, ensure_ascii=False)
    Path(args.output).write_text(output_json, encoding="utf-8")
    print(f"统一拓扑已生成: {args.output}")


if __name__ == "__main__":
    main()
