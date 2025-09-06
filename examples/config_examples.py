#!/usr/bin/env python3
"""
RopeDP 配置使用示例

本文件展示了如何使用 RopeDP 的配置系统，包括：
1. 基本配置管理
2. 环境变量使用
3. 配置验证
4. 动态配置更新
5. 配置模板生成
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from repodp.core.config_manager import ConfigManager, ConfigValidationError


def example_basic_config():
    """基本配置管理示例"""
    print("=" * 60)
    print("1. 基本配置管理示例")
    print("=" * 60)
    
    # 创建配置管理器
    config = ConfigManager()
    
    # 获取配置值
    print(f"支持的文件类型: {config.get('extraction.file_types')}")
    print(f"最大文件大小: {config.get('extraction.max_file_size')} 字节")
    print(f"日志级别: {config.get('logging.level')}")
    print(f"最大并发数: {config.get('performance.max_workers')}")
    
    # 设置配置值
    config.set('extraction.max_file_size', 20 * 1024 * 1024)  # 20MB
    print(f"\n更新后的最大文件大小: {config.get('extraction.max_file_size')} 字节")
    
    # 批量更新配置
    updates = {
        'performance.max_workers': 8,
        'logging.level': 'DEBUG',
        'analysis.complexity_analysis': True
    }
    config.update(updates)
    print(f"\n批量更新后的配置:")
    for key, value in updates.items():
        print(f"  {key}: {config.get(key)}")


def example_environment_variables():
    """环境变量使用示例"""
    print("\n" + "=" * 60)
    print("2. 环境变量使用示例")
    print("=" * 60)
    
    # 设置环境变量
    os.environ['ROPEDP_LOG_LEVEL'] = 'DEBUG'
    os.environ['ROPEDP_MAX_WORKERS'] = '16'
    os.environ['ROPEDP_MEMORY_LIMIT'] = '8192'
    
    # 创建新的配置管理器（会读取环境变量）
    config = ConfigManager()
    
    print("环境变量覆盖的配置:")
    print(f"  日志级别: {config.get('logging.level')}")
    print(f"  最大并发数: {config.get('performance.max_workers')}")
    print(f"  内存限制: {config.get('performance.memory_limit')} MB")
    
    # 清理环境变量
    for key in ['ROPEDP_LOG_LEVEL', 'ROPEDP_MAX_WORKERS', 'ROPEDP_MEMORY_LIMIT']:
        if key in os.environ:
            del os.environ[key]


def example_config_validation():
    """配置验证示例"""
    print("\n" + "=" * 60)
    print("3. 配置验证示例")
    print("=" * 60)
    
    config = ConfigManager()
    
    # 正确的配置值
    try:
        config.set('extraction.max_file_size', 10485760)
        config.set('deduplication.similarity_threshold', 0.95)
        config.set('logging.level', 'INFO')
        print("✅ 正确配置值验证通过")
    except ConfigValidationError as e:
        print(f"❌ 配置验证失败: {e}")
    
    # 错误的配置值
    try:
        config.set('extraction.max_file_size', -1)  # 负数
        print("❌ 应该抛出验证错误")
    except ConfigValidationError as e:
        print(f"✅ 正确捕获验证错误: {e}")
    
    try:
        config.set('deduplication.similarity_threshold', 1.5)  # 超出范围
        print("❌ 应该抛出验证错误")
    except ConfigValidationError as e:
        print(f"✅ 正确捕获验证错误: {e}")
    
    try:
        config.set('logging.level', 'INVALID')  # 无效枚举值
        print("❌ 应该抛出验证错误")
    except ConfigValidationError as e:
        print(f"✅ 正确捕获验证错误: {e}")


def example_config_info():
    """配置信息查询示例"""
    print("\n" + "=" * 60)
    print("4. 配置信息查询示例")
    print("=" * 60)
    
    config = ConfigManager()
    
    # 获取特定配置节的信息
    extraction_schema = config.get_schema('extraction')
    print("文件提取配置模式:")
    for schema in extraction_schema:
        print(f"  {schema.key}:")
        print(f"    类型: {schema.type.__name__}")
        print(f"    必需: {schema.required}")
        print(f"    默认值: {schema.default}")
        print(f"    描述: {schema.description}")
        if schema.env_var:
            print(f"    环境变量: {schema.env_var}")
        print()
    
    # 获取完整配置信息
    config_info = config.get_config_info()
    print("当前配置摘要:")
    for section, settings in config_info.items():
        print(f"\n{section.upper()}:")
        for key, info in settings.items():
            print(f"  {key}: {info['current_value']} ({info['type']})")


def example_config_template():
    """配置模板生成示例"""
    print("\n" + "=" * 60)
    print("5. 配置模板生成示例")
    print("=" * 60)
    
    config = ConfigManager()
    
    # 生成带注释的配置模板
    template_with_comments = config.generate_config_template(include_comments=True)
    print("带注释的配置模板（前500字符）:")
    print(template_with_comments[:500] + "...")
    
    # 生成不带注释的配置模板
    template_without_comments = config.generate_config_template(include_comments=False)
    print(f"\n不带注释的配置模板长度: {len(template_without_comments)} 字符")
    
    # 保存模板到文件
    template_file = Path("config_template.yaml")
    with open(template_file, 'w', encoding='utf-8') as f:
        f.write(template_with_comments)
    print(f"✅ 配置模板已保存到: {template_file}")


def example_config_file_validation():
    """配置文件验证示例"""
    print("\n" + "=" * 60)
    print("6. 配置文件验证示例")
    print("=" * 60)
    
    config = ConfigManager()
    
    # 创建测试配置文件
    test_config_file = Path("test_config.yaml")
    
    # 正确的配置文件
    correct_config = """
