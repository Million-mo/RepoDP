# RepoDP - 代码仓数据处理工具

RepoDP 是一个专门针对代码仓库的数据处理工具，支持多代码仓管理、文件内容提取、清洗、去重和数据分析。

## 功能特性

- 🔗 **多代码仓管理**: 支持管理多个 Git 代码仓库
- 📁 **文件内容提取**: 从代码仓中提取各种类型的文件内容
- 🧹 **文件清洗**: 清理和标准化文件结构
- ✨ **内容清洗**: 清理文件内容（去除注释、空白等）
- 📏 **文件指标清洗**: 基于文件大小、行数、注释比例等指标进行清洗
- 🔍 **文件去重**: 智能识别和去除重复文件
- 📊 **数据分析**: 提供强大的数据分析功能

## 安装

```bash
pip install -r requirements.txt
```

## 使用方法

### 方式1: 使用启动脚本 (推荐)
```bash
# 添加代码仓
./repodp add-repo <repo-url> <repo-name>

# 提取文件内容 (默认JSONL格式)
./repodp extract <repo-name>

# 提取文件内容 (指定格式)
./repodp extract <repo-name> --format jsonl
./repodp extract <repo-name> --format json

# 清洗文件
./repodp clean <repo-name>

# 文件指标清洗（基于文件大小、行数、注释比例等）
./repodp clean-metrics <repo-name>

# 去重分析
./repodp deduplicate <repo-name>

# 数据分析
./repodp analyze <repo-name>
```

### 方式2: 使用Python模块
```bash
# 设置环境变量
export PYTHONPATH=/path/to/RepoDP/src:$PYTHONPATH

# 运行命令
python -m repodp add-repo <repo-url> <repo-name>
python -m repodp extract <repo-name>
python -m repodp clean-metrics <repo-name> --verbose  # 查看详细的规则违规信息
```

## 数据格式

### JSONL格式 (默认)
提取的文件数据默认保存为JSONL格式，每行一个JSON对象：
```jsonl
{"path": "src/main.py", "content": "print('Hello')", "language": "python", ...}
{"path": "src/utils.py", "content": "def helper():", "language": "python", ...}
```

### JSON格式
也可以选择传统的JSON格式：
```json
[
  {"path": "src/main.py", "content": "print('Hello')", "language": "python", ...},
  {"path": "src/utils.py", "content": "def helper():", "language": "python", ...}
]
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
./repodp clean-metrics my-repo

# 干运行模式（仅分析，不执行清洗）
./repodp clean-metrics my-repo --dry-run

# 查看详细规则违规信息
./repodp clean-metrics my-repo --verbose

# 自定义阈值配置
./repodp clean-metrics my-repo --thresholds my_thresholds.json

# 禁用备份
./repodp clean-metrics my-repo --no-backup
```

## 项目结构

```
RepoDP/
├── src/
│   ├── core/           # 核心功能模块
│   ├── extractors/     # 文件提取器
│   ├── cleaners/       # 清洗器（包含文件指标清洗器）
│   ├── analyzers/      # 分析器
│   └── utils/          # 工具函数
├── config/             # 配置文件
├── data/               # 数据存储
│   ├── backups/        # 备份文件
│   ├── extracted/      # 提取的文件
│   ├── reports/        # 分析报告
│   └── logs/           # 日志文件
└── tests/              # 测试文件
```
