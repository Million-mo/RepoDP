"""
命令行界面
"""

import click
import logging
from pathlib import Path
from typing import List, Dict, Any

from .core import RepositoryManager, ConfigManager
from .core.pipeline_manager import PipelineManager
from .extractors import FileExtractor, CodeExtractor, TextExtractor
from .cleaners import Deduplicator, JSONLContentCleaner, FileMetricsCleaner
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
        # 直接覆盖原文件
        output_file = input_file
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
@click.option('--output', '-o', type=click.Path(), help='输出JSONL文件路径')
@click.option('--in-place', '-i', is_flag=True, help='直接覆盖原JSONL文件')
@click.pass_context
def deduplicate(ctx, name, strategy, output, in_place):
    """去重分析并处理JSONL文件"""
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
        # 直接覆盖原文件
        output_file = input_file
    elif output:
        output_file = Path(output)
    else:
        output_file = input_file.parent / f"{input_file.stem}_deduplicated{input_file.suffix}"
    
    # 确保输出目录存在
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # 去重分析
    click.echo(f"🔍 开始去重分析: {name}")
    
    deduplicator = Deduplicator(config_manager.config)
    
    # 先分析重复情况
    duplicate_report = deduplicator.analyze_jsonl_duplicates(input_file)
    
    click.echo(f"✅ 去重分析完成:")
    click.echo(f"  • 检查文件: {duplicate_report['total_files_checked']}")
    click.echo(f"  • 重复组: {duplicate_report['duplicate_groups']}")
    click.echo(f"  • 相似组: {duplicate_report['similar_groups']}")
    click.echo(f"  • 可节省空间: {duplicate_report['total_duplicate_size'] / 1024 / 1024:.1f} MB")
    
    # 如果有重复文件，询问是否处理
    if duplicate_report['duplicate_groups'] > 0:
        if click.confirm(f"发现 {duplicate_report['duplicate_groups']} 个重复组，是否创建去重后的JSONL文件？"):
            # 创建去重后的JSONL文件
            result = deduplicator.create_deduplicated_jsonl(input_file, output_file, duplicate_report, strategy)
            
            if result['success']:
                click.echo(f"✅ 去重处理完成:")
                click.echo(f"  • 原始文件数: {result['original_count']}")
                click.echo(f"  • 去重后文件数: {result['deduplicated_count']}")
                click.echo(f"  • 移除文件数: {result['removed_count']}")
                click.echo(f"  • 输出文件: {output_file}")
                
                # 如果是临时文件，清理掉
                if input_file.name == 'temp_extracted_files.jsonl':
                    input_file.unlink()
            else:
                click.echo(f"❌ 去重处理失败: {result['error']}")
                raise click.Abort()
    else:
        click.echo("ℹ️  没有发现重复文件，无需处理")


