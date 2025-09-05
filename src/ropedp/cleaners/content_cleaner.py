"""
内容清洗器
"""

import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class ContentCleaner:
    """内容清洗器，用于清理文件内容"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.cleaning_rules = config.get('cleaning', {})
    
    def clean_content(self, file_info: Dict[str, Any]) -> Dict[str, Any]:
        """清洗文件内容"""
        if file_info.get('is_binary', False):
            return file_info
        
        content = file_info.get('content', '')
        language = file_info.get('language', 'unknown')
        
        # 应用清洗规则
        cleaned_content = self._apply_cleaning_rules(content, language)
        
        # 更新文件信息
        cleaned_file_info = file_info.copy()
        cleaned_file_info['content'] = cleaned_content
        cleaned_file_info['original_content'] = content
        cleaned_file_info['cleaning_applied'] = self._get_applied_rules()
        
        # 计算清洗统计
        cleaned_file_info['cleaning_stats'] = self._calculate_cleaning_stats(content, cleaned_content)
        
        return cleaned_file_info
    
    def _apply_cleaning_rules(self, content: str, language: str) -> str:
        """应用清洗规则"""
        cleaned_content = content
        
        # 移除注释
        if self.cleaning_rules.get('remove_comments', False):
            cleaned_content = self._remove_comments(cleaned_content, language)
        
        # 移除空白行
        if self.cleaning_rules.get('remove_blank_lines', False):
            cleaned_content = self._remove_blank_lines(cleaned_content)
        
        # 标准化空白字符
        if self.cleaning_rules.get('normalize_whitespace', False):
            cleaned_content = self._normalize_whitespace(cleaned_content)
        
        # 移除导入语句
        if self.cleaning_rules.get('remove_imports', False):
            cleaned_content = self._remove_imports(cleaned_content, language)
        
        # 保留结构
        if self.cleaning_rules.get('preserve_structure', True):
            cleaned_content = self._preserve_structure(cleaned_content, language)
        
        return cleaned_content
    
    def _remove_comments(self, content: str, language: str) -> str:
        """移除注释"""
        if language == 'python':
            return self._remove_python_comments(content)
        elif language in ['javascript', 'typescript']:
            return self._remove_js_comments(content)
        elif language == 'java':
            return self._remove_java_comments(content)
        elif language in ['cpp', 'c']:
            return self._remove_cpp_comments(content)
        elif language == 'html':
            return self._remove_html_comments(content)
        elif language == 'css':
            return self._remove_css_comments(content)
        else:
            return self._remove_generic_comments(content)
    
    def _remove_python_comments(self, content: str) -> str:
        """移除Python注释"""
        lines = content.splitlines()
        cleaned_lines = []
        
        in_multiline_string = False
        string_delimiter = None
        
        for line in lines:
            cleaned_line = line
            
            # 处理多行字符串
            if not in_multiline_string:
                # 检查是否开始多行字符串
                for delimiter in ['"""', "'''"]:
                    if delimiter in line:
                        in_multiline_string = True
                        string_delimiter = delimiter
                        break
            else:
                # 检查是否结束多行字符串
                if string_delimiter in line:
                    in_multiline_string = False
                    string_delimiter = None
            
            # 如果不在多行字符串中，移除注释
            if not in_multiline_string:
                # 移除行内注释
                cleaned_line = re.sub(r'#.*$', '', cleaned_line)
            
            cleaned_lines.append(cleaned_line)
        
        return '\n'.join(cleaned_lines)
    
    def _remove_js_comments(self, content: str) -> str:
        """移除JavaScript/TypeScript注释"""
        # 移除单行注释
        content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
        
        # 移除多行注释
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        
        return content
    
    def _remove_java_comments(self, content: str) -> str:
        """移除Java注释"""
        # 移除单行注释
        content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
        
        # 移除多行注释
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        
        return content
    
    def _remove_cpp_comments(self, content: str) -> str:
        """移除C++/C注释"""
        # 移除单行注释
        content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
        
        # 移除多行注释
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        
        return content
    
    def _remove_html_comments(self, content: str) -> str:
        """移除HTML注释"""
        content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
        return content
    
    def _remove_css_comments(self, content: str) -> str:
        """移除CSS注释"""
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        return content
    
    def _remove_generic_comments(self, content: str) -> str:
        """移除通用注释"""
        # 移除以#开头的注释
        content = re.sub(r'^#.*$', '', content, flags=re.MULTILINE)
        
        # 移除以//开头的注释
        content = re.sub(r'^//.*$', '', content, flags=re.MULTILINE)
        
        return content
    
    def _remove_blank_lines(self, content: str) -> str:
        """移除空白行"""
        lines = content.splitlines()
        cleaned_lines = [line for line in lines if line.strip()]
        return '\n'.join(cleaned_lines)
    
    def _normalize_whitespace(self, content: str) -> str:
        """标准化空白字符"""
        # 将多个连续空白字符替换为单个空格
        content = re.sub(r'\s+', ' ', content)
        
        # 移除行首行尾空白
        lines = content.splitlines()
        cleaned_lines = [line.strip() for line in lines]
        
        return '\n'.join(cleaned_lines)
    
    def _remove_imports(self, content: str, language: str) -> str:
        """移除导入语句"""
        if language == 'python':
            return self._remove_python_imports(content)
        elif language in ['javascript', 'typescript']:
            return self._remove_js_imports(content)
        elif language == 'java':
            return self._remove_java_imports(content)
        elif language in ['cpp', 'c']:
            return self._remove_cpp_includes(content)
        else:
            return content
    
    def _remove_python_imports(self, content: str) -> str:
        """移除Python导入语句"""
        lines = content.splitlines()
        cleaned_lines = []
        
        for line in lines:
            stripped_line = line.strip()
            if not (stripped_line.startswith('import ') or stripped_line.startswith('from ')):
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def _remove_js_imports(self, content: str) -> str:
        """移除JavaScript/TypeScript导入语句"""
        lines = content.splitlines()
        cleaned_lines = []
        
        for line in lines:
            stripped_line = line.strip()
            if not (stripped_line.startswith('import ') or stripped_line.startswith('require(')):
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def _remove_java_imports(self, content: str) -> str:
        """移除Java导入语句"""
        lines = content.splitlines()
        cleaned_lines = []
        
        for line in lines:
            stripped_line = line.strip()
            if not stripped_line.startswith('import '):
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def _remove_cpp_includes(self, content: str) -> str:
        """移除C++/C包含语句"""
        lines = content.splitlines()
        cleaned_lines = []
        
        for line in lines:
            stripped_line = line.strip()
            if not stripped_line.startswith('#include'):
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def _preserve_structure(self, content: str, language: str) -> str:
        """保留代码结构"""
        # 确保函数、类等结构完整
        if language == 'python':
            return self._preserve_python_structure(content)
        elif language in ['javascript', 'typescript']:
            return self._preserve_js_structure(content)
        else:
            return content
    
    def _preserve_python_structure(self, content: str) -> str:
        """保留Python代码结构"""
        # 确保缩进正确
        lines = content.splitlines()
        cleaned_lines = []
        
        for line in lines:
            if line.strip():  # 非空行
                cleaned_lines.append(line)
            else:
                # 保留必要的空行（在函数、类定义后）
                if cleaned_lines and cleaned_lines[-1].strip().endswith(':'):
                    cleaned_lines.append('')
        
        return '\n'.join(cleaned_lines)
    
    def _preserve_js_structure(self, content: str) -> str:
        """保留JavaScript代码结构"""
        # 确保大括号匹配
        lines = content.splitlines()
        cleaned_lines = []
        
        for line in lines:
            if line.strip():  # 非空行
                cleaned_lines.append(line)
            else:
                # 保留必要的空行
                if cleaned_lines and cleaned_lines[-1].strip().endswith('{'):
                    cleaned_lines.append('')
        
        return '\n'.join(cleaned_lines)
    
    def _get_applied_rules(self) -> List[str]:
        """获取应用的清洗规则"""
        applied_rules = []
        
        if self.cleaning_rules.get('remove_comments', False):
            applied_rules.append('remove_comments')
        if self.cleaning_rules.get('remove_blank_lines', False):
            applied_rules.append('remove_blank_lines')
        if self.cleaning_rules.get('normalize_whitespace', False):
            applied_rules.append('normalize_whitespace')
        if self.cleaning_rules.get('remove_imports', False):
            applied_rules.append('remove_imports')
        if self.cleaning_rules.get('preserve_structure', True):
            applied_rules.append('preserve_structure')
        
        return applied_rules
    
    def _calculate_cleaning_stats(self, original_content: str, cleaned_content: str) -> Dict[str, Any]:
        """计算清洗统计信息"""
        original_lines = len(original_content.splitlines())
        cleaned_lines = len(cleaned_content.splitlines())
        
        original_chars = len(original_content)
        cleaned_chars = len(cleaned_content)
        
        return {
            'original_lines': original_lines,
            'cleaned_lines': cleaned_lines,
            'lines_removed': original_lines - cleaned_lines,
            'original_chars': original_chars,
            'cleaned_chars': cleaned_chars,
            'chars_removed': original_chars - cleaned_chars,
            'compression_ratio': cleaned_chars / original_chars if original_chars > 0 else 1.0
        }

