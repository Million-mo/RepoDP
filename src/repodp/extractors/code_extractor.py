"""
代码提取器
"""

import ast
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
import logging

logger = logging.getLogger(__name__)


class CodeExtractor:
    """代码提取器，专门用于提取代码结构信息"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    def extract_code_structure(self, file_info: Dict[str, Any]) -> Dict[str, Any]:
        """提取代码结构信息"""
        if file_info.get('is_binary', False):
            return {}
        
        language = file_info.get('language', 'unknown')
        content = file_info.get('content', '')
        
        if language == 'python':
            return self._extract_python_structure(content)
        elif language in ['javascript', 'typescript']:
            return self._extract_js_structure(content)
        elif language == 'java':
            return self._extract_java_structure(content)
        elif language in ['cpp', 'c']:
            return self._extract_cpp_structure(content)
        else:
            return self._extract_generic_structure(content, language)
    
    def _extract_python_structure(self, content: str) -> Dict[str, Any]:
        """提取Python代码结构"""
        try:
            tree = ast.parse(content)
            
            classes = []
            functions = []
            imports = []
            variables = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    classes.append({
                        'name': node.name,
                        'line': node.lineno,
                        'bases': [self._get_name(base) for base in node.bases],
                        'methods': [n.name for n in node.body if isinstance(n, ast.FunctionDef)],
                        'docstring': ast.get_docstring(node)
                    })
                
                elif isinstance(node, ast.FunctionDef):
                    functions.append({
                        'name': node.name,
                        'line': node.lineno,
                        'args': [arg.arg for arg in node.args.args],
                        'returns': self._get_name(node.returns) if node.returns else None,
                        'docstring': ast.get_docstring(node),
                        'is_async': isinstance(node, ast.AsyncFunctionDef)
                    })
                
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.append({
                                'module': alias.name,
                                'alias': alias.asname,
                                'type': 'import'
                            })
                    else:
                        for alias in node.names:
                            imports.append({
                                'module': node.module or '',
                                'name': alias.name,
                                'alias': alias.asname,
                                'type': 'from_import'
                            })
                
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            variables.append({
                                'name': target.id,
                                'line': node.lineno,
                                'type': 'assignment'
                            })
            
            return {
                'classes': classes,
                'functions': functions,
                'imports': imports,
                'variables': variables,
                'complexity': self._calculate_python_complexity(tree)
            }
            
        except SyntaxError as e:
            logger.warning(f"Python语法错误: {e}")
            return {}
        except Exception as e:
            logger.error(f"提取Python结构失败: {e}")
            return {}
    
    def _extract_js_structure(self, content: str) -> Dict[str, Any]:
        """提取JavaScript/TypeScript代码结构"""
        functions = []
        classes = []
        imports = []
        variables = []
        
        # 提取函数
        function_pattern = r'(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?(?:function|\([^)]*\)\s*=>))'
        for match in re.finditer(function_pattern, content):
            func_name = match.group(1) or match.group(2)
            functions.append({
                'name': func_name,
                'line': content[:match.start()].count('\n') + 1,
                'type': 'function'
            })
        
        # 提取类
        class_pattern = r'class\s+(\w+)'
        for match in re.finditer(class_pattern, content):
            classes.append({
                'name': match.group(1),
                'line': content[:match.start()].count('\n') + 1,
                'type': 'class'
            })
        
        # 提取导入
        import_pattern = r'(?:import\s+(?:\{[^}]*\}|\w+|\*\s+as\s+\w+)\s+from\s+[\'"]([^\'"]+)[\'"]|require\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\))'
        for match in re.finditer(import_pattern, content):
            module = match.group(1) or match.group(2)
            imports.append({
                'module': module,
                'line': content[:match.start()].count('\n') + 1,
                'type': 'import'
            })
        
        return {
            'functions': functions,
            'classes': classes,
            'imports': imports,
            'variables': variables,
            'complexity': self._calculate_js_complexity(content)
        }
    
    def _extract_java_structure(self, content: str) -> Dict[str, Any]:
        """提取Java代码结构"""
        classes = []
        methods = []
        imports = []
        
        # 提取类
        class_pattern = r'(?:public|private|protected)?\s*(?:static\s+)?(?:final\s+)?class\s+(\w+)'
        for match in re.finditer(class_pattern, content):
            classes.append({
                'name': match.group(1),
                'line': content[:match.start()].count('\n') + 1,
                'type': 'class'
            })
        
        # 提取方法
        method_pattern = r'(?:public|private|protected)?\s*(?:static\s+)?(?:final\s+)?(?:\w+\s+)*(\w+)\s*\([^)]*\)\s*(?:throws\s+[\w\s,]+)?\s*\{'
        for match in re.finditer(method_pattern, content):
            methods.append({
                'name': match.group(1),
                'line': content[:match.start()].count('\n') + 1,
                'type': 'method'
            })
        
        # 提取导入
        import_pattern = r'import\s+([\w.]+);'
        for match in re.finditer(import_pattern, content):
            imports.append({
                'module': match.group(1),
                'line': content[:match.start()].count('\n') + 1,
                'type': 'import'
            })
        
        return {
            'classes': classes,
            'methods': methods,
            'imports': imports,
            'complexity': self._calculate_java_complexity(content)
        }
    
    def _extract_cpp_structure(self, content: str) -> Dict[str, Any]:
        """提取C++代码结构"""
        classes = []
        functions = []
        includes = []
        
        # 提取类
        class_pattern = r'class\s+(\w+)(?:\s*:\s*[\w\s,]+)?\s*\{'
        for match in re.finditer(class_pattern, content):
            classes.append({
                'name': match.group(1),
                'line': content[:match.start()].count('\n') + 1,
                'type': 'class'
            })
        
        # 提取函数
        function_pattern = r'(?:\w+\s+)*(\w+)\s*\([^)]*\)\s*(?:const\s*)?\s*\{'
        for match in re.finditer(function_pattern, content):
            functions.append({
                'name': match.group(1),
                'line': content[:match.start()].count('\n') + 1,
                'type': 'function'
            })
        
        # 提取包含
        include_pattern = r'#include\s*[<"]([^>"]+)[>"]'
        for match in re.finditer(include_pattern, content):
            includes.append({
                'header': match.group(1),
                'line': content[:match.start()].count('\n') + 1,
                'type': 'include'
            })
        
        return {
            'classes': classes,
            'functions': functions,
            'includes': includes,
            'complexity': self._calculate_cpp_complexity(content)
        }
    
    def _extract_generic_structure(self, content: str, language: str) -> Dict[str, Any]:
        """提取通用代码结构"""
        # 简单的行数统计和基本模式匹配
        lines = content.splitlines()
        non_empty_lines = [line for line in lines if line.strip()]
        
        return {
            'total_lines': len(lines),
            'non_empty_lines': len(non_empty_lines),
            'language': language,
            'complexity': len(non_empty_lines)  # 简单的复杂度度量
        }
    
    def _get_name(self, node) -> str:
        """获取AST节点名称"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        else:
            return str(type(node).__name__)
    
    def _calculate_python_complexity(self, tree) -> int:
        """计算Python代码复杂度"""
        complexity = 0
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor, ast.ExceptHandler, ast.With, ast.AsyncWith)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        
        return complexity
    
    def _calculate_js_complexity(self, content: str) -> int:
        """计算JavaScript代码复杂度"""
        complexity = 0
        
        # 计算控制流语句
        patterns = [
            r'\bif\s*\(',
            r'\bwhile\s*\(',
            r'\bfor\s*\(',
            r'\bswitch\s*\(',
            r'\bcatch\s*\(',
            r'\?\s*.*\s*:',
            r'&&',
            r'\|\|'
        ]
        
        for pattern in patterns:
            complexity += len(re.findall(pattern, content))
        
        return complexity
    
    def _calculate_java_complexity(self, content: str) -> int:
        """计算Java代码复杂度"""
        complexity = 0
        
        patterns = [
            r'\bif\s*\(',
            r'\bwhile\s*\(',
            r'\bfor\s*\(',
            r'\bswitch\s*\(',
            r'\bcatch\s*\(',
            r'\?\s*.*\s*:',
            r'&&',
            r'\|\|'
        ]
        
        for pattern in patterns:
            complexity += len(re.findall(pattern, content))
        
        return complexity
    
    def _calculate_cpp_complexity(self, content: str) -> int:
        """计算C++代码复杂度"""
        complexity = 0
        
        patterns = [
            r'\bif\s*\(',
            r'\bwhile\s*\(',
            r'\bfor\s*\(',
            r'\bswitch\s*\(',
            r'\bcatch\s*\(',
            r'\?\s*.*\s*:',
            r'&&',
            r'\|\|'
        ]
        
        for pattern in patterns:
            complexity += len(re.findall(pattern, content))
        
        return complexity

