---
name: vision-bridge
description: 视觉协作桥接 — 当主对话模型不支持图像输入时，将图像路由至外部视觉模型分析，结果返回主模型继续对话。支持两阶段工作流：视觉模型分析 → 主模型评审与执行。
version: 1.0.0
enabled: true
---

# Vision Bridge — 视觉协作桥接

当主对话模型（如 DeepSeek V4 Pro 等纯文本模型）无法直接查看图像时，自动通过外部视觉模型完成图像分析，分析结果返回主模型继续对话和执行任务。

## 触发条件

**用户主动触发**（关键词匹配）：
- 中文：视觉协作、看图、分析图像、查看监控、图像分析、图片、看一下、帮我看看
- 英文：vision bridge、view image、analyze image、image analysis、visual collaboration
- 用户明确要求查看某张图像或目录下的图像

**自动触发**（能力检测）：
- 主模型尝试 Read 图像文件返回 `[Unsupported Image]` 时
- 主模型意识到当前不支持多模态输入时
- 任务需要视觉分析但主模型无法直接处理时

## 架构

```
┌──────────────┐     ┌─────────────────┐     ┌──────────────┐
│  主对话模型   │────▶│  vision_bridge   │────▶│  视觉模型     │
│ (纯文本)     │     │     .py 脚本     │     │ (多模态)     │
│              │◀────│                 │◀────│              │
│ 评审+执行    │     │  文本描述返回     │     │  深度分析     │
└──────────────┘     └─────────────────┘     └──────────────┘
```

**两阶段工作流**：
1. **视觉模型**：图像 → 结构化视觉分析 → 问题识别 → 建议（聚焦视觉层面，不涉及代码）
2. **主模型**：评审分析结果 → 映射到代码/操作 → 执行修改 → 验证

视觉模型做像素级推理，主模型做代码级执行；各司其职。

## 首次配置

首次使用时，脚本会引导你完成配置。也可以直接设置环境变量：

### 环境变量

| 变量 | 必需 | 说明 |
|------|------|------|
| `VISION_API_KEY` | 是 | 视觉模型 API Key |
| `VISION_BASE_URL` | 否 | API 地址（默认 MiMo V2.5） |
| `VISION_MODEL` | 否 | 模型名（默认 `mimo-v2.5`） |
| `VISION_DOMAIN` | 否 | 可选的领域上下文，注入到每次分析提示词中 |

### 支持的视觉模型

任何兼容 Anthropic Messages API 的多模态模型均可使用：

| 模型 | Base URL |
|------|----------|
| MiMo V2.5 | `https://token-plan-sgp.xiaomimimo.com/anthropic/v1/messages` |
| Anthropic Claude | `https://api.anthropic.com/v1/messages` |
| 其他兼容服务 | 自定义 |

### 领域上下文（可选）

如果你的图像分析需要特定领域知识，设置 `VISION_DOMAIN` 环境变量或使用 `--domain` 参数。例如：

```bash
# 环境变量方式（持久）
export VISION_DOMAIN="You are analyzing medical X-ray images. Look for fractures, lesions, and abnormalities."

# 命令行方式（一次性）
python vision_bridge.py xray.png --domain "You are analyzing medical X-ray images."
```

## 使用方式

脚本位于本 skill 目录的 `scripts/vision_bridge.py`。

### 1. 深度分析（默认）

```bash
python scripts/vision_bridge.py <image_path>
```

输出结构化分析：Visual Observation → Issue Identification → Pattern Analysis → Recommendations

### 2. 快速描述

```bash
python scripts/vision_bridge.py <image_path> --brief
```

### 3. 自定义问题

```bash
python scripts/vision_bridge.py <image_path> "图中有什么异常？"
```

### 4. 显示推理过程

```bash
python scripts/vision_bridge.py <image_path> --verbose
```

### 5. 注入领域上下文

```bash
python scripts/vision_bridge.py <image_path> --domain "你在分析卫星遥感图像。关注云层、地形和水体分布。"
```

## 工作流示例

```
用户：帮我看看 screenshots/error.png 报了什么错

主模型：[检测到图像请求，启动 vision-bridge]
       → python scripts/vision_bridge.py screenshots/error.png "描述这个错误截图中的内容"
       → 视觉模型返回：红色错误弹窗，标题"Connection Refused"，端口 5432...

主模型：[评审分析结果]
       "错误是 PostgreSQL 连接被拒绝，端口 5432。
        检查：PostgreSQL 服务是否运行？防火墙规则？连接字符串配置？"

主模型：[执行修复]
       → 检查 docker-compose.yml 的 postgres 配置
       → 验证连接字符串中的端口
```

## 视觉模型的职责边界

**应该做**：
- 描述像素级视觉现象
- 识别问题、异常、关键信息
- 分析趋势和模式
- 提出视觉层面的改进建议

**不应该做**：
- 建议代码修改（不知道代码库结构）
- 执行操作（没有执行环境）
- 做出需要业务上下文才能判断的决策

这些边界确保视觉模型发挥其推理优势，同时避免无上下文的错误建议。

## 注意事项

- 图像 base64 编码会增加 payload 大小，建议单张 < 10MB
- 视觉模型调用有延迟（通常 10-60 秒）
- 批量分析多张图像时，使用 Bash 循环调用
- 分析质量取决于视觉模型能力，关键任务建议使用更强模型
- API Key 不要硬编码在脚本中，始终使用环境变量
