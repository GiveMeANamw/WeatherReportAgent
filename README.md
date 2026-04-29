# 天气预报 Agent 操作指南

## 环境准备

本项目基于 Python 3.9 开发，请先确保你的系统中已安装 Python 3.9。推荐使用虚拟环境来隔离依赖，你可以选择以下任意一种方式创建并激活环境。

**使用 conda（如果已安装 Anaconda 或 Miniconda）**

```bash
conda create -n weather_agent python=3.9
conda activate weather_agent
```

**使用 venv（Python 内置虚拟环境工具）**

```bash
# Linux / macOS
python3.9 -m venv venv
source venv/bin/activate

# Windows
python3.9 -m venv venv
venv\Scripts\activate
```

激活环境后，命令行前缀会显示环境名称，表示操作成功。

## 安装依赖

进入项目根目录（包含 `requirements.txt` 的文件夹），执行以下命令安装所有必需的 Python 包：

```bash
pip install -r requirements.txt
```

## 配置环境变量

项目中已提供环境变量模板文件 `.env.example`，你需要先复制一份，然后根据自己的 API 账户信息进行编辑。

1. 复制模板文件为 `.env`：

   ```bash
   cp .env.example .env
   ```

2. 用任意文本编辑器打开 `.env` 文件，将以下三项替换为你自己的信息：

   ```env
   OPENAI_API_KEY=你的API密钥
   OPENAI_BASE_URL=你的API接口地址
   LLM_MODEL=你所使用的模型名称
   ```

   示例（使用 OpenAI 官方服务）：

   ```env
   OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   OPENAI_BASE_URL=https://api.openai.com/v1
   LLM_MODEL=gpt-3.5-turbo
   ```

   如果你使用的是其他兼容 OpenAI 接口的服务（如 DeepSeek、通义千问等），只需修改 `OPENAI_BASE_URL` 和 `LLM_MODEL` 即可，例如：

   ```env
   OPENAI_API_KEY=你的DeepSeek API Key
   OPENAI_BASE_URL=https://api.deepseek.com/v1
   LLM_MODEL=deepseek-chat
   ```

   修改完成后保存并关闭文件。

## 运行 Agent

在项目根目录下，直接运行主程序：

```bash
python agentv2.py
```

程序启动后会显示欢迎信息，并进入交互式命令行界面。你可以直接输入自然语言问题，例如：

- “北京今天天气怎么样？”
- “明天上海会下雨吗？”
- “成都后天温度多少？”

Agent 会理解你的意图，自动调用天气工具查询，并以自然语言回复结果。需要退出时，输入 `exit` 或 `quit` 并回车即可结束程序。

## 常见问题

- **运行时报错 `ModuleNotFoundError`**  
  请确认已激活正确的虚拟环境，并重新执行 `pip install -r requirements.txt` 确保所有依赖安装完整。

- **返回天气查询失败或网络错误**  
  程序使用免费的 wttr.in 天气服务，若访问不稳定，可尝试检查网络连接或稍后重试。如需更稳定的天气数据源，可自行修改 `agentv2.py` 中的 `get_weather` 函数，替换为其他天气 API。

- **LLM 调用失败或返回 401 错误**  
  请检查 `.env` 文件中的 `OPENAI_API_KEY` 是否正确填写，以及 `OPENAI_BASE_URL` 是否与你的 API 服务商匹配。大部分 API 错误都与密钥或地址配置有关。

- **中文城市名无法识别**  
  当前代码内置了常见城市的中英文映射表，若遇到未覆盖的城市，建议直接使用该城市的英文或拼音名称进行查询。
