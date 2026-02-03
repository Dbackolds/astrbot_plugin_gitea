"""
Gitea 仓库监控插件
监控 Gitea 仓库的推送、合并请求和议题事件，并发送通知到指定的 QQ 群组
"""
import os
from datetime import datetime
from astrbot.api.star import Context, Star, register
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api import logger

# 导入插件组件
from .config_manager import ConfigManager
from .signature_verifier import SignatureVerifier
from .event_parser import EventParser
from .message_formatter import MessageFormatter
from .notification_sender import NotificationSender
from .webhook_handler import WebhookHandler
from .webhook_server import WebhookServer


@register(
    "astrbot_plugin_gitea",
    "Your Name",
    "监控 Gitea 仓库活动并发送通知到 QQ 群组",
    "1.0.0",
    "https://github.com/Dbackolds/astrbot_plugin_gitea"
)
class GiteaRepoMonitor(Star):
    """Gitea 仓库监控插件主类"""
    
    def __init__(self, context: Context):
        super().__init__(context)
        logger.info("Gitea 仓库监控插件初始化中...")
        
        # 获取插件配置
        plugin_config = context.get_config()
        webhook_host = plugin_config.get("webhook_host", "0.0.0.0")
        webhook_port = plugin_config.get("webhook_port", 8765)
        
        # 初始化配置管理器（使用 AstrBot 标准数据目录）
        # 数据应该存放在 data/plugin_data/{插件名}/ 目录下
        plugin_name = "astrbot_plugin_gitea"
        
        # 获取插件目录
        plugin_dir = os.path.dirname(os.path.abspath(__file__))
        logger.info(f"插件目录: {plugin_dir}")
        
        # 查找 data 目录
        # 插件可能在 /AstrBot/data/addons/plugins/xxx/ 或 /AstrBot/addons/plugins/xxx/
        # 需要找到包含 data 目录的根目录
        current = plugin_dir
        astrbot_root = None
        
        # 向上查找，直到找到包含 data 目录的父目录
        for _ in range(5):  # 最多向上查找5级
            parent = os.path.dirname(current)
            if parent == current:  # 已到达根目录
                break
            
            # 检查当前目录是否是 data 目录
            if os.path.basename(current) == "data":
                astrbot_root = parent
                break
            
            # 检查父目录是否包含 data 目录
            potential_data_dir = os.path.join(parent, "data")
            if os.path.exists(potential_data_dir) and os.path.isdir(potential_data_dir):
                astrbot_root = parent
                break
            
            current = parent
        
        # 如果没找到，使用插件目录的上上级作为备选
        if astrbot_root is None:
            astrbot_root = os.path.dirname(os.path.dirname(plugin_dir))
            logger.warning(f"未找到 data 目录，使用默认根目录: {astrbot_root}")
        
        data_dir = os.path.join(astrbot_root, "data", "plugin_data", plugin_name)
        
        # 确保数据目录存在
        os.makedirs(data_dir, exist_ok=True)
        
        storage_path = os.path.join(data_dir, "monitors.json")
        logger.info(f"AstrBot 根目录: {astrbot_root}")
        logger.info(f"数据目录: {data_dir}")
        logger.info(f"配置文件路径: {storage_path}")
        
        self.config_manager = ConfigManager(storage_path)
        
        # 初始化其他组件
        self.signature_verifier = SignatureVerifier()
        self.event_parser = EventParser()
        self.message_formatter = MessageFormatter()
        self.notification_sender = NotificationSender(context)
        
        # 初始化 Webhook 处理器
        self.webhook_handler = WebhookHandler(
            self.config_manager,
            self.signature_verifier,
            self.event_parser,
            self.message_formatter,
            self.notification_sender
        )
        
        # 初始化 Webhook 服务器
        self.webhook_server = WebhookServer(webhook_host, webhook_port, self.webhook_handler)
        
        # 启动 Webhook 服务器
        try:
            import asyncio
            asyncio.create_task(self.webhook_server.start())
            logger.info("Gitea 仓库监控插件初始化完成")
        except Exception as e:
            logger.error(f"启动 Webhook 服务器失败: {e}")
    
    async def terminate(self):
        """插件卸载时调用"""
        logger.info("Gitea 仓库监控插件正在停止...")
        try:
            await self.webhook_server.stop()
            logger.info("Gitea 仓库监控插件已停止")
        except Exception as e:
            logger.error(f"停止插件时发生错误: {e}")
    
    def _get_monitors(self):
        """获取所有监控配置"""
        # 直接使用 config_manager 获取配置
        return self.config_manager.list_monitors()
    
    def _save_monitors(self, monitors):
        """保存监控配置（已由 config_manager 自动处理）"""
        # 不再需要手动保存，config_manager 会自动保存
        return True
    
    def _find_monitor(self, repo_url):
        """查找指定仓库的监控配置"""
        return self.config_manager.get_monitor(repo_url)
    
    # ==================== 管理指令 ====================
    
    @filter.command_group("gitea")
    def gitea_group(self):
        """Gitea 仓库监控管理指令组"""
        pass
    
    @gitea_group.command("add")
    async def add_monitor(self, event: AstrMessageEvent, repo_url: str, secret: str, group_id: str):
        """
        添加仓库监控配置
        
        用法: /gitea add <repo_url> <secret> <group_id>
        示例: /gitea add https://gitea.example.com/user/repo my_secret_key 123456789
        """
        # 验证参数
        if not repo_url or not secret or not group_id:
            yield event.plain_result("❌ 参数不完整！\n用法: /gitea add <repo_url> <secret> <group_id>")
            return
        
        # 检查是否已存在
        if self._find_monitor(repo_url):
            yield event.plain_result(f"❌ 该仓库的监控配置已存在！\n仓库: {repo_url}")
            return
        
        # 添加监控配置
        success = self.config_manager.add_monitor(repo_url, secret, group_id)
        
        if success:
            yield event.plain_result(f"✅ 成功添加监控配置！\n仓库: {repo_url}\n目标群组: {group_id}\n\n💡 提示：配置已实时保存")
            logger.info(f"通过指令添加监控配置: {repo_url} -> 群组 {group_id}")
        else:
            yield event.plain_result(f"❌ 添加监控配置失败！\n可能原因：保存配置时发生错误")
    
    @gitea_group.command("list")
    async def list_monitors(self, event: AstrMessageEvent):
        """
        列出所有监控配置
        
        用法: /gitea list
        """
        monitors = self.config_manager.list_monitors()
        
        if not monitors:
            yield event.plain_result("📋 当前没有任何监控配置")
            return
        
        message = f"📋 当前监控配置列表（共 {len(monitors)} 个）:\n\n"
        
        for i, config in enumerate(monitors, 1):
            message += f"{i}. {config.repo_url}\n"
            message += f"   目标群组: {config.group_id}\n"
            message += f"   创建时间: {config.created_at}\n\n"
        
        yield event.plain_result(message.strip())
    
    @gitea_group.command("remove")
    async def remove_monitor(self, event: AstrMessageEvent, repo_url: str):
        """
        删除监控配置
        
        用法: /gitea remove <repo_url>
        示例: /gitea remove https://gitea.example.com/user/repo
        """
        if not repo_url:
            yield event.plain_result("❌ 请提供仓库 URL！\n用法: /gitea remove <repo_url>")
            return
        
        # 删除监控配置
        success = self.config_manager.remove_monitor(repo_url)
        
        if success:
            yield event.plain_result(f"✅ 成功删除监控配置！\n仓库: {repo_url}")
            logger.info(f"通过指令删除监控配置: {repo_url}")
        else:
            yield event.plain_result(f"❌ 删除失败！\n该仓库的监控配置不存在")
    
    @gitea_group.command("info")
    async def show_info(self, event: AstrMessageEvent):
        """
        显示 Webhook 配置信息
        
        用法: /gitea info
        """
        plugin_config = self.context.get_config()
        webhook_host = plugin_config.get("webhook_host", "0.0.0.0")
        webhook_port = plugin_config.get("webhook_port", 8765)
        
        message = f"""📖 Gitea Webhook 配置说明

🌐 Webhook URL 格式:
http://你的服务器IP:{webhook_port}/webhook

📝 配置步骤:
1. 在 Gitea 仓库设置中找到 Webhooks
2. 添加新的 Webhook
3. URL 填写上面的 Webhook URL
4. 密钥填写你设置的 secret
5. 选择触发事件: Push, Pull Request, Issues
6. 保存配置

💡 使用指令:
/gitea add <repo_url> <secret> <group_id> - 添加监控
/gitea list - 查看所有监控
/gitea remove <repo_url> - 删除监控
/gitea info - 查看此帮助信息

⚠️ 注意事项:
- 确保服务器端口 {webhook_port} 可从外网访问
- secret 需要与 Gitea Webhook 配置中的密钥一致
- group_id 是目标 QQ 群的群号
- 可以通过指令或 WebUI 配置界面添加监控
- 两种方式添加的配置都会生效"""
        
        yield event.plain_result(message)
