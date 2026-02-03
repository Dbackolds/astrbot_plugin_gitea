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
            logger.info(f"准备发送通知到群组 {group_id}")
            logger.debug(f"消息内容: {message}")
            
            # 构造 unified_msg_origin
            # 尝试多种格式
            unified_msg_origins = [
                f"aiocqhttp_group_{group_id}",
                f"group_{group_id}",
                f"{group_id}",
            ]
            
            # 构造消息链
            message_chain = MessageChain().message(message)
            
            # 尝试发送消息
            for umo in unified_msg_origins:
                try:
                    logger.debug(f"尝试使用 unified_msg_origin: {umo}")
                    await self.context.send_message(umo, message_chain)
                    logger.info(f"✅ 成功发送通知到群组 {group_id} (使用格式: {umo})")
                    return True
                except Exception as e:
                    logger.debug(f"使用 {umo} 发送失败: {e}")
                    continue
            
            logger.error(f"❌ 所有格式都发送失败，群组 {group_id}")
            return False
            
        except Exception as e:
            logger.error(f"发送通知时发生异常: {e}", exc_info=True)
            return False
