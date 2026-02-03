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
    
    async def send(self, unified_msg_origin: str, message: str) -> bool:
        """
        发送通知消息到目标会话
        
        Args:
            unified_msg_origin: 目标会话的 unified_msg_origin
            message: 通知消息内容
            
        Returns:
            成功返回 True，失败返回 False
        """
        try:
            logger.info(f"准备发送通知到会话: {unified_msg_origin}")
            logger.debug(f"消息内容: {message[:100]}...")
            
            # 构造消息链
            message_chain = MessageChain().message(message)
            
            # 直接使用存储的 unified_msg_origin 发送
            result = await self.context.send_message(unified_msg_origin, message_chain)
            
            logger.info(f"✅ 成功发送通知到会话: {unified_msg_origin}")
            logger.debug(f"发送结果: {result}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 发送通知失败: {type(e).__name__}: {e}")
            logger.error(f"会话 ID: {unified_msg_origin}")
            logger.error("请检查:")
            logger.error(f"  1. 机器人是否在目标群组中")
            logger.error(f"  2. 机器人是否有发送消息的权限")
            logger.error(f"  3. 会话 ID 是否有效（可能需要重新添加配置）")
            logger.error(f"  4. QQ 适配器是否正常运行")
            
            import traceback
            logger.error(traceback.format_exc())
            return False
