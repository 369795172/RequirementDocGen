# 部署检查清单

## ✅ 已完成的准备工作

### 1. Dockerfile
- ✅ 使用 Python 3.11-slim 基础镜像
- ✅ 多阶段构建（前端 + 后端）
- ✅ 使用 shell form CMD: `sh -c "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"`
- ✅ 正确使用 PORT 环境变量
- ✅ EXPOSE 8000
- ✅ 前端构建并复制到 static 目录

### 2. 应用代码
- ✅ `main.py` 正确读取 PORT 环境变量: `os.getenv("PORT", "8000")`
- ✅ 单进程单端口（FastAPI 同时服务 API 和静态文件）
- ✅ 静态文件通过 `app.mount("/", StaticFiles(...))` 提供

### 3. 依赖管理
- ✅ `requirements.txt` 包含所有必需依赖
- ✅ 使用 `pip install --no-cache-dir` 优化镜像大小

### 4. 环境变量
- ✅ 使用 `AI_BUILDER_TOKEN`（部署时会自动注入）
- ✅ `.env.example` 文件已创建

### 5. 文件结构
- ✅ `.dockerignore` 已创建，优化构建上下文
- ✅ 前端构建脚本存在 (`scripts/build-frontend.sh`)

## 📋 部署前检查

### 必须完成
1. **提交所有更改到 GitHub**
   ```bash
   git add .
   git commit -m "Add Dockerfile and deployment configuration"
   git push
   ```

2. **确认 GitHub 仓库是公开的**
   - 部署系统只能访问公开仓库

3. **准备部署信息**
   - GitHub Repository URL: `https://github.com/username/repo-name`
   - Service Name: `car-finder` (或你选择的名字)
   - Git Branch: `main` (或 `master`)

### 可选但推荐
1. **本地测试 Dockerfile**（如果 Docker 可用）
   ```bash
   docker build -t car-finder-test .
   docker run -p 8000:8000 -e PORT=8000 -e AI_BUILDER_TOKEN=your_token car-finder-test
   ```

2. **验证静态文件服务**
   - 访问 `http://localhost:8000` 应该能看到前端界面
   - 访问 `http://localhost:8000/api/status/test` 应该返回 404（正常）

## 🚀 部署步骤

1. **调用部署 API**
   ```python
   POST /v1/deployments
   {
     "repo_url": "https://github.com/username/repo-name",
     "service_name": "car-finder",
     "branch": "main",
     "port": 8000
   }
   ```

2. **等待部署完成**（5-10 分钟）
   - 状态会从 `queued` -> `deploying` -> `HEALTHY`

3. **访问部署的服务**
   - URL: `https://car-finder.ai-builders.space`

## ⚠️ 注意事项

1. **资源限制**
   - 容器只有 256 MB RAM
   - 避免内存密集型操作
   - 图片会自动清理（MAX_IMAGE_COUNT=1000）

2. **环境变量**
   - `AI_BUILDER_TOKEN` 会自动注入
   - `PORT` 由 Koyeb 设置
   - 其他环境变量需要在部署时指定

3. **日志**
   - 查看部署日志了解问题
   - 如果部署失败，检查 Dockerfile 和代码

## 🔍 故障排查

### 如果部署失败
1. 检查 Dockerfile 语法
2. 确认所有依赖都在 requirements.txt 中
3. 验证前端构建是否成功
4. 检查应用是否能在指定端口启动

### 常见问题
- **端口错误**: 确保使用 `${PORT:-8000}` 而不是硬编码端口
- **静态文件404**: 确认前端构建产物已复制到 static 目录
- **依赖缺失**: 检查 requirements.txt 是否完整

---

**最后更新**: 2025-12-31

