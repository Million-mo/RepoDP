"""
代码分析器
"""

import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from collections import defaultdict, Counter
import logging

logger = logging.getLogger(__name__)


class CodeAnalyzer:
    """代码分析器，用于分析代码质量和结构"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.analysis_config = config.get('analysis', {})
    
    def analyze_repository(self, file_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析整个代码仓库"""
        logger.info(f"开始分析代码仓库，共 {len(file_list)} 个文件")
        
        # 按语言分组
        language_groups = self._group_by_language(file_list)
        
        # 分析每个语言组
        language_analysis = {}
        for language, files in language_groups.items():
            if files:
                language_analysis[language] = self._analyze_language_group(language, files)
        
        # 生成总体分析
        overall_analysis = self._generate_overall_analysis(language_analysis)
        
        return {
            'overall': overall_analysis,
            'by_language': language_analysis,
            'file_count': len(file_list),
            'language_count': len(language_groups)
        }
    
    def _group_by_language(self, file_list: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """按语言分组文件"""
        language_groups = defaultdict(list)
        
        for file_info in file_list:
            if file_info.get('is_binary', False):
                continue
            
            language = file_info.get('language', 'unknown')
            language_groups[language].append(file_info)
        
        return dict(language_groups)
    
    def _analyze_language_group(self, language: str, files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析特定语言的文件组"""
        total_files = len(files)
        total_lines = sum(file_info.get('lines', 0) for file_info in files)
        total_size = sum(file_info.get('size', 0) for file_info in files)
        
        # 分析代码结构
        structure_analysis = self._analyze_code_structure(files, language)
        
        # 分析代码质量
        quality_analysis = self._analyze_code_quality(files, language)
        
        # 分析复杂度
        complexity_analysis = self._analyze_complexity(files, language)
        
        # 分析依赖关系
        dependency_analysis = self._analyze_dependencies(files, language)
        
        return {
            'basic_stats': {
                'file_count': total_files,
                'total_lines': total_lines,
                'total_size': total_size,
                'avg_lines_per_file': total_lines / total_files if total_files > 0 else 0,
                'avg_size_per_file': total_size / total_files if total_files > 0 else 0
            },
            'structure': structure_analysis,
            'quality': quality_analysis,
            'complexity': complexity_analysis,
            'dependencies': dependency_analysis
        }
    
    def _analyze_code_structure(self, files: List[Dict[str, Any]], language: str) -> Dict[str, Any]:
        """分析代码结构"""
        total_classes = 0
        total_functions = 0
        total_imports = 0
        
        for file_info in files:
            code_structure = file_info.get('code_structure', {})
            
            if language == 'python':
                total_classes += len(code_structure.get('classes', []))
                total_functions += len(code_structure.get('functions', []))
                total_imports += len(code_structure.get('imports', []))
            elif language in ['javascript', 'typescript']:
                total_classes += len(code_structure.get('classes', []))
                total_functions += len(code_structure.get('functions', []))
                total_imports += len(code_structure.get('imports', []))
            elif language == 'java':
                total_classes += len(code_structure.get('classes', []))
                total_functions += len(code_structure.get('methods', []))
                total_imports += len(code_structure.get('imports', []))
            elif language in ['cpp', 'c']:
                total_classes += len(code_structure.get('classes', []))
                total_functions += len(code_structure.get('functions', []))
                total_imports += len(code_structure.get('includes', []))
        
        return {
            'total_classes': total_classes,
            'total_functions': total_functions,
            'total_imports': total_imports,
            'avg_classes_per_file': total_classes / len(files) if files else 0,
            'avg_functions_per_file': total_functions / len(files) if files else 0,
            'avg_imports_per_file': total_imports / len(files) if files else 0
        }
    
    def _analyze_code_quality(self, files: List[Dict[str, Any]], language: str) -> Dict[str, Any]:
        """分析代码质量"""
        quality_issues = []
        total_issues = 0
        
        for file_info in files:
            file_issues = self._analyze_file_quality(file_info, language)
            if file_issues:
                quality_issues.extend(file_issues)
                total_issues += len(file_issues)
        
        # 统计问题类型
        issue_types = Counter(issue['type'] for issue in quality_issues)
        
        return {
            'total_issues': total_issues,
            'issue_types': dict(issue_types),
            'avg_issues_per_file': total_issues / len(files) if files else 0,
            'issues': quality_issues[:100]  # 限制返回的问题数量
        }
    
    def _analyze_file_quality(self, file_info: Dict[str, Any], language: str) -> List[Dict[str, Any]]:
        """分析单个文件的质量"""
        issues = []
        content = file_info.get('content', '')
        lines = content.splitlines()
        
        # 检查长行
        for i, line in enumerate(lines, 1):
            if len(line) > 120:
                issues.append({
                    'type': 'long_line',
                    'file': file_info.get('path', ''),
                    'line': i,
                    'message': f"行长度超过120字符: {len(line)}字符"
                })
        
        # 检查空行
        consecutive_empty_lines = 0
        for i, line in enumerate(lines, 1):
            if not line.strip():
                consecutive_empty_lines += 1
                if consecutive_empty_lines > 2:
                    issues.append({
                        'type': 'too_many_empty_lines',
                        'file': file_info.get('path', ''),
                        'line': i,
                        'message': f"连续空行超过2行: {consecutive_empty_lines}行"
                    })
            else:
                consecutive_empty_lines = 0
        
        # 检查文件大小
        if file_info.get('size', 0) > 1000 * 1024:  # 1MB
            issues.append({
                'type': 'large_file',
                'file': file_info.get('path', ''),
                'line': 0,
                'message': f"文件过大: {file_info.get('size', 0) / 1024:.1f}KB"
            })
        
        # 语言特定的质量检查
        if language == 'python':
            issues.extend(self._analyze_python_quality(file_info))
        elif language in ['javascript', 'typescript']:
            issues.extend(self._analyze_js_quality(file_info))
        elif language == 'java':
            issues.extend(self._analyze_java_quality(file_info))
        
        return issues
    
    def _analyze_python_quality(self, file_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """分析Python代码质量"""
        issues = []
        content = file_info.get('content', '')
        lines = content.splitlines()
        
        # 检查缩进
        for i, line in enumerate(lines, 1):
            if line.strip() and not line.startswith(' ') and not line.startswith('\t'):
                # 检查是否是顶级语句
                if not any(line.strip().startswith(keyword) for keyword in 
                          ['import', 'from', 'def', 'class', 'if', 'for', 'while', 'try', 'with']):
                    continue
                
                # 检查缩进是否一致
                if i > 1 and lines[i-2].strip() and lines[i-2].endswith(':'):
                    expected_indent = len(lines[i-2]) - len(lines[i-2].lstrip()) + 4
                    actual_indent = len(line) - len(line.lstrip())
                    if actual_indent != expected_indent:
                        issues.append({
                            'type': 'indentation_error',
                            'file': file_info.get('path', ''),
                            'line': i,
                            'message': f"缩进错误: 期望{expected_indent}个空格，实际{actual_indent}个"
                        })
        
        return issues
    
    def _analyze_js_quality(self, file_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """分析JavaScript代码质量"""
        issues = []
        content = file_info.get('content', '')
        
        # 检查分号
        lines = content.splitlines()
        for i, line in enumerate(lines, 1):
            if line.strip() and not line.strip().endswith((';', '{', '}', ':', ',')):
                if not any(line.strip().startswith(keyword) for keyword in 
                          ['if', 'for', 'while', 'switch', 'function', 'class', 'const', 'let', 'var']):
                    issues.append({
                        'type': 'missing_semicolon',
                        'file': file_info.get('path', ''),
                        'line': i,
                        'message': "可能缺少分号"
                    })
        
        return issues
    
    def _analyze_java_quality(self, file_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """分析Java代码质量"""
        issues = []
        content = file_info.get('content', '')
        
        # 检查包声明
        if not content.strip().startswith('package '):
            issues.append({
                'type': 'missing_package',
                'file': file_info.get('path', ''),
                'line': 1,
                'message': "缺少package声明"
            })
        
        return issues
    
    def _analyze_complexity(self, files: List[Dict[str, Any]], language: str) -> Dict[str, Any]:
        """分析代码复杂度"""
        total_complexity = 0
        max_complexity = 0
        complexity_distribution = defaultdict(int)
        
        for file_info in files:
            code_structure = file_info.get('code_structure', {})
            file_complexity = code_structure.get('complexity', 0)
            
            total_complexity += file_complexity
            max_complexity = max(max_complexity, file_complexity)
            
            # 复杂度分布
            if file_complexity <= 5:
                complexity_distribution['low'] += 1
            elif file_complexity <= 15:
                complexity_distribution['medium'] += 1
            elif file_complexity <= 30:
                complexity_distribution['high'] += 1
            else:
                complexity_distribution['very_high'] += 1
        
        return {
            'total_complexity': total_complexity,
            'avg_complexity': total_complexity / len(files) if files else 0,
            'max_complexity': max_complexity,
            'complexity_distribution': dict(complexity_distribution)
        }
    
    def _analyze_dependencies(self, files: List[Dict[str, Any]], language: str) -> Dict[str, Any]:
        """分析依赖关系"""
        all_imports = []
        import_sources = defaultdict(int)
        
        for file_info in files:
            code_structure = file_info.get('code_structure', {})
            imports = code_structure.get('imports', [])
            
            for imp in imports:
                if isinstance(imp, dict):
                    module = imp.get('module', '')
                    if module:
                        all_imports.append(module)
                        import_sources[module] += 1
        
        # 统计最常用的导入
        most_common_imports = Counter(all_imports).most_common(10)
        
        return {
            'total_imports': len(all_imports),
            'unique_imports': len(set(all_imports)),
            'most_common_imports': most_common_imports,
            'import_frequency': dict(import_sources)
        }
    
    def _generate_overall_analysis(self, language_analysis: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """生成总体分析"""
        total_files = sum(analysis['basic_stats']['file_count'] for analysis in language_analysis.values())
        total_lines = sum(analysis['basic_stats']['total_lines'] for analysis in language_analysis.values())
        total_size = sum(analysis['basic_stats']['total_size'] for analysis in language_analysis.values())
        
        # 计算总体质量指标
        total_issues = sum(analysis['quality']['total_issues'] for analysis in language_analysis.values())
        total_complexity = sum(analysis['complexity']['total_complexity'] for analysis in language_analysis.values())
        
        return {
            'total_files': total_files,
            'total_lines': total_lines,
            'total_size': total_size,
            'total_issues': total_issues,
            'total_complexity': total_complexity,
            'avg_issues_per_file': total_issues / total_files if total_files > 0 else 0,
            'avg_complexity_per_file': total_complexity / total_files if total_files > 0 else 0,
            'language_distribution': {
                lang: analysis['basic_stats']['file_count'] 
                for lang, analysis in language_analysis.items()
            }
        }

