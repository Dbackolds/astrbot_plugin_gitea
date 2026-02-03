"""
签名验证器模块
负责验证 Gitea Webhook 请求的 HMAC-SHA256 签名
"""
import hmac
import hashlib
from astrbot.api import logger


class SignatureVerifier:
    """Webhook 签名验证器"""
    
    def verify(self, payload: bytes, signature: str, secret: str) -> bool:
        """
        验证 Webhook 请求签名
        
        Args:
            payload: 请求体（字节）
            signature: 请求头中的签名
            secret: Webhook 密钥
            
        Returns:
            签名有效返回 True，否则返回 False
        """
        if not signature or not secret:
            logger.warning("签名或密钥为空")
            return False
        
        try:
            # 计算期望的签名
            expected_signature = hmac.new(
                secret.encode('utf-8'),
                payload,
                hashlib.sha256
            ).hexdigest()
            
            # 安全比较签名
            # 使用 hmac.compare_digest 防止时序攻击
            is_valid = hmac.compare_digest(signature, expected_signature)
            
            if not is_valid:
                logger.warning(f"签名验证失败: 期望 {expected_signature}, 收到 {signature}")
            
            return is_valid
            
        except Exception as e:
            logger.error(f"签名验证过程中发生错误: {e}")
            return False
