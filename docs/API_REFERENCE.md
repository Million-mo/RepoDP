# RepoDP API 参考

## 命令结构

RepoDP 采用分组命令结构，使功能更加清晰和易于使用：

```
repodp [OPTIONS] COMMAND [ARGS]...

Commands:
  config    配置管理命令
  data      数据处理命令  
  pipeline  Pipeline管理命令
  repo      仓库管理命令
```

## 全局选项

```bash
--help, -h              显示帮助信息
--version, -v           显示版本信息
--verbose              启用详细输出
--config FILE           指定配置文件路径
--log-level LEVEL       设置日志级别 (DEBUG, INFO, WARNING, ERROR)
```

## 仓库管理命令 (`repo`)

管理代码仓库的添加、更新、删除等操作。

### `repo list`
列出所有已添加的仓库。

```bash
python -m src.repodp repo list [OPTIONS]

Options:
  --format FORMAT        输出格式 (table, json, yaml) [default: table]
  --filter TYPE          过滤仓库类型 (remote, local_reference, local_path)
  --show-details         显示详细信息
```

**示例**:
```bash
# 列出所有仓库
python -m src.repodp repo list

# 只显示远程仓库
python -m src.repodp repo list --filter remote

# 以JSON格式输出
python -m src.repodp repo list --format json
```

### `repo add`
添加新的代码仓库。

```bash
python -m src.repodp repo add <url_or_path> [url_or_path ...] [OPTIONS]

Arguments:
  url_or_path           仓库URL或本地路径，可指定多个

Options:
  --name NAME           指定仓库名称（可选）
  --branch BRANCH       指定分支名称 [default: main]
  --depth DEPTH         Git克隆深度 [default: 1]
  --no-update           不自动更新仓库
```

**示例**:
```bash
# 添加GitHub仓库
python -m src.repodp repo add https://github.com/user/repo.git

# 添加本地仓库
python -m src.repodp repo add /path/to/local/repo

# 添加当前目录
python -m src.repodp repo add .

# 添加多个仓库
python -m src.repodp repo add https://github.com/user/repo1.git https://github.com/user/repo2.git

# 指定仓库名称
python -m src.repodp repo add https://github.com/user/repo.git --name my-repo
```

### `repo update`
更新指定仓库到最新版本。

```bash
python -m src.repodp repo update <name> [OPTIONS]

Arguments:
  name                  仓库名称

Options:
  --force               强制更新，即使有未提交的更改
  --branch BRANCH       更新到指定分支
```

**示例**:
```bash
# 更新仓库
python -m src.repodp repo update my-repo

# 强制更新
python -m src.repodp repo update my-repo --force
```

### `repo remove`
删除指定的仓库。

```bash
python -m src.repodp repo remove <name> [OPTIONS]

Arguments:
  name                  仓库名称

Options:
  --keep-data           保留数据文件
  --confirm             跳过确认提示
```

**示例**:
```bash
# 删除仓库
python -m src.repodp repo remove my-repo

# 删除仓库但保留数据
python -m src.repodp repo remove my-repo --keep-data
```

### `repo cleanup`
清理空的仓库目录。

```bash
python -m src.repodp repo cleanup [OPTIONS]

Options:
  --dry-run             仅显示将要清理的目录
  --force               跳过确认提示
```

## 数据处理命令 (`data`)

处理代码仓库的数据提取、清洗、去重、分析等操作。

### `data extract`
从代码仓库中提取文件内容。

```bash
python -m src.repodp data extract <name> [OPTIONS]

Arguments:
  name                  仓库名称

Options:
  --output DIR          输出目录 [default: data/extracted]
  --format FORMAT       输出格式 (json, jsonl) [default: jsonl]
  --file-types TYPES    支持的文件类型，逗号分隔
  --exclude-dirs DIRS   排除的目录，逗号分隔
  --max-file-size SIZE  最大文件大小（字节）
  --include-metadata    包含文件元数据
  --verbose             详细输出
```

**示例**:
```bash
# 基本提取
python -m src.repodp data extract my-repo

# 指定输出格式
python -m src.repodp data extract my-repo --format json

# 指定输出目录
python -m src.repodp data extract my-repo --output /path/to/output

# 只提取特定文件类型
python -m src.repodp data extract my-repo --file-types .py,.js,.ts

# 排除特定目录
python -m src.repodp data extract my-repo --exclude-dirs node_modules,.git
```

### `data clean`
清洗文件内容。

```bash
python -m src.repodp data clean <name> [OPTIONS]

Arguments:
  name                  仓库名称

Options:
  --output FILE         输出文件路径
  --in-place            直接修改原文件
  --remove-comments     移除注释
  --remove-imports      移除导入语句
  --normalize-whitespace 标准化空白字符
  --backup              创建备份
  --verbose             详细输出
```

