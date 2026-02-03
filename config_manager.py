"""
配置管理器模块
负责管理仓库监控配置的增删改查和持久化
"""
import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Optional
from pathlib import Path
from astrbot.api import logger


@dataclass
class MonitorConfig:
    """仓库监控配置"""
    repo_url: str  # 仓库 URL
    secret: str  # Webhook 密钥
    group_id: str  # 目标群组 ID
    created_at: str  # 创建时间


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, storage_path: str):
        """
        初始化配置管理器
        
        Args:
            storage_path: 配置文件存储路径
        """
        self.storage_path = Path(storage_path)
        self.monitors: dict[str, MonitorConfig] = {}
        
        # 确保存储目录存在
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 加载现有配置
        self.load()
    
    def add_monitor(self, repo_url: str, secret: str, group_id: str) -> bool:
        """
        添加仓库监控配置
        
        Args:
            repo_url: 仓库 URL
            secret: Webhook 密钥
            group_id: 目标群组 ID
            
        Returns:
            成功返回 True，失败返回 False
        """
        # 验证必需字段
        if not repo_url or not secret or not group_id:
            logger.error("添加监控配置失败：缺少必需字段")
            return False
        
        # 检查是否已存在
        if repo_url in self.monitors:
            logger.warning(f"仓库 {repo_url} 的监控配置已存在")
            return False
        
        # 创建配置
        config = MonitorConfig(
            repo_url=repo_url,
            secret=secret,
            group_id=group_id,
            created_at=datetime.now().isoformat()
        )
        
        self.monitors[repo_url] = config
        
        # 保存到文件
        if self.save():
            logger.info(f"成功添加仓库监控配置: {repo_url} -> 群组 {group_id}")
            return True
        else:
            # 保存失败，回滚
            del self.monitors[repo_url]
            return False
    
    def remove_monitor(self, repo_url: str) -> bool:
        """
        删除仓库监控配置
        
        Args:
            repo_url: 仓库 URL
            
        Returns:
            成功返回 True，失败返回 False
        """
        if repo_url not in self.monitors:
            logger.warning(f"仓库 {repo_url} 的监控配置不存在")
            return False
        
        # 删除配置
        del self.monitors[repo_url]
        
        # 保存到文件
        if self.save():
            logger.info(f"成功删除仓库监控配置: {repo_url}")
            return True
        else:
            return False
    
    def get_monitor(self, repo_url: str) -> Optional[MonitorConfig]:
        """
        获取指定仓库的监控配置
        
        Args:
            repo_url: 仓库 URL
            
        Returns:
            MonitorConfig 对象，如果不存在则返回 None
        """
        return self.monitors.get(repo_url)
    
    def list_monitors(self) -> List[MonitorConfig]:
        """
        列出所有监控配置
        
        Returns:
            MonitorConfig 对象列表
        """
        return list(self.monitors.values())
    
    def save(self) -> bool:
        """
        保存配置到文件
        
        Returns:
            成功返回 True，失败返回 False
        """
        try:
            data = {
                "monitors": [asdict(config) for config in self.monitors.values()]
            }
            
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.debug(f"配置已保存到 {self.storage_path}")
            return True
            
        except Exception as e:
            logger.error(f"保存配置失败: {e}")
            return False
    
    def load(self) -> bool:
        """
        从文件加载配置
        
        Returns:
            成功返回 True，失败返回 False
        """
        try:
            if not self.storage_path.exists():
                logger.info("配置文件不存在，使用空配置")
                return True
            
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            monitors_data = data.get("monitors", [])
            self.monitors = {}
            
            for monitor_dict in monitors_data:
                config = MonitorConfig(**monitor_dict)
                self.monitors[config.repo_url] = config
            
            logger.info(f"成功加载 {len(self.monitors)} 个监控配置")
            return True
            
        except Exception as e:
            logger.error(f"加载配置失败: {e}")
            return False
