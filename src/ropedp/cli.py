"""
命令行界面
"""

import click
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any

from .core import RepositoryManager, ConfigManager
from .extractors import FileExtractor, CodeExtractor, TextExtractor
from .cleaners import FileCleaner, ContentCleaner, Deduplicator
from .analyzers import CodeAnalyzer, MetricsCalculator, ReportGenerator

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_extracted_files(name: str) -> List[Dict[str, Any]]:
    """加载提取的文件数据"""
    extracted_file_json = Path('data/extracted') / name / 'extracted_files.json'
    extracted_file_jsonl = Path('data/extracted') / name / 'extracted_files.jsonl'
    
    file_list = []
    if extracted_file_jsonl.exists():
        # 读取JSONL文件
        import json
        with open(extracted_file_jsonl, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    file_list.append(json.loads(line.strip()))
        click.echo(f"📄 从JSONL文件加载: {extracted_file_jsonl}")
    elif extracted_file_json.exists():
        # 读取JSON文件
        import json
        with open(extracted_file_json, 'r', encoding='utf-8') as f:
            file_list = json.load(f)
        click.echo(f"📄 从JSON文件加载: {extracted_file_json}")
    else:
        click.echo(f"❌ 提取文件不存在: {extracted_file_jsonl} 或 {extracted_file_json}")
        click.echo("请先运行 'ropedp extract' 命令")
        raise click.Abort()
    
    return file_list


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='启用详细输出')
@click.option('--config', '-c', type=click.Path(), help='配置文件路径')
@click.pass_context
def main(ctx, verbose, config):
    """RopeDP - 代码仓数据处理工具"""
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # 初始化配置管理器
    config_manager = ConfigManager()
    if config:
        config_manager.import_config(config)
    
    ctx.ensure_object(dict)
    ctx.obj['config_manager'] = config_manager
    ctx.obj['repo_manager'] = RepositoryManager()


@main.command()
@click.argument('url')
@click.argument('name')
@click.option('--branch', '-b', default='main', help='分支名称')
@click.pass_context
def add_repo(ctx, url, name, branch):
    """添加新的代码仓库"""
    repo_manager = ctx.obj['repo_manager']
    
    if repo_manager.add_repository(name, url, branch):
        click.echo(f"✅ 成功添加仓库: {name}")
    else:
        click.echo(f"❌ 添加仓库失败: {name}")
        raise click.Abort()


@main.command()
@click.argument('name')
@click.pass_context
def update_repo(ctx, name):
    """更新代码仓库"""
    repo_manager = ctx.obj['repo_manager']
    
    if repo_manager.update_repository(name):
        click.echo(f"✅ 成功更新仓库: {name}")
    else:
        click.echo(f"❌ 更新仓库失败: {name}")
        raise click.Abort()


@main.command()
@click.argument('name')
@click.pass_context
def remove_repo(ctx, name):
    """删除代码仓库"""
    repo_manager = ctx.obj['repo_manager']
    
    if click.confirm(f"确定要删除仓库 '{name}' 吗？"):
        if repo_manager.remove_repository(name):
            click.echo(f"✅ 成功删除仓库: {name}")
        else:
            click.echo(f"❌ 删除仓库失败: {name}")
            raise click.Abort()


@main.command()
@click.pass_context
def list_repos(ctx):
    """列出所有仓库"""
    repo_manager = ctx.obj['repo_manager']
    repos = repo_manager.list_repositories()
    
    if not repos:
        click.echo("没有找到任何仓库")
        return
    
    click.echo("📁 代码仓库列表:")
    for repo in repos:
        click.echo(f"  • {repo['url']} (分支: {repo['branch']})")
        click.echo(f"    路径: {repo['path']}")
        click.echo(f"    最后更新: {repo['last_updated']}")
        click.echo()


