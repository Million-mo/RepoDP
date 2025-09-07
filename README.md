# RepoDP - 代码仓数据处理工具

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-active-brightgreen.svg)](https://github.com/Million-mo/RepoDP)

RepoDP 是一个专业的代码仓库数据处理工具，专为大规模代码分析和处理而设计。它提供了完整的代码仓库管理、文件提取、数据清洗、去重分析和报告生成功能。

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

### 环境要求
- Python 3.8+
- Git
- 8GB+ 内存（推荐）

### 安装
```bash
# 克隆项目
git clone https://github.com/Million-mo/RepoDP.git
cd RepoDP

# 安装依赖
pip install -r requirements.txt

# 快速启动（可选）
python quick_start.py
```

### 基本使用
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

# 批量处理所有仓库
python -m src.repodp pipeline batch --all
```

## 📚 详细使用指南

### 命令结构
RepoDP 采用分组命令结构，使功能更加清晰：

```bash
repodp [OPTIONS] COMMAND [ARGS]...

Commands:
  config    配置管理命令
  data      数据处理命令  
  pipeline  Pipeline管理命令
  repo      仓库管理命令
```

### 仓库管理
```bash
# 列出所有仓库
python -m src.repodp repo list

# 添加仓库
python -m src.repodp repo add https://github.com/user/repo.git

# 更新仓库
python -m src.repodp repo update repo-name

# 删除仓库
python -m src.repodp repo remove repo-name
```

### 数据处理
```bash
# 提取文件内容
python -m src.repodp data extract repo-name

# 清洗内容
python -m src.repodp data clean repo-name

# 去重处理
python -m src.repodp data deduplicate repo-name

# 指标清洗
python -m src.repodp data clean-metrics repo-name --verbose

# 数据分析
python -m src.repodp data analyze repo-name --format html
```

### Pipeline工作流
```bash
# 批量处理所有仓库
python -m src.repodp pipeline batch --all

# 处理指定仓库
python -m src.repodp pipeline batch repo1 repo2 repo3

# 模拟执行
python -m src.repodp pipeline batch --all --dry-run
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

## 📁 数据格式

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

## 🔧 高级功能

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

## 📚 相关文档

- **[用户使用指南](USER_GUIDE.md)** - 详细的使用说明和最佳实践
- **[CLI命令指南](CLI_COMMANDS_GUIDE.md)** - 完整的命令行参考
- **[Pipeline使用指南](PIPELINE_GUIDE.md)** - Pipeline工作流详细说明
- **[快速开始指南](QUICK_START_GUIDE.md)** - 快速上手指南
- **[项目总结](PROJECT_SUMMARY.md)** - 项目功能总结

## 🏗️ 项目结构

```
RepoDP/
├── src/repodp/                 # 核心源代码
│   ├── core/                   # 核心功能模块
│   │   ├── repository_manager.py  # 代码仓管理
│   │   ├── config_manager.py      # 配置管理
│   │   └── pipeline_manager.py    # Pipeline管理
│   ├── extractors/             # 文件提取器
│   │   ├── file_extractor.py      # 基础文件提取
│   │   ├── code_extractor.py      # 代码结构提取
│   │   └── text_extractor.py      # 文本特征提取
│   ├── cleaners/               # 清洗器
│   │   ├── content_cleaner.py     # 内容清洗
│   │   ├── file_metrics_cleaner.py # 指标清洗
│   │   ├── jsonl_content_cleaner.py # JSONL清洗
│   │   └── deduplicator.py        # 去重器
│   ├── analyzers/              # 分析器
│   │   ├── code_analyzer.py       # 代码分析
│   │   ├── metrics_calculator.py  # 指标计算
│   │   └── report_generator.py    # 报告生成
│   ├── utils/                  # 工具函数
│   └── cli.py                  # 命令行界面
├── config/                     # 配置文件
├── data/                       # 数据存储目录
├── examples/                   # 使用示例
├── tools/                      # 辅助工具
├── requirements.txt            # 依赖列表
├── setup.py                   # 安装配置
└── README.md                  # 项目说明
```

## 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

感谢所有为这个项目做出贡献的开发者和用户！

---

**RepoDP** - 让代码仓库数据处理变得简单高效！ 🚀
