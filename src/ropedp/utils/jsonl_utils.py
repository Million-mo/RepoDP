"""
JSONL工具函数
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Generator, Optional
import logging

logger = logging.getLogger(__name__)


class JSONLUtils:
    """JSONL工具类"""
    
    @staticmethod
    def read_jsonl(file_path: Path) -> Generator[Dict[str, Any], None, None]:
        """读取JSONL文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line:
                        try:
                            yield json.loads(line)
                        except json.JSONDecodeError as e:
                            logger.error(f"JSONL文件第{line_num}行解析失败: {e}")
                            continue
        except FileNotFoundError:
            logger.error(f"JSONL文件不存在: {file_path}")
        except Exception as e:
            logger.error(f"读取JSONL文件失败: {e}")
    
    @staticmethod
    def read_jsonl_all(file_path: Path) -> List[Dict[str, Any]]:
        """读取JSONL文件的所有数据"""
        return list(JSONLUtils.read_jsonl(file_path))
    
    @staticmethod
    def write_jsonl(data: List[Dict[str, Any]], file_path: Path) -> bool:
        """写入JSONL文件"""
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                for item in data:
                    f.write(json.dumps(item, ensure_ascii=False, default=str) + '\n')
            return True
        except Exception as e:
            logger.error(f"写入JSONL文件失败: {e}")
            return False
    
    @staticmethod
    def append_jsonl(item: Dict[str, Any], file_path: Path) -> bool:
        """追加数据到JSONL文件"""
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(item, ensure_ascii=False, default=str) + '\n')
            return True
        except Exception as e:
            logger.error(f"追加JSONL文件失败: {e}")
            return False
    
    @staticmethod
    def count_lines(file_path: Path) -> int:
        """计算JSONL文件行数"""
        try:
            count = 0
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        count += 1
            return count
        except Exception as e:
            logger.error(f"计算JSONL文件行数失败: {e}")
            return 0
    
    @staticmethod
    def validate_jsonl(file_path: Path) -> bool:
        """验证JSONL文件格式"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line:
                        try:
                            json.loads(line)
                        except json.JSONDecodeError:
                            logger.error(f"JSONL文件第{line_num}行格式错误")
                            return False
            return True
        except Exception as e:
            logger.error(f"验证JSONL文件失败: {e}")
            return False
    
    @staticmethod
    def convert_json_to_jsonl(json_file: Path, jsonl_file: Path) -> bool:
        """将JSON文件转换为JSONL文件"""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, list):
                return JSONLUtils.write_jsonl(data, jsonl_file)
            else:
                logger.error("JSON文件必须包含数组数据")
                return False
        except Exception as e:
            logger.error(f"转换JSON到JSONL失败: {e}")
            return False
    
    @staticmethod
    def convert_jsonl_to_json(jsonl_file: Path, json_file: Path) -> bool:
        """将JSONL文件转换为JSON文件"""
        try:
            data = JSONLUtils.read_jsonl_all(jsonl_file)
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            return True
        except Exception as e:
            logger.error(f"转换JSONL到JSON失败: {e}")
            return False
