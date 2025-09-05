"""
指标计算器
"""

import math
from typing import Dict, Any, List, Optional, Tuple
from collections import defaultdict, Counter
import logging

logger = logging.getLogger(__name__)


class MetricsCalculator:
    """指标计算器，用于计算各种代码指标"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    def calculate_metrics(self, file_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """计算所有指标"""
        logger.info(f"开始计算指标，共 {len(file_list)} 个文件")
        
        # 基本指标
        basic_metrics = self._calculate_basic_metrics(file_list)
        
        # 代码质量指标
        quality_metrics = self._calculate_quality_metrics(file_list)
        
        # 复杂度指标
        complexity_metrics = self._calculate_complexity_metrics(file_list)
        
        # 维护性指标
        maintainability_metrics = self._calculate_maintainability_metrics(file_list)
        
        # 可读性指标
        readability_metrics = self._calculate_readability_metrics(file_list)
        
        # 测试覆盖率指标
        test_coverage_metrics = self._calculate_test_coverage_metrics(file_list)
        
        return {
            'basic': basic_metrics,
            'quality': quality_metrics,
            'complexity': complexity_metrics,
            'maintainability': maintainability_metrics,
            'readability': readability_metrics,
            'test_coverage': test_coverage_metrics
        }
    
    def _calculate_basic_metrics(self, file_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """计算基本指标"""
        total_files = len(file_list)
        total_lines = sum(file_info.get('lines', 0) for file_info in file_list)
        total_size = sum(file_info.get('size', 0) for file_info in file_list)
        
        # 按语言分组
        language_stats = defaultdict(lambda: {'files': 0, 'lines': 0, 'size': 0})
        for file_info in file_list:
            language = file_info.get('language', 'unknown')
            language_stats[language]['files'] += 1
            language_stats[language]['lines'] += file_info.get('lines', 0)
            language_stats[language]['size'] += file_info.get('size', 0)
        
        # 计算文件大小分布
        file_sizes = [file_info.get('size', 0) for file_info in file_list]
        size_distribution = self._calculate_distribution(file_sizes)
        
        # 计算行数分布
        line_counts = [file_info.get('lines', 0) for file_info in file_list]
        line_distribution = self._calculate_distribution(line_counts)
        
        return {
            'total_files': total_files,
            'total_lines': total_lines,
            'total_size': total_size,
            'avg_lines_per_file': total_lines / total_files if total_files > 0 else 0,
            'avg_size_per_file': total_size / total_files if total_files > 0 else 0,
            'language_distribution': dict(language_stats),
            'size_distribution': size_distribution,
            'line_distribution': line_distribution
        }
    
    def _calculate_quality_metrics(self, file_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """计算代码质量指标"""
        total_issues = 0
        issue_types = defaultdict(int)
        quality_scores = []
        
        for file_info in file_list:
            # 计算文件质量分数
            quality_score = self._calculate_file_quality_score(file_info)
            quality_scores.append(quality_score)
            
            # 统计问题
            code_structure = file_info.get('code_structure', {})
            if 'quality_issues' in code_structure:
                for issue in code_structure['quality_issues']:
                    total_issues += 1
                    issue_types[issue.get('type', 'unknown')] += 1
        
        # 计算质量分数分布
        quality_distribution = self._calculate_distribution(quality_scores)
        
        return {
            'total_issues': total_issues,
            'avg_issues_per_file': total_issues / len(file_list) if file_list else 0,
            'issue_types': dict(issue_types),
            'avg_quality_score': sum(quality_scores) / len(quality_scores) if quality_scores else 0,
            'quality_distribution': quality_distribution
        }
    
    def _calculate_file_quality_score(self, file_info: Dict[str, Any]) -> float:
        """计算单个文件的质量分数"""
        score = 100.0
        
        # 基于文件大小扣分
        size = file_info.get('size', 0)
        if size > 1000 * 1024:  # 1MB
            score -= 20
        elif size > 500 * 1024:  # 500KB
            score -= 10
        
        # 基于行数扣分
        lines = file_info.get('lines', 0)
        if lines > 1000:
            score -= 15
        elif lines > 500:
            score -= 8
        
        # 基于复杂度扣分
        code_structure = file_info.get('code_structure', {})
        complexity = code_structure.get('complexity', 0)
        if complexity > 20:
            score -= 25
        elif complexity > 10:
            score -= 15
        elif complexity > 5:
            score -= 8
        
        # 基于问题数量扣分
        quality_issues = code_structure.get('quality_issues', [])
        issue_count = len(quality_issues)
        if issue_count > 10:
            score -= 20
        elif issue_count > 5:
            score -= 10
        elif issue_count > 0:
            score -= issue_count * 2
        
        return max(0, score)
    
    def _calculate_complexity_metrics(self, file_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """计算复杂度指标"""
        complexities = []
        total_complexity = 0
        
        for file_info in file_list:
            code_structure = file_info.get('code_structure', {})
            complexity = code_structure.get('complexity', 0)
            complexities.append(complexity)
            total_complexity += complexity
        
        # 计算复杂度分布
        complexity_distribution = self._calculate_distribution(complexities)
        
        # 计算复杂度等级
        complexity_levels = {
            'low': sum(1 for c in complexities if c <= 5),
            'medium': sum(1 for c in complexities if 5 < c <= 15),
            'high': sum(1 for c in complexities if 15 < c <= 30),
            'very_high': sum(1 for c in complexities if c > 30)
        }
        
        return {
            'total_complexity': total_complexity,
            'avg_complexity': total_complexity / len(file_list) if file_list else 0,
            'max_complexity': max(complexities) if complexities else 0,
            'min_complexity': min(complexities) if complexities else 0,
            'complexity_distribution': complexity_distribution,
            'complexity_levels': complexity_levels
        }
    
    def _calculate_maintainability_metrics(self, file_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """计算维护性指标"""
        maintainability_scores = []
        
        for file_info in file_list:
            score = self._calculate_file_maintainability_score(file_info)
            maintainability_scores.append(score)
        
        # 计算维护性分数分布
        maintainability_distribution = self._calculate_distribution(maintainability_scores)
        
        return {
            'avg_maintainability_score': sum(maintainability_scores) / len(maintainability_scores) if maintainability_scores else 0,
            'maintainability_distribution': maintainability_distribution,
            'maintainable_files': sum(1 for s in maintainability_scores if s >= 70),
            'difficult_to_maintain_files': sum(1 for s in maintainability_scores if s < 50)
        }
    
    def _calculate_file_maintainability_score(self, file_info: Dict[str, Any]) -> float:
        """计算单个文件的维护性分数"""
        score = 100.0
        
        # 基于文件大小
        size = file_info.get('size', 0)
        if size > 2000 * 1024:  # 2MB
            score -= 30
        elif size > 1000 * 1024:  # 1MB
            score -= 20
        elif size > 500 * 1024:  # 500KB
            score -= 10
        
        # 基于行数
        lines = file_info.get('lines', 0)
        if lines > 2000:
            score -= 25
        elif lines > 1000:
            score -= 15
        elif lines > 500:
            score -= 8
        
        # 基于复杂度
        code_structure = file_info.get('code_structure', {})
        complexity = code_structure.get('complexity', 0)
        if complexity > 30:
            score -= 35
        elif complexity > 20:
            score -= 25
        elif complexity > 10:
            score -= 15
        elif complexity > 5:
            score -= 8
        
        # 基于函数/方法数量
        functions = len(code_structure.get('functions', []))
        if functions > 50:
            score -= 20
        elif functions > 30:
            score -= 12
        elif functions > 20:
            score -= 6
        
        return max(0, score)
    
    def _calculate_readability_metrics(self, file_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """计算可读性指标"""
        readability_scores = []
        
        for file_info in file_list:
            if file_info.get('is_binary', False):
                continue
            
            text_features = file_info.get('text_features', {})
            readability = text_features.get('readability', {})
            
            # 计算可读性分数
            flesch_score = readability.get('flesch_reading_ease', 0)
            fk_grade = readability.get('flesch_kincaid_grade', 0)
            
            # 综合可读性分数
            readability_score = self._calculate_readability_score(flesch_score, fk_grade)
            readability_scores.append(readability_score)
        
        # 计算可读性分布
        readability_distribution = self._calculate_distribution(readability_scores)
        
        return {
            'avg_readability_score': sum(readability_scores) / len(readability_scores) if readability_scores else 0,
            'readability_distribution': readability_distribution,
            'highly_readable_files': sum(1 for s in readability_scores if s >= 80),
            'difficult_to_read_files': sum(1 for s in readability_scores if s < 50)
        }
    
    def _calculate_readability_score(self, flesch_score: float, fk_grade: float) -> float:
        """计算可读性分数"""
        # 基于Flesch Reading Ease分数
        if flesch_score >= 90:
            score = 100
        elif flesch_score >= 80:
            score = 90
        elif flesch_score >= 70:
            score = 80
        elif flesch_score >= 60:
            score = 70
        elif flesch_score >= 50:
            score = 60
        elif flesch_score >= 30:
            score = 50
        else:
            score = 30
        
        # 基于Flesch-Kincaid Grade Level调整
        if fk_grade <= 6:
            score += 10
        elif fk_grade <= 8:
            score += 5
        elif fk_grade >= 16:
            score -= 20
        elif fk_grade >= 12:
            score -= 10
        
        return max(0, min(100, score))
    
    def _calculate_test_coverage_metrics(self, file_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """计算测试覆盖率指标"""
        test_files = []
        source_files = []
        
        for file_info in file_list:
            path = file_info.get('path', '').lower()
            if any(test_pattern in path for test_pattern in ['test', 'spec', 'specs']):
                test_files.append(file_info)
            else:
                source_files.append(file_info)
        
        # 计算测试覆盖率（简化版本）
        test_ratio = len(test_files) / len(source_files) if source_files else 0
        
        return {
            'test_files': len(test_files),
            'source_files': len(source_files),
            'test_ratio': test_ratio,
            'test_coverage_estimate': min(100, test_ratio * 100)
        }
    
    def _calculate_distribution(self, values: List[float]) -> Dict[str, Any]:
        """计算数值分布"""
        if not values:
            return {}
        
        values.sort()
        n = len(values)
        
        return {
            'min': values[0],
            'max': values[-1],
            'mean': sum(values) / n,
            'median': values[n // 2] if n % 2 == 1 else (values[n // 2 - 1] + values[n // 2]) / 2,
            'q1': values[n // 4],
            'q3': values[3 * n // 4],
            'std': math.sqrt(sum((x - sum(values) / n) ** 2 for x in values) / n)
        }

