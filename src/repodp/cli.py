"""
命令行界面
"""

import click
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any

from .core import RepositoryManager, ConfigManager
from .extractors import FileExtractor, CodeExtractor, TextExtractor
from .cleaners import ContentCleaner, Deduplicator, JSONLContentCleaner
from .analyzers import CodeAnalyzer, MetricsCalculator, ReportGenerator

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def extract_repo_name(url_or_path: str) -> str:
    """从URL或路径提取仓库名称"""
    try:
        # 处理本地路径
        path = Path(url_or_path)
        if path.exists() and path.is_dir():
            # 如果是本地目录，返回目录名
            return path.name
        
        # 处理URL (GitHub, GitLab, Bitbucket等)
        # 移除末尾的.git（如果存在）
        if url_or_path.endswith('.git'):
            url_or_path = url_or_path[:-4]
        
        # 提取最后一部分作为仓库名
        # 处理各种URL格式:
        # https://github.com/user/repo
        # git@github.com:user/repo
        # https://gitlab.com/user/repo.git
        # etc.
        
        # 首先尝试处理URL格式
        if '://' in url_or_path or '@' in url_or_path:
            # 移除协议部分
            if '://' in url_or_path:
                url_or_path = url_or_path.split('://', 1)[1]
            elif '@' in url_or_path:
                url_or_path = url_or_path.split('@', 1)[1]
            
            # 移除域名部分
            if '/' in url_or_path:
                parts = url_or_path.split('/')
                if len(parts) >= 2:
                    # 返回最后一部分（仓库名）
                    return parts[-1]
        
        # 如果不是URL格式，直接返回最后一部分
        if '/' in url_or_path or '\\' in url_or_path:
            return Path(url_or_path).name
        
        # 如果没有路径分隔符，直接返回原字符串
        return url_or_path
        
    except Exception as e:
        logger.warning(f"提取仓库名称失败: {e}, 使用原始字符串")
        return Path(url_or_path).name if '/' in url_or_path or '\\' in url_or_path else url_or_path


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
        click.echo("请先运行 'repodp extract' 命令")
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
@click.argument('url_or_path')
@click.argument('name', required=False)
@click.option('--branch', '-b', default='main', help='分支名称')
@click.option('--local', '-l', is_flag=True, help='指定为本地仓库路径')
@click.option('--reference', '-r', is_flag=True, help='引用模式（仅复制引用，不复制文件）')
@click.pass_context
def add_repo(ctx, url_or_path, name, branch, local, reference):
    """添加新的代码仓库（支持远程URL或本地路径）"""
    repo_manager = ctx.obj['repo_manager']
    
    # 如果没有提供名称，自动提取
    if not name:
        name = extract_repo_name(url_or_path)
        click.echo(f"🤖 自动提取仓库名称: {name}")
    
    # 检测是否为本地路径
    path = Path(url_or_path)
    if local or (path.exists() and path.is_dir()):
        # 本地仓库
        if reference:
            # 引用模式
            if repo_manager.add_local_repository_reference(name, url_or_path, branch):
                click.echo(f"✅ 成功添加本地仓库引用: {name}")
            else:
                click.echo(f"❌ 添加本地仓库引用失败: {name}")
                raise click.Abort()
        else:
            # 复制模式
            if repo_manager.add_local_repository(name, url_or_path, branch):
                click.echo(f"✅ 成功添加本地仓库: {name}")
            else:
                click.echo(f"❌ 添加本地仓库失败: {name}")
                raise click.Abort()
    else:
        # 远程仓库
        if repo_manager.add_repository(name, url_or_path, branch):
            click.echo(f"✅ 成功添加远程仓库: {name}")
        else:
            click.echo(f"❌ 添加远程仓库失败: {name}")
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
@click.argument('directory', type=click.Path(exists=True))
@click.option('--pattern', '-p', default='*', help='仓库名称匹配模式（支持通配符）')
@click.option('--reference', '-r', is_flag=True, help='引用模式（仅复制引用，不复制文件）')
@click.option('--prefix', help='仓库名称前缀')
@click.option('--suffix', help='仓库名称后缀')
@click.pass_context
def add_dir(ctx, directory, pattern, reference, prefix, suffix):
    """添加目录下的所有代码仓库"""
    repo_manager = ctx.obj['repo_manager']
    
    import glob
    from pathlib import Path
    from git import Repo, InvalidGitRepositoryError
    
    directory_path = Path(directory)
    if not directory_path.is_dir():
        click.echo(f"❌ 指定的路径不是目录: {directory}")
        raise click.Abort()
    
    # 查找所有子目录
    repo_count = 0
    success_count = 0
    error_count = 0
    
    click.echo(f"🔍 扫描目录: {directory}")
    
    # 使用glob模式查找匹配的目录
    search_pattern = directory_path / pattern
    potential_dirs = glob.glob(str(search_pattern))
    
    for dir_path in potential_dirs:
        dir_path = Path(dir_path)
        if not dir_path.is_dir():
            continue
            
        repo_count += 1
        
        try:
            # 检查是否为有效的git仓库
            repo = Repo(dir_path)
            
            # 获取仓库信息
            try:
                current_branch = repo.active_branch.name
            except TypeError:
                # 如果处于detached HEAD状态，使用main作为默认分支
                current_branch = "main"
            
            # 获取远程仓库URL
            if 'origin' in repo.remotes:
                remote_url = repo.remotes.origin.url
                url_info = f" (远程: {remote_url})"
            elif repo.remotes:
                remote_url = repo.remotes[0].url
                url_info = f" (远程: {remote_url})"
            else:
                remote_url = str(dir_path)
                url_info = " (无远程仓库)"
            
            # 生成仓库名称
            repo_name = dir_path.name
            if prefix:
                repo_name = f"{prefix}{repo_name}"
            if suffix:
                repo_name = f"{repo_name}{suffix}"
            
            # 检查仓库是否已存在
            if repo_manager.get_repository(repo_name):
                click.echo(f"⚠️  仓库已存在，跳过: {repo_name}{url_info}")
                continue
            
            # 添加仓库
            if reference:
                success = repo_manager.add_local_repository_reference(
                    repo_name, str(dir_path), current_branch
                )
                if success:
                    click.echo(f"✅ 成功添加仓库引用: {repo_name} ({dir_path}){url_info}")
                    success_count += 1
                else:
                    click.echo(f"❌ 添加仓库引用失败: {repo_name}{url_info}")
                    error_count += 1
            else:
                success = repo_manager.add_local_repository(
                    repo_name, str(dir_path), current_branch
                )
                if success:
                    click.echo(f"✅ 成功添加仓库: {repo_name} ({dir_path}){url_info}")
                    success_count += 1
                else:
                    click.echo(f"❌ 添加仓库失败: {repo_name}{url_info}")
                    error_count += 1
                    
        except InvalidGitRepositoryError:
            click.echo(f"⏭️  跳过非Git仓库: {dir_path}")
            continue
        except Exception as e:
            click.echo(f"❌ 处理仓库失败 {dir_path}: {e}")
            error_count += 1
            continue
    
    click.echo(f"\n📊 添加完成:")
    click.echo(f"  • 扫描目录: {repo_count}")
    click.echo(f"  • 成功添加: {success_count}")
    click.echo(f"  • 失败/跳过: {error_count}")


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
        repo_type = repo.get('type', 'remote')
        if repo_type == 'local_reference':
            type_icon = '🔗'
            type_name = 'local_ref'
        elif repo_type == 'local':
            type_icon = '📁'
            type_name = 'local'
        else:
            type_icon = '🌐'
            type_name = 'remote'
        click.echo(f"  {type_icon} {repo['url']} (分支: {repo['branch']}) [{type_name}]")
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
@click.option('--output', '-o', type=click.Path(), help='输出JSONL文件路径')
@click.option('--in-place', '-i', is_flag=True, help='直接覆盖原JSONL文件')
@click.pass_context
def clean(ctx, name, output, in_place):
    """清洗JSONL文件内容（注释脱敏、敏感信息处理）"""
    repo_manager = ctx.obj['repo_manager']
    config_manager = ctx.obj['config_manager']
    
    # 检查提取的文件是否存在
    extracted_file_jsonl = Path('data/extracted') / name / 'extracted_files.jsonl'
    extracted_file_json = Path('data/extracted') / name / 'extracted_files.json'
    
    input_file = None
    if extracted_file_jsonl.exists():
        input_file = extracted_file_jsonl
        click.echo(f"📄 找到JSONL文件: {extracted_file_jsonl}")
    elif extracted_file_json.exists():
        # 如果是JSON格式，先转换为JSONL处理
        click.echo(f"📄 找到JSON文件，转换为JSONL格式处理: {extracted_file_json}")
        import json
        with open(extracted_file_json, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 创建临时JSONL文件
        input_file = Path('data/extracted') / name / 'temp_extracted_files.jsonl'
        with open(input_file, 'w', encoding='utf-8') as f:
            for item in data:
                f.write(json.dumps(item, ensure_ascii=False, default=str) + '\n')
    else:
        click.echo(f"❌ 未找到提取文件: {extracted_file_jsonl} 或 {extracted_file_json}")
        click.echo("请先运行 'repodp extract' 命令提取文件")
        raise click.Abort()
    
    # 设置输出文件路径
    if in_place:
        # 直接覆盖原文件，先创建备份
        backup_file = input_file.with_suffix('.jsonl.backup')
        import shutil
        shutil.copy2(input_file, backup_file)
        output_file = input_file
        click.echo(f"💾 已创建备份文件: {backup_file}")
    elif output:
        output_file = Path(output)
    else:
        output_file = input_file.parent / f"{input_file.stem}_cleaned{input_file.suffix}"
    
    # 确保输出目录存在
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # 创建内容清洗器并执行清洗
    click.echo(f"🧹 开始清洗JSONL内容: {name}")
    
    content_cleaner = JSONLContentCleaner(config_manager.config)
    results = content_cleaner.clean_jsonl_file(input_file, output_file)
    
    if results['success']:
        stats = results['stats']
        click.echo(f"✅ 内容清洗完成:")
        click.echo(f"  • 处理文件: {stats['total_files']}")
        click.echo(f"  • 清洗文件: {stats['files_cleaned']}")
        click.echo(f"  • 删除注释: {stats['comments_removed']}")
        click.echo(f"  • 脱敏注释: {stats['comments_desensitized']}")
        click.echo(f"  • 敏感信息: {stats['sensitive_info_removed']} (涉及 {stats['files_with_sensitive_info']} 个文件)")
        click.echo(f"  • 输出文件: {output_file}")
        
        # 如果是临时文件，清理掉
        if input_file.name == 'temp_extracted_files.jsonl':
            input_file.unlink()
    else:
        click.echo(f"❌ 内容清洗失败: {results['error']}")
        raise click.Abort()


@main.command()
@click.argument('name')
@click.option('--output', '-o', type=click.Path(), help='输出JSONL文件路径')
@click.option('--in-place', '-i', is_flag=True, help='直接覆盖原JSONL文件')
@click.pass_context
def clean(ctx, name, output, in_place):
    """清洗JSONL文件内容（注释脱敏、敏感信息处理）"""
    repo_manager = ctx.obj['repo_manager']
    config_manager = ctx.obj['config_manager']
    
    # 检查提取的文件是否存在
    extracted_file_jsonl = Path('data/extracted') / name / 'extracted_files.jsonl'
    extracted_file_json = Path('data/extracted') / name / 'extracted_files.json'
    
    input_file = None
    if extracted_file_jsonl.exists():
        input_file = extracted_file_jsonl
        click.echo(f"📄 找到JSONL文件: {extracted_file_jsonl}")
    elif extracted_file_json.exists():
        # 如果是JSON格式，先转换为JSONL处理
        click.echo(f"📄 找到JSON文件，转换为JSONL格式处理: {extracted_file_json}")
        import json
        with open(extracted_file_json, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 创建临时JSONL文件
        input_file = Path('data/extracted') / name / 'temp_extracted_files.jsonl'
        with open(input_file, 'w', encoding='utf-8') as f:
            for item in data:
                f.write(json.dumps(item, ensure_ascii=False, default=str) + '\n')
    else:
        click.echo(f"❌ 未找到提取文件: {extracted_file_jsonl} 或 {extracted_file_json}")
        click.echo("请先运行 'repodp extract' 命令提取文件")
        raise click.Abort()
    
    # 设置输出文件路径
    if in_place:
        # 直接覆盖原文件，先创建备份
        backup_file = input_file.with_suffix('.jsonl.backup')
        import shutil
        shutil.copy2(input_file, backup_file)
        output_file = input_file
        click.echo(f"💾 已创建备份文件: {backup_file}")
    elif output:
        output_file = Path(output)
    else:
        output_file = input_file.parent / f"{input_file.stem}_cleaned{input_file.suffix}"
    
    # 确保输出目录存在
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # 创建内容清洗器并执行清洗
    click.echo(f"🧹 开始清洗JSONL内容: {name}")
    
    content_cleaner = JSONLContentCleaner(config_manager.config)
    results = content_cleaner.clean_jsonl_file(input_file, output_file)
    
    if results['success']:
        stats = results['stats']
        click.echo(f"✅ 内容清洗完成:")
        click.echo(f"  • 处理文件: {stats['total_files']}")
        click.echo(f"  • 清洗文件: {stats['files_cleaned']}")
        click.echo(f"  • 删除注释: {stats['comments_removed']}")
        click.echo(f"  • 脱敏注释: {stats['comments_desensitized']}")
        click.echo(f"  • 敏感信息: {stats['sensitive_info_removed']} (涉及 {stats['files_with_sensitive_info']} 个文件)")
        click.echo(f"  • 输出文件: {output_file}")
        
        # 如果是临时文件，清理掉
        if input_file.name == 'temp_extracted_files.jsonl':
            input_file.unlink()
    else:
        click.echo(f"❌ 内容清洗失败: {results['error']}")
        raise click.Abort()


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
        elif value.startswith('[') and value.endswith(']'):
            # 解析列表
            import ast
            value = ast.literal_eval(value)
        
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


@main.command()
@click.option('--output', '-o', type=click.Path(), help='输出文件路径')
@click.option('--no-comments', is_flag=True, help='不包含注释')
@click.pass_context
def generate_config(ctx, output, no_comments):
    """生成配置模板"""
    config_manager = ctx.obj['config_manager']
    
    template = config_manager.generate_config_template(include_comments=not no_comments)
    
    if output:
        with open(output, 'w', encoding='utf-8') as f:
            f.write(template)
        click.echo(f"✅ 配置模板已生成: {output}")
    else:
        click.echo(template)


@main.command()
@click.argument('file', type=click.Path(exists=True))
@click.pass_context
def validate_config(ctx, file):
    """验证配置文件"""
    config_manager = ctx.obj['config_manager']
    
    errors = config_manager.validate_config_file(file)
    
    if not errors:
        click.echo("✅ 配置文件验证通过")
    else:
        click.echo("❌ 配置文件验证失败:")
        for error in errors:
            click.echo(f"  • {error}")


@main.command()
@click.option('--section', '-s', help='指定配置节')
@click.pass_context
def config_info(ctx, section):
    """显示配置信息"""
    config_manager = ctx.obj['config_manager']
    
    info = config_manager.get_config_info()
    
    if section:
        if section in info:
            click.echo(f"📋 {section.upper()} 配置信息:")
            for key, details in info[section].items():
                click.echo(f"  {key}:")
                click.echo(f"    类型: {details['type']}")
                click.echo(f"    必需: {details['required']}")
                click.echo(f"    默认值: {details['default']}")
                click.echo(f"    当前值: {details['current_value']}")
                click.echo(f"    描述: {details['description']}")
                if details['env_var']:
                    click.echo(f"    环境变量: {details['env_var']}")
                click.echo()
        else:
            click.echo(f"❌ 配置节不存在: {section}")
    else:
        for section_name, section_info in info.items():
            click.echo(f"📋 {section_name.upper()}:")
            for key, details in section_info.items():
                click.echo(f"  {key}: {details['current_value']} ({details['type']})")
            click.echo()


@main.command()
@click.option('--interactive', '-i', is_flag=True, help='交互式配置向导')
@click.pass_context
def config_wizard(ctx, interactive):
    """配置向导"""
    config_manager = ctx.obj['config_manager']
    
    if interactive:
        click.echo("🔧 RopeDP 配置向导")
        click.echo("=" * 50)
        
        # 文件提取配置
        click.echo("\n📁 文件提取配置:")
        file_types = click.prompt("支持的文件类型 (用逗号分隔)", 
                                default=",".join(config_manager.get('extraction.file_types', [])))
        config_manager.set('extraction.file_types', [t.strip() for t in file_types.split(',')])
        
        max_size = click.prompt("最大文件大小 (MB)", 
                               default=config_manager.get('extraction.max_file_size', 10485760) // 1024 // 1024)
        config_manager.set('extraction.max_file_size', max_size * 1024 * 1024)
        
        # 性能配置
        click.echo("\n⚡ 性能配置:")
        workers = click.prompt("最大并发数", 
                              default=config_manager.get('performance.max_workers', 4))
        config_manager.set('performance.max_workers', workers)
        
        memory = click.prompt("内存限制 (MB)", 
                             default=config_manager.get('performance.memory_limit', 1024))
        config_manager.set('performance.memory_limit', memory)
        
        # 日志配置
        click.echo("\n📝 日志配置:")
        log_level = click.prompt("日志级别", 
                                default=config_manager.get('logging.level', 'INFO'),
                                type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']))
        config_manager.set('logging.level', log_level)
        
        click.echo("\n✅ 配置向导完成!")
    else:
        # 显示当前配置摘要
        click.echo("📋 当前配置摘要:")
        click.echo("=" * 50)
        
        sections = ['extraction', 'performance', 'logging', 'analysis']
        for section in sections:
            if section in config_manager.config:
                click.echo(f"\n{section.upper()}:")
                for key, value in config_manager.config[section].items():
                    click.echo(f"  {key}: {value}")


if __name__ == '__main__':
    main()

