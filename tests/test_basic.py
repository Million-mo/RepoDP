#!/usr/bin/env python3
"""
基本测试
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import sys

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from ropedp.core import RepositoryManager, ConfigManager
from ropedp.extractors import FileExtractor
from ropedp.cleaners import ContentCleaner
from ropedp.analyzers import CodeAnalyzer


class TestBasic(unittest.TestCase):
    """基本测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.config_manager = ConfigManager()
        self.repo_manager = RepositoryManager(str(self.temp_dir / 'data'))
    
    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.temp_dir)
    
    def test_config_manager(self):
        """测试配置管理器"""
        # 测试获取配置
        file_types = self.config_manager.get('extraction.file_types')
        self.assertIsInstance(file_types, list)
        self.assertIn('.py', file_types)
        
        # 测试设置配置
        self.config_manager.set('test.value', 'test')
        self.assertEqual(self.config_manager.get('test.value'), 'test')
    
    def test_file_extractor(self):
        """测试文件提取器"""
        # 创建测试文件
        test_file = self.temp_dir / 'test.py'
        test_file.write_text('print("Hello, World!")')
        
        # 创建文件信息
        file_info = {
            'path': str(test_file),
            'content': test_file.read_text(),
            'size': test_file.stat().st_size,
            'is_binary': False,
            'language': 'python'
        }
        
        # 测试文件提取器
        file_extractor = FileExtractor(self.config_manager.config)
        self.assertTrue(file_extractor.should_extract_file(test_file))
        self.assertFalse(file_extractor.should_extract_dir(self.temp_dir / 'node_modules'))
    
    def test_content_cleaner(self):
        """测试内容清洗器"""
        # 创建测试内容
        test_content = '''
# 这是一个注释
def hello():
    print("Hello, World!")  # 行内注释
    
    return "Hello"
'''
        
        file_info = {
            'content': test_content,
            'is_binary': False,
            'language': 'python'
        }
        
        # 测试内容清洗器
        content_cleaner = ContentCleaner(self.config_manager.config)
        cleaned_file = content_cleaner.clean_content(file_info)
        
        self.assertIn('content', cleaned_file)
        self.assertIn('original_content', cleaned_file)
        self.assertIn('cleaning_stats', cleaned_file)
    
    def test_code_analyzer(self):
        """测试代码分析器"""
        # 创建测试文件列表
        file_list = [
            {
                'path': 'test1.py',
                'content': 'def hello():\n    print("Hello")\n',
                'is_binary': False,
                'language': 'python',
                'lines': 2,
                'size': 30
            },
            {
                'path': 'test2.py',
                'content': 'def world():\n    print("World")\n',
                'is_binary': False,
                'language': 'python',
                'lines': 2,
                'size': 30
            }
        ]
        
        # 测试代码分析器
        code_analyzer = CodeAnalyzer(self.config_manager.config)
        analysis_data = code_analyzer.analyze_repository(file_list)
        
        self.assertIn('overall', analysis_data)
        self.assertIn('by_language', analysis_data)
        self.assertEqual(analysis_data['overall']['total_files'], 2)
        self.assertEqual(analysis_data['overall']['total_lines'], 4)


if __name__ == '__main__':
    unittest.main()