@main.command()
@click.argument('name')
@click.option('--thresholds', '-t', help='阈值配置文件路径 (JSON格式)')
@click.option('--dry-run', '-d', is_flag=True, help='仅分析，不执行清洗操作')
@click.option('--output', '-o', type=click.Path(), help='输出JSONL文件路径')
@click.option('--in-place', '-i', is_flag=True, help='直接覆盖原JSONL文件')
@click.option('--verbose', '-v', is_flag=True, help='显示详细的规则违规信息')
@click.option('--max-files', '-m', type=int, default=10, help='显示违规文件的最大数量')
@click.pass_context
def clean_metrics(ctx, name, thresholds, dry_run, output, in_place, verbose, max_files):
    """基于文件指标的清洗（文件大小、行数、注释比例等）"""
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
    
    # 加载阈值配置
    if thresholds:
        import json
        try:
            with open(thresholds, 'r', encoding='utf-8') as f:
                threshold_config = json.load(f)
            config_manager.set('file_metrics_cleaning.thresholds', threshold_config)
        except Exception as e:
            click.echo(f"❌ 加载阈值配置失败: {e}")
            raise click.Abort()
    
    # 设置输出文件路径
    if in_place:
        # 直接覆盖原文件
        output_file = input_file
    elif output:
        output_file = Path(output)
    else:
        output_file = input_file.parent / f"{input_file.stem}_metrics_cleaned{input_file.suffix}"
    
    # 确保输出目录存在
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # 执行文件指标清洗
    click.echo(f"📊 开始文件指标清洗: {name}")
    if dry_run:
        click.echo("🔍 干运行模式 - 仅分析，不执行清洗操作")
    
    file_metrics_cleaner = FileMetricsCleaner(config_manager.config)
    
    if dry_run:
        # 仅分析模式
        results = file_metrics_cleaner.analyze_jsonl_metrics(input_file, name)
    else:
        # 完整清洗模式
        results = file_metrics_cleaner.clean_jsonl_by_metrics(input_file, output_file, name)
    
    # 显示结果
    click.echo(f"✅ 文件指标分析完成:")
    click.echo(f"  • 总文件数: {results['total_files']}")
    click.echo(f"  • 清洗文件: {results['cleaned_files']}")
    click.echo(f"  • 删除文件: {results['removed_files']}")
    click.echo(f"  • 忽略文件: {results['ignored_files']}")
    
    if results['errors']:
        click.echo(f"  • 错误: {len(results['errors'])} 个")
        for error in results['errors'][:5]:  # 只显示前5个错误
            click.echo(f"    - {error}")
    
    # 显示指标摘要
    metrics_summary = results.get('metrics_summary', {})
    if metrics_summary:
        click.echo(f"\n📈 指标摘要:")
        avg_metrics = metrics_summary.get('average_metrics', {})
        if avg_metrics:
            click.echo(f"  • 平均文件大小: {avg_metrics.get('file_size', 0) / 1024:.1f} KB")
            click.echo(f"  • 平均行数: {avg_metrics.get('line_count', 0):.0f}")
            click.echo(f"  • 平均最大行长度: {avg_metrics.get('max_line_length', 0):.0f}")
            click.echo(f"  • 平均注释比例: {avg_metrics.get('comment_percentage', 0):.1f}%")
            click.echo(f"  • 平均数字比例: {avg_metrics.get('digit_percentage', 0):.1f}%")
            click.echo(f"  • 平均十六进制比例: {avg_metrics.get('hex_percentage', 0):.1f}%")
        
        violations = metrics_summary.get('threshold_violations', {})
        if violations:
            click.echo(f"\n⚠️  阈值违规:")
            if violations.get('oversized_files', 0) > 0:
                click.echo(f"  • 超大文件: {violations['oversized_files']} 个")
            if violations.get('long_line_files', 0) > 0:
                click.echo(f"  • 超长行文件: {violations['long_line_files']} 个")
            if violations.get('high_line_count_files', 0) > 0:
                click.echo(f"  • 过多行文件: {violations['high_line_count_files']} 个")
            if violations.get('high_digit_files', 0) > 0:
                click.echo(f"  • 高数字比例文件: {violations['high_digit_files']} 个")
            if violations.get('high_hex_files', 0) > 0:
                click.echo(f"  • 高十六进制比例文件: {violations['high_hex_files']} 个")
    
    if not dry_run:
        click.echo(f"📄 输出文件: {output_file}")
        
        # 如果是临时文件，清理掉
        if input_file.name == 'temp_extracted_files.jsonl':
            input_file.unlink()
    
    # 显示详细的规则违规信息（如果启用verbose模式）
    if verbose:
        detailed_violations = results.get('detailed_violations', [])
        if detailed_violations:
            click.echo(f"\n📋 详细规则违规信息:")
            
            # 按操作类型分组
            remove_files = [v for v in detailed_violations if v['action'] == 'remove']
            clean_files = [v for v in detailed_violations if v['action'] == 'clean']
            
            if remove_files:
                click.echo(f"\n🔴 将被删除的文件 ({len(remove_files)} 个):")
                for i, violation in enumerate(remove_files[:max_files]):
                    click.echo(f"  {i+1}. {violation['file']}")
                    for rule_violation in violation['violations']:
                        rule_name = {
                            'min_comment_percentage': '注释比例过低',
                            'max_comment_percentage': '注释比例过高',
                            'max_digit_percentage': '数字比例过高',
                            'max_hex_percentage': '十六进制比例过高',
                            'max_average_line_length': '平均行长过长'
                        }.get(rule_violation['rule'], rule_violation['rule'])
                        
                        severity_icon = {
                            'critical': '🔴',
                            'high': '🟠',
                            'medium': '🟡'
                        }.get(rule_violation['severity'], '⚪')
                        
                        click.echo(f"     {severity_icon} {rule_name}: {rule_violation['actual']:.1f} (阈值: {rule_violation['threshold']:.1f})")
                
                if len(remove_files) > max_files:
                    click.echo(f"     ... 还有 {len(remove_files) - max_files} 个文件")
            
            if clean_files:
                click.echo(f"\n🟡 将被清洗的文件 ({len(clean_files)} 个):")
                for i, violation in enumerate(clean_files[:max_files]):
                    click.echo(f"  {i+1}. {violation['file']}")
                    for rule_violation in violation['violations']:
                        rule_name = {
                            'max_line_length': '单行过长',
                            'max_file_size': '文件过大',
                            'max_line_count': '行数过多'
                        }.get(rule_violation['rule'], rule_violation['rule'])
                        
                        severity_icon = {
                            'high': '🟠',
                            'medium': '🟡'
                        }.get(rule_violation['severity'], '⚪')
                        
                        if rule_violation['rule'] == 'max_file_size':
                            actual_str = f"{rule_violation['actual']/1024:.1f}KB"
                            threshold_str = f"{rule_violation['threshold']/1024:.1f}KB"
                        else:
                            actual_str = f"{rule_violation['actual']:.0f}"
                            threshold_str = f"{rule_violation['threshold']:.0f}"
                        
                        click.echo(f"     {severity_icon} {rule_name}: {actual_str} (阈值: {threshold_str})")
                
                if len(clean_files) > max_files:
                    click.echo(f"     ... 还有 {len(clean_files) - max_files} 个文件")
            
            # 显示规则统计
            rule_stats = {}
            for violation in detailed_violations:
                for rule_violation in violation['violations']:
                    rule = rule_violation['rule']
                    rule_stats[rule] = rule_stats.get(rule, 0) + 1
            
            if rule_stats:
                click.echo(f"\n📊 规则违规统计:")
                rule_names = {
                    'max_line_length': '单行过长',
                    'max_file_size': '文件过大',
                    'max_line_count': '行数过多',
                    'min_comment_percentage': '注释比例过低',
                    'max_comment_percentage': '注释比例过高',
                    'max_digit_percentage': '数字比例过高',
                    'max_hex_percentage': '十六进制比例过高',
                    'max_average_line_length': '平均行长过长'
                }
                
                for rule, count in sorted(rule_stats.items(), key=lambda x: x[1], reverse=True):
                    rule_name = rule_names.get(rule, rule)
                    click.echo(f"  • {rule_name}: {count} 个文件")


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


