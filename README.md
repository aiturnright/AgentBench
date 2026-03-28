# AgentBench

面向超级个体的 AI Agent 评测平台。

AgentBench 是一个 AI Agent 工具评测平台（Benchmark），核心关注 **模型与其配合的 Agent 框架/工具链的整体产出效果**，帮助用户快速判断"哪个模型 + 哪个 Agent 工具组合"在实际场景中表现最好。

## 评测领域

围绕"超级个体"的四大高价值领域进行评测：

- **代码开发** — 编码、调试、架构设计、项目搭建等端到端开发任务
- **自媒体** — 文案撰写、内容策划、多平台适配、SEO 优化等内容生产任务
- **期权投资** — 市场分析、策略生成、风险评估、数据解读等投资辅助任务
- **个体健康** — 健康数据解读、运动计划、饮食建议、症状初筛等健康管理任务

## 项目结构

```
agentbench/
├── config.py              # 配置与模型注册表
├── runner.py              # 评测主运行器
├── models/                # 模型适配器
│   ├── base.py            # 模型抽象基类
│   └── openrouter_model.py # OpenRouter 统一 API 适配器
├── tasks/                 # 任务管理
│   ├── base.py            # Task 数据结构
│   └── loader.py          # JSON 任务加载器
└── evaluators/            # 评测打分
    ├── base.py            # 评估器抽象基类
    └── llm_judge.py       # LLM-as-Judge 评估器
benchmarks/
└── text_generation.json   # 文本生成基准测试集
run.py                     # CLI 入口
```

## 快速开始

### 环境要求

- Python 3.10+

### 安装

```bash
git clone https://github.com/aiturnright/AgentBench.git
cd AgentBench
pip install -e .
```

### 配置

复制环境变量模板并填入 API Key：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```
OPENROUTER_API_KEY=sk-or-your-openrouter-api-key
```

### 运行评测

```bash
# 使用豆包模型运行评测（默认）
python run.py

# 运行指定国产模型
python run.py --models doubao
python run.py --models qwen
python run.py --models doubao,qwen

# 使用国产模型进行评估
python run.py --models doubao --judge doubao
python run.py --models qwen --judge qwen
python run.py --models doubao --judge qwen

# 指定任务集和输出路径
python run.py --models doubao,qwen --tasks benchmarks/text_generation.json --output results/output.json

# 指定 LLM 评审模型
python run.py --models doubao --judge doubao
```

### CLI 参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--models` | `doubao` | 逗号分隔的模型名称，可选：`doubao`、`qwen` |
| `--tasks` | `benchmarks/text_generation.json` | 基准测试 JSON 文件路径 |
| `--output` | `results/output.json` | 结果输出 JSON 文件路径 |
| `--judge` | `doubao` | LLM 评审使用的模型，可以是已注册的模型名称（如 `doubao`、`qwen`），使用该模型的 API 进行评估 |

## ASMR 音频评测

AgentBench 支持对 AI 音频生成模型进行 ASMR（自发性知觉经络反应）音频质量评测，帮助自媒体创作者、助眠内容制作者选择最适合的音频生成工具。

### 环境配置

在 `.env` 文件中添加对应模型的 API Key：

```
# OpenAI TTS
OPENAI_API_KEY=sk-your-openai-api-key

# Google Gemini TTS
GOOGLE_API_KEY=your-google-api-key

# MiniMax Music
MINIMAX_API_KEY=your-minimax-api-key
MINIMAX_GROUP_ID=your-minimax-group-id
```

### 运行 ASMR 音频评测

```bash
# 使用默认模型（openai-tts, gemini-tts, minimax-music）
python run_audio.py

# 指定模型
python run_audio.py --models openai-tts,gemini-tts

# 指定任务集和输出路径
python run_audio.py --models openai-tts,gemini-tts --tasks benchmarks/asmr_audio.json --output-dir results/audio --output-json results/audio_results.json
```

### ASMR 评测 CLI 参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--models` | `openai-tts,gemini-tts,minimax-music` | 逗号分隔的音频模型名称 |
| `--tasks` | `benchmarks/asmr_audio.json` | ASMR 音频基准测试 JSON 文件路径 |
| `--output-dir` | `results/audio` | 生成的音频文件保存目录 |
| `--output-json` | `results/audio_results.json` | 结果输出 JSON 文件路径 |

### 支持的音频模型

