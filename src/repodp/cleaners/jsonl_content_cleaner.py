"""
JSONL内容清洗器 - 专门针对JSONL文件进行内容清洗和脱敏
"""

import re
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Set, Tuple
import logging
from datetime import datetime
from tqdm import tqdm

logger = logging.getLogger(__name__)


class JSONLContentCleaner:
    """JSONL内容清洗器，专门针对提取的JSONL数据进行内容清洗和脱敏"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.cleaning_config = config.get('jsonl_cleaning', {})
        
        # 敏感信息模式
        self.sensitive_patterns = self._compile_sensitive_patterns()
        
        # 无效注释模式
        self.invalid_comment_patterns = self._compile_invalid_patterns()
        
        # 版权相关模式
        self.copyright_patterns = self._compile_copyright_patterns()
        
        # 统计信息
        self.cleaning_stats = {
            'total_files': 0,
            'files_cleaned': 0,
            'comments_removed': 0,
            'comments_desensitized': 0,
            'sensitive_info_removed': 0
        }
    
    def _compile_sensitive_patterns(self) -> Dict[str, re.Pattern]:
        """编译敏感信息识别模式"""
        patterns = {
            # URL (优先处理，避免包含其他模式)
            'url': re.compile(r'https?://[^\s<>"{}|\\^`\[\]]+'),
            
            # 邮箱
            'email': re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            
            # 身份证号 (15或18位)
            'id_card': re.compile(r'\b\d{15}|\d{17}[\dXx]\b'),
            
            # 手机号 (11位，1开头)
            'phone': re.compile(r'(?<!\d)1[3-9]\d{9}(?!\d)|\b\d{3,4}[-\s]?\d{7,8}\b'),
            
            # IP地址
            'ip_address': re.compile(r'\b(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)(?:\.(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)){3}\b'),
            
            # 工号/员工ID (避免匹配普通数字)
            'employee_id': re.compile(r'\b(?:emp|employee|staff|worker|id)[-_:]?\d{3,}\b|\b[A-Z]{2,}\d{3,}\b', re.IGNORECASE),
            
            # 日期时间 (避免匹配4位数字的年份)
            'datetime': re.compile(r'\b(?:19|20)\d{2}[-/]\d{1,2}[-/]\d{1,2}|\b\d{1,2}[-/]\d{1,2}[-/](?:19|20)\d{2}|\b\d{1,2}:\d{2}:\d{2}\b'),
            
            # 人名 (中文2-4字，英文名字大写开头，避免匹配普通单词)
            'person_name': re.compile(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b|\b[\u4e00-\u9fa5]{2,4}\b(?![\u4e00-\u9fa5])'),
            
            # 公司/组织名 (常见后缀，避免过度匹配)
            'organization': re.compile(r'\b[A-Za-z][\w\s]*(?:Inc|Corp|Ltd|LLC|Company|Corporation|Limited|公司|有限公司|科技|软件)\b', re.IGNORECASE)
        }
        return patterns
    
    def _compile_invalid_patterns(self) -> List[re.Pattern]:
        """编译无效注释模式"""
        patterns = [
            # TODO/FIXME 等临时注释
            re.compile(r'(?i)\b(?:todo|fixme|hack|xxx|note:|warning:|attention:)\b.*$'),
            
            # 个人签名
            re.compile(r'(?i)\b(?:created?|written?|authored?|coded?)\s+(?:by|:)\s+\w+'),
            
            # 版本历史注释
            re.compile(r'(?i)\bversion\s*:?\s*[\d.]+.*$'),
            re.compile(r'(?i)\bv\d+\.\d+(?:\.\d+)?.*$'),
            
            # 过度详细的变更记录
            re.compile(r'(?i)\b(?:modified?|updated?|changed?)\s+(?:by|:)\s+\w+.*$'),
            re.compile(r'(?i)\b(?:date|time)\s*:?\s*\d+.*$')
        ]
        return patterns
    
    def _compile_copyright_patterns(self) -> List[re.Pattern]:
        """编译版权注释模式"""
        patterns = [
            # 版权声明 (保留结构，脱敏内容)
            re.compile(r'(?i)\bcopyright\s+[©\(c\)]?\s*(?:\d{4}\s*)?(?:\s*-\s*\d{4})?\s*([^\n]+)'),
            re.compile(r'(?i)©\s*(?:\d{4}\s*)?(?:\s*-\s*\d{4})?\s*([^\n]+)'),
            re.compile(r'(?i)all rights reserved.*?$'),
            
            # 许可证声明
            re.compile(r'(?i)licensed under\s+([^\n]+)'),
            re.compile(r'(?i)\bmit\s+license\b'),
            re.compile(r'(?i)\bapache\s+license\b'),
            re.compile(r'(?i)\bgpl\b.*$')
        ]
        return patterns
    
    def clean_jsonl_file(self, input_file: Path, output_file: Path) -> Dict[str, Any]:
        """清洗JSONL文件"""
        logger.info(f"开始清洗JSONL文件: {input_file}")
        
        self.cleaning_stats = {
            'total_files': 0,
            'files_cleaned': 0,
            'comments_removed': 0,
            'comments_desensitized': 0,
            'sensitive_info_removed': 0,
            'files_with_sensitive_info': 0
        }
        
        try:
            # 读取所有记录
            records = []
            with open(input_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        records.append(json.loads(line))
            
            self.cleaning_stats['total_files'] = len(records)
            
            # 清洗记录
            cleaned_records = []
            for record in tqdm(records, desc="清洗内容"):
                cleaned_record = self.clean_record(record)
                cleaned_records.append(cleaned_record)
            
            # 写入清洗后的文件
            with open(output_file, 'w', encoding='utf-8') as f:
                for record in cleaned_records:
                    f.write(json.dumps(record, ensure_ascii=False, default=str) + '\n')
            
            logger.info(f"清洗完成，输出文件: {output_file}")
            logger.info(f"统计信息: {self.cleaning_stats}")
            
            return {
                'success': True,
                'input_file': str(input_file),
                'output_file': str(output_file),
                'stats': self.cleaning_stats
            }
            
        except Exception as e:
            logger.error(f"清洗JSONL文件失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'input_file': str(input_file)
            }
    
    def clean_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """清洗单条记录"""
        if record.get('is_binary', False):
            return record
        
        content = record.get('content', '')
        language = record.get('language', 'unknown')
        
        if not content:
            return record
        
        original_content = content
        has_sensitive_info = False
        
        # 清洗注释
        content = self._clean_comments(content, language)
        
        # 脱敏处理（在非注释内容中也进行）
        content, found_sensitive = self._desensitize_content(content)
        if found_sensitive:
            has_sensitive_info = True
            self.cleaning_stats['sensitive_info_removed'] += found_sensitive
        
        # 检查是否有清洗操作
        if content != original_content:
            self.cleaning_stats['files_cleaned'] += 1
            if has_sensitive_info:
                self.cleaning_stats['files_with_sensitive_info'] += 1
        
        # 更新记录
        cleaned_record = record.copy()
        cleaned_record['content'] = content
        cleaned_record['original_content'] = original_content
        cleaned_record['has_sensitive_info'] = has_sensitive_info
        cleaned_record['cleaning_applied'] = True
        
        return cleaned_record
    
    def _clean_comments(self, content: str, language: str) -> str:
        """清洗注释"""
        if language == 'python':
            return self._clean_python_comments(content)
        elif language in ['javascript', 'typescript']:
            return self._clean_js_comments(content)
        elif language == 'java':
            return self._clean_java_comments(content)
        elif language in ['cpp', 'c']:
            return self._clean_cpp_comments(content)
        elif language == 'html':
            return self._clean_html_comments(content)
        elif language == 'css':
            return self._clean_css_comments(content)
        else:
            return self._clean_generic_comments(content)
    
    def _clean_python_comments(self, content: str) -> str:
        """清洗Python注释"""
        lines = content.splitlines()
        cleaned_lines = []
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # 检查多行字符串开始（可能是文档字符串）
            if '"""' in line or "'''" in line:
                delimiter = '"""' if '"""' in line else "'''"
                
                # 检查是否是单行多行字符串
                if line.count(delimiter) == 2:
                    # 单行文档字符串，检查是否需要脱敏
                    if self._should_desensitize_docstring(line):
                        cleaned_line = self._desensitize_docstring(line, delimiter)
                        cleaned_lines.append(cleaned_line)
                        self.cleaning_stats['comments_desensitized'] += 1
                    else:
                        cleaned_lines.append(line)
                    i += 1
                    continue
                
                # 多行文档字符串
                docstring_lines = [line]
                start_line = i
                i += 1
                
                # 收集完整的多行字符串
                while i < len(lines) and delimiter not in lines[i]:
                    docstring_lines.append(lines[i])
                    i += 1
                
                if i < len(lines):
                    docstring_lines.append(lines[i])  # 结束行
                
                # 处理文档字符串
                full_docstring = '\n'.join(docstring_lines)
                if self._should_desensitize_docstring(full_docstring):
                    cleaned_docstring = self._desensitize_docstring(full_docstring, delimiter)
                    cleaned_lines.extend(cleaned_docstring.splitlines())
                    self.cleaning_stats['comments_desensitized'] += 1
                else:
                    cleaned_lines.extend(docstring_lines)
                
                i += 1
                continue
            
            # 处理单行注释
            if '#' in line:
                code_part, comment_part = line.split('#', 1)
                
                # 如果注释部分需要删除
                if self._should_remove_comment(comment_part.strip()):
                    cleaned_lines.append(code_part.rstrip())
                    self.cleaning_stats['comments_removed'] += 1
                else:
                    # 对注释进行脱敏
                    desensitized_comment = self._desensitize_comment(comment_part)
                    if desensitized_comment != comment_part:
                        self.cleaning_stats['comments_desensitized'] += 1
                    cleaned_lines.append(f"{code_part}#{desensitized_comment}")
            else:
                cleaned_lines.append(line)
            
            i += 1
        
        return '\n'.join(cleaned_lines)
    
    def _clean_js_comments(self, content: str) -> str:
        """清洗JavaScript注释"""
        # 处理多行注释
        def process_multiline_comment(match):
            comment = match.group(0)
            if self._should_remove_comment(comment):
                self.cleaning_stats['comments_removed'] += 1
                return ''
            else:
                # 脱敏处理
                desensitized = self._desensitize_comment(comment)
                if desensitized != comment:
                    self.cleaning_stats['comments_desensitized'] += 1
                return desensitized
        
        # 处理单行注释
        def process_single_line_comment(match):
            comment = match.group(0)
            comment_text = comment[2:].strip()  # 移除 //
            
            if self._should_remove_comment(comment_text):
                self.cleaning_stats['comments_removed'] += 1
                return ''
            else:
                # 脱敏处理
                desensitized_text = self._desensitize_comment(comment_text)
                if desensitized_text != comment_text:
                    self.cleaning_stats['comments_desensitized'] += 1
                return f"// {desensitized_text}"
        
        # 应用处理
        content = re.sub(r'/\*.*?\*/', process_multiline_comment, content, flags=re.DOTALL)
        content = re.sub(r'//.*$', process_single_line_comment, content, flags=re.MULTILINE)
        
        return content
    
    def _clean_java_comments(self, content: str) -> str:
        """清洗Java注释"""
        # Java注释处理类似JavaScript
        return self._clean_js_comments(content)
    
    def _clean_cpp_comments(self, content: str) -> str:
        """清洗C/C++注释"""
        # C/C++注释处理类似JavaScript
        return self._clean_js_comments(content)
    
    def _clean_html_comments(self, content: str) -> str:
        """清洗HTML注释"""
        def process_html_comment(match):
            comment = match.group(0)
            comment_text = comment[4:-3].strip()  # 移除 <!-- 和 -->
            
            if self._should_remove_comment(comment_text):
                self.cleaning_stats['comments_removed'] += 1
                return ''
            else:
                # 脱敏处理
                desensitized_text = self._desensitize_comment(comment_text)
                if desensitized_text != comment_text:
                    self.cleaning_stats['comments_desensitized'] += 1
                return f"<!-- {desensitized_text} -->"
        
        return re.sub(r'<!--.*?-->', process_html_comment, content, flags=re.DOTALL)
    
    def _clean_css_comments(self, content: str) -> str:
        """清洗CSS注释"""
        def process_css_comment(match):
            comment = match.group(0)
            comment_text = comment[2:-2].strip()  # 移除 /* 和 */
            
            if self._should_remove_comment(comment_text):
                self.cleaning_stats['comments_removed'] += 1
                return ''
            else:
                # 脱敏处理
                desensitized_text = self._desensitize_comment(comment_text)
                if desensitized_text != comment_text:
                    self.cleaning_stats['comments_desensitized'] += 1
                return f"/* {desensitized_text} */"
        
        return re.sub(r'/\*.*?\*/', process_css_comment, content, flags=re.DOTALL)
    
    def _clean_generic_comments(self, content: str) -> str:
        """清洗通用注释"""
        # 移除以#开头的注释（如配置文件）
        def process_hash_comment(match):
            comment = match.group(0)
            comment_text = comment[1:].strip()
            
            if self._should_remove_comment(comment_text):
                self.cleaning_stats['comments_removed'] += 1
                return ''
            else:
                desensitized_text = self._desensitize_comment(comment_text)
                if desensitized_text != comment_text:
                    self.cleaning_stats['comments_desensitized'] += 1
                return f"# {desensitized_text}"
        
        content = re.sub(r'^#.*$', process_hash_comment, content, flags=re.MULTILINE)
        content = re.sub(r'^//.*$', process_hash_comment, content, flags=re.MULTILINE)
        
        return content
    
    def _should_remove_comment(self, comment: str) -> bool:
        """判断是否应该删除注释"""
        if not comment.strip():
            return True
        
        # 检查无效注释模式
        for pattern in self.invalid_comment_patterns:
            if pattern.search(comment):
                return True
        
        return False
    
    def _should_desensitize_docstring(self, docstring: str) -> bool:
        """判断是否应该脱敏文档字符串"""
        # 检查是否包含版权信息
        for pattern in self.copyright_patterns:
            if pattern.search(docstring):
                return True
        
        # 检查是否包含个人信息  
        for pattern_name, pattern in self.sensitive_patterns.items():
            if pattern_name in ['email', 'person_name', 'employee_id', 'phone'] and pattern.search(docstring):
                return True
        
        return False
    
    def _desensitize_docstring(self, docstring: str, delimiter: str) -> str:
        """脱敏文档字符串"""
        # 保留文档字符串结构，只脱敏具体内容
        lines = docstring.splitlines()
        desensitized_lines = []
        
        for line in lines:
            # 对每行进行脱敏处理
            desensitized_line = self._desensitize_line(line)
            desensitized_lines.append(desensitized_line)
        
        return '\n'.join(desensitized_lines)
    
    def _desensitize_comment(self, comment: str) -> str:
        """脱敏注释内容"""
        return self._desensitize_line(comment)
    
    def _desensitize_line(self, line: str) -> str:
        """脱敏单行内容 - 避免重复替换"""
        # 使用单次遍历，避免重复替换
        # 创建一个替换映射，按位置排序
        replacements = []
        
        # 收集所有匹配的位置
        for pattern_name, pattern in self.sensitive_patterns.items():
            for match in pattern.finditer(line):
                start, end = match.span()
                # 根据模式类型确定替换内容
                if pattern_name == 'email':
                    replacement = '<EMAIL>'
                elif pattern_name == 'id_card':
                    replacement = '<ID_CARD>'
                elif pattern_name == 'phone':
                    replacement = '<PHONE>'
                elif pattern_name == 'ip_address':
                    replacement = '<IP_ADDRESS>'
                elif pattern_name == 'employee_id':
                    replacement = '<EMPLOYEE_ID>'
                elif pattern_name == 'datetime':
                    replacement = '<DATE>'
                elif pattern_name == 'person_name':
                    replacement = '<NAME>'
                elif pattern_name == 'url':
                    replacement = '<URL>'
                elif pattern_name == 'organization':
                    replacement = '<ORGANIZATION>'
                else:
                    replacement = f'<{pattern_name.upper()}>'
                
                replacements.append((start, end, replacement))
        
        # 按开始位置排序，处理重叠的情况
        replacements.sort(key=lambda x: x[0])
        
        # 构建新的字符串，避免重叠替换
        result = ""
        last_end = 0
        for start, end, replacement in replacements:
            # 如果当前匹配与之前的重叠，跳过
            if start < last_end:
                continue
            
            result += line[last_end:start] + replacement
            last_end = end
        
        # 添加剩余部分
        result += line[last_end:]
        
        return result if result else line
    
    def _desensitize_content(self, content: str) -> Tuple[str, int]:
        """脱敏代码内容"""
        found_count = 0
        
        # 统计找到的敏感信息数量
        for pattern_name, pattern in self.sensitive_patterns.items():
            matches = pattern.findall(content)
            found_count += len(matches)
        
        if found_count == 0:
            return content, 0
        
        # 脱敏处理（与注释脱敏相同）
        desensitized_content = self._desensitize_line(content)
        
        return desensitized_content, found_count