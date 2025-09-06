"""
文件清洗器
"""

import os
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional, Generator
import logging
from tqdm import tqdm

logger = logging.getLogger(__name__)


class FileCleaner:
    """文件清洗器，用于清理和标准化文件结构"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.file_cleaning_config = config.get('file_cleaning', {})
        self.cleanup_rules = self.file_cleaning_config.get('cleanup_rules', {})
        self.backup_enabled = self.file_cleaning_config.get('backup_enabled', True)
        self.backup_dir = Path(self.file_cleaning_config.get('backup_dir', 'data/backups'))
        
        # 创建备份目录
        if self.backup_enabled:
            self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def clean_repository(self, repo_path: Path, repo_name: str) -> Dict[str, Any]:
        """清洗整个代码仓库"""
        if not repo_path.exists():
            logger.error(f"仓库路径不存在: {repo_path}")
            return {}
        
        # 创建备份
        if self.backup_enabled:
            backup_path = self._create_backup(repo_path, repo_name)
            if not backup_path:
                logger.error("创建备份失败，停止清洗操作")
                return {}
        
        results = {
            'cleaned_files': 0,
            'removed_files': 0,
            'renamed_files': 0,
            'errors': [],
            'backup_path': str(backup_path) if self.backup_enabled else None
        }
        
        try:
            # 清理文件
            for file_info in self._clean_files(repo_path):
                if file_info['action'] == 'cleaned':
                    results['cleaned_files'] += 1
                elif file_info['action'] == 'removed':
                    results['removed_files'] += 1
                elif file_info['action'] == 'renamed':
                    results['renamed_files'] += 1
                elif file_info['action'] == 'error':
                    results['errors'].append(file_info['error'])
            
            logger.info(f"清洗完成: {results}")
            return results
            
        except Exception as e:
            logger.error(f"清洗仓库失败: {e}")
            results['errors'].append(str(e))
            return results
    
    def _create_backup(self, repo_path: Path, repo_name: str) -> Optional[Path]:
        """创建备份"""
        try:
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{repo_name}_backup_{timestamp}"
            backup_path = self.backup_dir / backup_name
            
            shutil.copytree(repo_path, backup_path)
            logger.info(f"备份已创建: {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"创建备份失败: {e}")
            return None
    
    def _clean_files(self, repo_path: Path) -> Generator[Dict[str, Any], None, None]:
        """清洗文件"""
        for root, dirs, files in os.walk(repo_path):
            root_path = Path(root)
            
            # 清理目录
            for dir_name in dirs[:]:  # 使用切片避免修改正在迭代的列表
                dir_path = root_path / dir_name
                if self._should_remove_dir(dir_path):
                    try:
                        shutil.rmtree(dir_path)
                        dirs.remove(dir_name)  # 从dirs列表中移除
                        yield {
                            'path': str(dir_path.relative_to(repo_path)),
                            'action': 'removed',
                            'type': 'directory'
                        }
                    except Exception as e:
                        yield {
                            'path': str(dir_path.relative_to(repo_path)),
                            'action': 'error',
                            'error': f"删除目录失败: {e}"
                        }
            
            # 清理文件
            for file_name in files:
                file_path = root_path / file_name
                
                if self._should_remove_file(file_path):
                    try:
                        file_path.unlink()
                        yield {
                            'path': str(file_path.relative_to(repo_path)),
                            'action': 'removed',
                            'type': 'file'
                        }
                    except Exception as e:
                        yield {
                            'path': str(file_path.relative_to(repo_path)),
                            'action': 'error',
                            'error': f"删除文件失败: {e}"
                        }
                
                elif self._should_rename_file(file_path):
                    new_name = self._get_new_filename(file_path)
                    if new_name and new_name != file_name:
                        try:
                            new_path = file_path.parent / new_name
                            file_path.rename(new_path)
                            yield {
                                'path': str(file_path.relative_to(repo_path)),
                                'new_path': str(new_path.relative_to(repo_path)),
                                'action': 'renamed',
                                'type': 'file'
                            }
                        except Exception as e:
                            yield {
                                'path': str(file_path.relative_to(repo_path)),
                                'action': 'error',
                                'error': f"重命名文件失败: {e}"
                            }
                
                elif self._should_clean_file(file_path):
                    try:
                        self._clean_single_file(file_path)
                        yield {
                            'path': str(file_path.relative_to(repo_path)),
                            'action': 'cleaned',
                            'type': 'file'
                        }
                    except Exception as e:
                        yield {
                            'path': str(file_path.relative_to(repo_path)),
                            'action': 'error',
                            'error': f"清洗文件失败: {e}"
                        }
    
    def _should_remove_dir(self, dir_path: Path) -> bool:
        """判断是否应该删除目录"""
        dir_name = dir_path.name
        
        # 检查排除的目录
        exclude_dirs = self.cleanup_rules.get('exclude_dirs', [
            '.git', '__pycache__', 'node_modules', '.venv', 'venv', 
            'build', 'dist', 'target', '.idea', '.vscode', '.DS_Store'
        ])
        
        if dir_name in exclude_dirs:
            return True
        
        # 检查空目录
        if self.cleanup_rules.get('remove_empty_dirs', False):
            try:
                if not any(dir_path.iterdir()):
                    return True
            except OSError:
                pass
        
        return False
    
    def _should_remove_file(self, file_path: Path) -> bool:
        """判断是否应该删除文件"""
        file_name = file_path.name
        
        # 检查排除的文件
        exclude_files = self.cleanup_rules.get('exclude_files', [
            '.DS_Store', 'Thumbs.db', 'desktop.ini', '.gitkeep'
        ])
        
        if file_name in exclude_files:
            return True
        
        # 检查临时文件
        if self.cleanup_rules.get('remove_temp_files', True):
            temp_extensions = ['.tmp', '.temp', '.bak', '.swp', '.swo', '~']
            if any(file_name.endswith(ext) for ext in temp_extensions):
                return True
        
        # 检查空文件
        if self.cleanup_rules.get('remove_empty_files', False):
            try:
                if file_path.stat().st_size == 0:
                    return True
            except OSError:
                pass
        
        return False
    
    def _should_rename_file(self, file_path: Path) -> bool:
        """判断是否应该重命名文件"""
        file_name = file_path.name
        
        # 检查需要标准化的文件名
        if self.cleanup_rules.get('normalize_filenames', True):
            # 检查特殊字符
            if any(char in file_name for char in [' ', '(', ')', '[', ']', '{', '}']):
                return True
            
            # 检查大小写
            if file_name != file_name.lower() and self.cleanup_rules.get('lowercase_filenames', False):
                return True
        
        return False
    
    def _get_new_filename(self, file_path: Path) -> str:
        """获取新的文件名"""
        file_name = file_path.name
        
        if self.cleanup_rules.get('normalize_filenames', True):
            # 替换特殊字符
            new_name = file_name
            replacements = {
                ' ': '_',
                '(': '',
                ')': '',
                '[': '',
                ']': '',
                '{': '',
                '}': ''
            }
            
            for old, new in replacements.items():
                new_name = new_name.replace(old, new)
            
            # 转换为小写
            if self.cleanup_rules.get('lowercase_filenames', False):
                new_name = new_name.lower()
            
            return new_name
        
        return file_name
    
    def _should_clean_file(self, file_path: Path) -> bool:
        """判断是否应该清洗文件"""
        # 检查文件扩展名
        cleanable_extensions = self.cleanup_rules.get('cleanable_extensions', [
            '.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.go', '.rs', 
            '.php', '.rb', '.swift', '.kt', '.cs', '.scala', '.r', '.m', 
            '.sh', '.sql', '.html', '.css', '.xml', '.json', '.yaml', '.yml', 
            '.md', '.txt'
        ])
        
        return file_path.suffix.lower() in cleanable_extensions
    
    def _clean_single_file(self, file_path: Path):
        """清洗单个文件"""
        try:
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # 应用清洗规则
            cleaned_content = self._apply_cleaning_rules(content, file_path)
            
            # 如果内容有变化，写回文件
            if cleaned_content != content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(cleaned_content)
                
                logger.debug(f"文件已清洗: {file_path}")
        
        except Exception as e:
            logger.error(f"清洗文件失败 {file_path}: {e}")
            raise
    
    def _apply_cleaning_rules(self, content: str, file_path: Path) -> str:
        """应用清洗规则"""
        cleaned_content = content
        
        # 移除行尾空白
        if self.cleanup_rules.get('remove_trailing_whitespace', True):
            lines = cleaned_content.splitlines()
            cleaned_content = '\n'.join(line.rstrip() for line in lines)
        
        # 统一换行符
        if self.cleanup_rules.get('normalize_line_endings', True):
            cleaned_content = cleaned_content.replace('\r\n', '\n').replace('\r', '\n')
        
        # 移除文件末尾的空白行
        if self.cleanup_rules.get('remove_trailing_blank_lines', True):
            cleaned_content = cleaned_content.rstrip() + '\n'
        
        # 确保文件以换行符结尾
        if self.cleanup_rules.get('ensure_final_newline', True):
            if not cleaned_content.endswith('\n'):
                cleaned_content += '\n'
        
        return cleaned_content