| 名称 | 说明 | API Key 环境变量 |
|------|------|-----------------|
| `openai-tts` | OpenAI 文本转语音模型 | `OPENAI_API_KEY` |
| `gemini-tts` | Google Gemini 文本转语音模型 | `GOOGLE_API_KEY` |
| `minimax-music` | MiniMax 海螺音乐生成模型 | `MINIMAX_API_KEY` + `MINIMAX_GROUP_ID` |

### ASMR 评测维度

评测覆盖 5 种 ASMR 音频类型：

| 类型 | 说明 | 示例 |
|------|------|------|
| **人声耳语型 (whisper)** | 轻柔耳语、低声细语 | 晚安耳语、呼吸声 |
| **触发音效型 (trigger)** | 敲击、刮擦、翻页等物理触发音 | 指甲轻敲木头 |
| **环境氛围型 (ambient)** | 雨声、篝火、森林等自然环境音 | 森林雨声 |
| **角色扮演型 (roleplay)** | 模拟场景的人声+音效混合 | 图书管理员耳语 |
| **音乐氛围型 (music)** | 极低 BPM 的轻柔背景音乐 | 60 BPM 助眠钢琴曲 |

### 评测指标

评测结果包含以下客观技术指标：

| 指标 | 说明 |
|------|------|
| **duration_seconds** | 音频时长 |
| **sample_rate** | 采样率 |
| **snr_db** | 信噪比 |
| **spectral_centroid_hz** | 频谱质心 |
| **loudness_lufs** | 响度（LUFS） |
| **peak_dbfs** | 峰值电平 |
| **rms_dbfs** | 均方根电平 |
| **spectral_rolloff_hz** | 频谱滚降点 |
| **crest_factor_db** | 峰值因子 |
| **low_freq_energy_ratio** | 低频能量比 |

## 工作原理

1. 从 JSON 文件加载评测任务
2. 初始化 LLM 评审模型（默认使用 GPT-5.2）
3. 初始化被评测的模型（OpenAI / Anthropic）
4. 对每个模型、每个任务：
   - 模型根据 prompt 生成输出
   - LLM 评审根据评分标准打分（1-10 分）
5. 输出评测报告并保存结果

## 支持的模型

### 国产模型

| 名称 | 模型 ID | 说明 | API Key 环境变量 |
|------|---------|------|------------------|
| `doubao` | doubao-seed-2-0-pro-260215 | 字节跳动豆包 Seed 2.0 Pro | DOUBAO_API_KEY |
| `qwen` | qwen-turbo | 阿里通义千问 Turbo (Qwen) | QWEN_API_KEY |

## 基准测试集

当前包含 `text_generation.json`，涵盖 4 个领域共 6 个评测任务：

| 任务 ID | 领域 | 内容 |
|---------|------|------|
| code-doc-1 | 代码开发 | 编写 Python 重试装饰器 API 文档 |
| code-doc-2 | 代码开发 | 编写 Flask 限流中间件技术设计文档 |
| media-post-1 | 自媒体 | 撰写 AI 与效率主题公众号文章 |
| options-report-1 | 期权投资 | 编写期权策略分析报告 |
| health-plan-1 | 个体健康 | 制定 4 周健身计划 |
| health-diet-1 | 个体健康 | 制定力量训练配套饮食方案 |

### 自定义任务

任务文件为 JSON 格式，结构如下：

```json
{
  "tasks": [
    {
      "id": "task-id",
      "domain": "领域名称",
      "capability": "能力维度",
      "prompt": "评测提示词",
      "criteria": "评分标准"
    }
  ]
}
```

## 扩展模型

实现 `BaseModel` 抽象类即可添加新的模型适配器：

```python
from agentbench.models.base import BaseModel

class MyModel(BaseModel):
    @property
    def name(self) -> str:
        return "my-model"

    def generate(self, prompt: str) -> str:
        # 调用模型 API 并返回生成结果
        ...
```

然后在 `agentbench/config.py` 的 `MODEL_REGISTRY` 中注册：

```python
MODEL_REGISTRY = {
    "openai": OpenRouterModel,
    "anthropic": OpenRouterModel,
    "google": OpenRouterModel,
    "deepseek": OpenRouterModel,
    "my-model": MyModel,
}
```

## 技术栈

- **Python 3.10+**
- **OpenAI SDK** (`openai>=1.0`) — OpenRouter API 调用（兼容 OpenAI 格式）
- **python-dotenv** (`python-dotenv>=1.0`) — 环境变量管理

## 许可证

本项目为私有项目。
