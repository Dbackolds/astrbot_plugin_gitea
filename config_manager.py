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
from urllib.parse import urlparse
from astrbot.api import logger


@dataclass
class MonitorConfig:
    """仓库监控配置"""
    repo_url: str  # 仓库 URL
    secret: str  # Webhook 密钥
    unified_msg_origin: str  # 目标会话的 unified_msg_origin
    created_at: str  # 创建时间
    
    @property
    def group_id(self) -> str:
        """从 unified_msg_origin 提取群组 ID（用于显示）"""
        try:
            parts = self.unified_msg_origin.split('_')
            if len(parts) >= 3 and parts[1] == 'group':
                return parts[2]
            return "未知"
        except:
            return "未知"


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
    
    @staticmethod
    def _normalize_repo_path(url: str) -> str:
        """
        标准化仓库路径，提取路径部分用于匹配
        
        Args:
            url: 仓库 URL
            
        Returns:
            标准化的仓库路径（小写，去除前后斜杠）
        """
        try:
            parsed = urlparse(url)
            # 提取路径部分，去除前后斜杠，转小写
            path = parsed.path.strip('/').lower()
            return path
        except Exception as e:
            logger.warning(f"解析 URL 失败: {url}, 错误: {e}")
            return url.lower()
    
    def _find_monitor_by_path(self, repo_url: str) -> Optional[MonitorConfig]:
        """
        通过仓库路径查找监控配置（支持不同域名的相同仓库）
        
        Args:
            repo_url: 仓库 URL
            
        Returns:
            MonitorConfig 对象，如果不存在则返回 None
        """
        target_path = self._normalize_repo_path(repo_url)
        
        for config in self.monitors.values():
            config_path = self._normalize_repo_path(config.repo_url)
            if config_path == target_path:
                return config
        
        return None
    
    def add_monitor(self, repo_url: str, secret: str, unified_msg_origin: str) -> bool:
        """
        添加仓库监控配置
        
        Args:
            repo_url: 仓库 URL
            secret: Webhook 密钥
            unified_msg_origin: 目标会话的 unified_msg_origin
            
        Returns:
            成功返回 True，失败返回 False
        """
        # 验证必需字段
        if not repo_url or not secret or not unified_msg_origin:
            logger.error("添加监控配置失败：缺少必需字段")
            return False
        
        # 检查是否已存在（精确匹配）
        if repo_url in self.monitors:
            logger.warning(f"仓库 {repo_url} 的监控配置已存在")
            return False
        
        # 检查是否存在相同路径的配置（路径匹配）
        existing_config = self._find_monitor_by_path(repo_url)
        if existing_config:
            logger.warning(f"仓库路径已存在监控配置: {existing_config.repo_url}")
            logger.info(f"提示: 新 URL {repo_url} 与已有配置 {existing_config.repo_url} 指向同一仓库")
            return False
        
        # 创建配置
        config = MonitorConfig(
            repo_url=repo_url,
            secret=secret,
            unified_msg_origin=unified_msg_origin,
            created_at=datetime.now().isoformat()
        )
        
        self.monitors[repo_url] = config
        
        # 保存到文件
        if self.save():
            logger.info(f"成功添加仓库监控配置: {repo_url} -> {unified_msg_origin}")
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
        获取指定仓库的监控配置（支持智能匹配）
        
        Args:
            repo_url: 仓库 URL
            
        Returns:
            MonitorConfig 对象，如果不存在则返回 None
        """
        # 先尝试精确匹配
        config = self.monitors.get(repo_url)
        if config:
            return config
        
        # 如果精确匹配失败，尝试路径匹配
        config = self._find_monitor_by_path(repo_url)
        if config:
            logger.info(f"通过路径匹配找到配置: {repo_url} -> {config.repo_url}")
            return config
        
        return None
    
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
            
            logger.info(f"准备保存配置到: {self.storage_path}")
            logger.info(f"配置数量: {len(self.monitors)}")
            
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"配置已成功保存到 {self.storage_path}")
            
            # 验证文件是否真的被创建
            if self.storage_path.exists():
                file_size = self.storage_path.stat().st_size
                logger.info(f"文件已创建，大小: {file_size} 字节")
            else:
                logger.error(f"文件保存后不存在: {self.storage_path}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"保存配置失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    def load(self) -> bool:
        """
        从文件加载配置
        
        Returns:
            成功返回 True，失败返回 False
        """
        try:
            logger.info(f"尝试从 {self.storage_path} 加载配置")
            
            if not self.storage_path.exists():
                logger.info(f"配置文件不存在: {self.storage_path}，使用空配置")
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
            import traceback
            logger.error(traceback.format_exc())
            return False
