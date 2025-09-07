# RepoDP 用户使用指南

## 📖 项目简介

RepoDP 是一个专业的代码仓库数据处理工具，专为大规模代码分析和处理而设计。它提供了完整的代码仓库管理、文件提取、数据清洗、去重分析和报告生成功能，支持多种编程语言和灵活的数据处理流程。

## ✨ 核心特性

- 🔗 **多仓库管理**: 支持管理多个Git代码仓库，本地和远程仓库
- 📁 **智能文件提取**: 支持20+编程语言，智能识别文件类型
- 🧹 **多层次数据清洗**: 内容清洗、指标清洗、结构清洗
- 🔍 **智能去重分析**: 基于哈希和相似度的去重算法
- 📊 **全面数据分析**: 代码质量、复杂度、维护性分析
- 🚀 **Pipeline工作流**: 可配置的数据处理流程
- 📈 **多格式报告**: JSON、CSV、HTML、Markdown报告
- ⚙️ **灵活配置**: 丰富的配置选项和自定义规则

## 🚀 快速开始

### 1. 环境要求

- Python 3.8+
- Git
- 8GB+ 内存（推荐）

### 2. 安装

```bash
# 克隆项目
git clone https://github.com/Million-mo/RepoDP.git
cd RepoDP

# 安装依赖
pip install -r requirements.txt

# 快速启动（可选）
python quick_start.py
```

### 3. 基本使用

```bash
# 查看帮助
python -m src.repodp --help

# 添加代码仓库
python -m src.repodp repo add https://github.com/user/repo.git

# 提取文件内容
python -m src.repodp data extract repo

# 清洗数据
python -m src.repodp data clean repo

# 生成分析报告
python -m src.repodp data analyze repo
```

## 📚 详细使用指南

### 1. 仓库管理 (`repo`)

#### 添加仓库
```bash
# 添加远程仓库
python -m src.repodp repo add https://github.com/user/repo.git

# 添加本地仓库
python -m src.repodp repo add /path/to/local/repo

# 添加当前目录
python -m src.repodp repo add .

# 批量添加多个仓库
python -m src.repodp repo add repo1.git repo2.git repo3.git
```

#### 管理仓库
```bash
# 列出所有仓库
python -m src.repodp repo list

# 更新仓库
python -m src.repodp repo update repo-name

# 删除仓库
python -m src.repodp repo remove repo-name

# 清理空目录
python -m src.repodp repo cleanup
```

### 2. 数据处理 (`data`)

#### 文件提取
```bash
# 基本提取（JSONL格式）
python -m src.repodp data extract repo-name

# 指定输出格式
python -m src.repodp data extract repo-name --format json
python -m src.repodp data extract repo-name --format jsonl

# 指定输出目录
python -m src.repodp data extract repo-name --output /path/to/output
```

#### 内容清洗
```bash
# 基本清洗
python -m src.repodp data clean repo-name

# 直接覆盖原文件
python -m src.repodp data clean repo-name --in-place

# 指定输出文件
python -m src.repodp data clean repo-name --output cleaned_data.jsonl
```

#### 去重处理
```bash
# 基本去重
python -m src.repodp data deduplicate repo-name

# 指定保留策略
python -m src.repodp data deduplicate repo-name --strategy newest
python -m src.repodp data deduplicate repo-name --strategy oldest

# 直接覆盖原文件
python -m src.repodp data deduplicate repo-name --in-place
```

#### 指标清洗
```bash
# 基本指标清洗
python -m src.repodp data clean-metrics repo-name

# 干运行模式（仅分析）
python -m src.repodp data clean-metrics repo-name --dry-run

# 详细模式（显示违规信息）
python -m src.repodp data clean-metrics repo-name --verbose

# 自定义阈值配置
python -m src.repodp data clean-metrics repo-name --thresholds thresholds.json
```

#### 数据分析
```bash
# 基本分析
python -m src.repodp data analyze repo-name

# 指定报告格式
python -m src.repodp data analyze repo-name --format html
python -m src.repodp data analyze repo-name --format csv

# 指定输出目录
python -m src.repodp data analyze repo-name --output /path/to/reports
```

