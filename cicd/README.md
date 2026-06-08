# CI/CD 集成指南

将跨系统影响分析集成到 CI/CD 流程中，在 PR 阶段自动检测潜在影响。

## 架构概览

```
PR 创建/更新
    ↓
触发 CI 流水线
    ↓
┌─────────────────────────────────────┐
│ 1. 变更分析                         │
│    - 识别修改的字段/接口             │
│    - 识别修改的服务                 │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 2. 拓扑扫描                         │
│    - Kafka 消费关系                 │
│    - API 调用关系                   │
│    - 数据库依赖                     │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 3. 影响分析                         │
│    - 运行 cross-system-impact Skill │
│    - 生成影响报告                   │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 4. 结果输出                         │
│    - PR 评论                        │
│    - 标签标记                       │
│    - Slack 通知（可选）              │
└─────────────────────────────────────┘
```

## 支持的 CI 平台

| 平台 | 状态 | 配置文件 |
|------|------|---------|
| GitHub Actions | ✅ 支持 | `.github/workflows/impact-analysis.yml` |
| GitLab CI | ✅ 支持 | `.gitlab-ci.yml` |
| Jenkins | 🚧 计划中 | `Jenkinsfile` |
| CircleCI | 🚧 计划中 | `.circleci/config.yml` |

## GitHub Actions 配置

### 基础配置

创建 `.github/workflows/impact-analysis.yml`：

```yaml
name: Cross-System Impact Analysis

on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  impact-analysis:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install kafka-python
          pip install -r automation/requirements.txt
      
      - name: Run Impact Analysis
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          # 1. 分析变更
          python scripts/analyze-changes.py \
            --base-ref ${{ github.base_ref }} \
            --head-ref ${{ github.head_ref }} \
            --output changes.json
          
          # 2. 扫描依赖
          python automation/api-scanner/scan.py \
            --repo-path . \
            --output api-dependencies.json
          
          # 3. 生成报告
          python scripts/generate-report.py \
            --changes changes.json \
            --dependencies api-dependencies.json \
            --output report.md
      
      - name: Comment PR
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const report = fs.readFileSync('report.md', 'utf8');
            
            await github.rest.issues.createComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.issue.number,
              body: report
            });
      
      - name: Add labels
        if: contains(steps.analysis.outputs.impact_level, 'Critical')
        uses: actions/github-script@v7
        with:
          script: |
            await github.rest.issues.addLabels({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.issue.number,
              labels: ['critical-impact', 'needs-review']
            });
```

### 高级配置

```yaml
name: Cross-System Impact Analysis

on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  impact-analysis:
    runs-on: ubuntu-latest
    
    services:
      kafka:
        image: confluentinc/cp-kafka:latest
        ports:
          - 9092:9092
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install kafka-python anthropic
      
      - name: Run Impact Analysis
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          KAFKA_BOOTSTRAP_SERVERS: localhost:9092
        run: |
          # 完整分析流程
          python scripts/full-analysis.py \
            --base-ref ${{ github.base_ref }} \
            --head-ref ${{ github.head_ref }} \
            --kafka-servers $KAFKA_BOOTSTRAP_SERVERS \
            --output report.md
      
      - name: Upload Report
        uses: actions/upload-artifact@v4
        with:
          name: impact-report
          path: report.md
      
      - name: Comment PR
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const report = fs.readFileSync('report.md', 'utf8');
            
            // 截断过长的报告
            const maxLength = 65536;
            const truncatedReport = report.length > maxLength 
              ? report.substring(0, maxLength) + '\n\n... (报告已截断，完整报告见 Artifacts)'
              : report;
            
            await github.rest.issues.createComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.issue.number,
              body: truncatedReport
            });
```

## GitLab CI 配置

创建 `.gitlab-ci.yml`：

```yaml
stages:
  - analysis
  - report

impact-analysis:
  stage: analysis
  image: python:3.11
  
  variables:
    KAFKA_BOOTSTRAP_SERVERS: "kafka:9092"
  
  script:
    - pip install kafka-python anthropic
    - python scripts/analyze-changes.py --base-ref $CI_MERGE_REQUEST_TARGET_BRANCH_NAME --output changes.json
    - python automation/api-scanner/scan.py --repo-path . --output api-dependencies.json
    - python scripts/generate-report.py --changes changes.json --dependencies api-dependencies.json --output report.md
  
  artifacts:
    paths:
      - report.md
      - changes.json
      - api-dependencies.json
  
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"

report:
  stage: report
  image: alpine:latest
  
  script:
    - echo "Impact analysis report generated"
    - cat report.md
  
  dependencies:
    - impact-analysis
  
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
```

## Jenkins 配置

创建 `Jenkinsfile`：

```groovy
pipeline {
    agent any
    
    parameters {
        string(name: 'BASE_REF', defaultValue: 'main', description: 'Base branch')
        string(name: 'HEAD_REF', defaultValue: 'HEAD', description: 'Head branch')
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Impact Analysis') {
            steps {
                script {
                    // 分析变更
                    sh '''
                        python scripts/analyze-changes.py \
                            --base-ref ${params.BASE_REF} \
                            --head-ref ${params.HEAD_REF} \
                            --output changes.json
                    '''
                    
                    // 扫描依赖
                    sh '''
                        python automation/api-scanner/scan.py \
                            --repo-path . \
                            --output api-dependencies.json
                    '''
                    
                    // 生成报告
                    sh '''
                        python scripts/generate-report.py \
                            --changes changes.json \
                            --dependencies api-dependencies.json \
                            --output report.md
                    '''
                }
            }
            
            post {
                always {
                    archiveArtifacts artifacts: 'report.md', allowEmptyArchive: true
                    publishHTML(target: [
                        reportName: 'Impact Analysis Report',
                        reportDir: '.',
                        reportFiles: 'report.md',
                        keepAll: true
                    ])
                }
            }
        }
    }
}
```

