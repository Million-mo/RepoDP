# RopeDP - 代码仓数据处理工具

RopeDP 是一个专门针对代码仓库的数据处理工具，支持多代码仓管理、文件内容提取、清洗、去重和数据分析。

## 功能特性

- 🔗 **多代码仓管理**: 支持管理多个 Git 代码仓库
- 📁 **文件内容提取**: 从代码仓中提取各种类型的文件内容
- 🧹 **文件清洗**: 清理和标准化文件结构
- ✨ **内容清洗**: 清理文件内容（去除注释、空白等）
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

# 去重分析
./repodp deduplicate <repo-name>

# 数据分析
./repodp analyze <repo-name>
```

### 方式2: 使用Python模块
```bash
# 设置环境变量
export PYTHONPATH=/path/to/RopeDP/src:$PYTHONPATH

# 运行命令
python -m repodp add-repo <repo-url> <repo-name>
python -m repodp extract <repo-name>
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

## 项目结构

```
RopeDP/
├── src/
│   ├── core/           # 核心功能模块
│   ├── extractors/     # 文件提取器
│   ├── cleaners/       # 清洗器
│   ├── analyzers/      # 分析器
│   └── utils/          # 工具函数
├── config/             # 配置文件
├── data/               # 数据存储
└── tests/              # 测试文件
```

