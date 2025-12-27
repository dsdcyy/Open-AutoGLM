# AutoGLM Control - Docker Compose 使用指南

## 快速启动

### 1. 启动服务

```bash
docker-compose up -d
```

### 2. 查看日志

```bash
docker-compose logs -f好的，帮我生成一个标准的docker compose启动文件，后续使用docker compose命令启动容器
```

### 3. 停止服务

```bash
docker-compose down
```

### 4. 重启服务

```bash
docker-compose restart
```

## 访问地址

服务启动后访问：**http://localhost:9000**

## 自定义配置

### 修改端口

编辑 `docker-compose.yml`，修改 `PORT` 环境变量：

```yaml
environment:
  - PORT=8080 # 改为你想要的端口
```

### 添加数据持久化

取消注释 `volumes` 部分：

```yaml
volumes:
  - ./logs:/app/logs
  - ./data:/app/data
```

### 添加资源限制

取消注释 `deploy.resources` 部分并根据需要调整。

## 常用命令

```bash
# 查看运行状态
docker-compose ps

# 查看实时日志
docker-compose logs -f autoglm

# 进入容器
docker-compose exec autoglm bash

# 在容器中执行 ADB 命令
docker-compose exec autoglm adb devices

# 重新构建并启动
docker-compose up -d --build

# 完全清理（删除容器和网络）
docker-compose down --volumes
```

## 注意事项

1. **网络模式**：本配置使用 `host` 网络模式，容器可以直接访问宿主机的 ADB 服务
2. **端口占用**：如果端口 9000 已被占用，请修改 `PORT` 环境变量
3. **ADB 连接**：确保宿主机上的 ADB 服务正在运行，并且手机已通过 USB 连接

## 故障排查

### 容器无法启动

```bash
# 查看详细错误日志
docker-compose logs autoglm
```

### ADB 设备未检测到

```bash
# 在宿主机检查 ADB
adb devices

# 在容器中检查 ADB
docker-compose exec autoglm adb devices
```

### 端口冲突

```bash
# 检查端口占用
lsof -i :9000

# 或修改 docker-compose.yml 中的 PORT
```