@main.command()
@click.argument('name')
@click.option('--output', '-o', type=click.Path(), help='输出目录')
@click.option('--format', 'output_format', type=click.Choice(['json', 'jsonl']), default='jsonl', help='输出格式')
@click.pass_context
def extract(ctx, name, output, output_format):
    """提取文件内容"""
    repo_manager = ctx.obj['repo_manager']
    config_manager = ctx.obj['config_manager']
    
    # 检查仓库是否存在
    repo_info = repo_manager.get_repository(name)
    if not repo_info:
        click.echo(f"❌ 仓库不存在: {name}")
        raise click.Abort()
    
    repo_path = Path(repo_info['path'])
    if not repo_path.exists():
        click.echo(f"❌ 仓库路径不存在: {repo_path}")
        raise click.Abort()
    
    # 设置输出目录
    if not output:
        output = Path('data/extracted') / name
    else:
        output = Path(output)
    
    output.mkdir(parents=True, exist_ok=True)
    
    # 提取文件
    click.echo(f"🔍 开始提取文件: {name}")
    
    file_extractor = FileExtractor(config_manager.config)
    code_extractor = CodeExtractor(config_manager.config)
    text_extractor = TextExtractor(config_manager.config)
    
    # 设置输出文件
    if output_format == 'jsonl':
        output_file = output / 'extracted_files.jsonl'
        # 使用JSONL格式直接写入
        extracted_files = []
        for file_info in file_extractor.extract_files(repo_path, output_file):
            # 提取代码结构
            if not file_info.get('is_binary', False):
                code_structure = code_extractor.extract_code_structure(file_info)
                file_info['code_structure'] = code_structure
                
                # 提取文本特征
                text_features = text_extractor.extract_text_features(file_info)
                file_info['text_features'] = text_features
            
            extracted_files.append(file_info)
        
        click.echo(f"✅ 提取完成，共 {len(extracted_files)} 个文件")
        click.echo(f"📄 JSONL结果保存到: {output_file}")
        
    else:  # JSON格式
        extracted_files = []
        for file_info in file_extractor.extract_files(repo_path):
            # 提取代码结构
            if not file_info.get('is_binary', False):
                code_structure = code_extractor.extract_code_structure(file_info)
                file_info['code_structure'] = code_structure
                
                # 提取文本特征
                text_features = text_extractor.extract_text_features(file_info)
                file_info['text_features'] = text_features
            
            extracted_files.append(file_info)
        
        # 保存提取结果
        import json
        output_file = output / 'extracted_files.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(extracted_files, f, indent=2, ensure_ascii=False, default=str)
        
        click.echo(f"✅ 提取完成，共 {len(extracted_files)} 个文件")
        click.echo(f"📄 JSON结果保存到: {output_file}")


@main.command()
@click.argument('name')
@click.option('--backup', is_flag=True, help='创建备份')
@click.pass_context
def clean(ctx, name, backup):
    """清洗文件"""
    repo_manager = ctx.obj['repo_manager']
    config_manager = ctx.obj['config_manager']
    
    # 检查仓库是否存在
    repo_info = repo_manager.get_repository(name)
    if not repo_info:
        click.echo(f"❌ 仓库不存在: {name}")
        raise click.Abort()
    
    repo_path = Path(repo_info['path'])
    if not repo_path.exists():
        click.echo(f"❌ 仓库路径不存在: {repo_path}")
        raise click.Abort()
    
    # 更新配置
    config = config_manager.config.copy()
    config['backup_enabled'] = backup
    
    # 清洗文件
    click.echo(f"🧹 开始清洗文件: {name}")
    
    file_cleaner = FileCleaner(config)
    results = file_cleaner.clean_repository(repo_path, name)
    
    click.echo(f"✅ 清洗完成:")
    click.echo(f"  • 清洗文件: {results['cleaned_files']}")
    click.echo(f"  • 删除文件: {results['removed_files']}")
    click.echo(f"  • 重命名文件: {results['renamed_files']}")
    if results['errors']:
        click.echo(f"  • 错误: {len(results['errors'])}")
        for error in results['errors']:
            click.echo(f"    - {error}")


@main.command()
@click.argument('name')
@click.option('--strategy', type=click.Choice(['newest', 'oldest', 'first', 'last']), 
              default='newest', help='保留策略')
@click.pass_context
def deduplicate(ctx, name, strategy):
    """去重分析"""
    repo_manager = ctx.obj['repo_manager']
    config_manager = ctx.obj['config_manager']
    
    # 检查仓库是否存在
    repo_info = repo_manager.get_repository(name)
    if not repo_info:
        click.echo(f"❌ 仓库不存在: {name}")
        raise click.Abort()
    
    # 加载提取的文件
    file_list = load_extracted_files(name)
    
    # 去重分析
    click.echo(f"🔍 开始去重分析: {name}")
    
    deduplicator = Deduplicator(config_manager.config)
    duplicate_report = deduplicator.find_duplicates(file_list)
    
    click.echo(f"✅ 去重分析完成:")
    click.echo(f"  • 检查文件: {duplicate_report['total_files_checked']}")
    click.echo(f"  • 重复组: {duplicate_report['duplicate_groups']}")
    click.echo(f"  • 相似组: {duplicate_report['similar_groups']}")
    click.echo(f"  • 可节省空间: {duplicate_report['total_duplicate_size'] / 1024 / 1024:.1f} MB")
    
    # 询问是否删除重复文件
    if duplicate_report['duplicate_groups'] > 0:
        if click.confirm(f"发现 {duplicate_report['duplicate_groups']} 个重复组，是否删除重复文件？"):
            removal_results = deduplicator.remove_duplicates(duplicate_report, strategy)
            click.echo(f"✅ 删除完成:")
            click.echo(f"  • 删除文件: {removal_results['total_removed']}")
            click.echo(f"  • 错误: {removal_results['total_errors']}")


