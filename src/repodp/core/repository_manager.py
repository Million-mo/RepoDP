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
        
        # 创建数据目录（但不创建repos目录，只在需要时创建）
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
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
        """添加新的代码仓库（远程）"""
        try:
            # 确保repos目录存在
            self.repos_dir.mkdir(parents=True, exist_ok=True)
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
                "commit_hash": repo.head.commit.hexsha,
                "type": "remote"
            }
            
            self._save_repositories()
            logger.info(f"成功添加远程仓库: {name}")
            return True
            
        except Exception as e:
            logger.error(f"添加远程仓库失败: {e}")
            return False
    
    def _get_repository_url(self, repo: Repo) -> str:
        """从Git配置中获取仓库URL"""
        try:
            # 优先获取origin远程仓库的URL
            if 'origin' in repo.remotes:
                return repo.remotes.origin.url
            
            # 如果没有origin，获取第一个远程仓库的URL
            if repo.remotes:
                return repo.remotes[0].url
                
            # 如果没有远程仓库，返回本地路径
            return str(repo.working_dir)
            
        except Exception as e:
            logger.warning(f"获取仓库URL失败: {e}")
            return str(repo.working_dir)
    
    def add_local_repository_reference(self, name: str, local_path: str, branch: str = "main") -> bool:
        """添加本地代码仓库引用（不复制文件）"""
        try:
            source_path = Path(local_path)
            if not source_path.exists():
                logger.error(f"本地路径不存在: {local_path}")
                return False
            
            if not source_path.is_dir():
                logger.error(f"本地路径不是目录: {local_path}")
                return False
            
            # 验证是否为有效的git仓库
            try:
                source_repo = Repo(source_path)
            except InvalidGitRepositoryError:
                logger.error(f"本地路径不是有效的git仓库: {local_path}")
                return False
            
            # 获取远程仓库URL（如果存在）
            repo_url = self._get_repository_url(source_repo)
            
            # 引用模式：直接使用源路径，不复制文件
            # 保存仓库信息
            self.repositories[name] = {
                "url": repo_url,  # 使用检测到的URL或本地路径
                "path": str(source_path),  # 直接使用源路径
                "branch": branch,
                "last_updated": source_repo.head.commit.committed_datetime.isoformat(),
                "commit_hash": source_repo.head.commit.hexsha,
                "type": "local_reference"  # 新的类型：本地引用
            }
            
            self._save_repositories()
            logger.info(f"成功添加本地仓库引用: {name}")
            return True
            
        except Exception as e:
            logger.error(f"添加本地仓库引用失败: {e}")
            return False
    
    def add_local_repository(self, name: str, local_path: str, branch: str = "main") -> bool:
        """添加本地代码仓库（复制模式）"""
        try:
            source_path = Path(local_path)
            if not source_path.exists():
                logger.error(f"本地路径不存在: {local_path}")
                return False
            
            if not source_path.is_dir():
                logger.error(f"本地路径不是目录: {local_path}")
                return False
            
            # 验证是否为有效的git仓库
            try:
                source_repo = Repo(source_path)
            except InvalidGitRepositoryError:
                logger.error(f"本地路径不是有效的git仓库: {local_path}")
                return False
            
            # 确保repos目录存在
            self.repos_dir.mkdir(parents=True, exist_ok=True)
            repo_path = self.repos_dir / name
            
            # 如果目标目录已存在，先删除
            if repo_path.exists():
                shutil.rmtree(repo_path)
            
            # 复制本地仓库到目标位置
            logger.info(f"正在复制本地仓库: {local_path}")
            shutil.copytree(source_path, repo_path)
            
            # 获取仓库信息
            repo = Repo(repo_path)
            
            # 获取远程仓库URL（如果存在）
            repo_url = self._get_repository_url(repo)
            
            # 保存仓库信息
            self.repositories[name] = {
                "url": repo_url,  # 使用检测到的URL或本地路径
                "path": str(repo_path),
                "branch": branch,
                "last_updated": repo.head.commit.committed_datetime.isoformat(),
                "commit_hash": repo.head.commit.hexsha,
                "type": "local"
            }
            
            self._save_repositories()
            logger.info(f"成功添加本地仓库: {name}")
            return True
            
        except Exception as e:
            logger.error(f"添加本地仓库失败: {e}")
            return False
    
    def update_repository(self, name: str) -> bool:
        """更新代码仓库"""
        if name not in self.repositories:
            logger.error(f"仓库不存在: {name}")
            return False
        
        try:
            repo_path = Path(self.repositories[name]["path"])
            repo = Repo(repo_path)
            
            # 检查仓库类型
            repo_type = self.repositories[name].get("type", "remote")
            
            if repo_type in ["local", "local_reference"]:
                # 本地仓库不执行拉取操作，只更新信息
                logger.info(f"本地仓库 {name} 跳过拉取操作")
            else:
                # 远程仓库拉取最新代码
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
            repo_type = self.repositories[name].get("type", "remote")
            
            # 删除本地目录（仅对于非引用模式）
            if repo_path.exists() and repo_type != "local_reference":
                # 只对复制模式的本地仓库和远程仓库删除目录
                if repo_path.is_relative_to(self.repos_dir):
                    shutil.rmtree(repo_path)
                    logger.info(f"已删除仓库目录: {repo_path}")
                else:
                    logger.warning(f"跳过节删除仓库目录（路径不在repos目录中）: {repo_path}")
            elif repo_type == "local_reference":
                logger.info(f"引用模式仓库，不删除源目录: {repo_path}")
            
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
    
    def get_all_repositories(self) -> Dict[str, dict]:
        """获取所有仓库信息"""
        return self.repositories.copy()
    
    def cleanup_empty_dirs(self) -> List[str]:
        """清理空目录，返回被清理的目录列表"""
        cleaned_dirs = []
        
        # 检查repos目录是否为空
        if self.repos_dir.exists() and not any(self.repos_dir.iterdir()):
            try:
                self.repos_dir.rmdir()
                cleaned_dirs.append(str(self.repos_dir))
                logger.info(f"已清理空目录: {self.repos_dir}")
            except OSError as e:
                logger.warning(f"清理空目录失败 {self.repos_dir}: {e}")
        
        return cleaned_dirs

