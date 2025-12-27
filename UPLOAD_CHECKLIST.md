# GitHub 上传检查清单

## ✅ 上传前必做检查

### 1. 敏感文件检查
- [x] 已更新 `.gitignore` 忽略敏感文件
- [ ] 确认 `key` 文件未被 Git 跟踪
- [ ] 确认 `.env` 文件未被 Git 跟踪
- [ ] 检查是否有其他 API Key 或密码

### 2. 文件清理
- [ ] 删除或忽略 `Installation_Log.md`（包含个人信息）
- [ ] 决定是否保留 `ADBKeyboard.apk`（17KB）
- [ ] 确认 `venv/` 已被忽略

### 3. 文档准备
- [x] 创建 `README.zh-CN.md`（中文主 README）
- [x] 保留 `README_WEB.md`（详细文档）
- [x] 保留 `DOCKER_COMPOSE_GUIDE.md`

### 4. Git 提交准备
```bash
# 验证 .gitignore 是否生效
git status

# 确认以下文件未被跟踪：
# - key
# - Installation_Log.md
# - venv/
# - *.log
```

### 5. 测试验证
- [ ] 本地运行测试：`python web_ui/main.py`
- [ ] Docker 构建测试：`docker build -t test .`
- [ ] Docker Compose 测试：`docker-compose up -d`

## 📋 推荐的提交步骤

### Step 1: 添加新文件
```bash
git add .gitignore
git add .dockerignore
git add Dockerfile
git add docker-compose.yml
git add web_ui/
git add requirements.txt
git add phone_agent/agent.py
```

### Step 2: 添加文档
```bash
git add README.zh-CN.md
git add README_WEB.md
git add DOCKER_COMPOSE_GUIDE.md
```

### Step 3: 提交更改
```bash
git commit -m "feat: Add Web UI and Docker support

- Add FastAPI-based web control interface
- Add real-time log streaming via WebSocket
- Add screenshot display functionality
- Add Docker and Docker Compose deployment
- Update requirements.txt with web dependencies
- Add comprehensive documentation"
```

### Step 4: 推送到 GitHub
```bash
# 如果是新仓库
git branch -M main
git remote add origin <your-github-repo-url>
git push -u origin main

# 如果是现有仓库
git push
```

## 🔐 安全提示

### 在推送前务必确认：

1. **API Key 已移除**
   ```bash
   # 检查是否包含 API Key
   grep -r "智谱" . --exclude-dir=venv --exclude-dir=.git
   grep -r "lzEWMoZa" . --exclude-dir=venv --exclude-dir=.git
   ```

2. **key 文件已忽略**
   ```bash
   git check-ignore key
   # 应该输出：key
   ```

3. **敏感文件未在暂存区**
   ```bash
   git status | grep -E "key|\.env|password|secret"
   # 不应该有任何输出
   ```

## 📦 可选：创建 .env.example

创建一个示例配置文件告诉用户需要哪些环境变量：

```bash
cat > .env.example << 'ENVEOF'
# 智谱 AI API 配置
ZHIPU_API_KEY=your_api_key_here

# Web 服务配置
PORT=9000

# ADB 配置（可选）
ANDROID_ADB_SERVER_ADDRESS=127.0.0.1
ANDROID_ADB_SERVER_PORT=5037
ENVEOF

git add .env.example
```

## ⚠️ 紧急情况

### 如果不小心提交了敏感信息：

```bash
# 1. 立即从历史中删除
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch key" \
  --prune-empty --tag-name-filter cat -- --all

# 2. 强制推送（警告：会重写历史）
git push origin --force --all

# 3. 立即更换 API Key
# 去智谱 AI 控制台重新生成 API Key
```

## ✨ 推荐的仓库设置

在 GitHub 仓库页面设置：

1. **添加 Topics**:
   - `autoglm`
   - `web-ui`
   - `docker`
   - `fastapi`
   - `automation`
   - `chinese`

2. **添加 Description**:
   "基于 Open-AutoGLM 的 Web 控制界面，支持 Docker 容器化部署"

3. **设置 README**:
   选择 `README.zh-CN.md` 作为主 README

4. **添加 License**:
   已有 Apache 2.0 License

5. **启用 Issues** 和 **Discussions**
