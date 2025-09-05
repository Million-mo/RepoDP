"""
文本工具函数
"""

import re
from typing import List, Dict, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class TextUtils:
    """文本工具类"""
    
    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """标准化空白字符"""
        # 将多个连续空白字符替换为单个空格
        text = re.sub(r'\s+', ' ', text)
        # 移除行首行尾空白
        lines = text.splitlines()
        lines = [line.strip() for line in lines]
        return '\n'.join(lines)
    
    @staticmethod
    def remove_empty_lines(text: str) -> str:
        """移除空行"""
        lines = text.splitlines()
        non_empty_lines = [line for line in lines if line.strip()]
        return '\n'.join(non_empty_lines)
    
    @staticmethod
    def remove_trailing_whitespace(text: str) -> str:
        """移除行尾空白"""
        lines = text.splitlines()
        lines = [line.rstrip() for line in lines]
        return '\n'.join(lines)
    
    @staticmethod
    def normalize_line_endings(text: str) -> str:
        """标准化换行符"""
        return text.replace('\r\n', '\n').replace('\r', '\n')
    
    @staticmethod
    def count_lines(text: str) -> int:
        """计算行数"""
        return len(text.splitlines())
    
    @staticmethod
    def count_words(text: str) -> int:
        """计算单词数"""
        words = re.findall(r'\b\w+\b', text)
        return len(words)
    
    @staticmethod
    def count_characters(text: str) -> int:
        """计算字符数"""
        return len(text)
    
    @staticmethod
    def count_characters_no_spaces(text: str) -> int:
        """计算非空格字符数"""
        return len(text.replace(' ', ''))
    
    @staticmethod
    def extract_words(text: str) -> List[str]:
        """提取单词"""
        return re.findall(r'\b\w+\b', text)
    
    @staticmethod
    def extract_sentences(text: str) -> List[str]:
        """提取句子"""
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    @staticmethod
    def extract_paragraphs(text: str) -> List[str]:
        """提取段落"""
        paragraphs = text.split('\n\n')
        return [p.strip() for p in paragraphs if p.strip()]
    
    @staticmethod
    def extract_urls(text: str) -> List[str]:
        """提取URL"""
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        return re.findall(url_pattern, text)
    
    @staticmethod
    def extract_emails(text: str) -> List[str]:
        """提取邮箱地址"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return re.findall(email_pattern, text)
    
    @staticmethod
    def extract_numbers(text: str) -> List[str]:
        """提取数字"""
        number_pattern = r'\b\d+(?:\.\d+)?\b'
        return re.findall(number_pattern, text)
    
    @staticmethod
    def extract_hashtags(text: str) -> List[str]:
        """提取标签"""
        hashtag_pattern = r'#\w+'
        return re.findall(hashtag_pattern, text)
    
    @staticmethod
    def extract_mentions(text: str) -> List[str]:
        """提取提及"""
        mention_pattern = r'@\w+'
        return re.findall(mention_pattern, text)
    
    @staticmethod
    def clean_text(text: str) -> str:
        """清理文本"""
        # 移除控制字符
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
        # 标准化空白字符
        text = TextUtils.normalize_whitespace(text)
        # 移除行尾空白
        text = TextUtils.remove_trailing_whitespace(text)
        # 标准化换行符
        text = TextUtils.normalize_line_endings(text)
        return text
    
    @staticmethod
    def truncate_text(text: str, max_length: int, suffix: str = '...') -> str:
        """截断文本"""
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix
    
    @staticmethod
    def wrap_text(text: str, width: int) -> str:
        """文本换行"""
        lines = text.splitlines()
        wrapped_lines = []
        
        for line in lines:
            if len(line) <= width:
                wrapped_lines.append(line)
            else:
                # 按单词分割
                words = line.split()
                current_line = ''
                
                for word in words:
                    if len(current_line + word) <= width:
                        current_line += word + ' '
                    else:
                        if current_line:
                            wrapped_lines.append(current_line.rstrip())
                        current_line = word + ' '
                
                if current_line:
                    wrapped_lines.append(current_line.rstrip())
        
        return '\n'.join(wrapped_lines)
    
    @staticmethod
    def calculate_readability_score(text: str) -> Dict[str, float]:
        """计算可读性分数"""
        words = TextUtils.extract_words(text)
        sentences = TextUtils.extract_sentences(text)
        
        if not words or not sentences:
            return {'flesch_score': 0, 'fk_grade': 0}
        
        # 计算音节数（简化版本）
        syllables = sum(TextUtils._count_syllables(word) for word in words)
        
        # Flesch Reading Ease
        avg_sentence_length = len(words) / len(sentences)
        avg_syllables_per_word = syllables / len(words)
        flesch_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
        
        # Flesch-Kincaid Grade Level
        fk_grade = 0.39 * avg_sentence_length + 11.8 * avg_syllables_per_word - 15.59
        
        return {
            'flesch_score': max(0, min(100, flesch_score)),
            'fk_grade': max(0, fk_grade)
        }
    
    @staticmethod
    def _count_syllables(word: str) -> int:
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
    
    @staticmethod
    def extract_keywords(text: str, top_n: int = 10) -> List[Tuple[str, int]]:
        """提取关键词"""
        from collections import Counter
        
        # 提取单词
        words = TextUtils.extract_words(text.lower())
        
        # 过滤停用词
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
            'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those',
            'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'
        }
        
        # 过滤短词和停用词
        filtered_words = [word for word in words if len(word) > 2 and word not in stop_words]
        
        # 计算词频
        word_counts = Counter(filtered_words)
        
        # 返回最常见的词
        return word_counts.most_common(top_n)
    
    @staticmethod
    def detect_language(text: str) -> str:
        """检测语言（简化版本）"""
        # 简单的语言检测，基于字符特征
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        japanese_chars = len(re.findall(r'[\u3040-\u309f\u30a0-\u30ff]', text))
        korean_chars = len(re.findall(r'[\uac00-\ud7af]', text))
        arabic_chars = len(re.findall(r'[\u0600-\u06ff]', text))
        cyrillic_chars = len(re.findall(r'[\u0400-\u04ff]', text))
        
        total_chars = len(text)
        
        if total_chars == 0:
            return 'unknown'
        
        # 计算各语言字符比例
        chinese_ratio = chinese_chars / total_chars
        japanese_ratio = japanese_chars / total_chars
        korean_ratio = korean_chars / total_chars
        arabic_ratio = arabic_chars / total_chars
        cyrillic_ratio = cyrillic_chars / total_chars
        
        # 判断语言
        if chinese_ratio > 0.1:
            return 'chinese'
        elif japanese_ratio > 0.1:
            return 'japanese'
        elif korean_ratio > 0.1:
            return 'korean'
        elif arabic_ratio > 0.1:
            return 'arabic'
        elif cyrillic_ratio > 0.1:
            return 'russian'
        else:
            return 'english'

