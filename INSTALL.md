# Gitea 仓库监控插件 - 安装指南

## 快速安装

### 步骤 1: 安装依赖

```bash
D:\Environment\Python3.14.2\python.exe -m pip install aiohttp>=3.9.0 hypothesis>=6.0.0 pytest-asyncio>=0.21.0
```

### 步骤 2: 安装插件

#### 方法 A: 通过 AstrBot WebUI（推荐）

1. 打开 AstrBot 管理面板
2. 进入 **插件管理**
3. 点击 **安装插件**
4. 选择 **从本地文件夹安装**
5. 选择 `D:\ProjectCode\GiteaBot\gitea-repo-monitor` 文件夹
6. AstrBot 会自动安装插件

#### 方法 B: 手动安装

在项目根目录执行：

```powershell
Copy-Item -Path "gitea-repo-monitor" -Destination "data\plugins\gitea-repo-monitor" -Recurse -Force
```

然后重启 AstrBot。

### 步骤 3: 验证安装

重启 AstrBot 后，在 QQ 群中发送：

```
/gitea info
```

如果收到帮助信息，说明插件安装成功！

## 配置 Gitea Webhook

1. 进入 Gitea 仓库设置 → Webhooks
2. 添加新 Webhook：
   - URL: `http://你的服务器IP:8765/webhook`
   - 密钥: 自定义（记住这个密钥）
   - 触发事件: Push, Pull Request, Issues
3. 保存

## 添加监控

在 QQ 群中发送（需要管理员权限）：

```
/gitea add https://你的gitea地址/用户名/仓库名 你的密钥 群号
```

示例：
```
/gitea add https://gitea.example.com/user/repo my_secret_key 123456789
```

## 常见问题

### 导入错误已修复

✅ 所有模块导入已改为相对导入（使用 `.` 前缀）
✅ 插件现在可以正常加载

### 如果仍然出现问题

1. 确保所有文件都在 `data/plugins/gitea-repo-monitor/` 目录下
2. 检查 `__init__.py` 文件是否存在
3. 重启 AstrBot
4. 查看 AstrBot 日志获取详细错误信息

## 文件清单

确保以下文件都存在：

- `__init__.py`
- `main.py`
- `config_manager.py`
- `signature_verifier.py`
- `event_parser.py`
- `message_formatter.py`
- `notification_sender.py`
- `webhook_handler.py`
- `webhook_server.py`
- `metadata.yaml`
- `_conf_schema.json`
- `requirements.txt`
- `README.md`
