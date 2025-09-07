"""
Pipeline管理器 - 负责任务编排和执行
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Generator, Union
import logging
from datetime import datetime
from collections import defaultdict, deque

from ..extractors.file_extractor import FileExtractor
from ..cleaners.deduplicator import Deduplicator
from ..cleaners.content_cleaner import ContentCleaner
from ..cleaners.file_metrics_cleaner import FileMetricsCleaner
from ..cleaners.jsonl_content_cleaner import JSONLContentCleaner

logger = logging.getLogger(__name__)


class PipelineStep:
    """Pipeline步骤类"""
    
    def __init__(self, name: str, step_config: Dict[str, Any], pipeline_config: Dict[str, Any]):
        self.name = name
        self.type = step_config.get('type', 'unknown')
        self.enabled = step_config.get('enabled', True)
        self.depends_on = step_config.get('depends_on', [])
        self.config = step_config.get('config', {})
        self.pipeline_config = pipeline_config
        
        # 合并配置
        self.merged_config = self._merge_configs(pipeline_config, self.config)
        
        # 初始化处理器
        self.processor = self._create_processor()
    
    def _merge_configs(self, pipeline_config: Dict[str, Any], step_config: Dict[str, Any]) -> Dict[str, Any]:
        """合并配置"""
        merged = pipeline_config.copy()
        merged.update(step_config)
        return merged
    
    def _create_processor(self):
        """创建处理器实例"""
        if not self.enabled:
            return None
        
        try:
            if self.type == 'extractor':
                return FileExtractor(self.merged_config)
            elif self.type == 'cleaner':
                method = self.config.get('method', '')
                if method == 'deduplication':
                    return Deduplicator(self.merged_config)
                elif method == 'content_cleaning':
                    return ContentCleaner(self.merged_config)
                elif method == 'file_metrics_cleaning':
                    return FileMetricsCleaner(self.merged_config)
                elif method == 'jsonl_cleaning':
                    return JSONLContentCleaner(self.merged_config)
                else:
                    logger.error(f"未知的清洗方法: {method}")
                    return None
            elif self.type == 'analyzer':
                method = self.config.get('method', '')
                if method == 'duplicate_analysis':
                    return Deduplicator(self.merged_config)
                elif method == 'metrics_analysis':
                    return FileMetricsCleaner(self.merged_config)
                else:
                    logger.error(f"未知的分析方法: {method}")
                    return None
            else:
                logger.error(f"未知的步骤类型: {self.type}")
                return None
        except Exception as e:
            logger.error(f"创建处理器失败 {self.name}: {e}")
            return None
    
    def can_execute(self, completed_steps: set) -> bool:
        """检查是否可以执行"""
        if not self.enabled or not self.processor:
            return False
        
        # 检查依赖是否完成
        for dep in self.depends_on:
            if dep not in completed_steps:
                return False
        
        return True


class PipelineManager:
    """Pipeline管理器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.pipeline_config = config.get('pipeline', {})
        self.default_pipeline = self.pipeline_config.get('default_pipeline', 'standard')
        self.pipelines = self.pipeline_config.get('pipelines', {})
        
        # 工作目录
        self.work_dir = Path(config.get('work_dir', 'data'))
        self.work_dir.mkdir(parents=True, exist_ok=True)
        
        # 输出目录
        self.output_dir = self.work_dir / 'output'
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 临时目录
        self.temp_dir = self.work_dir / 'temp'
        self.temp_dir.mkdir(parents=True, exist_ok=True)
    
    def get_pipeline(self, pipeline_name: Optional[str] = None) -> Dict[str, Any]:
        """获取pipeline配置"""
        if pipeline_name is None:
            pipeline_name = self.default_pipeline
        
        if pipeline_name not in self.pipelines:
            raise ValueError(f"Pipeline '{pipeline_name}' 不存在")
        
        return self.pipelines[pipeline_name]
    
    def list_pipelines(self) -> List[Dict[str, Any]]:
        """列出所有可用的pipeline"""
        pipelines = []
        for name, config in self.pipelines.items():
            pipelines.append({
                'name': name,
                'display_name': config.get('name', name),
                'description': config.get('description', ''),
                'steps': len(config.get('steps', [])),
                'enabled_steps': sum(1 for step in config.get('steps', []) if step.get('enabled', True))
            })
        return pipelines
    
    def validate_pipeline(self, pipeline_name: str) -> Dict[str, Any]:
        """验证pipeline配置"""
        try:
            pipeline = self.get_pipeline(pipeline_name)
            steps = pipeline.get('steps', [])
            
            # 检查步骤名称唯一性
            step_names = [step['name'] for step in steps]
            if len(step_names) != len(set(step_names)):
                return {
                    'valid': False,
                    'error': '步骤名称必须唯一'
                }
            
            # 检查依赖关系
            step_deps = {step['name']: step.get('depends_on', []) for step in steps}
            for step_name, deps in step_deps.items():
                for dep in deps:
                    if dep not in step_names:
                        return {
                            'valid': False,
                            'error': f'步骤 {step_name} 依赖的步骤 {dep} 不存在'
                        }
            
            # 检查循环依赖
            if self._has_circular_dependency(step_deps):
                return {
                    'valid': False,
                    'error': '存在循环依赖'
                }
            
            return {
                'valid': True,
                'steps': len(steps),
                'enabled_steps': sum(1 for step in steps if step.get('enabled', True))
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': str(e)
            }
    
    def _has_circular_dependency(self, step_deps: Dict[str, List[str]]) -> bool:
        """检查是否存在循环依赖"""
        def dfs(node, visited, rec_stack):
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in step_deps.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor, visited, rec_stack):
                        return True
                elif neighbor in rec_stack:
                    return True
            
            rec_stack.remove(node)
            return False
        
        visited = set()
        for node in step_deps:
            if node not in visited:
                if dfs(node, visited, set()):
                    return True
        
        return False
    
    def execute_pipeline(self, 
                        repo_path: Union[str, Path], 
                        pipeline_name: Optional[str] = None,
                        repo_name: Optional[str] = None,
                        output_dir: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
        """执行pipeline"""
        repo_path = Path(repo_path)
        if not repo_path.exists():
            raise ValueError(f"仓库路径不存在: {repo_path}")
        
        if repo_name is None:
            repo_name = repo_path.name
        
        if output_dir is None:
            output_dir = self.output_dir / repo_name
        else:
            output_dir = Path(output_dir)
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 获取pipeline配置
        pipeline = self.get_pipeline(pipeline_name)
        steps = pipeline.get('steps', [])
        
        # 创建步骤实例
        pipeline_steps = {}
        for step_config in steps:
            step_name = step_config['name']
            pipeline_steps[step_name] = PipelineStep(step_name, step_config, self.config)
        
        # 执行结果
        results = {
            'pipeline_name': pipeline_name or self.default_pipeline,
            'repo_path': str(repo_path),
            'repo_name': repo_name,
            'output_dir': str(output_dir),
            'start_time': datetime.now().isoformat(),
            'steps': {},
            'success': True,
            'errors': []
        }
        
        # 执行步骤
        completed_steps = set()
        completed_steps_order = []  # 保持执行顺序
        current_input = None
        
        try:
            # 拓扑排序执行步骤
            execution_order = self._get_execution_order(pipeline_steps)
            
            for step_name in execution_order:
                step = pipeline_steps[step_name]
                
                if not step.can_execute(completed_steps):
                    logger.warning(f"跳过步骤 {step_name}，依赖未完成或已禁用")
                    continue
                
                logger.info(f"执行步骤: {step_name} ({step.type})")
                
                try:
                    step_result = self._execute_step(step, repo_path, repo_name, current_input, output_dir)
                    results['steps'][step_name] = step_result
                    
                    # 更新当前输入为下一步的输入
                    if step_result.get('output_file'):
                        current_input = Path(step_result['output_file'])
                    
                    completed_steps.add(step_name)
                    completed_steps_order.append(step_name)  # 按执行顺序添加
                    
                    logger.info(f"步骤 {step_name} 执行完成")
                    
                except Exception as e:
                    error_msg = f"步骤 {step_name} 执行失败: {e}"
                    logger.error(error_msg)
                    results['errors'].append(error_msg)
                    results['success'] = False
                    
                    # 根据配置决定是否继续执行
                    if not self.config.get('pipeline', {}).get('continue_on_error', True):
                        break
            
            results['end_time'] = datetime.now().isoformat()
            results['completed_steps'] = completed_steps_order
            
            # 生成执行报告
            self._generate_execution_report(results, output_dir)
            
            return results
            
        except Exception as e:
            error_msg = f"Pipeline执行失败: {e}"
            logger.error(error_msg)
            results['errors'].append(error_msg)
            results['success'] = False
            results['end_time'] = datetime.now().isoformat()
            return results
    
    def _get_execution_order(self, pipeline_steps: Dict[str, PipelineStep]) -> List[str]:
        """获取步骤执行顺序（拓扑排序）"""
        # 构建依赖图
        graph = defaultdict(list)
        in_degree = defaultdict(int)
        
        for step_name, step in pipeline_steps.items():
            in_degree[step_name] = len(step.depends_on)
            for dep in step.depends_on:
                graph[dep].append(step_name)
        
        # 拓扑排序
        queue = deque([step for step in pipeline_steps.keys() if in_degree[step] == 0])
        result = []
        
        while queue:
            current = queue.popleft()
            result.append(current)
            
            for neighbor in graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        return result
    
    def _execute_step(self, 
                     step: PipelineStep, 
                     repo_path: Path, 
                     repo_name: str, 
                     current_input: Optional[Path],
                     output_dir: Path) -> Dict[str, Any]:
        """执行单个步骤"""
        step_result = {
            'step_name': step.name,
            'step_type': step.type,
            'start_time': datetime.now().isoformat(),
            'success': False,
            'output_file': None,
            'stats': {},
            'errors': []
        }
        
        try:
            if step.type == 'extractor':
                # 文件提取
                output_file = output_dir / f"{repo_name}_extracted.jsonl"
                step_result['output_file'] = str(output_file)
                
                # 执行提取
                file_count = 0
                for file_info in step.processor.extract_files(repo_path, output_file):
                    file_count += 1
                
                step_result['stats'] = {
                    'files_extracted': file_count,
                    'output_file': str(output_file)
                }
                
            elif step.type == 'cleaner':
                method = step.config.get('method', '')
                
                if method == 'deduplication':
                    # 去重处理
                    if not current_input or not current_input.exists():
                        raise ValueError("去重步骤需要输入文件")
                    
                    output_file = output_dir / f"{repo_name}_deduplicated.jsonl"
                    step_result['output_file'] = str(output_file)
                    
                    # 执行去重
                    result = step.processor.deduplicate_jsonl_file(current_input, output_file)
                    step_result['stats'] = result
                    
                elif method == 'content_cleaning':
                    # 内容清洗
                    if not current_input or not current_input.exists():
                        raise ValueError("内容清洗步骤需要输入文件")
                    
                    output_file = output_dir / f"{repo_name}_content_cleaned.jsonl"
                    step_result['output_file'] = str(output_file)
                    
                    # 执行内容清洗
                    result = step.processor.clean_jsonl_content(current_input, output_file)
                    step_result['stats'] = result
                    
                elif method == 'file_metrics_cleaning':
                    # 文件指标清洗
                    if not current_input or not current_input.exists():
                        raise ValueError("文件指标清洗步骤需要输入文件")
                    
                    output_file = output_dir / f"{repo_name}_metrics_cleaned.jsonl"
                    step_result['output_file'] = str(output_file)
                    
                    # 执行文件指标清洗
                    result = step.processor.clean_jsonl_by_metrics(current_input, output_file, repo_name)
                    step_result['stats'] = result
                    
                elif method == 'jsonl_cleaning':
                    # JSONL清洗
                    if not current_input or not current_input.exists():
                        raise ValueError("JSONL清洗步骤需要输入文件")
                    
                    output_file = output_dir / f"{repo_name}_jsonl_cleaned.jsonl"
                    step_result['output_file'] = str(output_file)
                    
                    # 执行JSONL清洗
                    result = step.processor.clean_jsonl_file(current_input, output_file)
                    step_result['stats'] = result
                    
            elif step.type == 'analyzer':
                method = step.config.get('method', '')
                
                if method == 'duplicate_analysis':
                    # 重复文件分析
                    if not current_input or not current_input.exists():
                        raise ValueError("重复文件分析步骤需要输入文件")
                    
                    output_file = output_dir / f"{repo_name}_duplicate_analysis.json"
                    step_result['output_file'] = str(output_file)
                    
                    # 执行分析
                    result = step.processor.analyze_jsonl_duplicates(current_input)
                    
                    # 保存分析结果
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(result, f, ensure_ascii=False, indent=2)
                    
                    step_result['stats'] = result
                    
                elif method == 'metrics_analysis':
                    # 文件指标分析
                    if not current_input or not current_input.exists():
                        raise ValueError("文件指标分析步骤需要输入文件")
                    
                    output_file = output_dir / f"{repo_name}_metrics_analysis.json"
                    step_result['output_file'] = str(output_file)
                    
                    # 执行分析
                    result = step.processor.analyze_jsonl_metrics(current_input, repo_name)
                    
                    # 保存分析结果
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(result, f, ensure_ascii=False, indent=2)
                    
                    step_result['stats'] = result
            
            step_result['success'] = True
            
        except Exception as e:
            error_msg = f"步骤 {step.name} 执行失败: {e}"
            step_result['errors'].append(error_msg)
            logger.error(error_msg)
        
        step_result['end_time'] = datetime.now().isoformat()
        return step_result
    
    def _generate_execution_report(self, results: Dict[str, Any], output_dir: Path):
        """生成执行报告"""
        report_file = output_dir / "pipeline_report.json"
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Pipeline执行报告已保存: {report_file}")
            
        except Exception as e:
            logger.error(f"生成执行报告失败: {e}")
    
    def dry_run(self, pipeline_name: Optional[str] = None) -> Dict[str, Any]:
        """模拟执行pipeline（不实际执行）"""
        try:
            pipeline = self.get_pipeline(pipeline_name)
            steps = pipeline.get('steps', [])
            
            # 创建步骤实例
            pipeline_steps = {}
            for step_config in steps:
                step_name = step_config['name']
                pipeline_steps[step_name] = PipelineStep(step_name, step_config, self.config)
            
            # 获取执行顺序
            execution_order = self._get_execution_order(pipeline_steps)
            
            # 模拟执行
            dry_run_result = {
                'pipeline_name': pipeline_name or self.default_pipeline,
                'steps': [],
                'execution_order': execution_order,
                'total_steps': len(steps),
                'enabled_steps': sum(1 for step in pipeline_steps.values() if step.enabled),
                'estimated_outputs': []
            }
            
            completed_steps = set()
            current_output = "extracted_files.jsonl"
            
            for step_name in execution_order:
                step = pipeline_steps[step_name]
                
                if not step.can_execute(completed_steps):
                    continue
                
                step_info = {
                    'name': step_name,
                    'type': step.type,
                    'enabled': step.enabled,
                    'depends_on': step.depends_on,
                    'input_file': current_output if step_name != 'extract' else None,
                    'output_file': self._get_estimated_output_file(step_name, step.type)
                }
                
                dry_run_result['steps'].append(step_info)
                dry_run_result['estimated_outputs'].append(step_info['output_file'])
                
                completed_steps.add(step_name)
                current_output = step_info['output_file']
            
            return dry_run_result
            
        except Exception as e:
            return {
                'error': str(e),
                'success': False
            }
    
    def _get_estimated_output_file(self, step_name: str, step_type: str) -> str:
        """获取预估的输出文件名"""
        if step_type == 'extractor':
            return "extracted_files.jsonl"
        elif step_type == 'cleaner':
            method = step_name.split('_')[-1] if '_' in step_name else step_name
            return f"files_{method}.jsonl"
        elif step_type == 'analyzer':
            method = step_name.split('_')[-1] if '_' in step_name else step_name
            return f"{method}_analysis.json"
        else:
            return f"{step_name}_output.jsonl"