# Pipeline相关命令
@main.group()
@click.pass_context
def pipeline(ctx):
    """Pipeline管理命令"""
    pass


@pipeline.command()
@click.option('--pipeline', '-p', help='指定pipeline名称')
@click.pass_context
def list_pipelines(ctx, pipeline):
    """列出所有可用的pipeline"""
    config_manager = ctx.obj['config_manager']
    
    try:
        pipelines = config_manager.list_pipelines()
        
        if not pipelines:
            click.echo("❌ 没有找到任何pipeline")
            return
        
        click.echo("📋 可用的Pipeline:")
        click.echo("=" * 60)
        
        for p in pipelines:
            status = "✅" if p['enabled_steps'] > 0 else "❌"
            click.echo(f"{status} {p['name']}")
            click.echo(f"   显示名称: {p['display_name']}")
            click.echo(f"   描述: {p['description']}")
            click.echo(f"   步骤数: {p['steps']} (启用: {p['enabled_steps']})")
            click.echo()
        
        if pipeline:
            # 显示特定pipeline的详细信息
            try:
                pipeline_config = config_manager.get_pipeline_config(pipeline)
                click.echo(f"🔍 Pipeline '{pipeline}' 详细信息:")
                click.echo("=" * 40)
                click.echo(f"名称: {pipeline_config.get('name', pipeline)}")
                click.echo(f"描述: {pipeline_config.get('description', '无')}")
                click.echo(f"步骤:")
                
                for i, step in enumerate(pipeline_config.get('steps', []), 1):
                    status = "✅" if step.get('enabled', True) else "❌"
                    click.echo(f"  {i}. {status} {step['name']} ({step['type']})")
                    if step.get('depends_on'):
                        click.echo(f"     依赖: {', '.join(step['depends_on'])}")
                    if step.get('config'):
                        click.echo(f"     配置: {step['config']}")
                
            except ValueError as e:
                click.echo(f"❌ {e}")
    
    except Exception as e:
        click.echo(f"❌ 列出pipeline失败: {e}")


