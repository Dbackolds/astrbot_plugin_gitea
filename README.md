# Gitea 仓库监控插件

监控 Gitea 仓库的推送、合并请求和议题事件，并实时发送通知到指定的 QQ 群组。

## 功能特性

- 🔔 **实时通知**: 监控 Gitea 仓库的 Push、Pull Request 和 Issue 事件
- 🎯 **精准推送**: 每个仓库可配置独立的通知群组
- 🔐 **安全验证**: 使用 HMAC-SHA256 验证 Webhook 签名
- 🔗 **智能匹配**: 支持不同域名的相同仓库自动匹配（如内网和外网地址）
- 📝 **清晰格式**: 使用 emoji 和结构化格式展示事件信息
- ⚙️ **简单管理**: 通过指令轻松管理监控配置

## 安装

1. 将插件文件放置到 AstrBot 的插件目录
2. 安装依赖：`pip install -r requirements.txt`
3. 重启 AstrBot

## 配置

### 插件配置

在 AstrBot 管理面板中配置插件：

- **webhook_port**: Webhook 服务器监听端口（默认：8765）
- **webhook_host**: Webhook 服务器监听地址（默认：0.0.0.0）

### Gitea Webhook 配置

1. 在 Gitea 仓库中进入 **设置 → Webhooks**
2. 点击 **添加 Webhook**
3. 填写配置：
   - **目标 URL**: `http://你的服务器IP:端口/webhook`
   - **密钥**: 自定义密钥（需要记住，后续添加监控时使用）
   - **触发事件**: 选择 `Push`、`Pull Request`、`Issues`
   - **激活**: 勾选
4. 点击 **添加 Webhook**

## 使用指令

所有指令需要管理员权限。

### 添加监控配置

```
/gitea add <repo_url> <secret> <group_id>
```

**参数说明**:
- `repo_url`: Gitea 仓库的完整 URL（例如：`https://gitea.example.com/user/repo`）
- `secret`: Webhook 密钥（与 Gitea Webhook 配置中的密钥一致）
- `group_id`: 目标 QQ 群号

**示例**:
```
/gitea add https://gitea.example.com/user/myproject my_secret_key 123456789
```

### 查看所有监控配置

```
/gitea list
```

显示当前所有的监控配置，包括仓库 URL、目标群组和创建时间。

### 删除监控配置

```
/gitea remove <repo_url>
```

**示例**:
```
/gitea remove https://gitea.example.com/user/myproject
```

### 查看帮助信息

```
/gitea info
```

显示 Webhook 配置说明和使用指南。

## 通知消息格式

### Push 事件

```
📦 [仓库名] 新推送
🌿 分支: main
👤 推送者: username
📝 提交数: 3
💬 最新提交: Fix bug in parser
🔗 查看详情: [URL]
```

### Pull Request 事件

```
�  [仓库名] 合并请求
� #新123: Add new feature
� 发起者: usern]ame
🎯 目标分支: main ← feature-branch
✅ 状态: 打开
🔗 查看详情: [URL]
```

### Issue 事件

```
🐛 [仓库名] 议题
📋 #456: Bug report
� 发起详者: username
✅ 状态: 打开
🔗 查看详情: [URL]
```

## 常见问题

### Q: 仓库有多个访问地址怎么办？

**A**: 插件支持智能路径匹配！例如：
- 添加配置时使用: `http://internal.server:3000/user/repo`
- Gitea Webhook 发送: `https://git.example.com/user/repo`
- 只要仓库路径（`user/repo`）相同，就能自动匹配成功

### Q: Webhook 无法接收到请求？

**A**: 请检查：
1. 服务器防火墙是否开放了配置的端口
2. Gitea 服务器能否访问到你的 AstrBot 服务器
3. Webhook URL 是否正确配置
4. 查看 AstrBot 日志是否有错误信息

### Q: 收到 "签名验证失败" 错误？

**A**: 请确保：
1. 添加监控配置时使用的 `secret` 与 Gitea Webhook 配置中的密钥完全一致
2. 没有多余的空格或特殊字符

### Q: 消息没有发送到群组？

**A**: 请检查：
1. 群号是否正确
2. 机器人是否在该群组中
3. 机器人是否有发送消息的权限
4. 查看 AstrBot 日志中的错误信息

### Q: 如何修改 Webhook 端口？

**A**: 在 AstrBot 管理面板中找到插件配置，修改 `webhook_port` 参数，然后重启 AstrBot。

### Q: 支持哪些 Gitea 版本？

**A**: 理论上支持所有支持 Webhook 的 Gitea 版本（1.0+）。推荐使用 Gitea 1.13 及以上版本。

## 技术架构

插件采用模块化设计，主要组件包括：

- **ConfigManager**: 配置管理器，负责监控配置的增删改查和持久化
- **SignatureVerifier**: 签名验证器，验证 Webhook 请求的 HMAC-SHA256 签名
- **EventParser**: 事件解析器，解析 Gitea Webhook 事件载荷
- **MessageFormatter**: 消息格式化器，将事件格式化为可读的通知消息
- **NotificationSender**: 通知发送器，将消息发送到目标 QQ 群组
- **WebhookHandler**: Webhook 处理器，协调各组件处理请求
- **WebhookServer**: HTTP 服务器，接收 Gitea Webhook 请求

### 数据存储

配置数据存储在 AstrBot 的标准数据目录：
```
data/plugin_data/astrbot_plugin_gitea/monitors.json
```

这确保了数据的持久化和与其他插件的隔离。

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 作者

Your Name

## 更新日志

### v1.0.1 (2026-02-03)

- ✨ 新增智能 URL 匹配功能，支持不同域名的相同仓库自动匹配
- 🐛 修复配置存储位置不一致导致的查询失败问题
- 📝 改进日志输出，便于调试

### v1.0.0 (2026-02-03)

- 初始版本发布
- 支持 Push、Pull Request 和 Issue 事件监控
- 支持多仓库配置
- 实现签名验证
- 提供管理指令
