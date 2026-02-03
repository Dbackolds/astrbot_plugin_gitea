"""
Webhook 服务器模块
负责启动和管理 HTTP 服务器，接收 Gitea Webhook 请求
"""
import asyncio
from aiohttp import web
from astrbot.api import logger
from .webhook_handler import WebhookHandler


class WebhookServer:
    """Webhook HTTP 服务器"""
    
    def __init__(self, host: str, port: int, handler: WebhookHandler):
        """
        初始化 Webhook 服务器
        
        Args:
            host: 监听地址
            port: 监听端口
            handler: Webhook 处理器
        """
        self.host = host
        self.port = port
        self.handler = handler
        self.app = None
        self.runner = None
        self.site = None
    
    async def start(self) -> None:
        """启动 HTTP 服务器"""
        try:
            # 创建 aiohttp 应用
            self.app = web.Application()
            
            # 注册路由
            self.app.router.add_post('/webhook', self.handle_webhook)
            
            # 创建 runner
            self.runner = web.AppRunner(self.app)
            await self.runner.setup()
            
            # 创建 site 并启动
            self.site = web.TCPSite(self.runner, self.host, self.port)
            await self.site.start()
            
            logger.info(f"Webhook 服务器已启动: http://{self.host}:{self.port}/webhook")
            
        except OSError as e:
            if "address already in use" in str(e).lower() or "10048" in str(e):
                logger.error(f"端口 {self.port} 已被占用，请修改配置使用其他端口")
                raise
            else:
                logger.error(f"启动 Webhook 服务器失败: {e}")
                raise
        except Exception as e:
            logger.error(f"启动 Webhook 服务器时发生错误: {e}")
            raise
    
    async def stop(self) -> None:
        """停止 HTTP 服务器"""
        try:
            if self.site:
                await self.site.stop()
                logger.info("Webhook 服务器 site 已停止")
            
            if self.runner:
                await self.runner.cleanup()
                logger.info("Webhook 服务器 runner 已清理")
            
            logger.info("Webhook 服务器已停止")
            
        except Exception as e:
            logger.error(f"停止 Webhook 服务器时发生错误: {e}")
    
    async def handle_webhook(self, request: web.Request) -> web.Response:
        """
        处理 Webhook 请求
        
        Args:
            request: aiohttp 请求对象
            
        Returns:
            aiohttp 响应对象
        """
        try:
            # 提取请求头
            headers = dict(request.headers)
            
            # 读取请求体
            body = await request.read()
            
            # 调用处理器
            result = await self.handler.process_webhook(headers, body)
            
            # 根据处理结果返回响应
            status = result.get("status", "error")
            message = result.get("message", "Unknown error")
            
            if status == "success":
                return web.Response(
                    status=200,
                    text=message,
                    content_type='text/plain'
                )
            elif status == "ignored":
                # 不支持的事件类型或未监控的仓库，返回 200 避免 Gitea 重试
                return web.Response(
                    status=200,
                    text=message,
                    content_type='text/plain'
                )
            elif status == "error":
                if "signature" in message.lower():
                    # 签名验证失败，返回 401
                    return web.Response(
                        status=401,
                        text=message,
                        content_type='text/plain'
                    )
                else:
                    # 其他错误，返回 400
                    return web.Response(
                        status=400,
                        text=message,
                        content_type='text/plain'
                    )
            else:
                return web.Response(
                    status=500,
                    text="Internal server error",
                    content_type='text/plain'
                )
                
        except Exception as e:
            logger.error(f"处理 Webhook 请求时发生异常: {e}")
            return web.Response(
                status=500,
                text=f"Internal server error: {str(e)}",
                content_type='text/plain'
            )