@pipeline.command()
@click.argument('pipeline_name')
@click.pass_context
def validate(ctx, pipeline_name):
    """验证pipeline配置"""
    config_manager = ctx.obj['config_manager']
    
    try:
        result = config_manager.validate_pipeline(pipeline_name)
        
        if result['valid']:
            click.echo(f"✅ Pipeline '{pipeline_name}' 配置有效")
            click.echo(f"   步骤数: {result['steps']}")
            click.echo(f"   启用步骤数: {result['enabled_steps']}")
        else:
            click.echo(f"❌ Pipeline '{pipeline_name}' 配置无效")
            click.echo(f"   错误: {result['error']}")
    
    except Exception as e:
        click.echo(f"❌ 验证pipeline失败: {e}")


@pipeline.command()
@click.argument('pipeline_name')
@click.pass_context
def dry_run(ctx, pipeline_name):
    """模拟执行pipeline（不实际执行）"""
    config_manager = ctx.obj['config_manager']
    
    try:
        pipeline_manager = PipelineManager(config_manager.config)
        result = pipeline_manager.dry_run(pipeline_name)
        
        if 'error' in result:
            click.echo(f"❌ 模拟执行失败: {result['error']}")
            return
        
        click.echo(f"🔍 Pipeline '{pipeline_name}' 模拟执行结果:")
        click.echo("=" * 50)
        click.echo(f"总步骤数: {result['total_steps']}")
        click.echo(f"启用步骤数: {result['enabled_steps']}")
        click.echo(f"执行顺序: {' -> '.join(result['execution_order'])}")
        click.echo()
        
        click.echo("📋 步骤详情:")
        for step in result['steps']:
            status = "✅" if step['enabled'] else "❌"
            click.echo(f"  {status} {step['name']} ({step['type']})")
            if step['input_file']:
                click.echo(f"    输入: {step['input_file']}")
            if step['output_file']:
                click.echo(f"    输出: {step['output_file']}")
            if step['depends_on']:
                click.echo(f"    依赖: {', '.join(step['depends_on'])}")
        
        click.echo()
        click.echo("📁 预估输出文件:")
        for output_file in result['estimated_outputs']:
            click.echo(f"  - {output_file}")
    
    except Exception as e:
        click.echo(f"❌ 模拟执行失败: {e}")


