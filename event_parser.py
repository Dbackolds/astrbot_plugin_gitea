"""
事件解析器模块
负责解析 Gitea Webhook 事件载荷
"""
from dataclasses import dataclass
from typing import Dict, Any, Optional
from astrbot.api import logger


@dataclass
class ParsedEvent:
    """解析后的事件数据"""
    event_type: str  # "push", "pull_request", "issues"
    repo_url: str
    repo_name: str
    data: Dict[str, Any]  # 事件特定数据


class EventParser:
    """Gitea Webhook 事件解析器"""
    
    SUPPORTED_EVENTS = {"push", "pull_request", "issues"}
    
    def parse(self, event_type: str, payload: Dict[str, Any]) -> Optional[ParsedEvent]:
        """
        解析 Gitea Webhook 事件载荷
        
        Args:
            event_type: 事件类型 (push, pull_request, issues)
            payload: Webhook 载荷字典
            
        Returns:
            ParsedEvent 对象，如果解析失败则返回 None
        """
        if event_type not in self.SUPPORTED_EVENTS:
            logger.warning(f"不支持的事件类型: {event_type}")
            return None
        
        try:
            # 提取通用仓库信息
            repository = payload.get("repository", {})
            repo_url = repository.get("html_url", "")
            repo_name = repository.get("full_name", "")
            
            if not repo_url or not repo_name:
                logger.error("载荷中缺少仓库信息")
                return None
            
            # 根据事件类型提取特定数据
            if event_type == "push":
                data = self._parse_push_event(payload)
            elif event_type == "pull_request":
                data = self._parse_pull_request_event(payload)
            elif event_type == "issues":
                data = self._parse_issue_event(payload)
            else:
                return None
            
            if data is None:
                return None
            
            return ParsedEvent(
                event_type=event_type,
                repo_url=repo_url,
                repo_name=repo_name,
                data=data
            )
            
        except Exception as e:
            logger.error(f"解析事件时发生错误: {e}")
            return None
    
    def _parse_push_event(self, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        解析 Push 事件
        
        Returns:
            包含 ref, commits, pusher, compare_url 的字典
        """
        try:
            ref = payload.get("ref", "")
            commits = payload.get("commits", [])
            pusher = payload.get("pusher", {})
            compare_url = payload.get("compare_url", "")
            
            # 提取分支名称（从 refs/heads/main 提取 main）
            branch = ref.split("/")[-1] if ref else ""
            
            # 提取推送者信息
            pusher_name = pusher.get("username", pusher.get("login", "Unknown"))
            
            # 提取提交数量和最新提交信息
            commit_count = len(commits)
            latest_commit_message = ""
            if commits:
                latest_commit_message = commits[-1].get("message", "")
            
            return {
                "ref": ref,
                "branch": branch,
                "commits": commits,
                "commit_count": commit_count,
                "latest_commit_message": latest_commit_message,
                "pusher": pusher,
                "pusher_name": pusher_name,
                "compare_url": compare_url
            }
        except Exception as e:
            logger.error(f"解析 Push 事件失败: {e}")
            return None
    
    def _parse_pull_request_event(self, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        解析 Pull Request 事件
        
        Returns:
            包含 action, number, pull_request 的字典
        """
        try:
            action = payload.get("action", "")
            number = payload.get("number", 0)
            pull_request = payload.get("pull_request", {})
            
            # 提取 PR 详细信息
            pr_title = pull_request.get("title", "")
            pr_user = pull_request.get("user", {})
            pr_username = pr_user.get("username", pr_user.get("login", "Unknown"))
            pr_url = pull_request.get("html_url", "")
            
            # 提取分支信息
            base_branch = pull_request.get("base", {}).get("ref", "")
            head_branch = pull_request.get("head", {}).get("ref", "")
            
            return {
                "action": action,
                "number": number,
                "pull_request": pull_request,
                "title": pr_title,
                "username": pr_username,
                "url": pr_url,
                "base_branch": base_branch,
                "head_branch": head_branch
            }
        except Exception as e:
            logger.error(f"解析 Pull Request 事件失败: {e}")
            return None
    
    def _parse_issue_event(self, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        解析 Issue 事件
        
        Returns:
            包含 action, issue 的字典
        """
        try:
            action = payload.get("action", "")
            issue = payload.get("issue", {})
            
            # 提取 Issue 详细信息
            issue_number = issue.get("number", 0)
            issue_title = issue.get("title", "")
            issue_user = issue.get("user", {})
            issue_username = issue_user.get("username", issue_user.get("login", "Unknown"))
            issue_url = issue.get("html_url", "")
            
            return {
                "action": action,
                "issue": issue,
                "number": issue_number,
                "title": issue_title,
                "username": issue_username,
                "url": issue_url
            }
        except Exception as e:
            logger.error(f"解析 Issue 事件失败: {e}")
            return None
