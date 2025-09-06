"""
文件工具函数
"""

import os
import shutil
from pathlib import Path
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class FileUtils:
    """文件工具类"""
    
    @staticmethod
    def get_file_size(file_path: Path) -> int:
        """获取文件大小"""
        try:
            return file_path.stat().st_size
        except OSError:
            return 0
    
    @staticmethod
    def get_file_extension(file_path: Path) -> str:
        """获取文件扩展名"""
        return file_path.suffix.lower()
    
    @staticmethod
    def is_binary_file(file_path: Path) -> bool:
        """判断是否为二进制文件"""
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)
                return b'\0' in chunk
        except (OSError, IOError):
            return True
    
    @staticmethod
    def read_file_content(file_path: Path, encoding: str = 'utf-8') -> Optional[str]:
        """读取文件内容"""
        try:
            with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                return f.read()
        except (OSError, IOError, UnicodeDecodeError):
            return None
    
    @staticmethod
    def write_file_content(file_path: Path, content: str, encoding: str = 'utf-8') -> bool:
        """写入文件内容"""
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w', encoding=encoding) as f:
                f.write(content)
            return True
        except (OSError, IOError):
            return False
    
    @staticmethod
    def copy_file(src: Path, dst: Path) -> bool:
        """复制文件"""
        try:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            return True
        except (OSError, IOError):
            return False
    
    @staticmethod
    def move_file(src: Path, dst: Path) -> bool:
        """移动文件"""
        try:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))
            return True
        except (OSError, IOError):
            return False
    
    @staticmethod
    def delete_file(file_path: Path) -> bool:
        """删除文件"""
        try:
            file_path.unlink()
            return True
        except OSError:
            return False
    
    @staticmethod
    def create_directory(dir_path: Path) -> bool:
        """创建目录"""
        try:
            dir_path.mkdir(parents=True, exist_ok=True)
            return True
        except OSError:
            return False
    
    @staticmethod
    def delete_directory(dir_path: Path) -> bool:
        """删除目录"""
        try:
            shutil.rmtree(dir_path)
            return True
        except OSError:
            return False
    
    @staticmethod
    def list_files(directory: Path, pattern: str = "*", recursive: bool = True) -> List[Path]:
        """列出文件"""
        try:
            if recursive:
                return list(directory.rglob(pattern))
            else:
                return list(directory.glob(pattern))
        except OSError:
            return []
    
    @staticmethod
    def get_file_info(file_path: Path) -> Dict[str, Any]:
        """获取文件信息"""
        try:
            stat = file_path.stat()
            return {
                'path': str(file_path),
                'name': file_path.name,
                'size': stat.st_size,
                'created_time': stat.st_ctime,
                'modified_time': stat.st_mtime,
                'is_file': file_path.is_file(),
                'is_dir': file_path.is_dir(),
                'extension': file_path.suffix.lower()
            }
        except OSError:
            return {}
    
    @staticmethod
    def normalize_path(path: str) -> Path:
        """标准化路径"""
        return Path(path).resolve()
    
    @staticmethod
    def get_relative_path(file_path: Path, base_path: Path) -> str:
        """获取相对路径"""
        try:
            return str(file_path.relative_to(base_path))
        except ValueError:
            return str(file_path)
    
    @staticmethod
    def ensure_extension(file_path: Path, extension: str) -> Path:
        """确保文件有指定扩展名"""
        if not file_path.suffix:
            return file_path.with_suffix(extension)
        return file_path
    
    @staticmethod
    def get_safe_filename(filename: str) -> str:
        """获取安全的文件名"""
        import re
        # 移除或替换不安全的字符
        safe_name = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # 移除前后空格和点
        safe_name = safe_name.strip(' .')
        # 确保不为空
        if not safe_name:
            safe_name = 'unnamed'
        return safe_name

