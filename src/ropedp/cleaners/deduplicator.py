"""
文件去重器
"""

import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Set
from collections import defaultdict
import logging
from tqdm import tqdm

logger = logging.getLogger(__name__)


class Deduplicator:
    """文件去重器，用于识别和去除重复文件"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.dedup_config = config.get('deduplication', {})
        self.hash_algorithm = self.dedup_config.get('hash_algorithm', 'sha256')
        self.similarity_threshold = self.dedup_config.get('similarity_threshold', 0.95)
        self.min_file_size = self.dedup_config.get('min_file_size', 100)
    
    def find_duplicates(self, file_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """查找重复文件"""
        logger.info(f"开始查找重复文件，共 {len(file_list)} 个文件")
        
        # 过滤文件
        filtered_files = self._filter_files(file_list)
        logger.info(f"过滤后剩余 {len(filtered_files)} 个文件")
        
        # 按文件大小分组
        size_groups = self._group_by_size(filtered_files)
        logger.info(f"按大小分组后得到 {len(size_groups)} 个组")
        
        # 计算哈希值
        hash_groups = self._group_by_hash(size_groups)
        logger.info(f"按哈希分组后得到 {len(hash_groups)} 个组")
        
        # 查找相似文件
        similar_groups = self._find_similar_files(hash_groups)
        logger.info(f"找到 {len(similar_groups)} 个相似文件组")
        
        # 生成报告
        report = self._generate_report(hash_groups, similar_groups)
        
        return report
    
    def _filter_files(self, file_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """过滤文件"""
        filtered = []
        
        for file_info in file_list:
            # 检查文件大小
            if file_info.get('size', 0) < self.min_file_size:
                continue
            
            # 检查是否为二进制文件
            if file_info.get('is_binary', False):
                continue
            
            # 检查文件扩展名
            extension = file_info.get('extension', '').lower()
            if extension in ['.exe', '.dll', '.so', '.dylib', '.bin']:
                continue
            
            filtered.append(file_info)
        
        return filtered
    
    def _group_by_size(self, file_list: List[Dict[str, Any]]) -> Dict[int, List[Dict[str, Any]]]:
        """按文件大小分组"""
        size_groups = defaultdict(list)
        
        for file_info in file_list:
            size = file_info.get('size', 0)
            size_groups[size].append(file_info)
        
        # 只保留有多个文件的组
        return {size: files for size, files in size_groups.items() if len(files) > 1}
    
    def _group_by_hash(self, size_groups: Dict[int, List[Dict[str, Any]]]) -> Dict[str, List[Dict[str, Any]]]:
        """按哈希值分组"""
        hash_groups = defaultdict(list)
        
        for size, files in size_groups.items():
            for file_info in tqdm(files, desc=f"计算哈希值 (大小: {size})"):
                content = file_info.get('content', '')
                if content:
                    file_hash = self._calculate_hash(content)
                    file_info['hash'] = file_hash
                    hash_groups[file_hash].append(file_info)
        
        # 只保留有多个文件的组
        return {file_hash: files for file_hash, files in hash_groups.items() if len(files) > 1}
    
    def _calculate_hash(self, content: str) -> str:
        """计算内容哈希值"""
        if self.hash_algorithm == 'md5':
            return hashlib.md5(content.encode('utf-8')).hexdigest()
        elif self.hash_algorithm == 'sha1':
            return hashlib.sha1(content.encode('utf-8')).hexdigest()
        elif self.hash_algorithm == 'sha256':
            return hashlib.sha256(content.encode('utf-8')).hexdigest()
        else:
            return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def _find_similar_files(self, hash_groups: Dict[str, List[Dict[str, Any]]]) -> List[List[Dict[str, Any]]]:
        """查找相似文件"""
        similar_groups = []
        
        # 对于每个哈希组，检查是否有相似文件
        for file_hash, files in hash_groups.items():
            if len(files) > 1:
                # 完全相同的文件
                similar_groups.append(files)
            else:
                # 检查与其他文件的相似性
                similar_files = self._find_similar_to_file(files[0], hash_groups)
                if similar_files:
                    similar_groups.append([files[0]] + similar_files)
        
        return similar_groups
    
    def _find_similar_to_file(self, target_file: Dict[str, Any], hash_groups: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """查找与目标文件相似的文件"""
        similar_files = []
        target_content = target_file.get('content', '')
        
        if not target_content:
            return similar_files
        
        for file_hash, files in hash_groups.items():
            for file_info in files:
                if file_info == target_file:
                    continue
                
                content = file_info.get('content', '')
                if not content:
                    continue
                
                similarity = self._calculate_similarity(target_content, content)
                if similarity >= self.similarity_threshold:
                    file_info['similarity'] = similarity
                    similar_files.append(file_info)
        
        return similar_files
    
    def _calculate_similarity(self, content1: str, content2: str) -> float:
        """计算两个内容的相似度"""
        # 使用简单的字符级相似度
        if len(content1) == 0 and len(content2) == 0:
            return 1.0
        
        if len(content1) == 0 or len(content2) == 0:
            return 0.0
        
        # 计算最长公共子序列
        lcs_length = self._lcs_length(content1, content2)
        max_length = max(len(content1), len(content2))
        
        return lcs_length / max_length
    
    def _lcs_length(self, s1: str, s2: str) -> int:
        """计算最长公共子序列长度"""
        m, n = len(s1), len(s2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if s1[i-1] == s2[j-1]:
                    dp[i][j] = dp[i-1][j-1] + 1
                else:
                    dp[i][j] = max(dp[i-1][j], dp[i][j-1])
        
        return dp[m][n]
    
    def _generate_report(self, hash_groups: Dict[str, List[Dict[str, Any]]], similar_groups: List[List[Dict[str, Any]]]) -> Dict[str, Any]:
        """生成去重报告"""
        total_files = sum(len(files) for files in hash_groups.values())
        duplicate_groups = len(hash_groups)
        similar_groups_count = len(similar_groups)
        
        # 计算可节省的空间
        total_duplicate_size = 0
        for files in hash_groups.values():
            if len(files) > 1:
                # 保留一个文件，删除其他文件
                duplicate_size = sum(file_info.get('size', 0) for file_info in files[1:])
                total_duplicate_size += duplicate_size
        
        # 生成重复文件列表
        duplicate_list = []
        for file_hash, files in hash_groups.items():
            if len(files) > 1:
                group_info = {
                    'hash': file_hash,
                    'count': len(files),
                    'size': files[0].get('size', 0),
                    'files': [
                        {
                            'path': file_info.get('path', ''),
                            'size': file_info.get('size', 0),
                            'modified_time': file_info.get('modified_time', 0)
                        }
                        for file_info in files
                    ]
                }
                duplicate_list.append(group_info)
        
        return {
            'total_files_checked': total_files,
            'duplicate_groups': duplicate_groups,
            'similar_groups': similar_groups_count,
            'total_duplicate_size': total_duplicate_size,
            'duplicate_list': duplicate_list,
            'summary': {
                'files_with_duplicates': sum(len(files) for files in hash_groups.values() if len(files) > 1),
                'unique_files': sum(1 for files in hash_groups.values() if len(files) == 1),
                'space_savings': total_duplicate_size
            }
        }
    
    def remove_duplicates(self, duplicate_report: Dict[str, Any], keep_strategy: str = 'newest') -> Dict[str, Any]:
        """删除重复文件"""
        if keep_strategy not in ['newest', 'oldest', 'first', 'last']:
            keep_strategy = 'newest'
        
        removed_files = []
        errors = []
        
        for group in duplicate_report.get('duplicate_list', []):
            files = group['files']
            if len(files) <= 1:
                continue
            
            # 选择要保留的文件
            keep_file = self._select_file_to_keep(files, keep_strategy)
            files_to_remove = [f for f in files if f != keep_file]
            
            # 删除重复文件
            for file_info in files_to_remove:
                try:
                    file_path = Path(file_info['path'])
                    if file_path.exists():
                        file_path.unlink()
                        removed_files.append(file_info)
                        logger.info(f"已删除重复文件: {file_path}")
                except Exception as e:
                    error_msg = f"删除文件失败 {file_info['path']}: {e}"
                    errors.append(error_msg)
                    logger.error(error_msg)
        
        return {
            'removed_files': removed_files,
            'errors': errors,
            'total_removed': len(removed_files),
            'total_errors': len(errors)
        }
    
    def _select_file_to_keep(self, files: List[Dict[str, Any]], strategy: str) -> Dict[str, Any]:
        """选择要保留的文件"""
        if strategy == 'newest':
            return max(files, key=lambda f: f.get('modified_time', 0))
        elif strategy == 'oldest':
            return min(files, key=lambda f: f.get('modified_time', 0))
        elif strategy == 'first':
            return files[0]
        elif strategy == 'last':
            return files[-1]
        else:
            return files[0]

