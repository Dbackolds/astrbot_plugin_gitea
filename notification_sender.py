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
            logger.debug(f"消息内容: {message[:100]}...")
            
            # 构造消息链
            message_chain = MessageChain().message(message)
            
            # 尝试多种格式的 unified_msg_origin
            # 格式: {platform}_{type}_{id}
            unified_msg_origins = [
                f"aiocqhttp_group_{group_id}",    # aiocqhttp 适配器 + 群组
                f"qq_group_{group_id}",           # QQ 适配器 + 群组
                f"default_group_{group_id}",      # 默认适配器 + 群组
                f"group_{group_id}",              # 通用群组格式
            ]
            
            # 尝试发送消息
            last_error = None
            for umo in unified_msg_origins:
                try:
                    logger.debug(f"尝试使用 unified_msg_origin: {umo}")
                    
                    # 使用 context.send_message 发送
                    result = await self.context.send_message(
                        unified_msg_origin=umo,
                        message_chain=message_chain
                    )
                    
                    logger.info(f"✅ 成功发送通知到群组 {group_id} (使用格式: {umo})")
                    logger.debug(f"发送结果: {result}")
                    return True
                    
                except Exception as e:
                    last_error = e
                    logger.debug(f"使用 {umo} 发送失败: {type(e).__name__}: {e}")
                    continue
            
            # 所有格式都失败，记录详细错误
            logger.error(f"❌ 所有格式都发送失败，群组 {group_id}")
            if last_error:
                logger.error(f"最后一次错误类型: {type(last_error).__name__}")
                logger.error(f"最后一次错误信息: {last_error}")
            
            # 提示用户检查配置
            logger.error("请检查:")
            logger.error(f"  1. 机器人是否在群组 {group_id} 中")
            logger.error(f"  2. 机器人是否有发送消息的权限")
            logger.error(f"  3. 群号 {group_id} 是否正确")
            logger.error(f"  4. QQ 适配器是否正常运行")
            logger.error(f"  5. 适配器名称是否正确（查看 AstrBot 配置）")
            
            return False
            
        except Exception as e:
            logger.error(f"发送通知时发生异常: {type(e).__name__}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
