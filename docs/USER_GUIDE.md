# RepoDP 用户使用指南

## 目录
- [快速开始](#快速开始)
- [环境准备](#环境准备)
- [基本使用流程](#基本使用流程)
- [命令参考](#命令参考)
- [配置管理](#配置管理)
- [Pipeline工作流](#pipeline工作流)
- [高级功能](#高级功能)
- [故障排除](#故障排除)
- [最佳实践](#最佳实践)

## 快速开始

### 环境准备
```bash
# 安装依赖
pip install -r requirements.txt

# 运行快速检查
python quick_start.py
```

### 基本使用流程

#### 步骤1: 添加代码仓库
```bash
# 添加一个GitHub仓库
python -m src.repodp repo add https://github.com/octocat/Hello-World.git

# 添加本地仓库
python -m src.repodp repo add /path/to/local/repo

# 添加当前目录
python -m src.repodp repo add .

# 查看已添加的仓库
python -m src.repodp repo list
```

#### 步骤2: 提取文件内容
```bash
# 提取文件内容 (默认JSONL格式)
python -m src.repodp data extract repo-name

# 指定输出格式
python -m src.repodp data extract repo-name --format json
python -m src.repodp data extract repo-name --format jsonl

# 指定输出目录
python -m src.repodp data extract repo-name --output /path/to/output
```

#### 步骤3: 数据清洗
```bash
# 内容清洗
python -m src.repodp data clean repo-name

# 去重处理
python -m src.repodp data deduplicate repo-name

# 基于指标的清洗
python -m src.repodp data clean-metrics repo-name --verbose
```

#### 步骤4: 数据分析
```bash
# 生成分析报告
python -m src.repodp data analyze repo-name

# 指定报告格式
python -m src.repodp data analyze repo-name --format html
python -m src.repodp data analyze repo-name --format csv
python -m src.repodp data analyze repo-name --format markdown
```

## 命令参考

### 仓库管理命令 (`repo`)

管理代码仓库的添加、更新、删除等操作。

```bash
# 列出所有仓库
python -m src.repodp repo list

# 添加仓库
python -m src.repodp repo add <url_or_path> [url_or_path ...]
python -m src.repodp repo add https://github.com/user/repo.git
python -m src.repodp repo add /path/to/local/repo
python -m src.repodp repo add .  # 添加当前目录

# 更新仓库
python -m src.repodp repo update <name>

# 删除仓库
python -m src.repodp repo remove <name>

# 清理空目录
python -m src.repodp repo cleanup
```

### 数据处理命令 (`data`)

处理代码仓库的数据提取、清洗、去重、分析等操作。

```bash
# 提取文件内容
python -m src.repodp data extract <name> [--output DIR] [--format json|jsonl]

# 清洗内容
python -m src.repodp data clean <name> [--output FILE] [--in-place]

# 去重处理
python -m src.repodp data deduplicate <name> [--strategy newest|oldest|first|last] [--output FILE] [--in-place]

# 基于指标的清洗
python -m src.repodp data clean-metrics <name> [--thresholds FILE] [--dry-run] [--output FILE] [--in-place] [--verbose]

# 数据分析
python -m src.repodp data analyze <name> [--format json|csv|html|markdown|comprehensive] [--output DIR]
```

### 配置管理命令 (`config`)

管理系统配置的查看、设置、导入导出等操作。

```bash
# 设置配置值
python -m src.repodp config set <key> <value>

# 获取配置值
python -m src.repodp config get <key>

# 列出所有配置
python -m src.repodp config list

# 导出配置
python -m src.repodp config export [--file FILE]

# 导入配置
python -m src.repodp config import <file>

# 生成配置模板
python -m src.repodp config generate [--output FILE] [--no-comments]

# 验证配置文件
python -m src.repodp config validate <file>

# 显示配置信息
python -m src.repodp config info [--section SECTION]

# 配置向导
python -m src.repodp config wizard [--interactive]
```

### Pipeline管理命令 (`pipeline`)

管理数据处理流程的配置和执行。

```bash
# 列出所有pipeline
python -m src.repodp pipeline list-pipelines [--pipeline NAME]

# 验证pipeline配置
python -m src.repodp pipeline validate <pipeline_name>

# 模拟执行pipeline
python -m src.repodp pipeline dry-run <pipeline_name>

# 执行pipeline
python -m src.repodp pipeline run <repo_name> [--pipeline NAME] [--output DIR] [--dry-run]

# 批量执行pipeline
python -m src.repodp pipeline batch [repo_names ...] [--all] [--pipeline NAME] [--output DIR] [--workers N] [--no-merge] [--dry-run] [--filter TYPE]

# 添加pipeline配置
python -m src.repodp pipeline add <pipeline_name> <config_file>

# 删除pipeline配置
python -m src.repodp pipeline remove <pipeline_name>

# 更新pipeline配置
python -m src.repodp pipeline update <pipeline_name> <config_file>
```

## 配置管理

### 查看配置
```bash
python -m src.repodp config list
```

### 设置配置
```bash
# 设置最大文件大小
python -m src.repodp config set extraction.max_file_size 20971520  # 20MB

# 设置排除的目录
python -m src.repodp config set extraction.exclude_dirs '["node_modules", ".git"]'

# 设置支持的文件类型
python -m src.repodp config set extraction.file_types '[".py", ".js", ".ts", ".java"]'
```

### 导出/导入配置
```bash
# 导出配置
python -m src.repodp config export my_config.yaml

# 导入配置
python -m src.repodp config import my_config.yaml

# 生成配置模板
python -m src.repodp config generate --output template.yaml
```

### 主要配置选项

#### 文件提取配置
- `extraction.max_file_size`: 最大文件大小（字节）
- `extraction.exclude_dirs`: 排除的目录列表
- `extraction.file_types`: 支持的文件类型列表
- `extraction.include_metadata`: 是否包含元数据

#### 清洗配置
- `cleaning.remove_comments`: 是否移除注释
- `cleaning.remove_imports`: 是否移除导入语句
- `cleaning.normalize_whitespace`: 是否标准化空白字符

#### 去重配置
- `deduplication.strategy`: 去重策略（newest, oldest, first, last）
- `deduplication.min_file_size`: 最小文件大小
- `deduplication.similarity_threshold`: 相似度阈值

#### 文件指标清洗配置
- `file_metrics.max_file_size`: 文件大小阈值
- `file_metrics.max_line_count`: 最大行数
- `file_metrics.max_line_length`: 最大行长度
- `file_metrics.min_comment_percentage`: 最小注释比例
- `file_metrics.max_comment_percentage`: 最大注释比例
- `file_metrics.max_digit_percentage`: 最大数字比例
- `file_metrics.max_hex_percentage`: 最大十六进制比例
- `file_metrics.max_average_line_length`: 最大平均行长度

## Pipeline工作流

### 预设Pipeline

#### 1. 标准Pipeline (standard)
完整的代码仓库数据处理流程：
- 文件提取 → 去重 → 内容清洗 → 文件指标清洗

#### 2. 快速Pipeline (quick)
仅进行基础处理：
- 文件提取 → 去重

#### 3. 深度清洗Pipeline (deep_clean)
包含所有清洗步骤：
- 文件提取 → 去重 → 内容清洗 → JSONL清洗 → 文件指标清洗

#### 4. 分析Pipeline (analysis)
仅进行分析，不修改文件：
- 文件提取 → 重复文件分析 → 文件指标分析

### 使用Pipeline

```bash
# 列出可用的Pipeline
python -m src.repodp pipeline list-pipelines

# 执行标准Pipeline
python -m src.repodp pipeline run repo-name --pipeline standard

# 批量处理所有仓库
python -m src.repodp pipeline batch --all

# 模拟执行（预览处理计划）
python -m src.repodp pipeline batch --all --dry-run
```

## 高级功能

### 文件指标清洗

基于文件指标进行智能清洗，支持以下指标：

**清洗规则**（过高则清洗）：
- 单行最大长度 (`max_line_length`)
- 文件大小 (`max_file_size`)
- 文件行数 (`max_line_count`)

**删除规则**（超出范围则删除）：
- 注释比例 (`min_comment_percentage`, `max_comment_percentage`)
- 数字比例 (`max_digit_percentage`)
- 十六进制比例 (`max_hex_percentage`)
- 平均行长度 (`max_average_line_length`)

**使用示例**：
```bash
# 基本使用
python -m src.repodp data clean-metrics my-repo

# 干运行模式（仅分析，不执行清洗）
python -m src.repodp data clean-metrics my-repo --dry-run

# 查看详细规则违规信息
python -m src.repodp data clean-metrics my-repo --verbose

# 自定义阈值配置
python -m src.repodp data clean-metrics my-repo --thresholds my_thresholds.json
```

### 批量处理

```bash
# 添加多个仓库
python -m src.repodp repo add https://github.com/user/repo1.git https://github.com/user/repo2.git

# 批量处理所有已添加的仓库
python -m src.repodp pipeline batch --all

# 只处理特定类型的仓库
python -m src.repodp pipeline batch --all --filter local_reference

# 处理指定的多个仓库
python -m src.repodp pipeline batch repo1 repo2 repo3

# 设置并行工作线程数
python -m src.repodp pipeline batch --all --workers 8
```

### 输出数据使用

#### 读取JSONL文件
```python
from repodp.utils import JSONLUtils

# 读取所有数据
data = JSONLUtils.read_jsonl_all('data/extracted/repo/extracted_files.jsonl')

# 逐行处理
for record in JSONLUtils.read_jsonl('data/extracted/repo/extracted_files.jsonl'):
    print(f"文件: {record['path']}, 语言: {record['language']}")
```

#### 分析报告
- **HTML报告**: 在浏览器中打开查看可视化结果
- **CSV报告**: 导入Excel或数据分析工具
- **JSON报告**: 用于程序化处理

## 故障排除

### 常见问题

**问题1**: `No module named repodp`
```bash
# 解决方案: 使用正确的模块路径
python -m src.repodp --help

# 或者设置PYTHONPATH
export PYTHONPATH=/path/to/RepoDP/src:$PYTHONPATH
python -m repodp --help
```

**问题2**: 仓库克隆失败
```bash
# 检查网络连接
ping github.com

# 检查Git配置
git config --global user.name
git config --global user.email
```

**问题3**: 内存不足
```bash
# 使用JSONL格式 (默认)
python -m src.repodp data extract <repo-name> --format jsonl

# 调整配置
python -m src.repodp config set extraction.max_file_size 5242880  # 5MB
```

**问题4**: 权限问题
```bash
# 确保有足够的文件读写权限
chmod -R 755 /path/to/RepoDP/data
```

### 调试技巧

1. 使用 `--verbose` 选项获取详细日志
2. 使用 `--dry-run` 模式预览操作
3. 检查配置文件是否正确
4. 查看错误日志文件

## 最佳实践

### 1. 性能优化

#### 大仓库处理
```bash
# 增加排除目录
python -m src.repodp config set extraction.exclude_dirs '["node_modules", ".git", "build", "dist", "target"]'

# 限制文件大小
python -m src.repodp config set extraction.max_file_size 10485760  # 10MB

# 限制文件类型
python -m src.repodp config set extraction.file_types '[".py", ".js", ".ts", ".java"]'
```

#### 内存优化
- 使用JSONL格式 (默认)
- 分批处理大仓库
- 调整批处理大小

### 2. 工作流程建议

#### 基本数据处理流程
```bash
# 1. 添加仓库
python -m src.repodp repo add https://github.com/user/repo.git

# 2. 提取文件
python -m src.repodp data extract repo

# 3. 清洗内容
python -m src.repodp data clean repo

# 4. 去重处理
python -m src.repodp data deduplicate repo

# 5. 分析数据
python -m src.repodp data analyze repo
```

#### 批量处理流程
```bash
# 1. 添加多个仓库
python -m src.repodp repo add https://github.com/user/repo1.git https://github.com/user/repo2.git

# 2. 批量处理所有仓库
python -m src.repodp pipeline batch --all

# 3. 只处理特定类型的仓库
python -m src.repodp pipeline batch --all --filter local_reference
```

### 3. 数据备份

- 在执行清洗操作前备份重要数据
- 使用版本控制管理配置文件
- 定期导出配置和结果

### 4. 监控和日志

- 关注执行报告中的错误和警告信息
- 使用详细模式获取更多调试信息
- 定期检查输出文件的质量

## 获取帮助

```bash
# 查看主帮助
python -m src.repodp --help

# 查看特定功能组的帮助
python -m src.repodp repo --help
python -m src.repodp data --help
python -m src.repodp config --help
python -m src.repodp pipeline --help

# 查看特定命令的帮助
python -m src.repodp repo add --help
python -m src.repodp data extract --help
python -m src.repodp pipeline batch --help
```

如果您在文档中找不到所需信息，可以：

1. 查看命令行帮助：`python -m src.repodp --help`
2. 查看特定命令帮助：`python -m src.repodp <command> --help`
3. 提交 Issue 到 GitHub 仓库
4. 查看项目示例：`examples/` 目录

---

**提示**: 建议新用户按照 README.md → USER_GUIDE.md → PIPELINE_GUIDE.md 的顺序阅读文档。
