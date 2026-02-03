"""
Webhook 处理器模块
负责处理 Gitea Webhook 请求，协调签名验证、事件解析和消息发送
"""
import json
from typing import Dict, Any
from astrbot.api import logger
from .config_manager import ConfigManager
from .signature_verifier import SignatureVerifier
from .event_parser import EventParser
from .message_formatter import MessageFormatter
from .notification_sender import NotificationSender


class WebhookHandler:
    """Webhook 处理器"""
    
    def __init__(
        self,
        config_manager: ConfigManager,
        signature_verifier: SignatureVerifier,
        event_parser: EventParser,
        message_formatter: MessageFormatter,
        notification_sender: NotificationSender
    ):
        """
        初始化 Webhook 处理器
        
        Args:
            config_manager: 配置管理器
            signature_verifier: 签名验证器
            event_parser: 事件解析器
            message_formatter: 消息格式化器
            notification_sender: 通知发送器
        """
        self.config_manager = config_manager
        self.signature_verifier = signature_verifier
        self.event_parser = event_parser
        self.message_formatter = message_formatter
        self.notification_sender = notification_sender
    
    async def process_webhook(self, headers: Dict[str, str], body: bytes) -> Dict[str, Any]:
        """
        处理 Webhook 请求
        
        Args:
            headers: 请求头字典
            body: 请求体（字节）
            
        Returns:
            处理结果字典，包含 status 和 message
        """
        try:
            # 提取事件类型和签名
            event_type = headers.get("X-Gitea-Event", "").lower()
            signature = headers.get("X-Gitea-Signature", "")
            
            if not event_type:
                logger.warning("请求头中缺少 X-Gitea-Event")
                return {"status": "error", "message": "Missing X-Gitea-Event header"}
            
            logger.info(f"收到 Webhook 请求: 事件类型 = {event_type}")
            
            # 解析载荷
            try:
                payload = json.loads(body.decode('utf-8'))
            except Exception as e:
                logger.error(f"解析载荷失败: {e}")
                return {"status": "error", "message": "Invalid JSON payload"}
            
            # 提取仓库 URL
            repository = payload.get("repository", {})
            repo_url = repository.get("html_url", "")
            
            if not repo_url:
                logger.error("载荷中缺少仓库 URL")
                return {"status": "error", "message": "Missing repository URL"}
            
            # 查找仓库配置
            config = self.config_manager.get_monitor(repo_url)
            
            if not config:
                logger.warning(f"未找到仓库 {repo_url} 的监控配置")
                return {"status": "ignored", "message": "Repository not monitored"}
            
            logger.info(f"找到监控配置: repo_url={repo_url}, group_id={config.group_id}")
            
            # 验证签名
            logger.debug(f"使用密钥验证签名: {config.secret[:5]}...")
            
            if not self.signature_verifier.verify(body, signature, config.secret):
                logger.warning(f"签名验证失败: {repo_url}")
                return {"status": "error", "message": "Invalid signature"}
            
            # 解析事件
            parsed_event = self.event_parser.parse(event_type, payload)
            
            if not parsed_event:
                logger.warning(f"不支持的事件类型或解析失败: {event_type}")
                return {"status": "ignored", "message": f"Unsupported event type: {event_type}"}
            
            # 格式化消息
            message = self.message_formatter.format(parsed_event)
            logger.info(f"格式化后的消息: {message[:100]}...")
            
            # 发送通知
            logger.info(f"准备发送到群组: {config.group_id}")
            
            success = await self.notification_sender.send(config.group_id, message)
            
            if success:
                return {"status": "success", "message": "Notification sent"}
            else:
                return {"status": "error", "message": "Failed to send notification"}
                
        except Exception as e:
            logger.error(f"处理 Webhook 时发生错误: {e}")
            return {"status": "error", "message": str(e)}
