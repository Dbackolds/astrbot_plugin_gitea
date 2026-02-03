"""
消息格式化器模块
负责将解析的事件格式化为可读的通知消息
"""
from .event_parser import ParsedEvent
from astrbot.api import logger


class MessageFormatter:
    """消息格式化器"""
    
    def format(self, event: ParsedEvent) -> str:
        """
        格式化事件为通知消息
        
        Args:
            event: 解析后的事件对象
            
        Returns:
            格式化的消息字符串
        """
        try:
            if event.event_type == "push":
                return self._format_push_event(event)
            elif event.event_type == "pull_request":
                return self._format_pull_request_event(event)
            elif event.event_type == "issues":
                return self._format_issue_event(event)
            else:
                logger.warning(f"不支持的事件类型: {event.event_type}")
                return f"收到未知类型的事件: {event.event_type}"
                
        except Exception as e:
            logger.error(f"格式化消息时发生错误: {e}")
            return f"格式化消息失败: {str(e)}"
    
    def _format_push_event(self, event: ParsedEvent) -> str:
        """
        格式化 Push 事件消息
        
        Returns:
            格式化的消息字符串
        """
        data = event.data
        branch = data.get("branch", "unknown")
        pusher_name = data.get("pusher_name", "Unknown")
        commit_count = data.get("commit_count", 0)
        latest_commit_message = data.get("latest_commit_message", "")
        compare_url = data.get("compare_url", "")
        
        # 截断过长的提交消息
        if len(latest_commit_message) > 100:
            latest_commit_message = latest_commit_message[:100] + "..."
        
        message = f"""📦 [{event.repo_name}] 新推送
🌿 分支: {branch}
👤 推送者: {pusher_name}
📝 提交数: {commit_count}"""
        
        if latest_commit_message:
            message += f"\n💬 最新提交: {latest_commit_message}"
        
        if compare_url:
            message += f"\n🔗 查看详情: {compare_url}"
        
        return message
    
    def _format_pull_request_event(self, event: ParsedEvent) -> str:
        """
        格式化 Pull Request 事件消息
        
        Returns:
            格式化的消息字符串
        """
        data = event.data
        action = data.get("action", "unknown")
        number = data.get("number", 0)
        title = data.get("title", "")
        username = data.get("username", "Unknown")
        base_branch = data.get("base_branch", "")
        head_branch = data.get("head_branch", "")
        url = data.get("url", "")
        
        # 操作类型映射
        action_map = {
            "opened": "打开",
            "closed": "关闭",
            "reopened": "重新打开",
            "synchronized": "更新",
            "edited": "编辑",
            "assigned": "分配",
            "unassigned": "取消分配",
            "review_requested": "请求审查",
            "review_request_removed": "取消审查请求",
            "labeled": "添加标签",
            "unlabeled": "移除标签",
            "merged": "合并"
        }
        action_text = action_map.get(action, action)
        
        message = f"""🔀 [{event.repo_name}] 合并请求
📋 #{number}: {title}
👤 发起者: {username}
✅ 状态: {action_text}"""
        
        if base_branch and head_branch:
            message += f"\n🎯 目标分支: {base_branch} ← {head_branch}"
        
        if url:
            message += f"\n🔗 查看详情: {url}"
        
        return message
    
    def _format_issue_event(self, event: ParsedEvent) -> str:
        """
        格式化 Issue 事件消息
        
        Returns:
            格式化的消息字符串
        """
        data = event.data
        action = data.get("action", "unknown")
        number = data.get("number", 0)
        title = data.get("title", "")
        username = data.get("username", "Unknown")
        url = data.get("url", "")
        
        # 操作类型映射
        action_map = {
            "opened": "打开",
            "closed": "关闭",
            "reopened": "重新打开",
            "edited": "编辑",
            "assigned": "分配",
            "unassigned": "取消分配",
            "labeled": "添加标签",
            "unlabeled": "移除标签",
            "milestoned": "添加里程碑",
            "demilestoned": "移除里程碑"
        }
        action_text = action_map.get(action, action)
        
        message = f"""🐛 [{event.repo_name}] 议题
📋 #{number}: {title}
👤 发起者: {username}
✅ 状态: {action_text}"""
        
        if url:
            message += f"\n🔗 查看详情: {url}"
        
        return message