### 3. Pipeline工作流 (`pipeline`)

#### 基本Pipeline操作
```bash
# 列出所有可用的Pipeline
python -m src.repodp pipeline list-pipelines

# 查看特定Pipeline详情
python -m src.repodp pipeline list-pipelines --pipeline standard

# 验证Pipeline配置
python -m src.repodp pipeline validate standard

# 模拟执行Pipeline
python -m src.repodp pipeline dry-run standard
```

#### 执行Pipeline
```bash
# 执行单个仓库的Pipeline
python -m src.repodp pipeline run repo-name

# 指定Pipeline类型
python -m src.repodp pipeline run repo-name --pipeline quick

# 模拟执行
python -m src.repodp pipeline run repo-name --dry-run

# 指定输出目录
python -m src.repodp pipeline run repo-name --output /path/to/output
```

#### 批量处理
```bash
# 处理所有已添加的仓库
python -m src.repodp pipeline batch --all

# 处理指定的多个仓库
python -m src.repodp pipeline batch repo1 repo2 repo3

# 只处理特定类型的仓库
python -m src.repodp pipeline batch --all --filter local_reference
python -m src.repodp pipeline batch --all --filter remote

# 指定Pipeline和输出目录
python -m src.repodp pipeline batch --all --pipeline deep_clean --output /path/to/output

# 模拟执行
python -m src.repodp pipeline batch --all --dry-run

# 设置并行工作线程
python -m src.repodp pipeline batch --all --workers 8

# 不合并结果文件
python -m src.repodp pipeline batch --all --no-merge
```

### 4. 配置管理 (`config`)

#### 基本配置操作
```bash
# 查看所有配置
python -m src.repodp config list

# 获取特定配置值
python -m src.repodp config get extraction.max_file_size

# 设置配置值
python -m src.repodp config set extraction.max_file_size 20971520
```

#### 配置导入导出
```bash
# 导出配置
python -m src.repodp config export my_config.yaml

# 导入配置
python -m src.repodp config import my_config.yaml

# 生成配置模板
python -m src.repodp config generate --output template.yaml
```

#### 配置验证和信息
```bash
# 验证配置文件
python -m src.repodp config validate config.yaml

# 显示配置信息
python -m src.repodp config info

# 显示特定配置节信息
python -m src.repodp config info --section extraction

# 配置向导
python -m src.repodp config wizard --interactive
```

## 🔧 配置说明

### 主要配置项

#### 文件提取配置
```yaml
extraction:
  file_types: [".py", ".js", ".ts", ".java", ".cpp", ".c", ".h", ".go", ".rs"]
  exclude_dirs: [".git", "__pycache__", "node_modules", ".venv", "venv"]
  exclude_dir_patterns:  # 正则表达式排除模式
    - '^\.?venv.*$'      # 虚拟环境目录
    - '^.*_venv.*$'      # 包含_venv的目录
  max_file_size: 20971520  # 20MB
```

#### 清洗配置
```yaml
cleaning:
  normalize_whitespace: false
  preserve_structure: true
  remove_blank_lines: false
  remove_comments: false
  remove_imports: false
```

#### 文件指标清洗配置
```yaml
file_metrics_cleaning:
  thresholds:
    max_average_line_length: 200
    max_comment_percentage: 50
    max_digit_percentage: 50
    max_file_size: 1048576
    max_hex_percentage: 30
    max_line_count: 10000
    max_line_length: 500
    min_comment_percentage: 0
```

#### 去重配置
```yaml
deduplication:
  hash_algorithm: sha256
  min_file_size: 100
  similarity_threshold: 0.95
```

## 📊 支持的文件类型

### 编程语言
- **Python**: .py, .pyx, .pyi
- **JavaScript/TypeScript**: .js, .jsx, .ts, .tsx
- **Java**: .java
- **C/C++**: .c, .cpp, .cc, .cxx, .h, .hpp
- **Go**: .go
- **Rust**: .rs
- **PHP**: .php
- **Ruby**: .rb
- **Swift**: .swift
- **Kotlin**: .kt
- **C#**: .cs
- **Scala**: .scala