**示例**:
```bash
# 基本清洗
python -m src.repodp data clean my-repo

# 直接修改原文件
python -m src.repodp data clean my-repo --in-place

# 指定输出文件
python -m src.repodp data clean my-repo --output cleaned_files.jsonl
```

### `data deduplicate`
去除重复文件。

```bash
python -m src.repodp data deduplicate <name> [OPTIONS]

Arguments:
  name                  仓库名称

Options:
  --strategy STRATEGY   保留策略 (newest, oldest, first, last) [default: newest]
  --output FILE         输出文件路径
  --in-place            直接修改原文件
  --min-file-size SIZE  最小文件大小（字节）
  --similarity-threshold THRESHOLD  相似度阈值 [default: 0.95]
  --verbose             详细输出
```

**示例**:
```bash
# 基本去重
python -m src.repodp data deduplicate my-repo

# 保留最旧的文件
python -m src.repodp data deduplicate my-repo --strategy oldest

# 设置相似度阈值
python -m src.repodp data deduplicate my-repo --similarity-threshold 0.9
```

### `data clean-metrics`
基于文件指标进行清洗。

```bash
python -m src.repodp data clean-metrics <name> [OPTIONS]

Arguments:
  name                  仓库名称

Options:
  --thresholds FILE     自定义阈值配置文件
  --dry-run             仅分析，不执行清洗
  --output FILE         输出文件路径
  --in-place            直接修改原文件
  --backup              创建备份
  --verbose             详细输出
```

**示例**:
```bash
# 基本指标清洗
python -m src.repodp data clean-metrics my-repo

# 干运行模式
python -m src.repodp data clean-metrics my-repo --dry-run

# 使用自定义阈值
python -m src.repodp data clean-metrics my-repo --thresholds my_thresholds.json
```

### `data analyze`
分析代码质量和生成报告。

```bash
python -m src.repodp data analyze <name> [OPTIONS]

Arguments:
  name                  仓库名称

Options:
  --format FORMAT       报告格式 (json, csv, html, markdown, comprehensive) [default: json]
  --output DIR          输出目录 [default: data/reports]
  --include-metrics     包含详细指标
  --include-complexity  包含复杂度分析
  --include-maintainability 包含维护性分析
  --verbose             详细输出
```

**示例**:
```bash
# 基本分析
python -m src.repodp data analyze my-repo

# 生成HTML报告
python -m src.repodp data analyze my-repo --format html

# 生成综合报告
python -m src.repodp data analyze my-repo --format comprehensive
```

## 配置管理命令 (`config`)

管理系统配置的查看、设置、导入导出等操作。

### `config set`
设置配置值。

```bash
python -m src.repodp config set <key> <value> [OPTIONS]

Arguments:
  key                   配置键
  value                 配置值

Options:
  --section SECTION     配置节名称
  --type TYPE           值类型 (string, int, float, bool, list, dict)
```

**示例**:
```bash
# 设置文件大小限制
python -m src.repodp config set extraction.max_file_size 20971520

# 设置排除目录
python -m src.repodp config set extraction.exclude_dirs '["node_modules", ".git"]'

# 设置布尔值
python -m src.repodp config set extraction.include_metadata true --type bool
```

### `config get`
获取配置值。

```bash
python -m src.repodp config get <key> [OPTIONS]

Arguments:
  key                   配置键

Options:
  --section SECTION     配置节名称
  --format FORMAT       输出格式 (value, json, yaml) [default: value]
```

### `config list`
列出所有配置。

```bash
python -m src.repodp config list [OPTIONS]

Options:
  --section SECTION     只显示指定节的配置
  --format FORMAT       输出格式 (table, json, yaml) [default: table]
  --show-defaults       显示默认值
```

### `config export`
导出配置到文件。

```bash
python -m src.repodp config export [OPTIONS]

Options:
  --file FILE           输出文件路径 [default: config_export.yaml]
  --section SECTION     只导出指定节
  --include-defaults    包含默认值
  --format FORMAT       输出格式 (yaml, json) [default: yaml]
```

### `config import`
从文件导入配置。

```bash
python -m src.repodp config import <file> [OPTIONS]

Arguments:
  file                  配置文件路径

Options:
  --merge               合并到现有配置
  --backup              创建当前配置的备份
  --validate            验证配置格式
```

### `config generate`
生成配置模板。

```bash
python -m src.repodp config generate [OPTIONS]

Options:
  --output FILE         输出文件路径 [default: config_template.yaml]
  --no-comments         不包含注释
  --include-examples    包含示例值
```

### `config validate`
验证配置文件。

```bash
python -m src.repodp config validate <file> [OPTIONS]

Arguments:
  file                  配置文件路径

Options:
  --strict              严格模式验证
  --show-errors         显示详细错误信息
```

### `config info`
显示配置信息。

```bash
python -m src.repodp config info [OPTIONS]

Options:
  --section SECTION     只显示指定节的信息
  --format FORMAT       输出格式 (table, json, yaml) [default: table]
```

