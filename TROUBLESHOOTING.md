# 故障排查指南

## 数据持久化问题

### 问题描述
配置添加后重启插件丢失，数据没有持久化保存。

### 正确的数据存储位置

根据 AstrBot 的规范，插件数据应该存放在：
```
data/plugin_data/astrbot_plugin_gitea/monitors.json
```

**不是**存放在插件目录下！

### 已实施的修复

1. **使用正确的数据目录**
   - 数据存放在 `data/plugin_data/astrbot_plugin_gitea/`
   - 自动创建数据目录（如果不存在）
   - 使用绝对路径避免路径问题

2. **增强日志输出**
   - 启动时显示插件目录、AstrBot 根目录、数据目录
   - 保存时显示文件大小和状态
   - 加载时显示配置数量

3. **添加错误追踪**
   - 保存/加载失败时输出完整的错误堆栈
   - 验证文件是否真的被创建

### 如何验证

重启插件后，查看日志中的以下信息：

```
[Plug] [INFO] 插件目录: /path/to/addons/plugins/astrbot_plugin_gitea
[Plug] [INFO] AstrBot 根目录: /path/to/astrbot
[Plug] [INFO] 数据目录: /path/to/astrbot/data/plugin_data/astrbot_plugin_gitea
[Plug] [INFO] 配置文件路径: /path/to/astrbot/data/plugin_data/astrbot_plugin_gitea/monitors.json
```

添加配置后，应该看到：

```
[Plug] [INFO] 准备保存配置到: .../data/plugin_data/astrbot_plugin_gitea/monitors.json
[Plug] [INFO] 配置数量: 1
[Plug] [INFO] 配置已成功保存到 .../monitors.json
[Plug] [INFO] 文件已创建，大小: XXX 字节
```

重启后加载配置时，应该看到：

```
[Plug] [INFO] 尝试从 .../data/plugin_data/astrbot_plugin_gitea/monitors.json 加载配置
[Plug] [INFO] 成功加载 1 个监控配置
```

### 可能的原因

1. **权限问题**
   - data 目录没有写入权限
   - 解决方案：检查目录权限，确保 AstrBot 进程有写入权限

2. **路径问题**
   - 插件目录结构不标准
   - 解决方案：确保插件在 `addons/plugins/astrbot_plugin_gitea/` 目录下

3. **文件系统问题**
   - 磁盘空间不足
   - 文件系统只读
   - 解决方案：检查磁盘空间和文件系统状态

### 手动检查

1. 查找配置文件（应该在 data 目录下）：
   ```bash
   # Windows
   dir /s data\plugin_data\astrbot_plugin_gitea\monitors.json
   
   # Linux/Mac
   find data -name "monitors.json"
   ```

2. 检查文件内容：
   ```bash
   # Windows
   type data\plugin_data\astrbot_plugin_gitea\monitors.json
   
   # Linux/Mac
   cat data/plugin_data/astrbot_plugin_gitea/monitors.json
   ```

3. 检查目录结构：
   ```bash
   # Windows
   tree data\plugin_data /F
   
   # Linux/Mac
   tree data/plugin_data
   ```

### 临时解决方案

如果持久化仍然失败，可以手动创建配置文件：

1. 在 AstrBot 根目录创建目录结构：
   ```bash
   # Windows
   mkdir data\plugin_data\astrbot_plugin_gitea
   
   # Linux/Mac
   mkdir -p data/plugin_data/astrbot_plugin_gitea
   ```

2. 在该目录下创建 `monitors.json` 文件，添加以下内容：

```json
{
  "monitors": [
    {
      "repo_url": "https://your-gitea.com/user/repo",
      "secret": "your_secret_key",
      "group_id": "123456789",
      "created_at": "2026-02-03T15:00:00"
    }
  ]
}
```

3. 保存文件并重启插件

### 联系支持

如果问题仍然存在，请提供以下信息：

1. 完整的日志输出（包括启动、添加配置、重启的日志）
2. 操作系统和 AstrBot 版本
3. 插件目录的完整路径
4. data 目录的完整路径
5. 是否使用容器或虚拟环境
