"""
文件级别清洗器 - 基于文件指标的清洗
"""

import re
import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Generator
import logging

logger = logging.getLogger(__name__)


class FileMetricsCleaner:
    """文件级别清洗器，基于文件指标进行清洗"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.file_metrics_config = config.get('file_metrics_cleaning', {})
        self.thresholds = self.file_metrics_config.get('thresholds', {})
        
        # 默认阈值配置
        self.default_thresholds = {
            'max_file_size': self.thresholds.get('max_file_size', 1024 * 1024),  # 1MB
            'max_line_count': self.thresholds.get('max_line_count', 10000),
            'max_line_length': self.thresholds.get('max_line_length', 500),
            'min_comment_percentage': self.thresholds.get('min_comment_percentage', 0),
            'max_comment_percentage': self.thresholds.get('max_comment_percentage', 100),
            'max_digit_percentage': self.thresholds.get('max_digit_percentage', 50),
            'max_hex_percentage': self.thresholds.get('max_hex_percentage', 30),
            'max_average_line_length': self.thresholds.get('max_average_line_length', 200)
        }
    
    def clean_by_metrics(self, repo_path: Path, repo_name: str) -> Dict[str, Any]:
        """基于文件指标清洗代码仓库"""
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
            'total_files': 0,
            'cleaned_files': 0,
            'removed_files': 0,
            'ignored_files': 0,
            'metrics_summary': {},
            'errors': [],
            'backup_path': str(backup_path) if self.backup_enabled else None
        }
        
        try:
            # 分析所有文件
            file_metrics_list = []
            detailed_violations = []  # 详细违规信息
            
            for file_path in self._get_source_files(repo_path):
                try:
                    metrics = self._calculate_file_metrics(file_path)
                    if metrics:
                        rule_violations = self._get_rule_violations(metrics)
                        should_clean = len(rule_violations['clean_rules']) > 0
                        should_remove = len(rule_violations['remove_rules']) > 0
                        
                        file_info = {
                            'path': file_path,
                            'metrics': metrics,
                            'rule_violations': rule_violations,
                            'should_clean': should_clean,
                            'should_remove': should_remove
                        }
                        
                        file_metrics_list.append(file_info)
                        results['total_files'] += 1
                        
                        # 记录详细违规信息
                        if rule_violations['all_violations']:
                            detailed_violations.append({
                                'file': str(file_path.relative_to(repo_path)),
                                'violations': rule_violations['all_violations'],
                                'action': 'remove' if should_remove else 'clean' if should_clean else 'ignore'
                            })
                            
                except Exception as e:
                    logger.error(f"分析文件失败 {file_path}: {e}")
                    results['errors'].append(f"分析文件失败 {file_path}: {e}")
            
            # 添加详细违规信息到结果
            results['detailed_violations'] = detailed_violations
            
            # 执行清洗
            for file_info in file_metrics_list:
                try:
                    if file_info['should_remove']:
                        # 删除不符合指标的文件
                        file_info['path'].unlink()
                        results['removed_files'] += 1
                        logger.info(f"删除文件: {file_info['path']}")
                    elif file_info['should_clean']:
                        # 清洗文件
                        self._clean_file_by_metrics(file_info['path'], file_info['metrics'])
                        results['cleaned_files'] += 1
                        logger.info(f"清洗文件: {file_info['path']}")
                    else:
                        results['ignored_files'] += 1
                except Exception as e:
                    logger.error(f"处理文件失败 {file_info['path']}: {e}")
                    results['errors'].append(f"处理文件失败 {file_info['path']}: {e}")
            
            # 生成指标摘要
            results['metrics_summary'] = self._generate_metrics_summary(file_metrics_list)
            
            logger.info(f"文件指标清洗完成: {results}")
            return results
            
        except Exception as e:
            logger.error(f"文件指标清洗失败: {e}")
            results['errors'].append(str(e))
            return results
    
    
    def _get_source_files(self, repo_path: Path) -> Generator[Path, None, None]:
        """获取源代码文件"""
        # 支持的语言文件扩展名
        source_extensions = {
            '.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.go', '.rs',
            '.php', '.rb', '.swift', '.kt', '.cs', '.scala', '.r', '.m',
            '.sh', '.sql', '.html', '.css', '.xml', '.json', '.yaml', '.yml',
            '.md', '.txt', '.vue', '.jsx', '.tsx', '.svelte'
        }
        
        # 排除的目录
        exclude_dirs = {'.git', '__pycache__', 'node_modules', '.venv', 'venv', 
                       'build', 'dist', 'target', '.idea', '.vscode', '.DS_Store'}
        
        for root, dirs, files in os.walk(repo_path):
            root_path = Path(root)
            
            # 过滤目录
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            # 过滤文件
            for file_name in files:
                file_path = root_path / file_name
                if file_path.suffix.lower() in source_extensions:
                    yield file_path
    
    def _get_rule_violations(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """获取规则违规详情"""
        violations = {
            'clean_rules': [],  # 需要清洗的规则
            'remove_rules': [],  # 需要删除的规则
            'all_violations': []  # 所有违规
        }
        
        # 检查清洗规则
        if metrics['max_line_length'] > self.default_thresholds['max_line_length']:
            violations['clean_rules'].append({
                'rule': 'max_line_length',
                'threshold': self.default_thresholds['max_line_length'],
                'actual': metrics['max_line_length'],
                'severity': 'high' if metrics['max_line_length'] > self.default_thresholds['max_line_length'] * 1.5 else 'medium'
            })
        
        if metrics['file_size'] > self.default_thresholds['max_file_size']:
            violations['clean_rules'].append({
                'rule': 'max_file_size',
                'threshold': self.default_thresholds['max_file_size'],
                'actual': metrics['file_size'],
                'severity': 'high' if metrics['file_size'] > self.default_thresholds['max_file_size'] * 2 else 'medium'
            })
        
        if metrics['line_count'] > self.default_thresholds['max_line_count']:
            violations['clean_rules'].append({
                'rule': 'max_line_count',
                'threshold': self.default_thresholds['max_line_count'],
                'actual': metrics['line_count'],
                'severity': 'high' if metrics['line_count'] > self.default_thresholds['max_line_count'] * 1.5 else 'medium'
            })
        
        # 检查删除规则
        if metrics['comment_percentage'] < self.default_thresholds['min_comment_percentage']:
            violations['remove_rules'].append({
                'rule': 'min_comment_percentage',
                'threshold': self.default_thresholds['min_comment_percentage'],
                'actual': metrics['comment_percentage'],
                'severity': 'critical'
            })
        elif metrics['comment_percentage'] > self.default_thresholds['max_comment_percentage']:
            violations['remove_rules'].append({
                'rule': 'max_comment_percentage',
                'threshold': self.default_thresholds['max_comment_percentage'],
                'actual': metrics['comment_percentage'],
                'severity': 'medium'
            })
        
        if metrics['digit_percentage'] > self.default_thresholds['max_digit_percentage']:
            violations['remove_rules'].append({
                'rule': 'max_digit_percentage',
                'threshold': self.default_thresholds['max_digit_percentage'],
                'actual': metrics['digit_percentage'],
                'severity': 'high'
            })
        
        if metrics['hex_percentage'] > self.default_thresholds['max_hex_percentage']:
            violations['remove_rules'].append({
                'rule': 'max_hex_percentage',
                'threshold': self.default_thresholds['max_hex_percentage'],
                'actual': metrics['hex_percentage'],
                'severity': 'medium'
            })
        
        if metrics['average_line_length'] > self.default_thresholds['max_average_line_length']:
            violations['remove_rules'].append({
                'rule': 'max_average_line_length',
                'threshold': self.default_thresholds['max_average_line_length'],
                'actual': metrics['average_line_length'],
                'severity': 'medium'
            })
        
        # 合并所有违规
        violations['all_violations'] = violations['clean_rules'] + violations['remove_rules']
        
        return violations

    def _calculate_file_metrics(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """计算文件指标"""
        try:
            # 文件大小
            file_size = file_path.stat().st_size
            
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # 基础指标
            lines = content.splitlines()
            line_count = len(lines)
            
            if line_count == 0:
                return None
            
            # 行长度指标
            line_lengths = [len(line) for line in lines]
            max_line_length = max(line_lengths) if line_lengths else 0
            avg_line_length = sum(line_lengths) / len(line_lengths)
            
            # 注释分析（改进版）
            comment_lines = self._count_comment_lines(lines, file_path.suffix)
            
            # 计算两种注释百分比：
            # 1. 基于总行数（包含空行）- 传统方式
            comment_percentage_by_line = (comment_lines / line_count) * 100 if line_count > 0 else 0
            
            # 2. 基于有效行数（不包含空行）- 更准确的代码质量指标
            effective_lines = sum(1 for line in lines if line.strip())  # 非空行数
            comment_percentage_by_effective = (comment_lines / effective_lines) * 100 if effective_lines > 0 else 0
            
            # 使用基于有效行数的百分比作为主要指标（更合理）
            comment_percentage = comment_percentage_by_effective
            
            # 数字和十六进制分析
            total_chars = len(content)
            digit_count = sum(1 for char in content if char.isdigit())
            hex_pattern = re.compile(r'0x[0-9a-fA-F]+|[0-9a-fA-F]{4,}')
            hex_count = len(hex_pattern.findall(content))
            
            digit_percentage = (digit_count / total_chars) * 100 if total_chars > 0 else 0
            hex_percentage = (hex_count / total_chars) * 100 if total_chars > 0 else 0
            
            return {
                'file_size': file_size,
                'line_count': line_count,
                'effective_lines': effective_lines,  # 新增：有效行数
                'max_line_length': max_line_length,
                'average_line_length': avg_line_length,
                'comment_percentage': comment_percentage,
                'comment_percentage_by_line': comment_percentage_by_line,  # 新增：基于总行数
                'comment_percentage_by_effective': comment_percentage_by_effective,  # 新增：基于有效行数
                'digit_percentage': digit_percentage,
                'hex_percentage': hex_percentage,
                'comment_lines': comment_lines,
                'total_chars': total_chars
            }
            
        except Exception as e:
            logger.error(f"计算文件指标失败 {file_path}: {e}")
            return None
    
    def _count_comment_lines(self, lines: List[str], file_extension: str) -> int:
        """计算注释行数（改进版）
        
        主要改进：
        1. 区分Python文档字符串和普通多行字符串
        2. 文档字符串不计入注释统计
        3. 正确处理行内注释
        4. 空行不计入统计
        
        文档字符串识别规则：
        - 模块级文档字符串（文件开头）
        - 函数/类定义后的文档字符串
        - 同一行定义+文档字符串
        """
        comment_lines = 0
        in_docstring = False  # 改为跟踪文档字符串状态
        docstring_quotes = None  # 记录当前文档字符串使用的引号类型
        
        # 不同语言的注释模式（扩展版）
        comment_patterns = {
            '.py': {'single': '#', 'docstring': True},  # Python特殊标记
            '.js': {'single': '//', 'block_start': '/*', 'block_end': '*/'},
            '.ts': {'single': '//', 'block_start': '/*', 'block_end': '*/'},
            '.jsx': {'single': '//', 'block_start': '/*', 'block_end': '*/'},
            '.tsx': {'single': '//', 'block_start': '/*', 'block_end': '*/'},
            '.java': {'single': '//', 'block_start': '/*', 'block_end': '*/'},
            '.cpp': {'single': '//', 'block_start': '/*', 'block_end': '*/'},
            '.c': {'single': '//', 'block_start': '/*', 'block_end': '*/'},
            '.h': {'single': '//', 'block_start': '/*', 'block_end': '*/'},
            '.go': {'single': '//', 'block_start': '/*', 'block_end': '*/'},
            '.rs': {'single': '//', 'block_start': '/*', 'block_end': '*/'},
            '.php': {'single': '//', 'block_start': '/*', 'block_end': '*/'},
            '.rb': {'single': '#', 'block_start': '=begin', 'block_end': '=end'},
            '.swift': {'single': '//', 'block_start': '/*', 'block_end': '*/'},
            '.kt': {'single': '//', 'block_start': '/*', 'block_end': '*/'},
            '.cs': {'single': '//', 'block_start': '/*', 'block_end': '*/'},
            '.scala': {'single': '//', 'block_start': '/*', 'block_end': '*/'},
            '.r': {'single': '#', 'block_start': None, 'block_end': None},
            '.sh': {'single': '#', 'block_start': None, 'block_end': None},
            '.sql': {'single': '--', 'block_start': '/*', 'block_end': '*/'},
            '.html': {'single': None, 'block_start': '<!--', 'block_end': '-->'},
            '.css': {'single': None, 'block_start': '/*', 'block_end': '*/'},
            '.xml': {'single': None, 'block_start': '<!--', 'block_end': '-->'},
            '.json': {'single': None, 'block_start': None, 'block_end': None},
            '.yaml': {'single': '#', 'block_start': None, 'block_end': None},
            '.yml': {'single': '#', 'block_start': None, 'block_end': None},
            '.vue': {'single': '//', 'block_start': '/*', 'block_end': '*/'},
            '.svelte': {'single': '//', 'block_start': '/*', 'block_end': '*/'},
        }
        
        patterns = comment_patterns.get(file_extension, {'single': '#', 'block_start': None, 'block_end': None})
        
        # Python特殊处理：区分文档字符串和注释
        if file_extension == '.py' and patterns.get('docstring'):
            return self._count_python_comment_lines(lines, patterns)
        
        # 其他语言使用原有逻辑
        return self._count_general_comment_lines(lines, patterns)
    
    def _count_python_comment_lines(self, lines: List[str], patterns: Dict[str, Any]) -> int:
        """Python专用：区分文档字符串和注释"""
        comment_lines = 0
        in_docstring = False
        docstring_quotes = None
        
        for i, line in enumerate(lines):
            original_line = line
            line = line.strip()
            
            # 跳过空行（重要：空行不计入注释统计）
            if not line:
                continue
            
            # 处理文档字符串状态
            if in_docstring:
                # 检查文档字符串结束
                if docstring_quotes and docstring_quotes in line:
                    in_docstring = False
                    docstring_quotes = None
                # 文档字符串行是注释，计入统计
                comment_lines += 1
                continue
            
            # 检查文档字符串开始
            if '"""' in line or "'''" in line:
                quotes = '"""' if '"""' in line else "'''"
                
                # 同一行的文档字符串
                if line.count(quotes) == 2:
                    # 检查是否是文档字符串
                    if self._is_likely_docstring(lines, i, quotes):
                        comment_lines += 1  # 文档字符串是注释，计入统计
                        continue
                    else:
                        # 普通的多行字符串（变量赋值等），不是注释
                        continue
                else:
                    # 开始多行文档字符串
                    if self._is_likely_docstring(lines, i, quotes):
                        in_docstring = True
                        docstring_quotes = quotes
                        comment_lines += 1  # 文档字符串开始行是注释
                        continue
                    else:
                        # 普通的多行字符串开始（变量赋值等），不是注释
                        continue
            
            # 检测行内注释
            if patterns['single'] in original_line:
                # 纯注释行（以注释符号开头）
                if original_line.strip().startswith(patterns['single']):
                    comment_lines += 1
                    continue
                
                # 行内注释（代码 + 注释）
                parts = original_line.split(patterns['single'], 1)
                code_part = parts[0].strip()
                
                if code_part:  # 有代码部分
                    comment_lines += 1
                    continue
                else:  # 只有注释部分
                    comment_lines += 1
                    continue
            
            # 如果没有检测到注释，则认为是纯代码行
            continue
        
        return comment_lines
    
    def _is_likely_docstring(self, lines: List[str], current_line_idx: int, quotes: str) -> bool:
        """判断是否是文档字符串
        
        文档字符串的典型特征：
        1. 模块级文档字符串（文件开头）
        2. 函数/类定义后的第一行
        3. 同一行的定义+文档字符串
        """
        current_line = lines[current_line_idx].strip()
        
        # 1. 模块级文档字符串（文件开头）
        if current_line_idx <= 2:  # 前几行可能是模块文档字符串
            return True
        
        # 2. 检查前一行是否是函数/类定义
        if current_line_idx > 0:
            prev_line = lines[current_line_idx - 1].strip()
            # 检查是否是函数或类定义
            if (prev_line.endswith(':') and 
                ('def ' in prev_line or 'class ' in prev_line)):
                return True
        
        # 3. 检查是否是同一行的定义+文档字符串
        if ('def ' in current_line or 'class ' in current_line) and quotes in current_line:
            return True
        
        # 4. 检查是否在import语句之后（模块文档字符串的常见位置）
        if current_line_idx > 0:
            # 向前查找几行，看是否有import语句且没有函数/类定义
            lookback_range = range(max(0, current_line_idx-5), current_line_idx)
            has_import = False
            has_definition = False
            
            for i in lookback_range:
                line = lines[i].strip()
                if line.startswith('import ') or line.startswith('from '):
                    has_import = True
                if line.endswith(':') and ('def ' in line or 'class ' in line):
                    has_definition = True
            
            if has_import and not has_definition:
                return True
        
        # 5. 检查是否是shebang行后的文档字符串
        if current_line_idx == 1:  # 第二行
            first_line = lines[0].strip()
            if first_line.startswith('#!'):
                return True
        
        return False
    
    def _count_general_comment_lines(self, lines: List[str], patterns: Dict[str, Any]) -> int:
        """通用语言的注释计算"""
        comment_lines = 0
        in_block_comment = False
        
        for line in lines:
            original_line = line
            line = line.strip()
            
            # 跳过空行（重要：空行不计入注释统计）
            if not line:
                continue
            
            # 处理块注释
            if in_block_comment:
                comment_lines += 1
                if patterns['block_end'] and patterns['block_end'] in line:
                    in_block_comment = False
                continue
            
            # 检查块注释开始
            if patterns['block_start'] and patterns['block_start'] in line:
                # 同一行的块注释（开始和结束在同一行）
                if patterns['block_end'] and patterns['block_end'] in line and patterns['block_start'] != patterns['block_end']:
                    comment_lines += 1
                    continue
                else:
                    # 开始块注释
                    in_block_comment = True
                    comment_lines += 1
                    continue
            
            # 检测行内注释
            if patterns['single']:
                # 纯注释行（以注释符号开头）
                if original_line.strip().startswith(patterns['single']):
                    comment_lines += 1
                    continue
                
                # 行内注释（代码 + 注释）
                if patterns['single'] in original_line:
                    # 分离代码和注释部分
                    parts = original_line.split(patterns['single'], 1)
                    code_part = parts[0].strip()
                    
                    if code_part:  # 有代码部分
                        comment_lines += 1
                        continue
                    else:  # 只有注释部分
                        comment_lines += 1
                        continue
            
            # 如果没有检测到注释，则认为是纯代码行
            continue
        
        return comment_lines
    
    def _should_clean_by_metrics(self, metrics: Dict[str, Any]) -> bool:
        """判断是否应该清洗文件"""
        # 检查是否需要清洗（例如：过长的行）
        if metrics['max_line_length'] > self.default_thresholds['max_line_length']:
            return True
        
        # 检查文件是否过大
        if metrics['file_size'] > self.default_thresholds['max_file_size']:
            return True
        
        # 检查行数是否过多
        if metrics['line_count'] > self.default_thresholds['max_line_count']:
            return True
        
        return False
    
    def _should_remove_by_metrics(self, metrics: Dict[str, Any]) -> bool:
        """判断是否应该删除文件"""
        # 检查注释比例
        if not (self.default_thresholds['min_comment_percentage'] <= metrics['comment_percentage'] <= self.default_thresholds['max_comment_percentage']):
            return True
        
        # 检查数字比例
        if metrics['digit_percentage'] > self.default_thresholds['max_digit_percentage']:
            return True
        
        # 检查十六进制比例
        if metrics['hex_percentage'] > self.default_thresholds['max_hex_percentage']:
            return True
        
        # 检查平均行长度
        if metrics['average_line_length'] > self.default_thresholds['max_average_line_length']:
            return True
        
        return False
    
    def _clean_file_by_metrics(self, file_path: Path, metrics: Dict[str, Any]):
        """根据指标清洗文件"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            lines = content.splitlines()
            cleaned_lines = []
            
            # 清洗过长的行
            for line in lines:
                if len(line) > self.default_thresholds['max_line_length']:
                    # 尝试在合理位置断行
                    max_len = self.default_thresholds['max_line_length']
                    while len(line) > max_len:
                        # 查找最近的空格或标点符号
                        break_point = max_len
                        for i in range(max_len - 1, max(0, max_len - 50), -1):
                            if line[i] in ' \t,;:.!?':
                                break_point = i + 1
                                break
                        
                        cleaned_lines.append(line[:break_point].rstrip())
                        line = line[break_point:].lstrip()
                    cleaned_lines.append(line)
                else:
                    cleaned_lines.append(line)
            
            # 写回清洗后的内容
            cleaned_content = '\n'.join(cleaned_lines)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(cleaned_content)
            
            logger.info(f"已清洗文件: {file_path}")
            
        except Exception as e:
            logger.error(f"清洗文件失败 {file_path}: {e}")
            raise
    
    def analyze_metrics(self, repo_path: Path, repo_name: str) -> Dict[str, Any]:
        """仅分析文件指标，不执行清洗操作"""
        if not repo_path.exists():
            logger.error(f"仓库路径不存在: {repo_path}")
            return {}
        
        results = {
            'total_files': 0,
            'cleaned_files': 0,
            'removed_files': 0,
            'ignored_files': 0,
            'metrics_summary': {},
            'errors': [],
            'backup_path': None
        }
        
        try:
            # 分析所有文件
            file_metrics_list = []
            detailed_violations = []  # 详细违规信息
            
            for file_path in self._get_source_files(repo_path):
                try:
                    metrics = self._calculate_file_metrics(file_path)
                    if metrics:
                        rule_violations = self._get_rule_violations(metrics)
                        should_clean = len(rule_violations['clean_rules']) > 0
                        should_remove = len(rule_violations['remove_rules']) > 0
                        
                        file_info = {
                            'path': file_path,
                            'metrics': metrics,
                            'rule_violations': rule_violations,
                            'should_clean': should_clean,
                            'should_remove': should_remove
                        }
                        
                        file_metrics_list.append(file_info)
                        results['total_files'] += 1
                        
                        # 记录详细违规信息
                        if rule_violations['all_violations']:
                            detailed_violations.append({
                                'file': str(file_path.relative_to(repo_path)),
                                'violations': rule_violations['all_violations'],
                                'action': 'remove' if should_remove else 'clean' if should_clean else 'ignore'
                            })
                        
                        # 统计需要清洗/删除的文件
                        if should_remove:
                            results['removed_files'] += 1
                        elif should_clean:
                            results['cleaned_files'] += 1
                        else:
                            results['ignored_files'] += 1
                            
                except Exception as e:
                    logger.error(f"分析文件失败 {file_path}: {e}")
                    results['errors'].append(f"分析文件失败 {file_path}: {e}")
            
            # 添加详细违规信息到结果
            results['detailed_violations'] = detailed_violations
            
            # 生成指标摘要
            results['metrics_summary'] = self._generate_metrics_summary(file_metrics_list)
            
            logger.info(f"文件指标分析完成: {results}")
            return results
            
        except Exception as e:
            logger.error(f"文件指标分析失败: {e}")
            results['errors'].append(str(e))
            return results

    def _generate_metrics_summary(self, file_metrics_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成指标摘要"""
        if not file_metrics_list:
            return {}
        
        total_files = len(file_metrics_list)
        
        # 计算各项指标的平均值
        avg_file_size = sum(item['metrics']['file_size'] for item in file_metrics_list) / total_files
        avg_line_count = sum(item['metrics']['line_count'] for item in file_metrics_list) / total_files
        avg_max_line_length = sum(item['metrics']['max_line_length'] for item in file_metrics_list) / total_files
        avg_comment_percentage = sum(item['metrics']['comment_percentage'] for item in file_metrics_list) / total_files
        avg_digit_percentage = sum(item['metrics']['digit_percentage'] for item in file_metrics_list) / total_files
        avg_hex_percentage = sum(item['metrics']['hex_percentage'] for item in file_metrics_list) / total_files
        avg_average_line_length = sum(item['metrics']['average_line_length'] for item in file_metrics_list) / total_files
        
        # 统计超出阈值的文件数量
        oversized_files = sum(1 for item in file_metrics_list if item['metrics']['file_size'] > self.default_thresholds['max_file_size'])
        long_line_files = sum(1 for item in file_metrics_list if item['metrics']['max_line_length'] > self.default_thresholds['max_line_length'])
        high_line_count_files = sum(1 for item in file_metrics_list if item['metrics']['line_count'] > self.default_thresholds['max_line_count'])
        high_digit_files = sum(1 for item in file_metrics_list if item['metrics']['digit_percentage'] > self.default_thresholds['max_digit_percentage'])
        high_hex_files = sum(1 for item in file_metrics_list if item['metrics']['hex_percentage'] > self.default_thresholds['max_hex_percentage'])
        
        return {
            'total_files': total_files,
            'average_metrics': {
                'file_size': avg_file_size,
                'line_count': avg_line_count,
                'max_line_length': avg_max_line_length,
                'comment_percentage': avg_comment_percentage,
                'digit_percentage': avg_digit_percentage,
                'hex_percentage': avg_hex_percentage,
                'average_line_length': avg_average_line_length
            },
            'threshold_violations': {
                'oversized_files': oversized_files,
                'long_line_files': long_line_files,
                'high_line_count_files': high_line_count_files,
                'high_digit_files': high_digit_files,
                'high_hex_files': high_hex_files
            }
        }
    
    def clean_jsonl_by_metrics(self, input_file: Path, output_file: Path, repo_name: str) -> Dict[str, Any]:
        """基于文件指标清洗JSONL文件"""
        if not input_file.exists():
            logger.error(f"输入文件不存在: {input_file}")
            return {}
        
        results = {
            'total_files': 0,
            'cleaned_files': 0,
            'removed_files': 0,
            'ignored_files': 0,
            'metrics_summary': {},
            'errors': []
        }
        
        try:
            # 读取JSONL文件
            import json
            records = []
            with open(input_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        records.append(json.loads(line))
            
            results['total_files'] = len(records)
            
            # 分析所有记录
            file_metrics_list = []
            detailed_violations = []
            
            for record in records:
                try:
                    if record.get('is_binary', False):
                        # 跳过二进制文件
                        results['ignored_files'] += 1
                        continue
                    
                    content = record.get('content', '')
                    if not content:
                        results['ignored_files'] += 1
                        continue
                    
                    # 计算文件指标
                    metrics = self._calculate_content_metrics(content)
                    if not metrics:
                        results['ignored_files'] += 1
                        continue
                    
                    rule_violations = self._get_rule_violations(metrics)
                    should_clean = len(rule_violations['clean_rules']) > 0
                    should_remove = len(rule_violations['remove_rules']) > 0
                    
                    file_info = {
                        'record': record,
                        'metrics': metrics,
                        'rule_violations': rule_violations,
                        'should_clean': should_clean,
                        'should_remove': should_remove
                    }
                    
                    file_metrics_list.append(file_info)
                    
                    # 记录详细违规信息
                    if rule_violations['all_violations']:
                        detailed_violations.append({
                            'file': record.get('path', record.get('id', 'unknown')),
                            'violations': rule_violations['all_violations'],
                            'action': 'remove' if should_remove else 'clean' if should_clean else 'ignore'
                        })
                    
                    # 统计需要清洗/删除的文件
                    if should_remove:
                        results['removed_files'] += 1
                    elif should_clean:
                        results['cleaned_files'] += 1
                    else:
                        results['ignored_files'] += 1
                        
                except Exception as e:
                    logger.error(f"分析记录失败: {e}")
                    results['errors'].append(f"分析记录失败: {e}")
            
            # 添加详细违规信息到结果
            results['detailed_violations'] = detailed_violations
            
            # 生成指标摘要
            results['metrics_summary'] = self._generate_metrics_summary(file_metrics_list)
            
            # 处理记录
            cleaned_records = []
            for file_info in file_metrics_list:
                try:
                    if file_info['should_remove']:
                        # 跳过不符合指标的文件
                        continue
                    elif file_info['should_clean']:
                        # 清洗文件内容
                        cleaned_content = self._clean_content_by_metrics(file_info['record']['content'], file_info['metrics'])
                        file_info['record']['content'] = cleaned_content
                        file_info['record']['metrics_cleaned'] = True
                        cleaned_records.append(file_info['record'])
                    else:
                        cleaned_records.append(file_info['record'])
                except Exception as e:
                    logger.error(f"处理记录失败: {e}")
                    results['errors'].append(f"处理记录失败: {e}")
            
            # 写入清洗后的文件
            with open(output_file, 'w', encoding='utf-8') as f:
                for record in cleaned_records:
                    f.write(json.dumps(record, ensure_ascii=False, default=str) + '\n')
            
            logger.info(f"JSONL文件指标清洗完成: {results}")
            return results
            
        except Exception as e:
            logger.error(f"JSONL文件指标清洗失败: {e}")
            results['errors'].append(str(e))
            return results
    
    def analyze_jsonl_metrics(self, input_file: Path, repo_name: str) -> Dict[str, Any]:
        """仅分析JSONL文件指标，不执行清洗操作"""
        if not input_file.exists():
            logger.error(f"输入文件不存在: {input_file}")
            return {}
        
        results = {
            'total_files': 0,
            'cleaned_files': 0,
            'removed_files': 0,
            'ignored_files': 0,
            'metrics_summary': {},
            'errors': []
        }
        
        try:
            # 读取JSONL文件
            import json
            records = []
            with open(input_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        records.append(json.loads(line))
            
            results['total_files'] = len(records)
            
            # 分析所有记录
            file_metrics_list = []
            detailed_violations = []
            
            for record in records:
                try:
                    if record.get('is_binary', False):
                        # 跳过二进制文件
                        results['ignored_files'] += 1
                        continue
                    
                    content = record.get('content', '')
                    if not content:
                        results['ignored_files'] += 1
                        continue
                    
                    # 计算文件指标
                    metrics = self._calculate_content_metrics(content)
                    if not metrics:
                        results['ignored_files'] += 1
                        continue
                    
                    rule_violations = self._get_rule_violations(metrics)
                    should_clean = len(rule_violations['clean_rules']) > 0
                    should_remove = len(rule_violations['remove_rules']) > 0
                    
                    file_info = {
                        'record': record,
                        'metrics': metrics,
                        'rule_violations': rule_violations,
                        'should_clean': should_clean,
                        'should_remove': should_remove
                    }
                    
                    file_metrics_list.append(file_info)
                    
                    # 记录详细违规信息
                    if rule_violations['all_violations']:
                        detailed_violations.append({
                            'file': record.get('path', record.get('id', 'unknown')),
                            'violations': rule_violations['all_violations'],
                            'action': 'remove' if should_remove else 'clean' if should_clean else 'ignore'
                        })
                    
                    # 统计需要清洗/删除的文件
                    if should_remove:
                        results['removed_files'] += 1
                    elif should_clean:
                        results['cleaned_files'] += 1
                    else:
                        results['ignored_files'] += 1
                        
                except Exception as e:
                    logger.error(f"分析记录失败: {e}")
                    results['errors'].append(f"分析记录失败: {e}")
            
            # 添加详细违规信息到结果
            results['detailed_violations'] = detailed_violations
            
            # 生成指标摘要
            results['metrics_summary'] = self._generate_metrics_summary(file_metrics_list)
            
            logger.info(f"JSONL文件指标分析完成: {results}")
            return results
            
        except Exception as e:
            logger.error(f"JSONL文件指标分析失败: {e}")
            results['errors'].append(str(e))
            return results
    
    def _calculate_content_metrics(self, content: str) -> Optional[Dict[str, Any]]:
        """计算内容指标（基于字符串内容而不是文件）"""
        try:
            # 基础指标
            lines = content.splitlines()
            line_count = len(lines)
            
            if line_count == 0:
                return None
            
            # 行长度指标
            line_lengths = [len(line) for line in lines]
            max_line_length = max(line_lengths) if line_lengths else 0
            avg_line_length = sum(line_lengths) / len(line_lengths)
            
            # 注释分析（简化版，基于内容而不是文件扩展名）
            comment_lines = self._count_content_comment_lines(lines)
            
            # 计算注释百分比
            effective_lines = sum(1 for line in lines if line.strip())  # 非空行数
            comment_percentage = (comment_lines / effective_lines) * 100 if effective_lines > 0 else 0
            
            # 数字和十六进制分析
            total_chars = len(content)
            digit_count = sum(1 for char in content if char.isdigit())
            hex_pattern = re.compile(r'0x[0-9a-fA-F]+|[0-9a-fA-F]{4,}')
            hex_count = len(hex_pattern.findall(content))
            
            digit_percentage = (digit_count / total_chars) * 100 if total_chars > 0 else 0
            hex_percentage = (hex_count / total_chars) * 100 if total_chars > 0 else 0
            
            return {
                'file_size': total_chars,
                'line_count': line_count,
                'effective_lines': effective_lines,
                'max_line_length': max_line_length,
                'average_line_length': avg_line_length,
                'comment_percentage': comment_percentage,
                'digit_percentage': digit_percentage,
                'hex_percentage': hex_percentage,
                'comment_lines': comment_lines,
                'total_chars': total_chars
            }
            
        except Exception as e:
            logger.error(f"计算内容指标失败: {e}")
            return None
    
    def _count_content_comment_lines(self, lines: List[str]) -> int:
        """计算内容注释行数（简化版）"""
        comment_lines = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 检查常见的注释模式
            if (line.startswith('#') or 
                line.startswith('//') or 
                line.startswith('/*') or 
                line.startswith('*') or
                line.startswith('<!--') or
                line.startswith('--')):
                comment_lines += 1
        
        return comment_lines
    
    def _clean_content_by_metrics(self, content: str, metrics: Dict[str, Any]) -> str:
        """根据指标清洗内容"""
        try:
            lines = content.splitlines()
            cleaned_lines = []
            
            # 清洗过长的行
            for line in lines:
                if len(line) > self.default_thresholds['max_line_length']:
                    # 尝试在合理位置断行
                    max_len = self.default_thresholds['max_line_length']
                    while len(line) > max_len:
                        # 查找最近的空格或标点符号
                        break_point = max_len
                        for i in range(max_len - 1, max(0, max_len - 50), -1):
                            if line[i] in ' \t,;:.!?':
                                break_point = i + 1
                                break
                        
                        cleaned_lines.append(line[:break_point].rstrip())
                        line = line[break_point:].lstrip()
                    cleaned_lines.append(line)
                else:
                    cleaned_lines.append(line)
            
            return '\n'.join(cleaned_lines)
            
        except Exception as e:
            logger.error(f"清洗内容失败: {e}")
            return content