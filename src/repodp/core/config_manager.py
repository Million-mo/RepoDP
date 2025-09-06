"""
配置管理模块
"""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
import logging
import re
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ConfigValidationError(Exception):
    """配置验证错误"""
    pass


@dataclass
class ConfigSchema:
    """配置模式定义"""
    key: str
    type: type
    required: bool = True
    default: Any = None
    description: str = ""
    validation_func: Optional[callable] = None
    env_var: Optional[str] = None


class ConfigSection(Enum):
    """配置节枚举"""
    EXTRACTION = "extraction"
    CLEANING = "cleaning"
    DEDUPLICATION = "deduplication"
    ANALYSIS = "analysis"
    REPORTING = "reporting"
    LOGGING = "logging"
    PERFORMANCE = "performance"
    FILE_METRICS_CLEANING = "file_metrics_cleaning"


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        
        # 定义配置模式
        self.config_schema = self._define_config_schema()
        
        # 默认配置
        self.default_config = self._create_default_config()
        
        # 加载配置
        self.config = self._load_config()
        
        # 验证配置
        self._validate_config()
    
    def _define_config_schema(self) -> Dict[str, List[ConfigSchema]]:
        """定义配置模式"""
        return {
            ConfigSection.EXTRACTION.value: [
                ConfigSchema("file_types", list, True, [".py", ".js", ".ts", ".java", ".cpp", ".c", ".h", ".go", ".rs", ".php", ".rb", ".swift", ".kt"], "支持的文件类型", self._validate_file_types),
                ConfigSchema("exclude_dirs", list, True, [".git", "__pycache__", "node_modules", ".venv", "venv", "build", "dist", "target"], "排除的目录", self._validate_string_list),
                ConfigSchema("exclude_files", list, True, [".gitignore", ".gitattributes", "README.md", "LICENSE"], "排除的文件", self._validate_string_list),
                ConfigSchema("max_file_size", int, True, 10485760, "最大文件大小(字节)", self._validate_positive_int, "ROPEDP_MAX_FILE_SIZE"),
            ],
            ConfigSection.CLEANING.value: [
                ConfigSchema("remove_comments", bool, True, False, "移除注释"),
                ConfigSchema("remove_blank_lines", bool, True, False, "移除空白行"),
                ConfigSchema("normalize_whitespace", bool, True, False, "标准化空白字符"),
                ConfigSchema("remove_imports", bool, True, False, "移除导入语句"),
                ConfigSchema("preserve_structure", bool, True, True, "保留代码结构"),
            ],
            ConfigSection.DEDUPLICATION.value: [
                ConfigSchema("hash_algorithm", str, True, "sha256", "哈希算法", self._validate_hash_algorithm),
                ConfigSchema("similarity_threshold", float, True, 0.95, "相似度阈值", self._validate_threshold),
                ConfigSchema("min_file_size", int, True, 100, "最小文件大小(字节)", self._validate_positive_int),
            ],
            ConfigSection.ANALYSIS.value: [
                ConfigSchema("language_detection", bool, True, True, "语言检测"),
                ConfigSchema("complexity_analysis", bool, True, True, "复杂度分析"),
                ConfigSchema("dependency_analysis", bool, True, True, "依赖分析"),
                ConfigSchema("metrics_calculation", bool, True, True, "指标计算"),
            ],
            ConfigSection.REPORTING.value: [
                ConfigSchema("output_dir", str, True, "data/reports", "输出目录", self._validate_path),
                ConfigSchema("default_format", str, True, "comprehensive", "默认报告格式", self._validate_report_format),
                ConfigSchema("supported_formats", list, True, ["json", "csv", "html", "markdown", "comprehensive"], "支持的格式", self._validate_report_formats),
            ],
            ConfigSection.LOGGING.value: [
                ConfigSchema("level", str, True, "INFO", "日志级别", self._validate_log_level, "ROPEDP_LOG_LEVEL"),
                ConfigSchema("format", str, True, "%(asctime)s - %(name)s - %(levelname)s - %(message)s", "日志格式"),
                ConfigSchema("file", str, False, "data/logs/repodp.log", "日志文件", self._validate_path, "ROPEDP_LOG_FILE"),
                ConfigSchema("max_file_size", int, False, 10485760, "最大文件大小(字节)", self._validate_positive_int),
                ConfigSchema("backup_count", int, False, 5, "保留文件数", self._validate_positive_int),
            ],
            ConfigSection.PERFORMANCE.value: [
                ConfigSchema("max_workers", int, True, 4, "最大并发数", self._validate_positive_int, "ROPEDP_MAX_WORKERS"),
                ConfigSchema("batch_size", int, True, 100, "批处理大小", self._validate_positive_int),
                ConfigSchema("memory_limit", int, True, 1024, "内存限制(MB)", self._validate_positive_int, "ROPEDP_MEMORY_LIMIT"),
                ConfigSchema("timeout", int, True, 300, "超时时间(秒)", self._validate_positive_int, "ROPEDP_TIMEOUT"),
            ],
            ConfigSection.FILE_METRICS_CLEANING.value: [
                ConfigSchema("thresholds", dict, True, {
                    "max_file_size": 1048576,
                    "max_line_count": 10000,
                    "max_line_length": 500,
                    "min_comment_percentage": 0,
                    "max_comment_percentage": 100,
                    "max_digit_percentage": 50,
                    "max_hex_percentage": 30,
                    "max_average_line_length": 200
                }, "文件指标阈值"),
                ConfigSchema("backup_enabled", bool, True, True, "启用备份"),
                ConfigSchema("backup_dir", str, False, "data/backups", "备份目录", self._validate_path),
            ],
            'jsonl_cleaning': [
                ConfigSchema("enable_comment_cleaning", bool, True, True, "启用注释清洗"),
                ConfigSchema("enable_desensitization", bool, True, True, "启用脱敏处理"),
                ConfigSchema("remove_invalid_comments", bool, True, True, "删除无效注释"),
                ConfigSchema("preserve_copyright_structure", bool, True, True, "保留版权结构"),
                ConfigSchema("sensitive_patterns", list, True, ["email", "phone", "employee_id", "id_card", "ip_address", "url", "datetime", "person_name", "organization"], "敏感信息模式"),
                ConfigSchema("invalid_comment_patterns", list, True, ["todo", "fixme", "version_info", "personal_signature", "change_history"], "无效注释模式"),
            ]
        }
    
    def _create_default_config(self) -> Dict[str, Any]:
        """创建默认配置"""
        config = {}
        for section, schemas in self.config_schema.items():
            config[section] = {}
            for schema in schemas:
                config[section][schema.key] = schema.default
        return config
    
    def _validate_config(self):
        """验证配置"""
        for section, schemas in self.config_schema.items():
            if section not in self.config:
                self.config[section] = {}
            
            for schema in schemas:
                key = schema.key
                value = self.config[section].get(key, schema.default)
                
                # 检查环境变量覆盖
                if schema.env_var and os.getenv(schema.env_var):
                    env_value = os.getenv(schema.env_var)
                    value = self._convert_env_value(env_value, schema.type)
                
                # 验证类型
                if not isinstance(value, schema.type):
                    try:
                        value = self._convert_type(value, schema.type)
                    except (ValueError, TypeError) as e:
                        raise ConfigValidationError(f"配置项 {section}.{key} 类型错误: {e}")
                
                # 验证值
                if schema.validation_func and not schema.validation_func(value):
                    logger.error(f"配置验证失败: {section}.{key} = {value} (类型: {type(value)})")
                    raise ConfigValidationError(f"配置项 {section}.{key} 验证失败")
                
                # 设置验证后的值
                self.config[section][key] = value
    
    def _convert_env_value(self, env_value: str, target_type: type) -> Any:
        """转换环境变量值"""
        if target_type == bool:
            return env_value.lower() in ('true', '1', 'yes', 'on')
        elif target_type == int:
            return int(env_value)
        elif target_type == float:
            return float(env_value)
        elif target_type == list:
            return [item.strip() for item in env_value.split(',')]
        else:
            return env_value
    
    def _convert_type(self, value: Any, target_type: type) -> Any:
        """转换值类型"""
        if target_type == bool:
            if isinstance(value, str):
                return value.lower() in ('true', '1', 'yes', 'on')
            return bool(value)
        elif target_type == int:
            return int(value)
        elif target_type == float:
            return float(value)
        elif target_type == list and isinstance(value, str):
            return [item.strip() for item in value.split(',')]
        else:
            return target_type(value)
    
    def _validate_file_types(self, value: List[str]) -> bool:
        """验证文件类型列表"""
        if not isinstance(value, list):
            return False
        return all(isinstance(item, str) and item.startswith('.') for item in value)
    
    def _validate_string_list(self, value: List[str]) -> bool:
        """验证字符串列表"""
        return isinstance(value, list) and all(isinstance(item, str) for item in value)
    
    def _validate_positive_int(self, value: int) -> bool:
        """验证正整数"""
        return isinstance(value, int) and value > 0
    
    def _validate_hash_algorithm(self, value: str) -> bool:
        """验证哈希算法"""
        return value in ['md5', 'sha1', 'sha256', 'sha512']
    
    def _validate_threshold(self, value: float) -> bool:
        """验证阈值"""
        return isinstance(value, (int, float)) and 0 <= value <= 1
    
    def _validate_path(self, value: str) -> bool:
        """验证路径"""
        return isinstance(value, str) and len(value) > 0
    
    def _validate_log_level(self, value: str) -> bool:
        """验证日志级别"""
        return value.upper() in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    
    def _validate_report_format(self, value: str) -> bool:
        """验证报告格式"""
        return value in ['json', 'csv', 'html', 'markdown', 'comprehensive']
    
    def _validate_report_formats(self, value: List[str]) -> bool:
        """验证报告格式列表"""
        valid_formats = ['json', 'csv', 'html', 'markdown', 'comprehensive']
        return isinstance(value, list) and all(fmt in valid_formats for fmt in value)
    
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
    
    def get_schema(self, section: str, key: str = None) -> Union[ConfigSchema, List[ConfigSchema], None]:
        """获取配置模式"""
        if section not in self.config_schema:
            return None
        
        if key is None:
            return self.config_schema[section]
        
        for schema in self.config_schema[section]:
            if schema.key == key:
                return schema
        return None
    
    def get_config_info(self) -> Dict[str, Any]:
        """获取配置信息"""
        info = {}
        for section, schemas in self.config_schema.items():
            info[section] = {}
            for schema in schemas:
                info[section][schema.key] = {
                    'type': schema.type.__name__,
                    'required': schema.required,
                    'default': schema.default,
                    'description': schema.description,
                    'env_var': schema.env_var,
                    'current_value': self.get(f"{section}.{schema.key}")
                }
        return info
    
    def generate_config_template(self, include_comments: bool = True) -> str:
        """生成配置模板"""
        template_lines = ["# RopeDP 配置文件", ""]
        
        for section, schemas in self.config_schema.items():
            template_lines.append(f"# {section.upper()} 配置")
            template_lines.append(f"{section}:")
            
            for schema in schemas:
                if include_comments and schema.description:
                    template_lines.append(f"  # {schema.description}")
                
                if schema.type == list:
                    if schema.key == "file_types":
                        template_lines.append(f"  {schema.key}:")
                        for ext in schema.default:
                            template_lines.append(f"    - \"{ext}\"")
                    else:
                        template_lines.append(f"  {schema.key}: []")
                elif schema.type == bool:
                    template_lines.append(f"  {schema.key}: {str(schema.default).lower()}")
                elif schema.type == str:
                    template_lines.append(f"  {schema.key}: \"{schema.default}\"")
                else:
                    template_lines.append(f"  {schema.key}: {schema.default}")
                
                if schema.env_var:
                    template_lines.append(f"  # 环境变量: {schema.env_var}")
                
                template_lines.append("")
        
        return "\n".join(template_lines)
    
    def validate_config_file(self, file_path: str) -> List[str]:
        """验证配置文件"""
        errors = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # 验证每个配置项
            for section, schemas in self.config_schema.items():
                if section not in config:
                    continue
                
                for schema in schemas:
                    key = schema.key
                    if key not in config[section]:
                        continue
                    
                    value = config[section][key]
                    
                    # 验证类型
                    if not isinstance(value, schema.type):
                        try:
                            self._convert_type(value, schema.type)
                        except (ValueError, TypeError) as e:
                            errors.append(f"{section}.{key}: 类型错误 - {e}")
                    
                    # 验证值
                    if schema.validation_func and not schema.validation_func(value):
                        errors.append(f"{section}.{key}: 验证失败")
        
        except (yaml.YAMLError, IOError) as e:
            errors.append(f"文件读取错误: {e}")
        
        return errors
    
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
    
    def import_config_from_dict(self, config_dict: Dict[str, Any]):
        """从字典导入配置"""
        try:
            # 合并配置
            self.config = self._merge_config(self.default_config, config_dict)
            self._save_config(self.config)
            logger.info("从字典导入配置成功")
        except Exception as e:
            logger.error(f"从字典导入配置失败: {e}")
            raise

