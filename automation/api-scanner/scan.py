#!/usr/bin/env python3
"""
API Scanner - 扫描代码中的 HTTP API 调用关系
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


# HTTP 客户端调用模式
HTTP_PATTERNS = [
    # JavaScript/TypeScript
    r'fetch\s*\(\s*["\']([^"\']+)["\']',
    r'axios\s*\.\s*(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']',
    r'axios\s*\(\s*\{[^}]*url\s*:\s*["\']([^"\']+)["\']',
    r'got\s*\(\s*["\']([^"\']+)["\']',
    r'request\s*\(\s*["\']([^"\']+)["\']',
    r'\$\.ajax\s*\(\s*\{[^}]*url\s*:\s*["\']([^"\']+)["\']',

    # Python
    r'requests\s*\.\s*(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']',
    r'httpx\s*\.\s*(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']',
    r'urllib\s*\.\s*request\s*\.\s*urlopen\s*\(\s*["\']([^"\']+)["\']',

    # Java
    r'RestTemplate\s*\.\s*(getForObject|postForObject|exchange)\s*\(\s*["\']([^"\']+)["\']',
    r'WebClient\s*\.\s*get\s*\(\s*\)\s*\.uri\s*\(\s*["\']([^"\']+)["\']',
    r'HttpClient\s*\.\s*newBuilder\s*\(\s*\)\s*\.build\s*\(\s*\)',

    # Go
    r'http\s*\.\s*Get\s*\(\s*["\']([^"\']+)["\']',
    r'http\s*\.\s*NewRequest\s*\(\s*["\'][^"\']+["\']\s*,\s*["\']([^"\']+)["\']',
]


def scan_repo(repo_path, include=None, exclude=None):
    """扫描代码仓库"""
    results = {
        "scan_time": datetime.now(timezone.utc).isoformat(),
        "repo_path": str(repo_path),
        "api_calls": []
    }

    repo_path = Path(repo_path)
    if not repo_path.exists():
        print(f"错误: 路径不存在: {repo_path}")
        sys.exit(1)

    # 获取文件列表
    files = get_files(repo_path, include, exclude)
    print(f"找到 {len(files)} 个文件")

    # 扫描每个文件
    for file_path in files:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                lines = content.split("\n")

                for i, line in enumerate(lines, 1):
                    api_calls = extract_api_calls(line, file_path, i, repo_path)
                    results["api_calls"].extend(api_calls)

        except Exception as e:
            print(f"警告: 读取文件失败 {file_path}: {e}")

    print(f"找到 {len(results['api_calls'])} 个 API 调用")
    return results


def get_files(repo_path, include=None, exclude=None):
    """获取文件列表"""
    files = []

    # 默认排除的目录
    default_exclude = [
        "node_modules",
        ".git",
        "__pycache__",
        "venv",
        ".venv",
        "dist",
        "build",
        ".next",
        "target",
    ]

    for root, dirs, filenames in os.walk(repo_path):
        # 排除目录
        dirs[:] = [d for d in dirs if d not in default_exclude]

        if exclude:
            dirs[:] = [d for d in dirs if not re.match(exclude, d)]

        for filename in filenames:
            file_path = Path(root) / filename

            # 检查文件扩展名
            if include:
                if not re.match(include, filename):
                    continue
            else:
                # 默认只扫描代码文件
                if file_path.suffix not in [".js", ".ts", ".jsx", ".tsx", ".py", ".java", ".go", ".rs"]:
                    continue

            files.append(file_path)

    return files


def extract_api_calls(line, file_path, line_number, repo_path):
    """提取 API 调用"""
    calls = []

    for pattern in HTTP_PATTERNS:
        matches = re.finditer(pattern, line, re.IGNORECASE)
        for match in matches:
            # 获取 URL
            url = match.group(1) if match.lastindex >= 1 else match.group(0)

            # 跳过相对路径和变量
            if url.startswith("/") and not url.startswith("//"):
                continue
            if url.startswith("${") or url.startswith("{"):
                continue
            if "$" in url and "{" in url:
                continue

            # 提取目标服务
            target_service = extract_service_name(url)

            if target_service:
                calls.append({
                    "file": str(file_path.relative_to(repo_path)),
                    "line": line_number,
                    "method": extract_http_method(line),
                    "url": url,
                    "target_service": target_service
                })

    return calls


def extract_service_name(url):
    """从 URL 提取服务名"""
    # http://service-name/api/...
    match = re.match(r'https?://([^/:]+)', url)
    if match:
        host = match.group(1)
        # 移除端口号
        host = host.split(":")[0]
        # 移除域名后缀
        if "." in host:
            parts = host.split(".")
            if len(parts) > 1:
                return parts[0]
        return host

    return None


def extract_http_method(line):
    """提取 HTTP 方法"""
    line_lower = line.lower()

    if "get" in line_lower or ".get(" in line_lower:
        return "GET"
    elif "post" in line_lower or ".post(" in line_lower:
        return "POST"
    elif "put" in line_lower or ".put(" in line_lower:
        return "PUT"
    elif "delete" in line_lower or ".delete(" in line_lower:
        return "DELETE"
    elif "patch" in line_lower or ".patch(" in line_lower:
        return "PATCH"

    return "UNKNOWN"


def main():
    parser = argparse.ArgumentParser(description="API Scanner - 扫描代码中的 HTTP API 调用关系")
    parser.add_argument("--repo-path", required=True, help="代码仓库路径")
    parser.add_argument("--output", help="输出文件路径")
    parser.add_argument("--include", help="包含的文件模式（正则）")
    parser.add_argument("--exclude", help="排除的文件模式（正则）")

    args = parser.parse_args()

    # 扫描
    results = scan_repo(args.repo_path, args.include, args.exclude)

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
