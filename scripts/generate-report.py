#!/usr/bin/env python3
"""
generate-report.py - 生成跨系统变更影响报告
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


def generate_report(changes, dependencies=None, topology=None):
    """生成影响报告"""
    report = []

    # 标题
    report.append("# 跨系统变更影响报告")
    report.append("")
    report.append(f"**生成时间:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    report.append("")

    # 一、变更概况
    report.append("## 一、变更概况")
    report.append("")
    summary = changes.get("summary", {})
    report.append(f"| 指标 | 数值 |")
    report.append(f"|------|------|")
    report.append(f"| 变更文件数 | {summary.get('changed_files', 0)} / {summary.get('total_files', 0)} |")
    report.append(f"| 变更字段数 | {summary.get('total_changes', 0)} |")

    if summary.get("by_type"):
        report.append("| 文件类型分布 | " + "、".join(f"{k}: {v}" for k, v in summary["by_type"].items()) + " |")
    report.append("")

    # 二、变更详情
    report.append("## 二、变更详情")
    report.append("")

    for file_info in changes.get("files", []):
        report.append(f"### {file_info['file']}")
        report.append("")
        report.append(f"**类型:** {file_info['type']}")
        report.append("")
        report.append("| 变更类型 | 内容 |")
        report.append("|---------|------|")

        for change in file_info.get("changes", []):
            change_type = change.get("type", "")
            if change_type == "rename":
                content = f"{change.get('old_name', '')} → {change.get('new_name', '')}"
            elif change_type == "delete":
                content = f"删除 `{change.get('field', '')}`"
            elif change_type == "add":
                content = f"新增 `{change.get('field', '')}`"
            else:
                content = change.get("line", "")

            report.append(f"| {change_type} | {content} |")
        report.append("")

    # 三、依赖分析
    if dependencies:
        report.append("## 三、依赖分析")
        report.append("")

        api_calls = dependencies.get("api_calls", [])
        if api_calls:
            report.append("### API 调用关系")
            report.append("")
            report.append("| 源文件 | 目标服务 | 方法 | URL |")
            report.append("|--------|---------|------|-----|")

            for call in api_calls[:20]:  # 限制显示数量
                report.append(f"| {call.get('file', '')} | {call.get('target_service', '')} | {call.get('method', '')} | {call.get('url', '')} |")
            report.append("")

    # 四、影响评估
    report.append("## 四、影响评估")
    report.append("")
    report.append("> ⚠️ 请根据实际拓扑信息补充影响评估")
    report.append("")

    # 提取可能受影响的字段
    affected_fields = set()
    for file_info in changes.get("files", []):
        for change in file_info.get("changes", []):
            if change.get("type") in ("rename", "delete"):
                field = change.get("old_name") or change.get("field")
                if field:
                    affected_fields.add(field)

    if affected_fields:
        report.append("### 可能受影响的字段")
        report.append("")
        for field in sorted(affected_fields):
            report.append(f"- `{field}`")
        report.append("")

    # 五、行动建议
    report.append("## 五、行动建议")
    report.append("")
    report.append("### 待确认事项")
    report.append("")
    report.append("- [ ] 是否有其他服务使用了被修改的字段？")
    report.append("- [ ] 是否有消息队列消费者依赖这些字段？")
    report.append("- [ ] 是否有定时任务使用这些字段？")
    report.append("- [ ] 是否需要通知相关团队？")
    report.append("- [ ] 是否需要灰度发布？")
    report.append("")

    # 六、信息缺口
    report.append("## 六、信息缺口")
    report.append("")
    report.append("以下信息需要人工补充：")
    report.append("")
    report.append("- [ ] 完整的服务拓扑")
    report.append("- [ ] Kafka/RabbitMQ 消费关系")
    report.append("- [ ] 数据库直连的服务列表")
    report.append("- [ ] 第三方系统依赖")
    report.append("")

    return "\n".join(report)


def main():
    parser = argparse.ArgumentParser(description="生成跨系统变更影响报告")
    parser.add_argument("--changes", required=True, help="变更分析结果 JSON")
    parser.add_argument("--dependencies", help="依赖分析结果 JSON")
    parser.add_argument("--topology", help="拓扑信息 JSON")
    parser.add_argument("--output", required=True, help="输出报告路径")

    args = parser.parse_args()

    # 加载数据
    changes = load_json(args.changes)
    if not changes:
        sys.exit(1)

    dependencies = load_json(args.dependencies) if args.dependencies else None
    topology = load_json(args.topology) if args.topology else None

    # 生成报告
    report = generate_report(changes, dependencies, topology)

    # 保存
    Path(args.output).write_text(report, encoding="utf-8")
    print(f"报告已生成: {args.output}")


if __name__ == "__main__":
    main()
