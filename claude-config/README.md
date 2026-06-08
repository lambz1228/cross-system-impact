# Claude Code 配置

本目录包含 Claude Code 的配置示例。

## Hook 配置

在 `~/.claude/settings.json` 中添加以下配置：

### 自动触发影响分析

当检测到 git commit 包含特定关键词时，自动运行影响分析：

```json
{
  "hooks": {
    "pre-commit": [
      {
        "command": "cd $REPO_ROOT && python scripts/analyze-changes.py --base-ref HEAD~1 --head-ref HEAD --output /tmp/changes.json && python scripts/generate-report.py --changes /tmp/changes.json --output /tmp/impact-report.md"
      }
    ]
  }
}
```

### Skill 预设

在 `~/.claude/presets.json` 中添加：

```json
{
  "presets": {
    "impact-analysis": {
      "description": "跨系统变更影响分析",
      "skill": "cross-system-impact",
      "prompt": "分析以下变更的跨系统影响：\n\n{{diff}}",
      "auto_run": false
    }
  }
}
```

## 使用方式

### 方式 1: 手动触发

在 Claude Code 中：

```
你：/impact-analysis
Claude：[运行 cross-system-impact Skill]
```

### 方式 2: 对话触发

```
你：我改了订单服务的 order.total 字段，帮我分析影响范围
Claude：[自动识别并运行 cross-system-impact Skill]
```

### 方式 3: Git Hook 自动触发

```bash
# 提交时自动分析
git commit -m "feat: 重命名 order.total 为 order.amount"
# 自动输出影响报告
```

## 配置说明

| 配置项 | 说明 |
|--------|------|
| hooks.pre-commit | 提交前自动运行 |
| presets.impact-analysis | Skill 预设配置 |
| auto_run | 是否自动运行（建议设为 false） |

## 注意事项

- Hook 脚本需要有执行权限
- 首次使用需要安装依赖：`pip install -r automation/requirements.txt`
- 自动分析可能增加提交时间，建议仅在需要时启用
