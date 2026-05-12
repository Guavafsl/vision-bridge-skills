<p align="center">
  <a href="./README.md"><strong>English</strong></a> · 
  <a href="./README.zh.md"><strong>简体中文</strong></a>
</p>

---

# Vision Bridge — 视觉协作桥接

当主对话模型（如 DeepSeek、任意纯文本 LLM）无法直接查看图像时，将图像路由至视觉模型完成分析。

**两阶段工作流：**
1. 视觉模型分析图像 → 输出结构化文本报告
2. 主模型评审报告 → 映射到代码/操作 → 执行

兼容任何 Anthropic Messages API 格式的多模态模型（MiMo、Claude 等）。

## 快速开始

```bash
# 1. 设置 API Key
export VISION_API_KEY="your-api-key"

# 2. 分析图像
python scripts/vision_bridge.py screenshot.png
```

## 配置

所有设置通过环境变量控制：

| 变量 | 必需 | 默认值 | 说明 |
|------|------|--------|------|
| `VISION_API_KEY` | 是 | — | 视觉模型 API Key |
| `VISION_BASE_URL` | 否 | CN 节点（见下表） | Anthropic 兼容接口地址 |
| `VISION_MODEL` | 否 | `mimo-v2.5` | 模型名称 |
| `VISION_DOMAIN` | 否 | — | 领域上下文，注入到每次分析提示词中 |
| `VISION_REGION` | 否 | `cn` | API 区域：`cn` 或 `sgp` |

### 支持的视觉模型

任何兼容 Anthropic Messages API 的服务均可使用：

| 服务商 | 区域 | 接口地址 |
|--------|------|----------|
| MiMo V2.5（国内） | `cn`（默认） | `https://token-plan-cn.xiaomimimo.com/anthropic/v1/messages` |
| MiMo V2.5（新加坡） | `sgp` | `https://token-plan-sgp.xiaomimimo.com/anthropic/v1/messages` |
| Anthropic Claude | — | `https://api.anthropic.com/v1/messages` |
| 自定义服务 | — | 自行填写 |

## 使用方式

```bash
# 深度结构化分析（默认）
python scripts/vision_bridge.py image.png

# 快速一段式描述
python scripts/vision_bridge.py image.png --brief

# 自定义问题
python scripts/vision_bridge.py image.png "这张截图里有什么错误？"

# 显示模型推理过程
python scripts/vision_bridge.py image.png --verbose

# 注入领域专属上下文
python scripts/vision_bridge.py image.png --domain "你在分析医学 X 光片。关注骨折和病变。"

# 切换到新加坡节点（默认为国内节点）
python scripts/vision_bridge.py image.png --region sgp

# 注入对话上下文（推荐，由主模型生成）
python scripts/vision_bridge.py image.png --context "移动端UI截图。观察：布局错位、文字截断、组件重叠。"
```

## 领域上下文（`--domain`）

对于需要专业知识的图像分析，通过 `VISION_DOMAIN` 环境变量或 `--domain` 参数提供领域背景：

```bash
# 持久生效（环境变量）
export VISION_DOMAIN="你在分析 PCB 电路板布局。关注走线质量和过孔位置。"

# 单次生效（参数）
python scripts/vision_bridge.py pcb.png --domain "重点关注焊盘质量和过孔间距。"
```

领域上下文会拼接到每次提示词前，赋予视觉模型专业词汇和故障模式判断能力。

## 对话上下文（`--context`）

`--context` 用于将主模型根据当前对话生成的简短中立引导传入视觉模型，通过 `system` 字段注入，让视觉模型明确**观察什么**，而不预设结论。

### 格式

```
[领域/场景，≤10字]。观察：[重点1]、[重点2]、[重点3，名词短语]。
```

总长度 ≤ 60 字。

### 禁止词汇

不得包含结果预设或主观偏向：

| 禁止（中文） | 禁止（English） | 替代方式 |
|------|------|----------|
| 期望/想要/希望看到 | expect to see / want to see / hope to find | 直接列出观察对象名词 |
| 应该有/可能有 | should have / probably has | 去掉预设，只描述观察维度 |
| 我认为/我觉得 | I think / I believe / I assume | 删除主观判断词 |
| 请重点看我关心的 | please focus on what I care about | 直接说出关心的具体名词 |

### 示例

```bash
# ❌ 错误 — 包含结果预设
python scripts/vision_bridge.py ui.png --context "这是UI截图，我期望按钮对齐且文字应该不会被截断。"

# ✅ 正确 — 仅中立的观察目标
python scripts/vision_bridge.py ui.png --context "移动端UI截图。观察：按钮对齐状态、文字截断、组件重叠区域。"
```

## 工作原理

```
┌──────────────┐     ┌─────────────────┐     ┌──────────────┐
│  主对话模型   │────▶│  vision_bridge   │────▶│   视觉模型    │
│ （纯文本）   │     │     .py 脚本     │     │  （多模态）  │
│              │◀────│                  │◀────│              │
│  评审 + 执行 │     │   文本分析报告    │     │   图像分析   │
└──────────────┘     └─────────────────┘     └──────────────┘
```

视觉模型专注于像素级推理：描述可见内容、识别异常、发现模式，**不建议代码修改**。主模型拥有完整项目上下文，负责代码级决策和执行。

## 环境要求

- Python 3.7+（仅使用标准库，无需 pip 安装）
- 视觉模型的 API Key

## 许可证

MIT
