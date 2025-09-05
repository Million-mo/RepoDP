"""
配置管理模块
"""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        
        # 默认配置
        self.default_config = {
            "extraction": {
                "file_types": [".py", ".js", ".ts", ".java", ".cpp", ".c", ".h", ".go", ".rs", ".php", ".rb", ".swift", ".kt"],
                "exclude_dirs": [".git", "__pycache__", "node_modules", ".venv", "venv", "build", "dist", "target"],
                "exclude_files": [".gitignore", ".gitattributes", "README.md", "LICENSE"],
                "max_file_size": 10 * 1024 * 1024,  # 10MB
            },
            "cleaning": {
                "remove_comments": True,
                "remove_blank_lines": True,
                "normalize_whitespace": True,
                "remove_imports": False,
                "preserve_structure": True,
            },
            "deduplication": {
                "hash_algorithm": "sha256",
                "similarity_threshold": 0.95,
                "min_file_size": 100,  # bytes
            },
            "analysis": {
                "language_detection": True,
                "complexity_analysis": True,
                "dependency_analysis": True,
                "metrics_calculation": True,
            }
        }
        
        # 加载配置
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        config_file = self.config_dir / "config.yaml"
        
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                    # 合并默认配置
                    return self._merge_config(self.default_config, config)
            except (yaml.YAMLError, IOError) as e:
                logger.warning(f"加载配置文件失败: {e}")
        
        # 创建默认配置文件
        self._save_config(self.default_config)
        return self.default_config.copy()
    
    def _merge_config(self, default: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """合并配置"""
        result = default.copy()
        
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _save_config(self, config: Dict[str, Any]):
        """保存配置文件"""
        config_file = self.config_dir / "config.yaml"
        
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True, indent=2)
        except IOError as e:
            logger.error(f"保存配置文件失败: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """设置配置值"""
        keys = key.split('.')
        config = self.config
        
        # 导航到目标位置
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # 设置值
        config[keys[-1]] = value
        
        # 保存配置
        self._save_config(self.config)
    
    def update(self, updates: Dict[str, Any]):
        """批量更新配置"""
        for key, value in updates.items():
            self.set(key, value)
    
    def reset_to_default(self):
        """重置为默认配置"""
        self.config = self.default_config.copy()
        self._save_config(self.config)
    
    def export_config(self, file_path: str):
        """导出配置到文件"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                if file_path.endswith('.json'):
                    json.dump(self.config, f, indent=2, ensure_ascii=False)
                else:
                    yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True, indent=2)
        except IOError as e:
            logger.error(f"导出配置失败: {e}")
    
    def import_config(self, file_path: str):
        """从文件导入配置"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_path.endswith('.json'):
                    config = json.load(f)
                else:
                    config = yaml.safe_load(f)
                
                # 合并配置
                self.config = self._merge_config(self.default_config, config)
                self._save_config(self.config)
                
        except (yaml.YAMLError, json.JSONDecodeError, IOError) as e:
            logger.error(f"导入配置失败: {e}")

