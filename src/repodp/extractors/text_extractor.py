"""
文本提取器
"""

import re
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class TextExtractor:
    """文本提取器，用于提取文本内容特征"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    def extract_text_features(self, file_info: Dict[str, Any]) -> Dict[str, Any]:
        """提取文本特征"""
        if file_info.get('is_binary', False):
            return {}
        
        content = file_info.get('content', '')
        language = file_info.get('language', 'unknown')
        
        features = {
            'basic_stats': self._extract_basic_stats(content),
            'readability': self._calculate_readability(content),
            'keywords': self._extract_keywords(content, language),
            'patterns': self._extract_patterns(content, language),
            'encoding_info': self._detect_encoding_info(content)
        }
        
        return features
    
    def _extract_basic_stats(self, content: str) -> Dict[str, Any]:
        """提取基本统计信息"""
        lines = content.splitlines()
        words = re.findall(r'\b\w+\b', content)
        
        return {
            'total_lines': len(lines),
            'non_empty_lines': len([line for line in lines if line.strip()]),
            'total_words': len(words),
            'total_characters': len(content),
            'total_characters_no_spaces': len(content.replace(' ', '')),
            'average_line_length': sum(len(line) for line in lines) / len(lines) if lines else 0,
            'average_word_length': sum(len(word) for word in words) / len(words) if words else 0,
            'longest_line': max(len(line) for line in lines) if lines else 0,
            'shortest_line': min(len(line) for line in lines) if lines else 0
        }
    
    def _calculate_readability(self, content: str) -> Dict[str, Any]:
        """计算可读性指标"""
        words = re.findall(r'\b\w+\b', content)
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # 计算音节数（简化版本）
        syllables = sum(self._count_syllables(word) for word in words)
        
        # Flesch Reading Ease
        if len(sentences) > 0 and len(words) > 0:
            avg_sentence_length = len(words) / len(sentences)
            avg_syllables_per_word = syllables / len(words)
            flesch_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
        else:
            flesch_score = 0
        
        # Flesch-Kincaid Grade Level
        if len(sentences) > 0 and len(words) > 0:
            fk_grade = 0.39 * avg_sentence_length + 11.8 * avg_syllables_per_word - 15.59
        else:
            fk_grade = 0
        
        return {
            'flesch_reading_ease': max(0, min(100, flesch_score)),
            'flesch_kincaid_grade': max(0, fk_grade),
            'total_syllables': syllables,
            'avg_syllables_per_word': syllables / len(words) if words else 0,
            'avg_sentence_length': len(words) / len(sentences) if sentences else 0
        }
    
    def _count_syllables(self, word: str) -> int:
        """计算单词音节数（简化版本）"""
        word = word.lower()
        if not word:
            return 0
        
        # 移除常见的后缀
        word = re.sub(r'(es|ed|ing)$', '', word)
        
        # 计算元音组
        vowels = 'aeiouy'
        syllable_count = 0
        prev_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_was_vowel:
                syllable_count += 1
            prev_was_vowel = is_vowel
        
        # 处理特殊情况
        if word.endswith('e') and syllable_count > 1:
            syllable_count -= 1
        
        return max(1, syllable_count)
    
    def _extract_keywords(self, content: str, language: str) -> Dict[str, Any]:
        """提取关键词"""
        # 简单的关键词提取（基于词频）
        words = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', content)
        
        # 过滤常见停用词
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
            'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those',
            'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'
        }
        
        # 计算词频
        word_freq = {}
        for word in words:
            word_lower = word.lower()
            if word_lower not in stop_words and len(word_lower) > 2:
                word_freq[word_lower] = word_freq.get(word_lower, 0) + 1
        
        # 获取最常见的词
        top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:20]
        
        return {
            'top_words': top_words,
            'unique_words': len(word_freq),
            'total_words': len(words),
            'vocabulary_richness': len(word_freq) / len(words) if words else 0
        }
    
    def _extract_patterns(self, content: str, language: str) -> Dict[str, Any]:
        """提取文本模式"""
        patterns = {}
        
        # 提取URL
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, content)
        patterns['urls'] = urls
        
        # 提取邮箱
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, content)
        patterns['emails'] = emails
        
        # 提取数字
        number_pattern = r'\b\d+(?:\.\d+)?\b'
        numbers = re.findall(number_pattern, content)
        patterns['numbers'] = numbers
        
        # 提取代码模式（根据语言）
        if language in ['python', 'javascript', 'typescript', 'java', 'cpp', 'c']:
            patterns.update(self._extract_code_patterns(content, language))
        
        return patterns
    
    def _extract_code_patterns(self, content: str, language: str) -> Dict[str, Any]:
        """提取代码模式"""
        patterns = {}
        
        if language == 'python':
            # Python特定模式
            patterns['imports'] = re.findall(r'^(?:from\s+\w+\s+)?import\s+[\w\s,]+', content, re.MULTILINE)
            patterns['functions'] = re.findall(r'^def\s+(\w+)', content, re.MULTILINE)
            patterns['classes'] = re.findall(r'^class\s+(\w+)', content, re.MULTILINE)
            patterns['comments'] = re.findall(r'#.*$', content, re.MULTILINE)
            patterns['docstrings'] = re.findall(r'""".*?"""', content, re.DOTALL)
        
        elif language in ['javascript', 'typescript']:
            # JavaScript/TypeScript特定模式
            patterns['functions'] = re.findall(r'function\s+(\w+)', content)
            patterns['arrow_functions'] = re.findall(r'(?:const|let|var)\s+(\w+)\s*=\s*\([^)]*\)\s*=>', content)
            patterns['classes'] = re.findall(r'class\s+(\w+)', content)
            patterns['imports'] = re.findall(r'import\s+.*?from\s+[\'"]([^\'"]+)[\'"]', content)
            patterns['comments'] = re.findall(r'//.*$|/\*.*?\*/', content, re.MULTILINE | re.DOTALL)
        
        elif language == 'java':
            # Java特定模式
            patterns['classes'] = re.findall(r'class\s+(\w+)', content)
            patterns['methods'] = re.findall(r'(?:public|private|protected)?\s*(?:static\s+)?(?:\w+\s+)*(\w+)\s*\([^)]*\)\s*(?:throws\s+[\w\s,]+)?\s*\{', content)
            patterns['imports'] = re.findall(r'import\s+([\w.]+);', content)
            patterns['comments'] = re.findall(r'//.*$|/\*.*?\*/', content, re.MULTILINE | re.DOTALL)
        
        return patterns
    
    def _detect_encoding_info(self, content: str) -> Dict[str, Any]:
        """检测编码信息"""
        try:
            # 尝试不同的编码
            encodings = ['utf-8', 'utf-16', 'latin-1', 'cp1252', 'ascii']
            detected_encoding = 'utf-8'
            
            for encoding in encodings:
                try:
                    content.encode(encoding)
                    detected_encoding = encoding
                    break
                except UnicodeEncodeError:
                    continue
            
            return {
                'detected_encoding': detected_encoding,
                'is_ascii': all(ord(c) < 128 for c in content),
                'has_unicode': any(ord(c) > 127 for c in content),
                'bom_present': content.startswith('\ufeff')
            }
            
        except Exception as e:
            logger.error(f"编码检测失败: {e}")
            return {
                'detected_encoding': 'unknown',
                'is_ascii': False,
                'has_unicode': False,
                'bom_present': False
            }

