# CLI 命令使用指南

## 概述

RepoDP 的 CLI 命令已经按照功能进行了分组整理，使命令结构更加清晰和易于使用。

## 命令结构

```
repodp [OPTIONS] COMMAND [ARGS]...

Commands:
  config    配置管理命令
  data      数据处理命令  
  pipeline  Pipeline管理命令
  repo      仓库管理命令
```

## 详细命令说明

### 1. 仓库管理命令 (`repo`)

管理代码仓库的添加、更新、删除等操作。

```bash
# 列出所有仓库
repodp repo list

# 添加仓库
repodp repo add <url_or_path> [url_or_path ...]
repodp repo add https://github.com/user/repo.git
repodp repo add /path/to/local/repo
repodp repo add .  # 添加当前目录

# 更新仓库
repodp repo update <name>

# 删除仓库
repodp repo remove <name>

# 清理空目录
repodp repo cleanup
```

### 2. 数据处理命令 (`data`)

处理代码仓库的数据提取、清洗、去重、分析等操作。

```bash
# 提取文件内容
repodp data extract <name> [--output DIR] [--format json|jsonl]

# 清洗内容
repodp data clean <name> [--output FILE] [--in-place]

# 去重处理
repodp data deduplicate <name> [--strategy newest|oldest|first|last] [--output FILE] [--in-place]

# 基于指标的清洗
repodp data clean-metrics <name> [--thresholds FILE] [--dry-run] [--output FILE] [--in-place] [--verbose]

# 数据分析
repodp data analyze <name> [--format json|csv|html|markdown|comprehensive] [--output DIR]
```

### 3. 配置管理命令 (`config`)

管理系统配置的查看、设置、导入导出等操作。

```bash
# 设置配置值
repodp config set <key> <value>

# 获取配置值
repodp config get <key>

# 列出所有配置
repodp config list

# 导出配置
repodp config export [--file FILE]

# 导入配置
repodp config import <file>

# 生成配置模板
repodp config generate [--output FILE] [--no-comments]

# 验证配置文件
repodp config validate <file>

# 显示配置信息
repodp config info [--section SECTION]

# 配置向导
repodp config wizard [--interactive]
```

### 4. Pipeline管理命令 (`pipeline`)

管理数据处理流程的配置和执行。

```bash
# 列出所有pipeline
repodp pipeline list-pipelines [--pipeline NAME]

# 验证pipeline配置
repodp pipeline validate <pipeline_name>

# 模拟执行pipeline
repodp pipeline dry-run <pipeline_name>

# 执行pipeline
repodp pipeline run <repo_name> [--pipeline NAME] [--output DIR] [--dry-run]

# 批量执行pipeline
repodp pipeline batch [repo_names ...] [--all] [--pipeline NAME] [--output DIR] [--workers N] [--no-merge] [--dry-run] [--filter TYPE]

# 添加pipeline配置
repodp pipeline add <pipeline_name> <config_file>

# 删除pipeline配置
repodp pipeline remove <pipeline_name>

# 更新pipeline配置
repodp pipeline update <pipeline_name> <config_file>
```

## 常用工作流程

### 1. 基本数据处理流程

```bash
# 1. 添加仓库
repodp repo add https://github.com/user/repo.git

# 2. 提取文件
repodp data extract repo

# 3. 清洗内容
repodp data clean repo

# 4. 去重处理
repodp data deduplicate repo

# 5. 分析数据
repodp data analyze repo
```

### 2. 批量处理流程

```bash
# 1. 添加多个仓库
repodp repo add https://github.com/user/repo1.git https://github.com/user/repo2.git

# 2. 批量处理所有仓库
repodp pipeline batch --all

# 3. 只处理特定类型的仓库
repodp pipeline batch --all --filter local_reference
```

### 3. 配置管理流程

```bash
# 1. 查看当前配置
repodp config list

# 2. 设置特定配置
repodp config set extraction.max_file_size 20971520

# 3. 导出配置
repodp config export my_config.yaml

# 4. 验证配置
repodp config validate my_config.yaml
```

## 命令优势

### 1. 逻辑分组
- **仓库管理**: 所有仓库相关操作集中在一起
- **数据处理**: 数据提取、清洗、分析等操作有序排列
- **配置管理**: 配置相关操作统一管理
- **Pipeline管理**: 流程管理操作独立成组

### 2. 命令层次清晰
- 主命令 → 功能组 → 具体操作
- 减少命令冲突和歧义
- 便于记忆和使用

### 3. 向后兼容
- 保持了原有的功能
- 只是重新组织了命令结构
- 提供了更清晰的帮助信息

## 帮助信息

```bash
# 查看主帮助
repodp --help

# 查看特定功能组的帮助
repodp repo --help
repodp data --help
repodp config --help
repodp pipeline --help

# 查看特定命令的帮助
repodp repo add --help
repodp data extract --help
repodp pipeline batch --help
```
