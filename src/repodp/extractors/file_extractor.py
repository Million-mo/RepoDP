"""
文件提取器
"""

import os
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional, Generator
import logging
from tqdm import tqdm

logger = logging.getLogger(__name__)


class FileExtractor:
    """文件提取器基类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        # Support both direct config and nested extraction config
        extraction_config = config.get('extraction', config)
        self.file_types = extraction_config.get('file_types', [])
        self.exclude_dirs = extraction_config.get('exclude_dirs', [])
        self.exclude_files = extraction_config.get('exclude_files', [])
        self.max_file_size = extraction_config.get('max_file_size', 10 * 1024 * 1024)
    
    def should_extract_file(self, file_path: Path) -> bool:
        """判断是否应该提取文件"""
        # 检查文件扩展名
        if self.file_types and not any(str(file_path).endswith(ext) for ext in self.file_types):
            return False
        
        # 检查排除的文件
        if file_path.name in self.exclude_files:
            return False
        
        # 检查文件大小
        try:
            if file_path.stat().st_size > self.max_file_size:
                logger.warning(f"文件过大，跳过: {file_path}")
                return False
        except OSError:
            return False
        
        return True
    
    def should_extract_dir(self, dir_path: Path) -> bool:
        """判断是否应该提取目录"""
        return dir_path.name not in self.exclude_dirs
    
    def calculate_file_hash(self, file_path: Path) -> str:
        """计算文件哈希值"""
        hash_sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except (IOError, OSError) as e:
            logger.error(f"计算文件哈希失败 {file_path}: {e}")
            return ""
    
    def extract_files(self, repo_path: Path, output_file: Optional[Path] = None) -> Generator[Dict[str, Any], None, None]:
        """提取文件信息"""
        if not repo_path.exists():
            logger.error(f"仓库路径不存在: {repo_path}")
            return
        
        total_files = 0
        for root, dirs, files in os.walk(repo_path):
            root_path = Path(root)
            
            # 过滤目录
            dirs[:] = [d for d in dirs if self.should_extract_dir(root_path / d)]
            
            for file in files:
                file_path = root_path / file
                
                if self.should_extract_file(file_path):
                    total_files += 1
        
        # 如果指定了输出文件，创建JSONL文件
        jsonl_file = None
        if output_file:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            jsonl_file = open(output_file, 'w', encoding='utf-8')
        
        try:
            # 提取文件
            with tqdm(total=total_files, desc="提取文件") as pbar:
                for root, dirs, files in os.walk(repo_path):
                    root_path = Path(root)
                    
                    # 过滤目录
                    dirs[:] = [d for d in dirs if self.should_extract_dir(root_path / d)]
                    
                    for file in files:
                        file_path = root_path / file
                        
                        if self.should_extract_file(file_path):
                            try:
                                file_info = self._extract_single_file(file_path, repo_path)
                                if file_info:
                                    # 写入JSONL文件
                                    if jsonl_file:
                                        import json
                                        jsonl_file.write(json.dumps(file_info, ensure_ascii=False, default=str) + '\n')
                                        jsonl_file.flush()
                                    
                                    yield file_info
                            except Exception as e:
                                logger.error(f"提取文件失败 {file_path}: {e}")
                            finally:
                                pbar.update(1)
        finally:
            if jsonl_file:
                jsonl_file.close()
                logger.info(f"文件信息已保存到: {output_file}")
    
    def _extract_single_file(self, file_path: Path, repo_path: Path) -> Optional[Dict[str, Any]]:
        """提取单个文件信息"""
        try:
            relative_path = file_path.relative_to(repo_path)
            
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # 计算文件哈希
            file_hash = self.calculate_file_hash(file_path)
            
            # 获取文件统计信息
            stat = file_path.stat()
            
            return {
                'path': str(relative_path),
                'absolute_path': str(file_path),
                'name': file_path.name,
                'extension': file_path.suffix,
                'size': stat.st_size,
                'hash': file_hash,
                'content': content,
                'lines': len(content.splitlines()),
                'created_time': stat.st_ctime,
                'modified_time': stat.st_mtime,
                'is_binary': self._is_binary_file(content),
                'language': self._detect_language(file_path),
            }
            
        except Exception as e:
            logger.error(f"提取文件信息失败 {file_path}: {e}")
            return None
    
    def _is_binary_file(self, content: str) -> bool:
        """判断是否为二进制文件"""
        try:
            # 尝试解码，如果失败则可能是二进制文件
            content.encode('utf-8').decode('utf-8')
            return False
        except UnicodeDecodeError:
            return True
    
    def _detect_language(self, file_path: Path) -> str:
        """检测文件语言"""
        extension = file_path.suffix.lower()
        
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.h': 'c',
            '.go': 'go',
            '.rs': 'rust',
            '.php': 'php',
            '.rb': 'ruby',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.cs': 'csharp',
            '.scala': 'scala',
            '.r': 'r',
            '.m': 'matlab',
            '.sh': 'shell',
            '.sql': 'sql',
            '.html': 'html',
            '.css': 'css',
            '.xml': 'xml',
            '.json': 'json',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.md': 'markdown',
            '.txt': 'text',
        }
        
        return language_map.get(extension, 'unknown')

