#!/usr/bin/env python3
"""
RopeDP 使用示例
"""

import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from ropedp.core import RepositoryManager, ConfigManager
from ropedp.extractors import FileExtractor, CodeExtractor, TextExtractor
from ropedp.cleaners import FileCleaner, ContentCleaner, Deduplicator
from ropedp.analyzers import CodeAnalyzer, MetricsCalculator, ReportGenerator
from ropedp.utils import JSONLUtils


def main():
    """主函数"""
    print("🚀 RopeDP 使用示例")
    print("=" * 50)
    
    # 初始化配置管理器
    config_manager = ConfigManager()
    print("✅ 配置管理器初始化完成")
    
    # 初始化仓库管理器
    repo_manager = RepositoryManager()
    print("✅ 仓库管理器初始化完成")
    
    # 示例：添加仓库
    print("\n📁 添加示例仓库...")
    repo_url = "https://github.com/octocat/Hello-World.git"
    repo_name = "hello-world"
    
    if repo_manager.add_repository(repo_name, repo_url):
        print(f"✅ 成功添加仓库: {repo_name}")
    else:
        print(f"❌ 添加仓库失败: {repo_name}")
        return
    
            # 示例：提取文件
        print("\n🔍 提取文件内容...")
        repo_path = repo_manager.get_repository_path(repo_name)
        if repo_path and repo_path.exists():
            file_extractor = FileExtractor(config_manager.config)
            code_extractor = CodeExtractor(config_manager.config)
            text_extractor = TextExtractor(config_manager.config)
            
            # 设置输出文件
            output_dir = Path('data/extracted') / repo_name
            output_dir.mkdir(parents=True, exist_ok=True)
            jsonl_file = output_dir / 'extracted_files.jsonl'
            
            extracted_files = []
            for file_info in file_extractor.extract_files(repo_path, jsonl_file):
                # 提取代码结构
                if not file_info.get('is_binary', False):
                    code_structure = code_extractor.extract_code_structure(file_info)
                    file_info['code_structure'] = code_structure
                    
                    # 提取文本特征
                    text_features = text_extractor.extract_text_features(file_info)
                    file_info['text_features'] = text_features
                
                extracted_files.append(file_info)
            
            print(f"✅ 提取完成，共 {len(extracted_files)} 个文件")
            print(f"📄 JSONL文件已保存到: {jsonl_file}")
            
            # 示例：读取JSONL文件
            print("\n📖 读取JSONL文件...")
            loaded_files = JSONLUtils.read_jsonl_all(jsonl_file)
            print(f"✅ 从JSONL文件加载了 {len(loaded_files)} 个文件")
            
            # 示例：验证JSONL文件
            if JSONLUtils.validate_jsonl(jsonl_file):
                print("✅ JSONL文件格式验证通过")
            else:
                print("❌ JSONL文件格式验证失败")
        
        # 示例：清洗文件
        print("\n🧹 清洗文件...")
        file_cleaner = FileCleaner(config_manager.config)
        content_cleaner = ContentCleaner(config_manager.config)
        
        cleaned_files = []
        for file_info in extracted_files:
            if not file_info.get('is_binary', False):
                cleaned_file = content_cleaner.clean_content(file_info)
                cleaned_files.append(cleaned_file)
            else:
                cleaned_files.append(file_info)
        
        print(f"✅ 清洗完成，共 {len(cleaned_files)} 个文件")
        
        # 示例：去重分析
        print("\n🔍 去重分析...")
        deduplicator = Deduplicator(config_manager.config)
        duplicate_report = deduplicator.find_duplicates(cleaned_files)
        
        print(f"✅ 去重分析完成:")
        print(f"  • 检查文件: {duplicate_report['total_files_checked']}")
        print(f"  • 重复组: {duplicate_report['duplicate_groups']}")
        print(f"  • 相似组: {duplicate_report['similar_groups']}")
        print(f"  • 可节省空间: {duplicate_report['total_duplicate_size'] / 1024:.1f} KB")
        
        # 示例：代码分析
        print("\n📊 代码分析...")
        code_analyzer = CodeAnalyzer(config_manager.config)
        analysis_data = code_analyzer.analyze_repository(cleaned_files)
        
        print(f"✅ 代码分析完成:")
        print(f"  • 总文件数: {analysis_data['overall']['total_files']}")
        print(f"  • 总行数: {analysis_data['overall']['total_lines']}")
        print(f"  • 总问题数: {analysis_data['overall']['total_issues']}")
        print(f"  • 总复杂度: {analysis_data['overall']['total_complexity']}")
        
        # 示例：计算指标
        print("\n📈 计算指标...")
        metrics_calculator = MetricsCalculator(config_manager.config)
        metrics_data = metrics_calculator.calculate_metrics(cleaned_files)
        
        print(f"✅ 指标计算完成:")
        print(f"  • 平均质量分数: {metrics_data['quality']['avg_quality_score']:.1f}")
        print(f"  • 平均复杂度: {metrics_data['complexity']['avg_complexity']:.1f}")
        print(f"  • 平均维护性分数: {metrics_data['maintainability']['avg_maintainability_score']:.1f}")
        print(f"  • 平均可读性分数: {metrics_data['readability']['avg_readability_score']:.1f}")
        
        # 示例：生成报告
        print("\n📄 生成报告...")
        report_generator = ReportGenerator(config_manager.config)
        
        # 合并分析数据
        analysis_data.update(metrics_data)
        
        # 生成报告
        reports = report_generator.generate_report(analysis_data, 'comprehensive')
        
        print(f"✅ 报告生成完成:")
        for format_name, report_path in reports.items():
            if report_path:
                print(f"  • {format_name.upper()} 报告: {report_path}")
        
        # 清理示例仓库
        print("\n🧹 清理示例仓库...")
        if repo_manager.remove_repository(repo_name):
            print(f"✅ 成功删除仓库: {repo_name}")
        else:
            print(f"❌ 删除仓库失败: {repo_name}")
    
    else:
        print(f"❌ 仓库路径不存在: {repo_path}")
    
    print("\n🎉 示例运行完成！")


if __name__ == '__main__':
    main()

