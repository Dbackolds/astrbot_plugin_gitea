"""
通知发送器模块
负责将通知消息发送到目标 QQ 群组
"""
from astrbot.api.star import Context
from astrbot.api.event import MessageChain
from astrbot.api import logger
from .config_manager import ConfigManager


class NotificationSender:
    """通知发送器"""
    
    def __init__(self, context: Context, config_manager: ConfigManager):
        """
        初始化通知发送器
        
        Args:
            context: AstrBot 上下文
            config_manager: 配置管理器
        """
        self.context = context
        self.config_manager = config_manager
    
    async def send(self, repo_url: str, message: str) -> bool:
        """
        发送通知消息到目标群组
        
        Args:
            repo_url: 仓库 URL
            message: 通知消息内容
            
        Returns:
            成功返回 True，失败返回 False
        """
        try:
            # 查找仓库对应的监控配置
            config = self.config_manager.get_monitor(repo_url)
            
            if not config:
                logger.warning(f"找不到仓库 {repo_url} 的监控配置")
                return False
            
            group_id = config.group_id
            
            # 构造 unified_msg_origin
            # 格式：aiocqhttp_group_{group_id}
            unified_msg_origin = f"aiocqhttp_group_{group_id}"
            
            # 构造消息链
            message_chain = MessageChain().message(message)
            
            # 发送消息
            await self.context.send_message(unified_msg_origin, message_chain)
            
            logger.info(f"成功发送通知到群组 {group_id}: {repo_url}")
            return True
            
        except Exception as e:
            logger.error(f"发送通知失败: {e}")
            return False
