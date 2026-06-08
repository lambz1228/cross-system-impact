#!/usr/bin/env python3
"""
analyze-changes.py - 分析 Git diff 中的变更
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


def get_changed_files(base_ref, head_ref):
    """获取变更的文件列表"""
    try:
        cmd = ["git", "diff", "--name-only", f"{base_ref}...{head_ref}"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        files = result.stdout.strip().split("\n")
        return [f for f in files if f]
    except subprocess.CalledProcessError as e:
        print(f"错误: 无法获取变更文件 - {e}", file=sys.stderr)
        return []


def get_file_diff(base_ref, head_ref, file_path):
    """获取单个文件的 diff"""
    try:
        cmd = ["git", "diff", f"{base_ref}...{head_ref}", "--", file_path]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError:
        return ""


def extract_changes(diff, file_path):
    """从 diff 中提取变更"""
    changes = []

    # 字段重命名模式
    rename_patterns = [
        r'-(\w+)\s*[=:].*\+\1\s*[=:]',  # name: old -> name: new
        r'-(\w+)\s*=\s*.*\+\w+\s*=\s*',  # name = old -> name = new
        r'"(\w+)"\s*:.*"(\w+)"\s*:',      # JSON 字段
    ]

    # 删除模式
    delete_patterns = [
        r'^-\s*["\']?(\w+)["\']?\s*:',    # JSON/YAML 字段删除
        r'^-\s*(\w+)\s*=\s*',             # 配置删除
    ]

    # 新增模式
    add_patterns = [
        r'^\+\s*["\']?(\w+)["\']?\s*:',   # JSON/YAML 字段新增
        r'^\+\s*(\w+)\s*=\s*',            # 配置新增
    ]

    lines = diff.split("\n")

    for line in lines:
        # 检查重命名
        for pattern in rename_patterns:
            match = re.search(pattern, line)
            if match:
                changes.append({
                    "type": "rename",
                    "old_name": match.group(1),
                    "new_name": match.group(2) if match.lastindex >= 2 else None,
                    "line": line.strip()
                })

        # 检查删除
        if line.startswith("-") and not line.startswith("---"):
            for pattern in delete_patterns:
                match = re.search(pattern, line)
                if match:
                    changes.append({
                        "type": "delete",
                        "field": match.group(1),
                        "line": line.strip()
                    })

        # 检查新增
        if line.startswith("+") and not line.startswith("+++"):
            for pattern in add_patterns:
                match = re.search(pattern, line)
                if match:
                    changes.append({
                        "type": "add",
                        "field": match.group(1),
                        "line": line.strip()
                    })

    return changes


def classify_file(file_path):
    """分类文件类型"""
    if file_path.endswith((".ts", ".tsx", ".js", ".jsx")):
        return "javascript"
    elif file_path.endswith((".py",)):
        return "python"
    elif file_path.endswith((".java",)):
        return "java"
    elif file_path.endswith((".go",)):
        return "go"
    elif file_path.endswith((".sql",)):
        return "database"
    elif file_path.endswith((".yml", ".yaml")):
        return "config"
    elif file_path.endswith((".json",)):
        return "schema"
    elif file_path.endswith((".proto",)):
        return "protobuf"
    else:
        return "other"


def main():
    parser = argparse.ArgumentParser(description="分析 Git diff 中的变更")
    parser.add_argument("--base-ref", required=True, help="基准分支")
    parser.add_argument("--head-ref", required=True, help="目标分支")
    parser.add_argument("--output", help="输出文件路径")

    args = parser.parse_args()

    # 获取变更文件
    files = get_changed_files(args.base_ref, args.head_ref)
    if not files:
        print("未找到变更文件", file=sys.stderr)
        sys.exit(1)

    # 分析每个文件
    all_changes = []
    for file_path in files:
        diff = get_file_diff(args.base_ref, args.head_ref, file_path)
        if diff:
            changes = extract_changes(diff, file_path)
            if changes:
                all_changes.append({
                    "file": file_path,
                    "type": classify_file(file_path),
                    "changes": changes
                })

    # 统计
    summary = {
        "total_files": len(files),
        "changed_files": len(all_changes),
        "total_changes": sum(len(c["changes"]) for c in all_changes),
        "by_type": {}
    }

    for item in all_changes:
        file_type = item["type"]
        if file_type not in summary["by_type"]:
            summary["by_type"][file_type] = 0
        summary["by_type"][file_type] += len(item["changes"])

    result = {
        "base_ref": args.base_ref,
        "head_ref": args.head_ref,
        "summary": summary,
        "files": all_changes
    }

    # 输出
    output_json = json.dumps(result, indent=2, ensure_ascii=False)

    if args.output:
        Path(args.output).write_text(output_json, encoding="utf-8")
        print(f"结果已保存到: {args.output}")
    else:
        print(output_json)


if __name__ == "__main__":
    main()
