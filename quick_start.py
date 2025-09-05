#!/usr/bin/env python3
"""
RopeDP 快速启动脚本
"""

import os
import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def main():
    """主函数"""
    print("🚀 RopeDP - 代码仓数据处理工具")
    print("=" * 50)
    
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("❌ 需要Python 3.8或更高版本")
        sys.exit(1)
    
    print(f"✅ Python版本: {sys.version}")
    
    # 检查依赖
    try:
        import click
        import git
        import pandas
        import numpy
        import tqdm
        import yaml
        print("✅ 所有依赖已安装")
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        sys.exit(1)
    
    # 创建必要目录
    directories = ['data', 'data/repos', 'data/reports', 'data/backups', 'data/extracted', 'data/logs']
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ 目录结构已创建")
    
    # 显示使用说明
    print("\n📖 使用说明:")
    print("1. 添加代码仓库:")
    print("   python -m ropedp add-repo <仓库URL> <仓库名称>")
    print()
    print("2. 提取文件内容:")
    print("   python -m ropedp extract <仓库名称>")
    print()
    print("3. 清洗文件:")
    print("   python -m ropedp clean <仓库名称>")
    print()
    print("4. 去重分析:")
    print("   python -m ropedp deduplicate <仓库名称>")
    print()
    print("5. 数据分析:")
    print("   python -m ropedp analyze <仓库名称>")
    print()
    print("6. 查看帮助:")
    print("   python -m ropedp --help")
    print()
    print("🎉 RopeDP 已准备就绪！")

if __name__ == '__main__':
    main()