extraction:
  file_types: [".py", ".js", ".ts"]
  max_file_size: 10485760
  exclude_dirs: [".git", "__pycache__"]

performance:
  max_workers: 4
  memory_limit: 1024

logging:
  level: "INFO"
"""
    
    with open(test_config_file, 'w', encoding='utf-8') as f:
        f.write(correct_config)
    
    # 验证正确的配置文件
    errors = config.validate_config_file(str(test_config_file))
    if not errors:
        print("✅ 正确的配置文件验证通过")
    else:
        print("❌ 配置文件验证失败:")
        for error in errors:
            print(f"  • {error}")
    
    # 错误的配置文件
    incorrect_config = """
extraction:
  file_types: "invalid"  # 应该是列表
  max_file_size: -1      # 应该是正数
  exclude_dirs: 123      # 应该是列表

performance:
  max_workers: "invalid" # 应该是整数
  memory_limit: -100     # 应该是正数

logging:
  level: "INVALID"       # 无效的日志级别
"""
    
    with open(test_config_file, 'w', encoding='utf-8') as f:
        f.write(incorrect_config)
    
    # 验证错误的配置文件
    errors = config.validate_config_file(str(test_config_file))
    if errors:
        print("\n❌ 错误的配置文件验证失败:")
        for error in errors:
            print(f"  • {error}")
    
    # 清理测试文件
    if test_config_file.exists():
        test_config_file.unlink()


def example_custom_configuration():
    """自定义配置示例"""
    print("\n" + "=" * 60)
    print("7. 自定义配置示例")
    print("=" * 60)
    
    # 创建自定义配置
    custom_config = {
        'extraction': {
            'file_types': ['.py', '.js', '.ts', '.java'],
            'exclude_dirs': ['.git', '__pycache__', 'node_modules'],
            'max_file_size': 50 * 1024 * 1024  # 50MB
        },
        'performance': {
            'max_workers': 16,
            'memory_limit': 8192,
            'timeout': 600
        },
        'logging': {
            'level': 'DEBUG',
            'file': 'custom.log'
        }
    }
    
    # 创建配置管理器并导入自定义配置
    config = ConfigManager()
    config.import_config_from_dict(custom_config)
    
    print("自定义配置:")
    print(f"  文件类型: {config.get('extraction.file_types')}")
    print(f"  最大文件大小: {config.get('extraction.max_file_size')} 字节")
    print(f"  最大并发数: {config.get('performance.max_workers')}")
    print(f"  内存限制: {config.get('performance.memory_limit')} MB")
    print(f"  日志级别: {config.get('logging.level')}")


def example_advanced_usage():
    """高级用法示例"""
    print("\n" + "=" * 60)
    print("8. 高级用法示例")
    print("=" * 60)
    
    config = ConfigManager()
    
    # 动态配置更新
    print("动态配置更新:")
    original_workers = config.get('performance.max_workers')
    config.set('performance.max_workers', original_workers * 2)
    print(f"  原始并发数: {original_workers}")
    print(f"  更新后并发数: {config.get('performance.max_workers')}")
    
    # 配置导出和导入
    print("\n配置导出和导入:")
    export_file = Path("exported_config.yaml")
    config.export_config(str(export_file))
    print(f"✅ 配置已导出到: {export_file}")
    
    # 重置为默认配置
    config.reset_to_default()
    print("✅ 配置已重置为默认值")
    
    # 清理导出文件
    if export_file.exists():
        export_file.unlink()


def main():
    """主函数"""
    print("RopeDP 配置系统使用示例")
    print("=" * 60)
    
    try:
        example_basic_config()
        example_environment_variables()
        example_config_validation()
        example_config_info()
        example_config_template()
        example_config_file_validation()
        example_custom_configuration()
        example_advanced_usage()
        
        print("\n" + "=" * 60)
        print("✅ 所有示例执行完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 示例执行失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
