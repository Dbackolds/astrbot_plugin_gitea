"""
通知发送器模块
负责将通知消息发送到目标 QQ 群组
"""
from astrbot.api.star import Context
from astrbot.api.event import MessageChain
from astrbot.api import logger


class NotificationSender:
    """通知发送器"""
    
    def __init__(self, context: Context):
        """
        初始化通知发送器
        
        Args:
            context: AstrBot 上下文
        """
        self.context = context
    
    async def send(self, group_id: str, message: str) -> bool:
        """
        发送通知消息到目标群组
        
        Args:
            group_id: 目标群组 ID
            message: 通知消息内容
            
        Returns:
            成功返回 True，失败返回 False
        """
        try:
            # 构造 unified_msg_origin
            # 格式：aiocqhttp_group_{group_id}
            unified_msg_origin = f"aiocqhttp_group_{group_id}"
            
            # 构造消息链
            message_chain = MessageChain().message(message)
            
            # 发送消息
            await self.context.send_message(unified_msg_origin, message_chain)
            
            logger.info(f"成功发送通知到群组 {group_id}")
            return True
            
        except Exception as e:
            logger.error(f"发送通知失败: {e}")
            return False