@main.command()
@click.argument('name')
@click.option('--format', 'report_format', type=click.Choice(['json', 'csv', 'html', 'markdown', 'comprehensive']), 
              default='comprehensive', help='报告格式')
@click.option('--output', '-o', type=click.Path(), help='输出目录')
@click.pass_context
def analyze(ctx, name, report_format, output):
    """数据分析"""
    repo_manager = ctx.obj['repo_manager']
    config_manager = ctx.obj['config_manager']
    
    # 检查仓库是否存在
    repo_info = repo_manager.get_repository(name)
    if not repo_info:
        click.echo(f"❌ 仓库不存在: {name}")
        raise click.Abort()
    
    # 加载提取的文件
    file_list = load_extracted_files(name)
    
    # 设置输出目录
    if not output:
        output = Path('data/reports') / name
    else:
        output = Path(output)
    
    output.mkdir(parents=True, exist_ok=True)
    
    # 更新配置
    config = config_manager.config.copy()
    config['output_dir'] = str(output)
    
    # 分析代码
    click.echo(f"📊 开始分析代码: {name}")
    
    code_analyzer = CodeAnalyzer(config)
    analysis_data = code_analyzer.analyze_repository(file_list)
    
    # 计算指标
    metrics_calculator = MetricsCalculator(config)
    metrics_data = metrics_calculator.calculate_metrics(file_list)
    
    # 合并分析数据
    analysis_data.update(metrics_data)
    
    # 生成报告
    report_generator = ReportGenerator(config)
    reports = report_generator.generate_report(analysis_data, report_format)
    
    click.echo(f"✅ 分析完成:")
    for format_name, report_path in reports.items():
        if report_path:
            click.echo(f"  • {format_name.upper()} 报告: {report_path}")


@main.command()
@click.argument('key')
@click.argument('value')
@click.pass_context
def set_config(ctx, key, value):
    """设置配置值"""
    config_manager = ctx.obj['config_manager']
    
    try:
        # 尝试解析值
        if value.lower() in ['true', 'false']:
            value = value.lower() == 'true'
        elif value.isdigit():
            value = int(value)
        elif '.' in value and value.replace('.', '').isdigit():
            value = float(value)
        
        config_manager.set(key, value)
        click.echo(f"✅ 配置已设置: {key} = {value}")
    except Exception as e:
        click.echo(f"❌ 设置配置失败: {e}")
        raise click.Abort()


@main.command()
@click.argument('key')
@click.pass_context
def get_config(ctx, key):
    """获取配置值"""
    config_manager = ctx.obj['config_manager']
    
    value = config_manager.get(key)
    if value is not None:
        click.echo(f"{key} = {value}")
    else:
        click.echo(f"❌ 配置不存在: {key}")


@main.command()
@click.pass_context
def list_config(ctx):
    """列出所有配置"""
    config_manager = ctx.obj['config_manager']
    
    def print_config(config, prefix=""):
        for key, value in config.items():
            if isinstance(value, dict):
                click.echo(f"{prefix}{key}:")
                print_config(value, prefix + "  ")
            else:
                click.echo(f"{prefix}{key}: {value}")
    
    print_config(config_manager.config)


@main.command()
@click.option('--file', '-f', type=click.Path(), help='导出配置文件')
@click.pass_context
def export_config(ctx, file):
    """导出配置"""
    config_manager = ctx.obj['config_manager']
    
    if not file:
        file = 'config.yaml'
    
    config_manager.export_config(file)
    click.echo(f"✅ 配置已导出到: {file}")


@main.command()
@click.argument('file', type=click.Path(exists=True))
@click.pass_context
def import_config(ctx, file):
    """导入配置"""
    config_manager = ctx.obj['config_manager']
    
    config_manager.import_config(file)
    click.echo(f"✅ 配置已从 {file} 导入")


if __name__ == '__main__':
    main()

