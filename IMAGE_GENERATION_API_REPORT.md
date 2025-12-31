# Image Generation API 401 Unauthorized Issue - Diagnostic Report

## 问题描述

在使用 OpenAI SDK 调用 AI Builder Space 的图像生成 API (`/v1/images/generations`) 时，遇到 401 Unauthorized 错误。

**关键观察**：
- ✅ `/v1/chat/completions` API 正常工作（使用 `client.chat.completions.create()`）
- ❌ `/v1/images/generations` API 返回 401 Unauthorized（使用 `client._client.post()`）

## 根本原因分析

### 问题根源

OpenAI SDK 的底层 HTTP 客户端 (`client._client.post()`) **不会自动添加认证头**。

**对比**：
- `client.chat.completions.create()` - ✅ 自动添加 `Authorization: Bearer {token}` 头
- `client._client.post()` - ❌ **不会**自动添加认证头

### 测试结果

通过独立测试脚本 (`test_image_generation.py`) 验证：

1. **Chat Completions** (正常工作)
   ```
   ✅ Status: 200 OK
   Method: client.chat.completions.create()
   ```

2. **Image Generation - Method 1** (当前实现)
   ```
   ❌ Status: 401 Unauthorized
   Error: {"detail": "Missing bearer token"}
   Method: client._client.post("/images/generations")
   ```

3. **Image Generation - 修复后** (手动添加认证头)
   ```
   ✅ Status: 200 OK
   Method: client._client.post("/images/generations", headers={"Authorization": f"Bearer {token}"})
   ```

## 解决方案

### 方案 1: 客户端修复（已实施）

在调用 `client._client.post()` 时，手动添加 `Authorization` 头：

```python
response = await self.client._client.post(
    "/images/generations",
    json={...},
    headers={
        "Authorization": f"Bearer {self.token}"
    }
)
```

**优点**：
- ✅ 立即解决问题
- ✅ 不需要后端改动
- ✅ 代码简单

**缺点**：
- ⚠️ 需要手动管理认证头
- ⚠️ 与 OpenAI SDK 的高级 API 使用方式不一致

### 方案 2: 后端修复（推荐）

**建议后端检查**：

1. **路径处理问题**：
   - 当前路径：`/images/generations`（相对于 `base_url/v1`）
   - 完整路径：`/v1/images/generations`
   - 检查后端是否正确处理相对路径的认证

2. **认证中间件**：
   - 检查认证中间件是否对所有 `/v1/*` 路径生效
   - 确认 `/v1/images/generations` 也在认证范围内

3. **OpenAI SDK 兼容性**：
   - OpenAI SDK 的 `_client.post()` 方法不会自动添加认证头
   - 考虑是否应该支持这种方式，或者提供文档说明

## 技术细节

### OpenAI SDK 行为

```python
# 高级 API - 自动添加认证
client = AsyncOpenAI(api_key=token, base_url=base_url)
response = await client.chat.completions.create(...)
# ✅ 自动添加: Authorization: Bearer {token}

# 底层 HTTP 客户端 - 不自动添加认证
response = await client._client.post("/images/generations", json={...})
# ❌ 没有 Authorization 头
```

### 当前实现

```python
# services/ai_client.py - generate_image()
response = await self.client._client.post(
    "/images/generations",
    json={
        "prompt": prompt,
        "model": "gemini-2.5-flash-image",
        "size": size,
        "n": 1,
        "response_format": "b64_json"
    },
    headers={
        "Authorization": f"Bearer {self.token}"  # 手动添加
    }
)
```

## 测试脚本

已创建测试脚本验证问题：
- `test_image_generation.py` - 诊断脚本
- `test_image_generation_fixed.py` - 修复验证脚本

运行测试：
```bash
python3 test_image_generation.py
python3 test_image_generation_fixed.py
```

## 建议

### 短期方案（已实施）
✅ 在客户端代码中手动添加 `Authorization` 头

### 长期方案（建议后端考虑）
1. **统一认证处理**：
   - 确保所有 `/v1/*` 路径都使用相同的认证机制
   - 检查是否有路径被排除在认证中间件之外

2. **文档完善**：
   - 如果使用 `_client.post()` 需要手动添加认证头，应在 API 文档中明确说明
   - 或者提供示例代码

3. **API 一致性**：
   - 考虑是否应该让 `/v1/images/generations` 的行为与 `/v1/chat/completions` 一致
   - 或者提供 OpenAI SDK 兼容的高级 API 方法

## 相关文件

- `services/ai_client.py` - AI 客户端实现
- `test_image_generation.py` - 诊断测试脚本
- `test_image_generation_fixed.py` - 修复验证脚本

## 状态

- ✅ **问题已定位**：认证头未自动添加
- ✅ **临时修复已实施**：手动添加认证头
- ⏳ **等待后端确认**：是否需要后端改动或文档更新

---

**报告生成时间**: 2025-12-31  
**测试环境**: Python 3.12, OpenAI SDK, AI Builder Space Platform