## 脚本说明

### analyze-changes.py

分析 PR 中的变更：

```python
#!/usr/bin/env python3
"""分析 PR 中的变更"""

import argparse
import json
import subprocess
import re


def get_changed_files(base_ref, head_ref):
    """获取变更的文件列表"""
    cmd = f"git diff --name-only {base_ref}...{head_ref}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip().split("\n")


def analyze_changes(files):
    """分析变更内容"""
    changes = []
    
    for file in files:
        # 分析文件变更
        cmd = f"git diff {base_ref}...{head_ref} -- {file}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        # 提取变更的字段/接口
        field_changes = extract_field_changes(result.stdout)
        
        if field_changes:
            changes.append({
                "file": file,
                "changes": field_changes
            })
    
    return changes


def extract_field_changes(diff):
    """从 diff 中提取字段变更"""
    changes = []
    
    # 匹配字段重命名
    rename_pattern = r'-(\w+).*\+(\w+)'
    for match in re.finditer(rename_pattern, diff):
        changes.append({
            "type": "rename",
            "old": match.group(1),
            "new": match.group(2)
        })
    
    # 匹配字段删除
    delete_pattern = r'-(\w+)\s*:'
    for match in re.finditer(delete_pattern, diff):
        changes.append({
            "type": "delete",
            "field": match.group(1)
        })
    
    # 匹配字段新增
    add_pattern = r'\+(\w+)\s*:'
    for match in re.finditer(add_pattern, diff):
        changes.append({
            "type": "add",
            "field": match.group(1)
        })
    
    return changes


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-ref", required=True)
    parser.add_argument("--head-ref", required=True)
    parser.add_argument("--output", required=True)
    
    args = parser.parse_args()
    
    files = get_changed_files(args.base_ref, args.head_ref)
    changes = analyze_changes(files)
    
    with open(args.output, "w") as f:
        json.dump(changes, f, indent=2)


if __name__ == "__main__":
    main()
```

### generate-report.py

生成影响报告：

```python
#!/usr/bin/env python3
"""生成影响报告"""

import argparse
import json
import os


def generate_report(changes, dependencies):
    """生成影响报告"""
    report = []
    report.append("# 跨系统变更影响报告\n")
    report.append("## 变更概览\n")
    
    # 统计变更
    total_changes = sum(len(c["changes"]) for c in changes)
    report.append(f"- 变更文件数: {len(changes)}")
    report.append(f"- 变更字段数: {total_changes}")
    report.append("")
    
    # 分析影响
    impacts = analyze_impacts(changes, dependencies)
    
    if impacts:
        report.append("## 影响分析\n")
        for impact in impacts:
            report.append(f"### {impact['service']}")
            report.append(f"- 影响等级: {impact['level']}")
            report.append(f"- 影响描述: {impact['description']}")
            report.append("")
    
    return "\n".join(report)


def analyze_impacts(changes, dependencies):
    """分析影响"""
    impacts = []
    
    # 分析 API 调用影响
    for change in changes:
        for dep in dependencies.get("api_calls", []):
            if change["file"] in dep.get("file", ""):
                impacts.append({
                    "service": dep["target_service"],
                    "level": "High",
                    "description": f"API 调用可能受影响: {dep['url']}"
                })
    
    return impacts


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--changes", required=True)
    parser.add_argument("--dependencies", required=True)
    parser.add_argument("--output", required=True)
    
    args = parser.parse_args()
    
    with open(args.changes) as f:
        changes = json.load(f)
    
    with open(args.dependencies) as f:
        dependencies = json.load(f)
    
    report = generate_report(changes, dependencies)
    
    with open(args.output, "w") as f:
        f.write(report)


if __name__ == "__main__":
    main()
```

## 配置说明

### 必需的 Secrets

在 CI 平台配置以下 Secrets：

| Secret | 说明 |
|--------|------|
| `ANTHROPIC_API_KEY` | Claude API 密钥（用于 Skill 分析） |

### 可选的环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `KAFKA_BOOTSTRAP_SERVERS` | Kafka 集群地址 | 无 |
| `IMPACT_THRESHOLD` | 影响等级阈值 | Medium |
| `ENABLE_SLACK` | 启用 Slack 通知 | false |

## 输出示例

PR 评论示例：

```markdown
## 跨系统变更影响报告

### 变更概览
- 变更文件数: 3
- 变更字段数: 5

### 影响分析

#### 支付服务
- 影响等级: Critical
- 影响描述: 订单服务修改了 order.total 字段，支付服务消费该字段进行扣款

#### 计费服务
- 影响等级: High
- 影响描述: 计费服务直接查询 orders.total 列

### 行动建议
1. 通知支付服务团队
2. 通知计费服务团队
3. 建议灰度发布

### 详细报告
[完整报告见 Artifacts]
```

## 最佳实践

1. **增量分析**
   - 只分析变更的文件
   - 缓存之前的分析结果

2. **并行执行**
   - 多个扫描器并行运行
   - 减少 CI 时间

3. **失败处理**
   - 分析失败不阻断 CI
   - 记录错误日志

4. **结果缓存**
   - 缓存依赖扫描结果
   - 定期更新缓存

5. **通知策略**
   - Critical 影响：Slack 通知 + PR 评论
   - High 影响：PR 评论
   - Medium/Low 影响：仅记录