### 配置文件
- **YAML**: .yaml, .yml
- **JSON**: .json
- **XML**: .xml
- **INI**: .ini, .cfg
- **TOML**: .toml

### 文档和标记
- **Markdown**: .md, .markdown
- **HTML**: .html, .htm
- **CSS**: .css, .scss, .sass
- **SQL**: .sql

## 🎯 使用场景

### 1. 代码质量分析
```bash
# 完整代码质量分析流程
python -m src.repodp repo add https://github.com/user/project.git
python -m src.repodp data extract project
python -m src.repodp data clean project
python -m src.repodp data analyze project --format html
```

### 2. 大规模代码去重
```bash
# 批量处理多个仓库进行去重分析
python -m src.repodp repo add repo1.git repo2.git repo3.git
python -m src.repodp pipeline batch --all --pipeline quick
```

### 3. 代码库清理
```bash
# 清理代码库中的冗余文件
python -m src.repodp data extract project
python -m src.repodp data clean-metrics project --verbose
python -m src.repodp data deduplicate project
```

### 4. 多语言项目分析
```bash
# 分析多语言混合项目
python -m src.repodp data extract project
python -m src.repodp data analyze project --format comprehensive
```

## 📈 性能优化建议

### 1. 内存优化
- 使用JSONL格式处理大文件
- 调整`max_file_size`限制
- 使用批处理模式

### 2. 处理速度优化
- 增加并行工作线程数
- 使用快速Pipeline
- 排除不必要的文件类型

### 3. 存储优化
- 定期清理临时文件
- 使用压缩格式存储
- 配置合适的备份策略

## 🛠️ 故障排除

### 常见问题

#### 1. 内存不足
```bash
# 减少并行线程数
python -m src.repodp pipeline batch --all --workers 2

# 减少文件大小限制
python -m src.repodp config set extraction.max_file_size 10485760
```

#### 2. 处理速度慢
```bash
# 使用快速Pipeline
python -m src.repodp pipeline batch --all --pipeline quick

# 排除更多文件类型
python -m src.repodp config set extraction.exclude_dirs '["node_modules", ".git", "build", "dist"]'
```

#### 3. 磁盘空间不足
```bash
# 清理临时文件
python -m src.repodp repo cleanup

# 减少备份文件
python -m src.repodp config set file_metrics_cleaning.backup_enabled false
```

## 📝 输出文件说明

### 数据文件
- `extracted_files.jsonl`: 提取的文件内容
- `*_cleaned.jsonl`: 清洗后的文件内容
- `*_deduplicated.jsonl`: 去重后的文件内容
- `*_metrics_cleaned.jsonl`: 指标清洗后的文件内容

### 报告文件
- `analysis_report.html`: HTML格式分析报告
- `analysis_report.json`: JSON格式分析数据
- `analysis_report.csv`: CSV格式统计数据
- `pipeline_report.json`: Pipeline执行报告

### 配置文件
- `repositories.json`: 仓库配置信息
- `config.yaml`: 主配置文件
- `batch_pipeline_report.json`: 批量处理报告

## 🔗 相关文档

- [CLI命令指南](CLI_COMMANDS_GUIDE.md)
- [Pipeline使用指南](PIPELINE_GUIDE.md)
- [快速开始指南](QUICK_START_GUIDE.md)
- [项目总结](PROJECT_SUMMARY.md)

## 💡 最佳实践

1. **定期清理**: 使用`repo cleanup`清理临时文件
2. **配置管理**: 使用`config export/import`管理配置
3. **批量处理**: 使用`pipeline batch --all`处理多个仓库
4. **监控资源**: 使用`--dry-run`预览处理计划
5. **备份数据**: 启用备份功能保护重要数据

## 🆘 获取帮助

```bash
# 查看主帮助
python -m src.repodp --help

# 查看特定命令组帮助
python -m src.repodp repo --help
python -m src.repodp data --help
python -m src.repodp config --help
python -m src.repodp pipeline --help

# 查看特定命令帮助
python -m src.repodp data extract --help
python -m src.repodp pipeline batch --help
```

---

**RepoDP** - 让代码仓库数据处理变得简单高效！ 🚀
