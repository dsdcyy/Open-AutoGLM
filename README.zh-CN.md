# Open-AutoGLM Web Control

> 基于 [Open-AutoGLM](https://github.com/THUDM/AutoGLM) 开发的 Web 控制界面和 Docker 容器化方案

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Supported-2496ED?logo=docker)](Dockerfile)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python)](requirements.txt)

## 🌟 项目简介

本项目在清华大学开源的 [Open-AutoGLM](https://github.com/THUDM/AutoGLM) 基础上，**未修改核心源码**，仅扩展了以下功能：

- 🌐 **Web 控制界面** - 通过浏览器远程控制手机操作
- 🐋 **Docker 容器化** - 支持 Docker 和 Docker Compose 一键部署
- 📊 **实时监控** - 查看 Agent 思考过程、执行步骤和手机截图
- 🎨 **现代化 UI** - 暗色主题、可调整布局、实时日志流

## ✨ 核心特性

### Web 界面

- ✅ 实时显示 Agent 思考过程
- ✅ 查看手机屏幕截图
- ✅ 监控当前执行的操作
- ✅ 支持中文自然语言指令
- ✅ 可调整的双面板布局

### 容器化部署

- ✅ Docker 单容器部署
- ✅ Docker Compose 编排
- ✅ Host 网络模式访问 ADB
- ✅ 环境变量配置

## 🚀 快速开始

### 方式一：本地运行

```bash
# 1. 克隆仓库
git clone https://github.com/dsdcyy/Open-AutoGLM.git
cd Open-AutoGLM

# 2. 安装依赖
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. 确保 ADB 连接
adb devices

# 4. 启动 Web 服务
python web_ui/main.py

# 5. 访问界面
# 浏览器打开 http://localhost:8001
```

### 方式二：Docker Compose（推荐）

```bash
# 1. 启动服务
docker-compose up -d

# 2. 查看日志
docker-compose logs -f

# 3. 访问界面
# 浏览器打开 http://localhost:9000
```

### 方式三：Docker

```bash
# 构建镜像
docker build -t autoglm-control:latest .

# 运行容器（使用 Host 网络访问 ADB）
docker run -d \
  --name autoglm \
  --network host \
  -e PORT=9000 \
  autoglm-control:latest
```

## 📖 详细文档

- [完整使用指南](README_WEB.md) - 详细的安装、配置和使用说明
- [Docker Compose 指南](DOCKER_COMPOSE_GUIDE.md) - 容器化部署详细说明
- [原项目文档](README.md) - Open-AutoGLM 原始文档

## 🛠️ 技术栈

- **后端**: FastAPI, Uvicorn, WebSocket
- **前端**: HTML, CSS, JavaScript, TailwindCSS
- **容器**: Docker, Docker Compose
- **核心**: Open-AutoGLM Agent 引擎

## 📁 项目结构

```
Open-AutoGLM/
├── web_ui/                    # Web 界面（新增）
│   ├── main.py               # FastAPI 服务
│   ├── agent_manager.py      # Agent 管理
│   └── templates/            # HTML 模板
├── phone_agent/              # 原 AutoGLM 核心（未修改）
├── Dockerfile                # Docker 镜像（新增）
├── docker-compose.yml        # Docker Compose（新增）
├── requirements.txt          # Python 依赖（已更新）
└── README_WEB.md            # 详细文档（新增）
```

## ⚙️ 配置说明

### 环境变量

| 变量名 | 说明         | 默认值 |
| ------ | ------------ | ------ |
| `PORT` | Web 服务端口 | `8001` |

### API 配置

首次访问需要在设置页面配置：

- **Model API URL**: GLM API 地址
- **Model Name**: 模型名称（如 `glm-4-plus`）
- **API Key**: 您的 API 密钥

> ⚠️ **安全提示**: 请勿将 API Key 提交到代码仓库！

## 🎯 使用示例

1. 确保手机通过 USB 连接并开启 USB 调试
2. 执行 `adb devices` 确认设备已连接
3. 访问 Web 界面并配置 API
4. 在输入框输入任务，例如：
   - "打开抖音"
   - "搜索美食视频"
   - "给张三发微信消息：你好"

## 🐛 常见问题

### Q: Docker 容器无法访问 ADB？

**A**: 确保使用 `--network host` 模式运行容器

### Q: 端口被占用怎么办？

**A**: 修改环境变量 `PORT` 或使用 `--port` 参数

### Q: API Key 安全问题？

**A**: 使用环境变量传递，不要硬编码在代码中

详细问题解决请查看 [完整文档](README_WEB.md)

## 🙏 致谢

- 感谢 [THUDM](https://github.com/THUDM) 开源的 [AutoGLM](https://github.com/THUDM/AutoGLM) 项目
- 本项目仅在原项目基础上添加了 Web 界面和容器化功能

## 📄 许可证

本项目遵循原 Open-AutoGLM 项目的 [Apache 2.0 License](LICENSE)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

**Star ⭐ 如果这个项目对您有帮助！**
