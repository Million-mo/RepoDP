# RopeDP 快速开始指南

## 🚀 立即开始

### 1. 环境准备
```bash
# 安装依赖
pip install -r requirements.txt

# 运行快速检查
python quick_start.py
```

### 2. 基本使用流程

#### 步骤1: 添加代码仓库
```bash
# 添加一个GitHub仓库
./repodp add-repo https://github.com/octocat/Hello-World.git hello-world

# 查看已添加的仓库
./repodp list-repos
```

#### 步骤2: 提取文件内容 (JSONL格式)
```bash
# 提取文件内容 (默认JSONL格式)
./repodp extract hello-world

# 或者指定JSON格式
./repodp extract hello-world --format json
```

#### 步骤3: 清洗文件
```bash
# 清洗文件结构和内容
./repodp clean hello-world
```

#### 步骤4: 去重分析
```bash
# 分析重复文件
./repodp deduplicate hello-world
```

#### 步骤5: 数据分析
```bash
# 生成分析报告
./repodp analyze hello-world

# 指定报告格式
./repodp analyze hello-world --format html
```

### 3. 输出文件说明

#### JSONL格式 (推荐)
- **文件位置**: `data/extracted/<仓库名称>/extracted_files.jsonl`
- **格式**: 每行一个JSON对象
- **优势**: 流式处理，内存占用低，支持大文件

#### JSON格式
- **文件位置**: `data/extracted/<仓库名称>/extracted_files.json`
- **格式**: 标准JSON数组
- **优势**: 易于阅读和调试

#### 分析报告
- **位置**: `data/reports/<仓库名称>/`
- **格式**: JSON, CSV, HTML, Markdown
- **内容**: 代码质量、复杂度、维护性等指标

### 4. 配置管理

#### 查看配置
```bash
./repodp list-config
```

#### 设置配置
```bash
# 设置最大文件大小
./repodp set-config extraction.max_file_size 20971520  # 20MB

# 设置排除的目录
./repodp set-config extraction.exclude_dirs '["node_modules", ".git"]'
```

#### 导出/导入配置
```bash
# 导出配置
./repodp export-config my_config.yaml

# 导入配置
./repodp import-config my_config.yaml
```

### 5. 高级功能

#### 批量处理多个仓库
```bash
# 添加多个仓库
./repodp add-repos https://github.com/user/repo1.git https://github.com/user/repo2.git

# 或者添加本地仓库
./repodp add-repos /path/to/local/repo1 /path/to/local/repo2

# 批量处理所有已添加的仓库
./repodp pipeline batch --all

# 只处理远程仓库
./repodp pipeline batch --all --filter remote

# 只处理本地引用仓库
./repodp pipeline batch --all --filter local_reference

# 处理指定的多个仓库
./repodp pipeline batch repo1 repo2 repo3

# 预览处理计划（不实际执行）
./repodp pipeline batch --all --dry-run

# 批量分析
./repodp analyze repo1
./repodp analyze repo2
```

#### 自定义输出目录
```bash
# 指定输出目录
./repodp extract hello-world --output /path/to/output

# 指定报告输出目录
./repodp analyze hello-world --output /path/to/reports
```

### 6. 示例和测试

#### 运行示例
```bash
# 基本使用示例
python examples/example_usage.py

# JSONL工具示例
python examples/jsonl_example.py
```

#### 运行测试
```bash
# 运行所有测试
make test

# 运行基本测试
python tests/test_basic.py
```

### 7. 故障排除

#### 常见问题

**问题1**: `No module named repodp`
```bash
# 解决方案: 使用启动脚本
./repodp --help

# 或者设置PYTHONPATH
export PYTHONPATH=/path/to/RopeDP/src:$PYTHONPATH
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
./repodp extract <repo-name> --format jsonl

# 调整配置
./repodp set-config extraction.max_file_size 5242880  # 5MB
```

### 8. 性能优化

#### 大仓库处理
```bash
# 增加排除目录
./repodp set-config extraction.exclude_dirs '["node_modules", ".git", "build", "dist", "target"]'

# 限制文件大小
./repodp set-config extraction.max_file_size 10485760  # 10MB

# 限制文件类型
./repodp set-config extraction.file_types '[".py", ".js", ".ts", ".java"]'
```

#### 内存优化
- 使用JSONL格式 (默认)
- 分批处理大仓库
- 调整批处理大小

### 9. 输出数据使用

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

### 10. 下一步

1. **探索配置**: 根据项目需求调整配置参数
2. **批量处理**: 处理多个代码仓库
3. **自定义分析**: 基于提取的数据进行自定义分析
4. **集成工具**: 将RopeDP集成到CI/CD流程中

## 🎉 开始使用

现在您已经了解了RopeDP的基本使用方法，可以开始处理您的代码仓库了！

```bash
# 快速开始
./repodp add-repo <your-repo-url> <repo-name>
./repodp extract <repo-name>
./repodp analyze <repo-name>
```

祝您使用愉快！🚀
