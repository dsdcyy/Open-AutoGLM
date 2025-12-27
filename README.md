# Open-AutoGLM Web Control

> 基于 [Open-AutoGLM](https://github.com/THUDM/AutoGLM) 项目开发的 Web 控制界面

## 项目说明

本项目基于清华大学开源的 **Open-AutoGLM** 项目构建，**未对原始核心代码进行任何修改**，仅在其基础上扩展了以下功能：

- ✨ **Web 控制界面**：提供友好的 Web UI，可通过浏览器控制手机操作
- 🐋 **Docker 容器化部署**：支持 Docker 和 Docker Compose 一键部署
- 🔄 **实时日志流**：在 Web 界面实时查看 Agent 的思考过程和执行步骤
- 📸 **截图展示**：实时显示手机屏幕截图和当前执行的操作
- 🎨 **现代化 UI**：采用 TailwindCSS 设计的暗色主题界面
- 🔧 **可调整布局**：支持左右面板宽度自由调整
- 🧹 **一键清除**：支持清除日志和截图记录

## 主要特性

### Web 界面功能

1. **实时监控**

   - 查看 Agent 当前活动状态
   - 显示最后执行的操作
   - 实时展示手机屏幕截图

2. **任务控制**

   - 通过 Web 表单输入任务指令
   - 支持中文自然语言指令
   - 实时查看任务执行进度

3. **日志系统**
   - 实时打字机效果显示思考过程
   - 区分用户消息和系统日志
   - 支持一键清除历史记录

### 部署方式

- **本地运行**：传统 Python 虚拟环境方式
- **Docker 部署**：单容器快速启动
- **Docker Compose**：一键编排部署

## 安装与使用

### 方式一：本地运行

#### 1. 环境要求

- Python 3.10+
- ADB (Android Debug Bridge)
- USB 连接的 Android 设备（已开启 USB 调试）

#### 2. 安装步骤

```bash
# 克隆本仓库
git clone <your-repo-url>
cd Open-AutoGLM

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 验证 ADB 连接
adb devices
```

#### 3. 启动 Web 服务

```bash
# 默认端口 8001
python web_ui/main.py

# 自定义端口
python web_ui/main.py --port 9000
```

#### 4. 访问界面

打开浏览器访问：`http://localhost:8001`

在设置页面输入：

- **Model API URL**: 你的 GLM API 地址
- **Model Name**: 模型名称（如 `glm-4-plus`）
- **API Key**: 你的 API 密钥

---

### 方式二：Docker 部署

#### 1. 构建镜像

```bash
# 构建 Docker 镜像
docker build -t autoglm-control:latest .
```

#### 2. 运行容器

**推荐使用 Host 网络模式**（已验证可访问宿主机 ADB）：

```bash
docker run -d \
  --name autoglm \
  --network host \
  -e PORT=9000 \
  autoglm-control:latest
```

访问：`http://localhost:9000`

**其他选项**：

```bash
# 使用环境变量
docker run -d \
  --name autoglm \
  --network host \
  -e PORT=9000 \
  autoglm-control:latest

# 后台查看日志
docker logs -f autoglm

# 停止容器
docker stop autoglm

# 删除容器
docker rm autoglm
```

---

### 方式三：Docker Compose（推荐）

#### 1. 启动服务

```bash
# 启动（后台运行）
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

#### 2. 自定义配置

编辑 `docker-compose.yml` 修改端口或其他配置：

```yaml
environment:
  - PORT=9000 # 修改为你想要的端口
```

详细使用说明请参考：[DOCKER_COMPOSE_GUIDE.md](./DOCKER_COMPOSE_GUIDE.md)

---

## 使用说明

### 初次使用

1. **连接手机**

   ```bash
   # 确保 ADB 可以检测到设备
   adb devices

   # 应该看到类似输出：
   # List of devices attached
   # 3a056818    device
   ```

2. **访问 Web 界面**

   - 打开浏览器访问 `http://localhost:8001`（或你设置的端口）

3. **配置 API**

   - 在设置页面输入 GLM API 相关信息
   - 点击 "Check System" 验证 ADB 和键盘状态

4. **执行任务**
   - 在主界面输入框输入任务，例如：
     - "打开抖音"
     - "搜索美食视频"
     - "在微信给张三发消息说你好"

### 界面功能

#### 左侧：任务控制区

- **输入框**：输入自然语言任务指令
- **日志区域**：实时显示 Agent 思考过程和执行日志

#### 右侧：状态监控区

- **当前活动**：显示 Agent 当前状态
- **最后操作**：显示最近执行的动作
- **屏幕截图**：实时显示手机屏幕状态

#### 顶部工具栏

- **Clear All**：清除所有日志和截图
- **Exit**：返回首页

---

## 技术栈

### 后端

- **FastAPI**: Web 框架
- **Uvicorn**: ASGI 服务器
- **WebSocket**: 实时通信
- **Open-AutoGLM**: 核心 Agent 引擎

### 前端

- **Pure HTML/CSS/JavaScript**: 无框架依赖
- **TailwindCSS**: UI 样式（通过 CDN）
- **WebSocket API**: 实时数据流

### 容器化

- **Docker**: 容器化运行环境
- **Docker Compose**: 服务编排

---

## 项目结构

```
Open-AutoGLM/
├── web_ui/                    # Web 界面模块（新增）
│   ├── main.py               # FastAPI 服务入口
│   ├── agent_manager.py      # Agent 管理器
│   └── templates/            # HTML 模板
│       ├── index.html        # 设置页面
│       └── app.html          # 主控制界面
├── phone_agent/              # 原 AutoGLM 核心代码（未修改）
│   ├── agent.py             # Agent 核心逻辑
│   ├── adb/                 # ADB 相关功能
│   ├── actions/             # 操作执行模块
│   └── ...
├── Dockerfile                # Docker 镜像构建文件（新增）
├── docker-compose.yml        # Docker Compose 配置（新增）
├── .dockerignore            # Docker 忽略文件（新增）
├── requirements.txt          # Python 依赖（已更新 Web 依赖）
└── README.md                # 本说明文档
```

---

## 常见问题

### 1. ADB 设备检测不到

**问题**：Web 界面显示 ADB 连接失败

**解决方案**：

```bash
# 检查宿主机 ADB
adb devices

# 重启 ADB 服务
adb kill-server
adb start-server

# 确保手机已开启 USB 调试并授权
```

### 2. Docker 容器无法访问 ADB

**问题**：容器内 `adb devices` 无设备

**解决方案**：

- 确保使用 `--network host` 模式
- 或参考 [测试报告](#docker-adb-access-test) 的建议配置

### 3. 端口冲突

**问题**：`Address already in use`

**解决方案**：

```bash
# 方式1：更换端口
python web_ui/main.py --port 9001

# 方式2：查找并停止占用端口的进程
lsof -i :8001
kill -9 <PID>
```

### 4. 页面显示不正常

**问题**：CSS 样式未加载

**解决方案**：

- 检查网络连接（TailwindCSS 通过 CDN 加载）
- 清除浏览器缓存并刷新

---

## 致谢

- 感谢 [THUDM](https://github.com/THUDM) 团队开源的 [AutoGLM](https://github.com/THUDM/AutoGLM) 项目
- 本项目在原项目基础上仅添加了 Web 界面和容器化部署功能，核心 Agent 逻辑完全基于原项目

---

## 许可证

本项目遵循原 Open-AutoGLM 项目的许可证。

---

## 更新日志

### v1.3 (2025-12-27)

- ✅ 添加 Docker 支持
- ✅ 添加 Docker Compose 配置
- ✅ 测试并验证 Host 网络模式访问 ADB
- ✅ 优化导入顺序以支持容器化部署

### v1.2 (2025-12-26)

- ✅ 实现实时截图显示
- ✅ 添加步骤回调机制
- ✅ 优化 WebSocket 日志流

### v1.0 (2025-12-26)

- ✅ 初始版本
- ✅ Web 界面基础功能
- ✅ 实时日志流
- ✅ 任务控制
