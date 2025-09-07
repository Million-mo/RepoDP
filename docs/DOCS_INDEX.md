# RepoDP 文档索引

欢迎使用 RepoDP！这里是所有文档的索引，帮助您快速找到所需的信息。

## 📚 主要文档

### 🚀 快速开始
- **[README.md](../README.md)** - 项目概览和快速开始指南

### 📖 使用指南
- **[USER_GUIDE.md](USER_GUIDE.md)** - 完整的用户使用指南
- **[API_REFERENCE.md](API_REFERENCE.md)** - CLI命令详细参考

### 🔧 高级功能
- **[PIPELINE_GUIDE.md](PIPELINE_GUIDE.md)** - Pipeline工作流使用指南

## 🎯 按使用场景查找文档

### 新手用户
1. 阅读 [README.md](../README.md) 了解项目概览
2. 按照 [USER_GUIDE.md#快速开始](USER_GUIDE.md#快速开始) 进行快速上手
3. 参考 [USER_GUIDE.md](USER_GUIDE.md) 学习详细使用方法

### 日常使用
- **仓库管理**: [API_REFERENCE.md#仓库管理命令-repo](API_REFERENCE.md#仓库管理命令-repo)
- **数据处理**: [API_REFERENCE.md#数据处理命令-data](API_REFERENCE.md#数据处理命令-data)
- **配置管理**: [API_REFERENCE.md#配置管理命令-config](API_REFERENCE.md#配置管理命令-config)

### 高级用户
- **Pipeline工作流**: [PIPELINE_GUIDE.md](PIPELINE_GUIDE.md)
- **批量处理**: [USER_GUIDE.md#批量处理](USER_GUIDE.md#批量处理)
- **自定义配置**: [USER_GUIDE.md#配置管理](USER_GUIDE.md#配置管理)

### 开发者
- **项目结构**: [README.md#项目结构](../README.md#项目结构)
- **技术特性**: [README.md#核心特性](../README.md#核心特性)
- **API参考**: [API_REFERENCE.md](API_REFERENCE.md)

## 📝 文档结构说明

### README.md
- 项目简介和核心特性
- 快速安装和基本使用
- 支持的文件类型
- 项目结构概览

### USER_GUIDE.md
- 快速开始指南
- 详细的使用说明
- 配置选项说明
- 故障排除指南
- 最佳实践建议

### API_REFERENCE.md
- 按功能分组的命令说明
- 详细的参数说明
- 使用示例
- 命令组合建议

### PIPELINE_GUIDE.md
- Pipeline概念和设计
- 预设Pipeline说明
- 自定义Pipeline配置
- 批量处理流程

## 🔍 快速查找

### 按功能查找
- **安装配置**: [README.md#安装](../README.md#安装) | [USER_GUIDE.md#环境准备](USER_GUIDE.md#环境准备)
- **仓库管理**: [USER_GUIDE.md#仓库管理命令-repo](USER_GUIDE.md#仓库管理命令-repo) | [API_REFERENCE.md#仓库管理命令-repo](API_REFERENCE.md#仓库管理命令-repo)
- **文件提取**: [USER_GUIDE.md#数据处理命令-data](USER_GUIDE.md#数据处理命令-data) | [API_REFERENCE.md#数据处理命令-data](API_REFERENCE.md#数据处理命令-data)
- **数据清洗**: [USER_GUIDE.md#高级功能](USER_GUIDE.md#高级功能) | [API_REFERENCE.md#数据处理命令-data](API_REFERENCE.md#数据处理命令-data)
- **去重分析**: [USER_GUIDE.md#数据处理命令-data](USER_GUIDE.md#数据处理命令-data) | [API_REFERENCE.md#数据处理命令-data](API_REFERENCE.md#数据处理命令-data)
- **数据分析**: [USER_GUIDE.md#数据处理命令-data](USER_GUIDE.md#数据处理命令-data) | [API_REFERENCE.md#数据处理命令-data](API_REFERENCE.md#数据处理命令-data)
- **Pipeline**: [PIPELINE_GUIDE.md](PIPELINE_GUIDE.md) | [USER_GUIDE.md#Pipeline工作流](USER_GUIDE.md#pipeline工作流)

### 按问题类型查找
- **安装问题**: [USER_GUIDE.md#环境准备](USER_GUIDE.md#环境准备)
- **使用问题**: [USER_GUIDE.md#故障排除](USER_GUIDE.md#故障排除)
- **配置问题**: [USER_GUIDE.md#配置管理](USER_GUIDE.md#配置管理)
- **性能问题**: [USER_GUIDE.md#最佳实践](USER_GUIDE.md#最佳实践)

## 📞 获取帮助

如果您在文档中找不到所需信息，可以：

1. 查看命令行帮助：`python -m src.repodp --help`
2. 查看特定命令帮助：`python -m src.repodp <command> --help`
3. 提交 Issue 到 GitHub 仓库
4. 查看项目示例：`examples/` 目录

## 🔄 文档更新

本文档会随着项目功能的发展持续更新。如果您发现文档有误或需要补充，欢迎提交 Pull Request！

---

**提示**: 建议新用户按照 README.md → USER_GUIDE.md → API_REFERENCE.md 的顺序阅读文档。
