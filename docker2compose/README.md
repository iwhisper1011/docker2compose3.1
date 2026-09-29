# docker2compose

[![Docker Build](https://github.com/Jackie264/docker2compose/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/Jackie264/docker2compose/actions/workflows/docker-publish.yml)
[![Tests](https://github.com/Jackie264/docker2compose/actions/workflows/test.yml/badge.svg)](https://github.com/Jackie264/docker2compose/actions/workflows/test.yml)
[![Docker Pulls](https://img.shields.io/docker/pulls/jackie264/docker2compose)](https://hub.docker.com/r/jackie264/docker2compose)
[![Docker Image Size](https://img.shields.io/docker/image-size/jackie264/docker2compose/latest)](https://hub.docker.com/r/jackie264/docker2compose)

## 前言

本工具用于读取 NAS 中存量 Docker 容器信息，自动生成对应的 `docker-compose.yaml` 文件。

它会根据容器之间的网络关系（自定义网络或link连接）将相关容器分组，并为每组容器生成一个独立的docker-compose.yaml文件。

# 我的仓库

**1️⃣** ： 中文docker项目集成项目： [https://github.com/coracoo/awesome_docker_cn](https://github.com/coracoo/awesome_docker_cn)

**2️⃣** ： docker转compose：[https://github.com/coracoo/docker2compose](https://github.com/coracoo/docker2compose)

**3️⃣** ： 容器部署iSCSI：[https://github.com/coracoo/d-tgtadm/](https://github.com/coracoo/d-tgtadm/)

**4️⃣** ： 容器端口检查工具： [https://github.com/coracoo/DockPorts/](https://github.com/coracoo/DockPorts)

# 我的频道

### 首发平台——什么值得买：

### [⭐点我关注](https://zhiyou.smzdm.com/member/9674309982/) 

### 微信公众号：

![关注](https://github.com/user-attachments/assets/9a1c4de0-2f08-413f-ab7f-d7d463af1698)

-------------------------------------

## 🆕 v3.2 版本更新

### 新增与交互优化
- **🗑️ 备份记录删除按钮微型化与布局优化**：将原本粗大笨重的删除按钮统一标准化为精致的 `24px × 24px` 微型方圆标（Squircle）；在删除按钮与右侧展开折叠箭头之间增加 `10px` 呼吸间距，杜绝误触与挤压感。
- **🌓 双模主题文字黑白严格统一**：全面优化白天模式（浅色）与夜晚模式（深色）的对比度显示——白天模式下容器列表及备份记录内所有文本强制统一为高对比纯黑色（`#000000`），解决浅色背景下的阅读体验；夜晚模式下全部呈现纯白色（`#ffffff`），风格统一通透。
- **🛡️ 备份文件与目录防误删确认**：升级删除提示框，智能识别删除对象为单独配置文件或整个备份目录树，给出精准的不可逆删除预警。

-------------------------------------

## 🆕 v3.1 版本更新

### 新增与重构
- **🎨 UI/UX 极致重构**：基于 UI/UX Pro Max 规范全新打造的云原生 DevOps 现代化暗色控制台，深度毛玻璃质感、微光边框、Fira Code 编程字体、流线呼吸灯及细腻动效。
- **⚡ 启动任务体系**：全面将原“定时任务”重构升级为“启动任务”，优化调度执行机制与状态指示。
- **🔐 用户系统**：完整的用户权限与会话管理，默认管理员账号 `admin/admin123`，保障 NAS 与生产环境安全。
- **📊 实时调度器**：统一 Python 启动任务调度器，支持手动单次触发与多周期策略。
- **📝 暗色日志终端**：调度器执行日志实时高亮呈现，记录至 `/app/logs/scheduler.log`。
- **🙌 智能参数过滤**：增强关键词过滤，精细化网络、健康检测、入口点、命令、权限展示。

### 代码优化
- 优化前端性能与响应式布局，全面消除未对齐与视觉杂乱问题
- 完善 API 容错与无 Docker 环境下的开发调试体验

-------------------------------------

## 功能特点

- 纯AI打造，有问题提issuse，特殊容器贴原docker cli
- 读取系统中所有Docker容器信息
- 分析容器之间的网络关系（自定义network和link连接）
- 根据网络关系将相关容器分组
- 为每组容器生成对应的docker-compose.yaml文件（根据首个容器名称）
- **智能时区管理**：自动读取配置文件中的时区设置并应用到容器系统，确保定时任务在正确时区执行
- 支持提取容器的各种配置，包括：
  - 容器名称
  - 镜像
  - 端口映射
  - 环境变量
  - 数据卷(volume/bind)
  - 网络(host/bridge/macvlan单独配置，其它网络根据名称在一起)
  - 重启策略
  - 特权模式
  - 硬件设备挂载
  - cap_add 能力
  - command和entrypoint
  - 健康检测
  - 其他配置等等

## 🌐全新的 Web UI 访问

部署完成后，可通过浏览器访问Web界面：
- 本地访问：`http://localhost:5000`
- 局域网访问：`http://你的IP地址:5000`

### Web UI功能特点

- 📊 **容器管理**：实时查看所有Docker容器状态，按网络关系自动分组
- 📄 **Compose预览**：直接在界面中查看生成的docker-compose.yaml文件内容
- ⏰ **调度器监控**：实时监控定时任务状态，查看执行日志
- 🚀 **立即执行**：一键执行compose文件生成任务
- 🗂️ **文件管理**：浏览和管理生成的compose文件目录
- 📝 **日志查看**：查看详细的执行日志，支持清空日志功能
- 🎨 **响应式设计**：采用三栏式布局（容器列表:文件列表:编辑器 = 1:1:2），适配不同屏幕尺寸
- 🔘 **优化界面**："关于我"按钮采用白底设计，提供更好的视觉对比度


**🔻项目首页**
<img width="1859" height="903" alt="总览" src="https://github.com/user-attachments/assets/d43eec83-16da-4a6a-9fff-11ee064a109d" />

**🔻可视化配置编辑**
<img width="1838" height="897" alt="系统设置" src="https://github.com/user-attachments/assets/81a52a1b-7621-4dc5-92fb-c3097256659e" />

**🔻定时任务管理**
<img width="1847" height="872" alt="定时任务" src="https://github.com/user-attachments/assets/37c0a299-39bd-4456-9cf1-537afd31f61c" />

### 配置文件说明 (/app/config.json)
```
  "// CRON": "定时执行配置: '0 2 * * *'(每天凌晨2点), 'manual'(手动), 'once'(执行一次), 或自定义CRON",
  "CRON": "0 2 * * *",
  
  "// NETWORK": "控制bridge网络配置的显示方式: true(显示) 或 false(隐藏)",
  "NETWORK": "true",
  
  "// SHOW_HEALTHCHECK": "控制healthcheck配置的显示方式: true(显示) 或 false(隐藏)",
  "SHOW_HEALTHCHECK": "true",
  
  "// SHOW_CAP_ADD": "控制cap_add配置的显示方式: true(显示) 或 false(隐藏)",
  "SHOW_CAP_ADD": "true",
  
  "// SHOW_COMMAND": "控制command配置的显示方式: true(显示) 或 false(隐藏)",
  "SHOW_COMMAND": "true",
  
  "// SHOW_ENTRYPOINT": "控制entrypoint配置的显示方式: true(显示) 或 false(隐藏)",
  "SHOW_ENTRYPOINT": "true",
  
  "// ENV_FILTER_KEYWORDS": "环境变量过滤关键词，逗号分隔。匹配这些关键词的环境变量将被过滤掉",
  "ENV_FILTER_KEYWORDS": "VERSION",
  
  "// TZ": "时区设置,如Asia/Shanghai、Europe/London等",
  "TZ": "Asia/Shanghai"
```

### 输出目录说明

- `/app/compose`: 脚本输出目录，默认值为`/app/compose`
- `/app/compose/YYYY_MM_DD_HH_MM`: 定时任务输出目录，格式为`YYYY_MM_DD_HH_MM`，例如`2023_05_04_15_00`
- `/app/logs`：定时任务日志

### 输出说明

- 对于单个独立的容器，生成的文件名格式为：`{容器名}.yaml`
- 对于有网络关系的容器组，生成的文件名格式为：`{第一个容器名前缀}-group.yaml`
- 所有生成的文件都会保存在`compose/时间戳`目录下

### 注意事项

- 该工具需要Docker命令行权限才能正常工作
- 生成的docker-compose.yaml文件可能需要手动调整以满足特定需求
- 通过Docker运行时，会将宿主机的Docker套接字挂载到容器中，以便获取容器信息
- 工具支持定时执行，默认`once`（只执行一次），可通过CRON环境变量自定义执行时间
- **时区配置重要提醒**：
  - 容器启动时会自动读取 `config.json` 中的TZ配置并应用到系统
  - 如果定时任务时间不准确，请检查TZ配置是否正确
  - 可通过 `docker exec d2c-container date` 命令验证容器内时区是否正确
- 关于Macvlan网络，DHCP的理论上会展示`macvlan:{}`，
- 对于使用默认bridge网络但没有显式link的容器，它们可能会被分到不同的组中
- 工具会将自定义网络标记为`external: true`，因为它假设这些网络已经存在

-------------------------------------

# 使用方法(docker部署)

## 支持的平台
- `linux/amd64`
- `linux/arm64` 
- `linux/arm/v7`

## 启用前确保系统安装了docker

**🔻docker cli启动**
```bash
docker run -itd --name docker2compose \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  -v /{path}/d2c/compose:/app/compose \
  -v /{path}/d2c/logs:/app/logs \
  -v /{path}/d2c/config:/app/config \
  -p 5000:5000 \
  -e TZ=Asia/Shanghai \
  # -e DOCKER_API_VERSION=1.41 \ # 群晖等 docker版本比较老的，加这个参数控制 docker api 版本
  coracoo/docker2compose:latest
```

**🔻docker compose启动**
```yaml
services:
  d2c:
    image: coracoo/docker2compose:latest
    container_name: docker2compose
    ports:
      - "5000:5000"  # Web UI端口
    environment:
      - TZ=Asia/Shanghai  # 可选，时区设置
      - DOCKER_API_VERSION=1.41 # 群晖等 docker版本比较老的，加这个参数控制 docker api 版本
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - /{path}/d2c/compose:/app/compose
      - /{path}/d2c/logs:/app/logs
      - /{path}/d2c/config:/app/config
```

