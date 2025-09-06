"""
代码仓管理模块
"""

import os
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from git import Repo, InvalidGitRepositoryError
import logging

logger = logging.getLogger(__name__)


class RepositoryManager:
    """代码仓管理器"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.repos_dir = self.data_dir / "repos"
        self.config_file = self.data_dir / "repositories.json"
        
        # 创建必要的目录
        self.repos_dir.mkdir(parents=True, exist_ok=True)
        
        # 加载仓库配置
        self.repositories = self._load_repositories()
    
    def _load_repositories(self) -> Dict[str, dict]:
        """加载仓库配置"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"加载仓库配置失败: {e}")
                return {}
        return {}
    
    def _save_repositories(self):
        """保存仓库配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.repositories, f, indent=2, ensure_ascii=False)
        except IOError as e:
            logger.error(f"保存仓库配置失败: {e}")
    
    def add_repository(self, name: str, url: str, branch: str = "main") -> bool:
        """添加新的代码仓库"""
        try:
            repo_path = self.repos_dir / name
            
            # 如果目录已存在，先删除
            if repo_path.exists():
                shutil.rmtree(repo_path)
            
            # 克隆仓库
            logger.info(f"正在克隆仓库: {url}")
            repo = Repo.clone_from(url, repo_path, branch=branch)
            
            # 保存仓库信息
            self.repositories[name] = {
                "url": url,
                "path": str(repo_path),
                "branch": branch,
                "last_updated": repo.head.commit.committed_datetime.isoformat(),
                "commit_hash": repo.head.commit.hexsha
            }
            
            self._save_repositories()
            logger.info(f"成功添加仓库: {name}")
            return True
            
        except Exception as e:
            logger.error(f"添加仓库失败: {e}")
            return False
    
    def update_repository(self, name: str) -> bool:
        """更新代码仓库"""
        if name not in self.repositories:
            logger.error(f"仓库不存在: {name}")
            return False
        
        try:
            repo_path = Path(self.repositories[name]["path"])
            repo = Repo(repo_path)
            
            # 拉取最新代码
            origin = repo.remotes.origin
            origin.pull()
            
            # 更新仓库信息
            self.repositories[name].update({
                "last_updated": repo.head.commit.committed_datetime.isoformat(),
                "commit_hash": repo.head.commit.hexsha
            })
            
            self._save_repositories()
            logger.info(f"成功更新仓库: {name}")
            return True
            
        except Exception as e:
            logger.error(f"更新仓库失败: {e}")
            return False
    
    def remove_repository(self, name: str) -> bool:
        """删除代码仓库"""
        if name not in self.repositories:
            logger.error(f"仓库不存在: {name}")
            return False
        
        try:
            repo_path = Path(self.repositories[name]["path"])
            
            # 删除本地目录
            if repo_path.exists():
                shutil.rmtree(repo_path)
            
            # 从配置中移除
            del self.repositories[name]
            self._save_repositories()
            
            logger.info(f"成功删除仓库: {name}")
            return True
            
        except Exception as e:
            logger.error(f"删除仓库失败: {e}")
            return False
    
    def list_repositories(self) -> List[dict]:
        """列出所有仓库"""
        return list(self.repositories.values())
    
    def get_repository(self, name: str) -> Optional[dict]:
        """获取指定仓库信息"""
        return self.repositories.get(name)
    
    def get_repository_path(self, name: str) -> Optional[Path]:
        """获取仓库本地路径"""
        if name in self.repositories:
            return Path(self.repositories[name]["path"])
        return None
    
    def is_valid_repository(self, name: str) -> bool:
        """检查仓库是否有效"""
        if name not in self.repositories:
            return False
        
        repo_path = Path(self.repositories[name]["path"])
        if not repo_path.exists():
            return False
        
        try:
            Repo(repo_path)
            return True
        except InvalidGitRepositoryError:
            return False