### `config wizard`
配置向导。

```bash
python -m src.repodp config wizard [OPTIONS]

Options:
  --interactive         交互式模式
  --output FILE         输出配置文件路径
```

## Pipeline管理命令 (`pipeline`)

管理数据处理流程的配置和执行。

### `pipeline list-pipelines`
列出可用的Pipeline。

```bash
python -m src.repodp pipeline list-pipelines [OPTIONS]

Options:
  --pipeline NAME       显示指定Pipeline的详细信息
  --format FORMAT       输出格式 (table, json, yaml) [default: table]
  --show-steps          显示步骤详情
```

### `pipeline validate`
验证Pipeline配置。

```bash
python -m src.repodp pipeline validate <pipeline_name> [OPTIONS]

Arguments:
  pipeline_name         Pipeline名称

Options:
  --strict              严格模式验证
  --show-errors         显示详细错误信息
```

### `pipeline dry-run`
模拟执行Pipeline。

```bash
python -m src.repodp pipeline dry-run <pipeline_name> [OPTIONS]

Arguments:
  pipeline_name         Pipeline名称

Options:
  --repo-name NAME      指定仓库名称
  --show-details        显示详细信息
```

### `pipeline run`
执行Pipeline。

```bash
python -m src.repodp pipeline run <repo_name> [OPTIONS]

Arguments:
  repo_name             仓库名称

Options:
  --pipeline NAME       指定Pipeline名称 [default: standard]
  --output DIR          输出目录
  --dry-run             模拟执行
  --verbose             详细输出
```

### `pipeline batch`
批量执行Pipeline。

```bash
python -m src.repodp pipeline batch [repo_names ...] [OPTIONS]

Arguments:
  repo_names            仓库名称列表

Options:
  --all                 处理所有仓库
  --pipeline NAME       指定Pipeline名称 [default: standard]
  --output DIR          输出目录
  --workers N           并行工作线程数 [default: 4]
  --no-merge            不合并结果文件
  --dry-run             模拟执行
  --filter TYPE         过滤仓库类型 (remote, local_reference, local_path)
  --verbose             详细输出
```

**示例**:
```bash
# 处理所有仓库
python -m src.repodp pipeline batch --all

# 处理指定仓库
python -m src.repodp pipeline batch repo1 repo2 repo3

# 使用特定Pipeline
python -m src.repodp pipeline batch --all --pipeline deep_clean

# 设置并行线程数
python -m src.repodp pipeline batch --all --workers 8

# 模拟执行
python -m src.repodp pipeline batch --all --dry-run
```

### `pipeline add`
添加新的Pipeline配置。

```bash
python -m src.repodp pipeline add <pipeline_name> <config_file> [OPTIONS]

Arguments:
  pipeline_name         Pipeline名称
  config_file           配置文件路径

Options:
  --validate            验证配置格式
  --backup              备份现有配置
```

### `pipeline remove`
删除Pipeline配置。

```bash
python -m src.repodp pipeline remove <pipeline_name> [OPTIONS]

Arguments:
  pipeline_name         Pipeline名称

Options:
  --confirm             跳过确认提示
```

### `pipeline update`
更新Pipeline配置。

```bash
python -m src.repodp pipeline update <pipeline_name> <config_file> [OPTIONS]

Arguments:
  pipeline_name         Pipeline名称
  config_file           配置文件路径

Options:
  --validate            验证配置格式
  --backup              备份现有配置
```

## 常用工作流程

### 1. 基本数据处理流程

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

### 2. 批量处理流程

```bash
# 1. 添加多个仓库
python -m src.repodp repo add https://github.com/user/repo1.git https://github.com/user/repo2.git

# 2. 批量处理所有仓库
python -m src.repodp pipeline batch --all

# 3. 只处理特定类型的仓库
python -m src.repodp pipeline batch --all --filter local_reference
```

### 3. 配置管理流程

```bash
# 1. 查看当前配置
python -m src.repodp config list

# 2. 设置特定配置
python -m src.repodp config set extraction.max_file_size 20971520

# 3. 导出配置
python -m src.repodp config export my_config.yaml

# 4. 验证配置
python -m src.repodp config validate my_config.yaml
```

## 帮助信息

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

## 错误代码

| 代码 | 描述 | 解决方案 |
|------|------|----------|
| 1 | 通用错误 | 检查命令语法和参数 |
| 2 | 配置错误 | 验证配置文件格式 |
| 3 | 文件系统错误 | 检查文件权限和路径 |
| 4 | 网络错误 | 检查网络连接和URL |
| 5 | 仓库错误 | 检查仓库URL和Git配置 |
| 6 | 数据处理错误 | 检查输入文件格式 |
| 7 | Pipeline错误 | 验证Pipeline配置 |

---

**提示**: 使用 `--help` 选项可以获取任何命令的详细帮助信息。