@pipeline.command()
@click.argument('repo_name')
@click.option('--pipeline', '-p', help='指定pipeline名称（默认使用标准pipeline）')
@click.option('--output', '-o', type=click.Path(), help='输出目录')
@click.option('--dry-run', is_flag=True, help='模拟执行（不实际执行）')
@click.pass_context
def run(ctx, repo_name, pipeline, output, dry_run):
    """执行pipeline处理代码仓库"""
    config_manager = ctx.obj['config_manager']
    repo_manager = ctx.obj['repo_manager']
    
    try:
        # 检查仓库是否存在
        if not repo_manager.is_valid_repository(repo_name):
            click.echo(f"❌ 仓库 '{repo_name}' 不存在")
            return
        
        # 获取仓库路径
        repo_path = repo_manager.get_repository_path(repo_name)
        if not repo_path or not repo_path.exists():
            click.echo(f"❌ 仓库路径不存在: {repo_path}")
            return
        
        # 创建pipeline管理器
        pipeline_manager = PipelineManager(config_manager.config)
        
        if dry_run:
            # 模拟执行
            result = pipeline_manager.dry_run(pipeline)
            
            if 'error' in result:
                click.echo(f"❌ 模拟执行失败: {result['error']}")
                return
            
            click.echo(f"🔍 Pipeline '{pipeline or 'default'}' 模拟执行结果:")
            click.echo("=" * 50)
            click.echo(f"总步骤数: {result['total_steps']}")
            click.echo(f"启用步骤数: {result['enabled_steps']}")
            click.echo(f"执行顺序: {' -> '.join(result['execution_order'])}")
            click.echo()
            
            click.echo("📋 步骤详情:")
            for step in result['steps']:
                status = "✅" if step['enabled'] else "❌"
                click.echo(f"  {status} {step['name']} ({step['type']})")
                if step['input_file']:
                    click.echo(f"    输入: {step['input_file']}")
                if step['output_file']:
                    click.echo(f"    输出: {step['output_file']}")
                if step['depends_on']:
                    click.echo(f"    依赖: {', '.join(step['depends_on'])}")
            
            click.echo()
            click.echo("📁 预估输出文件:")
            for output_file in result['estimated_outputs']:
                click.echo(f"  - {output_file}")
            
            return
        
        # 实际执行
        click.echo(f"🚀 开始执行Pipeline '{pipeline or 'default'}' 处理仓库 '{repo_name}'")
        click.echo("=" * 60)
        
        result = pipeline_manager.execute_pipeline(
            repo_path=repo_path,
            pipeline_name=pipeline,
            repo_name=repo_name,
            output_dir=output
        )
        
        if result['success']:
            click.echo("✅ Pipeline执行成功!")
            click.echo(f"   输出目录: {result['output_dir']}")
            click.echo(f"   完成步骤: {', '.join(result['completed_steps'])}")
            click.echo(f"   开始时间: {result['start_time']}")
            click.echo(f"   结束时间: {result['end_time']}")
            
            # 显示步骤结果摘要
            click.echo()
            click.echo("📊 步骤执行结果:")
            for step_name, step_result in result['steps'].items():
                status = "✅" if step_result['success'] else "❌"
                click.echo(f"  {status} {step_name} ({step_result['step_type']})")
                if step_result.get('stats'):
                    stats = step_result['stats']
                    if 'files_extracted' in stats:
                        click.echo(f"    提取文件数: {stats['files_extracted']}")
                    if 'original_count' in stats:
                        click.echo(f"    原始文件数: {stats['original_count']}")
                    if 'deduplicated_count' in stats:
                        click.echo(f"    去重后文件数: {stats['deduplicated_count']}")
                    if 'removed_count' in stats:
                        click.echo(f"    移除文件数: {stats['removed_count']}")
                    if 'cleaned_files' in stats:
                        click.echo(f"    清洗文件数: {stats['cleaned_files']}")
            
            if result['errors']:
                click.echo()
                click.echo("⚠️  执行过程中的错误:")
                for error in result['errors']:
                    click.echo(f"  - {error}")
        else:
            click.echo("❌ Pipeline执行失败!")
            if result['errors']:
                click.echo("错误信息:")
                for error in result['errors']:
                    click.echo(f"  - {error}")
    
    except Exception as e:
        click.echo(f"❌ 执行pipeline失败: {e}")


@pipeline.command()
@click.argument('pipeline_name')
@click.argument('config_file', type=click.Path(exists=True))
@click.pass_context
def add(ctx, pipeline_name, config_file):
    """添加新的pipeline配置"""
    config_manager = ctx.obj['config_manager']
    
    try:
        import yaml
        with open(config_file, 'r', encoding='utf-8') as f:
            pipeline_config = yaml.safe_load(f)
        
        config_manager.add_pipeline(pipeline_name, pipeline_config)
        click.echo(f"✅ 成功添加pipeline '{pipeline_name}'")
    
    except Exception as e:
        click.echo(f"❌ 添加pipeline失败: {e}")


@pipeline.command()
@click.argument('pipeline_name')
@click.pass_context
def remove(ctx, pipeline_name):
    """删除pipeline配置"""
    config_manager = ctx.obj['config_manager']
    
    try:
        config_manager.remove_pipeline(pipeline_name)
        click.echo(f"✅ 成功删除pipeline '{pipeline_name}'")
    
    except Exception as e:
        click.echo(f"❌ 删除pipeline失败: {e}")


@pipeline.command()
@click.argument('pipeline_name')
@click.argument('config_file', type=click.Path(exists=True))
@click.pass_context
def update(ctx, pipeline_name, config_file):
    """更新pipeline配置"""
    config_manager = ctx.obj['config_manager']
    
    try:
        import yaml
        with open(config_file, 'r', encoding='utf-8') as f:
            pipeline_config = yaml.safe_load(f)
        
        config_manager.update_pipeline(pipeline_name, pipeline_config)
        click.echo(f"✅ 成功更新pipeline '{pipeline_name}'")
    
    except Exception as e:
        click.echo(f"❌ 更新pipeline失败: {e}")


if __name__ == '__main__':
    main()

