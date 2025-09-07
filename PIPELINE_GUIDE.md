# Pipeline使用指南

## 概述

Pipeline系统是RepoDP的核心功能，它允许您将文件提取、去重、内容清洗、文件清洗等操作串联起来，形成一个完整的数据处理流程。Pipeline支持任务编排，可以定义步骤之间的依赖关系，确保操作按正确的顺序执行。

## 特性

- **任务编排**: 支持定义步骤之间的依赖关系
- **多种Pipeline**: 提供标准、快速、深度清洗、分析等多种预设pipeline
- **灵活配置**: 每个步骤都可以独立配置参数
- **模拟执行**: 支持dry-run模式，可以预览执行计划
- **错误处理**: 支持错误恢复和继续执行
- **详细报告**: 提供完整的执行报告和统计信息

## 预设Pipeline

### 1. 标准Pipeline (standard)
完整的代码仓库数据处理流程：
- 文件提取 → 去重 → 内容清洗 → 文件指标清洗

### 2. 快速Pipeline (quick)
仅进行基础处理：
- 文件提取 → 去重

### 3. 深度清洗Pipeline (deep_clean)
包含所有清洗步骤：
- 文件提取 → 去重 → 内容清洗 → JSONL清洗 → 文件指标清洗

### 4. 分析Pipeline (analysis)
仅进行分析，不修改文件：
- 文件提取 → 重复文件分析 → 文件指标分析

## 使用方法

### 1. 列出可用的Pipeline

```bash
python -m src.repodp pipeline list-pipelines
```

### 2. 查看Pipeline详细信息

```bash
python -m src.repodp pipeline list-pipelines --pipeline standard
```

### 3. 验证Pipeline配置

```bash
python -m src.repodp pipeline validate standard
```

### 4. 模拟执行Pipeline

```bash
python -m src.repodp pipeline dry-run standard
```

### 5. 执行Pipeline

```bash
# 使用默认pipeline
python -m src.repodp pipeline run <repo_name>

# 指定pipeline
python -m src.repodp pipeline run <repo_name> --pipeline standard

# 指定输出目录
python -m src.repodp pipeline run <repo_name> --output /path/to/output

# 模拟执行
python -m src.repodp pipeline run <repo_name> --dry-run
```

## Pipeline配置

Pipeline配置在 `config/config.yaml` 文件中定义：

```yaml
pipeline:
  default_pipeline: "standard"
  pipelines:
    standard:
      name: "标准数据处理流程"
      description: "完整的代码仓库数据处理流程"
      steps:
        - name: "extract"
          type: "extractor"
          enabled: true
          config:
            output_format: "jsonl"
            include_metadata: true
        - name: "deduplicate"
          type: "cleaner"
          enabled: true
          depends_on: ["extract"]
          config:
            method: "deduplication"
            keep_strategy: "newest"
        # ... 更多步骤
```

## 步骤类型

### 1. 提取器 (extractor)
- **功能**: 从代码仓库中提取文件信息
- **输出**: JSONL格式的文件信息

### 2. 清洗器 (cleaner)
- **deduplication**: 文件去重
- **content_cleaning**: 内容清洗
- **file_metrics_cleaning**: 文件指标清洗
- **jsonl_cleaning**: JSONL内容清洗

### 3. 分析器 (analyzer)
- **duplicate_analysis**: 重复文件分析
- **metrics_analysis**: 文件指标分析

## 依赖关系

Pipeline步骤支持依赖关系定义：

```yaml
- name: "content_clean"
  type: "cleaner"
  enabled: true
  depends_on: ["deduplicate"]  # 依赖去重步骤
  config:
    method: "content_cleaning"
```

## 错误处理

Pipeline支持以下错误处理策略：

1. **继续执行**: 遇到错误时继续执行后续步骤
2. **停止执行**: 遇到错误时立即停止
3. **重试机制**: 支持步骤重试

## 输出文件

Pipeline执行后会在输出目录生成以下文件：

- `{repo_name}_extracted.jsonl`: 提取的文件信息
- `{repo_name}_deduplicated.jsonl`: 去重后的文件
- `{repo_name}_content_cleaned.jsonl`: 内容清洗后的文件
- `{repo_name}_metrics_cleaned.jsonl`: 文件指标清洗后的文件
- `pipeline_report.json`: 执行报告

## 自定义Pipeline

### 1. 添加新Pipeline

```bash
python -m src.repodp pipeline add <pipeline_name> <config_file.yaml>
```

### 2. 更新Pipeline

```bash
python -m src.repodp pipeline update <pipeline_name> <config_file.yaml>
```

### 3. 删除Pipeline

```bash
python -m src.repodp pipeline remove <pipeline_name>
```

## 示例

### 基本使用

```python
from repodp.core.config_manager import ConfigManager
from repodp.core.pipeline_manager import PipelineManager

# 创建配置管理器
config_manager = ConfigManager()

# 创建pipeline管理器
pipeline_manager = PipelineManager(config_manager.config)

# 模拟执行
result = pipeline_manager.dry_run('standard')
print(f"执行顺序: {' -> '.join(result['execution_order'])}")

# 实际执行
result = pipeline_manager.execute_pipeline(
    repo_path=Path('/path/to/repo'),
    pipeline_name='standard',
    repo_name='my_repo'
)
```

### 自定义Pipeline配置

```yaml
my_custom_pipeline:
  name: "自定义Pipeline"
  description: "我的自定义数据处理流程"
  steps:
    - name: "extract"
      type: "extractor"
      enabled: true
      config:
        file_types: [".py", ".js"]
        max_file_size: 1048576
    - name: "clean"
      type: "cleaner"
      enabled: true
      depends_on: ["extract"]
      config:
        method: "content_cleaning"
        remove_comments: true
        remove_imports: true
```

## 最佳实践

1. **使用模拟执行**: 在执行前先使用 `dry-run` 预览执行计划
2. **验证配置**: 使用 `validate` 命令检查pipeline配置
3. **分步执行**: 对于复杂流程，可以分步执行和调试
4. **备份数据**: 在执行清洗操作前备份重要数据
5. **监控输出**: 关注执行报告中的错误和警告信息

## 故障排除

### 常见问题

1. **依赖循环**: 检查步骤依赖关系是否存在循环
2. **配置错误**: 使用 `validate` 命令检查配置
3. **文件不存在**: 确保输入文件路径正确
4. **权限问题**: 确保有足够的文件读写权限

### 调试技巧

1. 使用 `--verbose` 选项获取详细日志
2. 检查 `pipeline_report.json` 文件了解执行详情
3. 使用模拟执行模式测试配置
4. 逐步启用/禁用步骤进行调试

## 总结

Pipeline系统为RepoDP提供了强大而灵活的数据处理能力。通过合理的配置和编排，您可以构建适合自己需求的数据处理流程，提高工作效率和数据质量。
