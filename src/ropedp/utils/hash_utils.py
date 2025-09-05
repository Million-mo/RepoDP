"""
哈希工具函数
"""

import hashlib
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class HashUtils:
    """哈希工具类"""
    
    @staticmethod
    def calculate_hash(data: str, algorithm: str = 'sha256') -> str:
        """计算字符串哈希值"""
        try:
            if algorithm == 'md5':
                return hashlib.md5(data.encode('utf-8')).hexdigest()
            elif algorithm == 'sha1':
                return hashlib.sha1(data.encode('utf-8')).hexdigest()
            elif algorithm == 'sha256':
                return hashlib.sha256(data.encode('utf-8')).hexdigest()
            elif algorithm == 'sha512':
                return hashlib.sha512(data.encode('utf-8')).hexdigest()
            else:
                return hashlib.sha256(data.encode('utf-8')).hexdigest()
        except Exception as e:
            logger.error(f"计算哈希失败: {e}")
            return ""
    
    @staticmethod
    def calculate_file_hash(file_path: str, algorithm: str = 'sha256') -> str:
        """计算文件哈希值"""
        try:
            hash_obj = hashlib.new(algorithm)
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_obj.update(chunk)
            return hash_obj.hexdigest()
        except Exception as e:
            logger.error(f"计算文件哈希失败: {e}")
            return ""
    
    @staticmethod
    def calculate_multiple_hashes(data: str) -> Dict[str, str]:
        """计算多种哈希值"""
        algorithms = ['md5', 'sha1', 'sha256', 'sha512']
        hashes = {}
        
        for algorithm in algorithms:
            hashes[algorithm] = HashUtils.calculate_hash(data, algorithm)
        
        return hashes
    
    @staticmethod
    def verify_hash(data: str, expected_hash: str, algorithm: str = 'sha256') -> bool:
        """验证哈希值"""
        calculated_hash = HashUtils.calculate_hash(data, algorithm)
        return calculated_hash == expected_hash
    
    @staticmethod
    def verify_file_hash(file_path: str, expected_hash: str, algorithm: str = 'sha256') -> bool:
        """验证文件哈希值"""
        calculated_hash = HashUtils.calculate_file_hash(file_path, algorithm)
        return calculated_hash == expected_hash
    
    @staticmethod
    def calculate_checksum(data: str) -> int:
        """计算简单校验和"""
        checksum = 0
        for char in data:
            checksum += ord(char)
        return checksum % 65536
    
    @staticmethod
    def calculate_similarity_hash(data: str, window_size: int = 3) -> str:
        """计算相似性哈希（用于检测相似内容）"""
        if len(data) < window_size:
            return HashUtils.calculate_hash(data)
        
        # 提取滑动窗口的字符
        windows = []
        for i in range(len(data) - window_size + 1):
            window = data[i:i + window_size]
            windows.append(window)
        
        # 计算每个窗口的哈希值
        window_hashes = [HashUtils.calculate_hash(w, 'md5') for w in windows]
        
        # 合并所有窗口哈希
        combined = ''.join(window_hashes)
        
        # 计算最终哈希
        return HashUtils.calculate_hash(combined)
    
    @staticmethod
    def calculate_content_fingerprint(data: str) -> str:
        """计算内容指纹（用于快速比较）"""
        # 移除空白字符
        cleaned_data = ''.join(data.split())
        
        # 转换为小写
        cleaned_data = cleaned_data.lower()
        
        # 计算哈希
        return HashUtils.calculate_hash(cleaned_data, 'sha256')
    
    @staticmethod
    def calculate_structural_hash(data: str) -> str:
        """计算结构哈希（基于代码结构）"""
        # 提取结构特征
        lines = data.splitlines()
        
        # 计算行数
        line_count = len(lines)
        
        # 计算非空行数
        non_empty_lines = len([line for line in lines if line.strip()])
        
        # 计算平均行长度
        avg_line_length = sum(len(line) for line in lines) / line_count if line_count > 0 else 0
        
        # 计算缩进特征
        indent_levels = []
        for line in lines:
            if line.strip():
                indent = len(line) - len(line.lstrip())
                indent_levels.append(indent)
        
        avg_indent = sum(indent_levels) / len(indent_levels) if indent_levels else 0
        
        # 创建结构特征字符串
        structure_features = f"lines:{line_count},non_empty:{non_empty_lines},avg_length:{avg_line_length:.2f},avg_indent:{avg_indent:.2f}"
        
        # 计算哈希
        return HashUtils.calculate_hash(structure_features, 'sha256')

