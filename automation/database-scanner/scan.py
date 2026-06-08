#!/usr/bin/env python3
"""
Database Scanner - 扫描代码中的数据库表读写关系
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


# SQL 查询模式
SQL_PATTERNS = [
    # SELECT 查询
    (r'SELECT\s+[\w\s,.*]+\s+FROM\s+(\w+)', "read"),
    (r'select\s+[\w\s,.*]+\s+from\s+(\w+)', "read"),

    # INSERT
    (r'INSERT\s+INTO\s+(\w+)', "write"),
    (r'insert\s+into\s+(\w+)', "write"),

    # UPDATE
    (r'UPDATE\s+(\w+)\s+SET', "write"),
    (r'update\s+(\w+)\s+set', "write"),

    # DELETE
    (r'DELETE\s+FROM\s+(\w+)', "write"),
    (r'delete\s+from\s+(\w+)', "write"),
]

# ORM 模型模式
ORM_PATTERNS = [
    # TypeORM / Sequelize
    (r'@Entity\s*\(\s*["\'](\w+)["\']', "entity"),
    (r'@Table\s*\(\s*["\'](\w+)["\']', "table"),
    (r'model\s+(\w+)\s*\{', "model"),

    # SQLAlchemy
    (r'__tablename__\s*=\s*["\'](\w+)["\']', "table"),

    # Django
    (r'class\s+(\w+)\s*\(.*Model\)', "model"),

    # ActiveRecord
    (r'self\.table_name\s*=\s*["\'](\w+)["\']', "table"),
]

# 字段提取模式
FIELD_PATTERNS = [
    r'SELECT\s+([\w\s,.*]+)\s+FROM',
    r'INSERT\s+INTO\s+\w+\s*\(([\w\s,]+)\)',
    r'(\w+)\s*=\s*[:@]',  # ORM 赋值
]


def scan_repo(repo_path):
    """扫描代码仓库"""
    results = {
        "scan_time": datetime.now(timezone.utc).isoformat(),
        "repo_path": str(repo_path),
        "database_operations": []
    }

    repo_path = Path(repo_path)
    if not repo_path.exists():
        print(f"错误: 路径不存在: {repo_path}", file=sys.stderr)
        sys.exit(1)

    # 获取文件列表
    files = get_files(repo_path)
    print(f"找到 {len(files)} 个文件")

    # 扫描每个文件
    for file_path in files:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                lines = content.split("\n")

                for i, line in enumerate(lines, 1):
                    operations = extract_operations(line, file_path, i, repo_path)
                    results["database_operations"].extend(operations)

        except Exception as e:
            print(f"警告: 读取文件失败 {file_path}: {e}", file=sys.stderr)

    print(f"找到 {len(results['database_operations'])} 个数据库操作")
    return results


def get_files(repo_path):
    """获取文件列表"""
    files = []

    # 排除的目录
    exclude_dirs = [
        "node_modules", ".git", "__pycache__", "venv", ".venv",
        "dist", "build", ".next", "target"
    ]

    for root, dirs, filenames in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        for filename in filenames:
            file_path = Path(root) / filename

            # 只扫描代码文件
            if file_path.suffix in [".ts", ".tsx", ".js", ".jsx", ".py", ".java", ".rb", ".go", ".sql"]:
                files.append(file_path)

    return files


def extract_operations(line, file_path, line_number, repo_path):
    """提取数据库操作"""
    operations = []

    # 检查 SQL 查询
    for pattern, operation_type in SQL_PATTERNS:
        matches = re.finditer(pattern, line, re.IGNORECASE)
        for match in matches:
            table_name = match.group(1)
            fields = extract_fields(line)

            operations.append({
                "file": str(file_path.relative_to(repo_path)),
                "line": line_number,
                "table": table_name,
                "operation": operation_type,
                "fields": fields,
                "type": "sql"
            })

    # 检查 ORM 定义
    for pattern, orm_type in ORM_PATTERNS:
        matches = re.finditer(pattern, line, re.IGNORECASE)
        for match in matches:
            table_name = match.group(1)

            operations.append({
                "file": str(file_path.relative_to(repo_path)),
                "line": line_number,
                "table": table_name,
                "operation": "definition",
                "fields": [],
                "type": f"orm_{orm_type}"
            })

    return operations


def extract_fields(line):
    """从 SQL 中提取字段"""
    fields = []

    # SELECT 字段
    select_match = re.search(r'SELECT\s+([\w\s,.*]+)\s+FROM', line, re.IGNORECASE)
    if select_match:
        fields_str = select_match.group(1)
        if fields_str.strip() == "*":
            return ["*"]
        fields = [f.strip().split(".")[-1] for f in fields_str.split(",")]

    # INSERT 字段
    insert_match = re.search(r'INSERT\s+INTO\s+\w+\s*\(([\w\s,]+)\)', line, re.IGNORECASE)
    if insert_match:
        fields_str = insert_match.group(1)
        fields = [f.strip() for f in fields_str.split(",")]

    return fields


def main():
    parser = argparse.ArgumentParser(description="Database Scanner - 扫描代码中的数据库表读写关系")
    parser.add_argument("--repo-path", required=True, help="代码仓库路径")
    parser.add_argument("--output", help="输出文件路径")

    args = parser.parse_args()

    # 扫描
    results = scan_repo(args.repo_path)

    # 输出
    output_json = json.dumps(results, indent=2, ensure_ascii=False)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output_json)
        print(f"结果已保存到: {args.output}")
    else:
        print(output_json)


if __name__ == "__main__":
    main()
