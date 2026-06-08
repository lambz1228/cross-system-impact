# Changelog

本项目的所有重要变更都会记录在此文件。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [1.0.0] - 2026-06-08

### 新增

#### 核心功能
- 跨系统变更影响分析 Skill
- 变更识别：从 diff 中提取变更对象、类型、范围
- 拓扑收集：结构化描述服务间数据流关系
- 路径追踪：沿拓扑图追踪所有传播路径
- 影响评估：按 Critical/High/Medium/Low 分级
- 报告输出：标准化影响报告 + 行动建议

#### 参考文档
- 拓扑描述格式 (`topology-format.md`)
- 影响报告模板 (`report-template.md`)
- 常见数据流模式 (`common-dataflows.md`)

#### 使用案例
- 字段重命名案例
- API 破坏性变更案例
- 消息 Schema 变更案例

#### 自动化工具
- Kafka Scanner：扫描 Kafka topic 消费关系
- API Scanner：扫描 HTTP API 调用关系
- Database Scanner：扫描数据库表读写关系
- 统一拓扑格式 (`topology-schema.json`)
- 格式转换工具 (`convert-to-unified.py`)

#### CI/CD 集成
- GitHub Actions 配置示例
- GitLab CI 配置示例
- Jenkins 配置示例
- 变更分析脚本 (`analyze-changes.py`)
- 报告生成脚本 (`generate-report.py`)

#### Claude Code 集成
- Hook 配置示例
- Skill 预设配置

### 文档
- README 项目介绍
- 安装指南
- 使用方法
- 贡献指南
- MIT 开源协议

## [未发布]

### 计划中
- 可视化拓扑图
- 更多 ORM 支持
- 单元测试
- 视频演示
- 国际化支持
