#!/usr/bin/env python3
"""
JSONL工具使用示例
"""

import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from repodp.utils import JSONLUtils


def main():
    """主函数"""
    print("📄 JSONL工具使用示例")
    print("=" * 50)
    
    # 创建示例数据
    sample_data = [
        {
            "path": "src/main.py",
            "content": "print('Hello, World!')",
            "language": "python",
            "lines": 1,
            "size": 25
        },
        {
            "path": "src/utils.py", 
            "content": "def helper():\n    return 'helper'",
            "language": "python",
            "lines": 2,
            "size": 35
        },
        {
            "path": "README.md",
            "content": "# My Project\nThis is a sample project.",
            "language": "markdown",
            "lines": 2,
            "size": 40
        }
    ]
    
    # 示例1: 写入JSONL文件
    print("\n1. 写入JSONL文件...")
    jsonl_file = Path("sample_data.jsonl")
    if JSONLUtils.write_jsonl(sample_data, jsonl_file):
        print(f"✅ 成功写入JSONL文件: {jsonl_file}")
    else:
        print("❌ 写入JSONL文件失败")
        return
    
    # 示例2: 读取JSONL文件
    print("\n2. 读取JSONL文件...")
    loaded_data = JSONLUtils.read_jsonl_all(jsonl_file)
    print(f"✅ 成功读取 {len(loaded_data)} 条记录")
    
    # 示例3: 逐行读取JSONL文件
    print("\n3. 逐行读取JSONL文件...")
    for i, record in enumerate(JSONLUtils.read_jsonl(jsonl_file), 1):
        print(f"  记录 {i}: {record['path']} ({record['language']})")
    
    # 示例4: 验证JSONL文件
    print("\n4. 验证JSONL文件...")
    if JSONLUtils.validate_jsonl(jsonl_file):
        print("✅ JSONL文件格式正确")
    else:
        print("❌ JSONL文件格式错误")
    
    # 示例5: 计算行数
    print("\n5. 计算JSONL文件行数...")
    line_count = JSONLUtils.count_lines(jsonl_file)
    print(f"✅ JSONL文件共有 {line_count} 行")
    
    # 示例6: 追加数据
    print("\n6. 追加数据到JSONL文件...")
    new_record = {
        "path": "src/config.py",
        "content": "DEBUG = True",
        "language": "python",
        "lines": 1,
        "size": 15
    }
    if JSONLUtils.append_jsonl(new_record, jsonl_file):
        print("✅ 成功追加数据")
    
    # 示例7: 转换为JSON格式
    print("\n7. 转换为JSON格式...")
    json_file = Path("sample_data.json")
    if JSONLUtils.convert_jsonl_to_json(jsonl_file, json_file):
        print(f"✅ 成功转换为JSON文件: {json_file}")
    
    # 示例8: 从JSON转换回JSONL
    print("\n8. 从JSON转换回JSONL...")
    jsonl_file2 = Path("sample_data2.jsonl")
    if JSONLUtils.convert_json_to_jsonl(json_file, jsonl_file2):
        print(f"✅ 成功转换为JSONL文件: {jsonl_file2}")
    
    # 清理示例文件
    print("\n9. 清理示例文件...")
    for file_path in [jsonl_file, json_file, jsonl_file2]:
        if file_path.exists():
            file_path.unlink()
            print(f"✅ 已删除: {file_path}")
    
    print("\n🎉 JSONL工具示例完成！")


if __name__ == '__main__':
    main()
