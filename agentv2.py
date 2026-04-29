import json
import os
import requests
from openai import OpenAI
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL")
)
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-3.5-turbo")


# ---------- 天气查询工具 ----------
def get_weather(city: str, date: str = "today") -> str:
    """
    使用 wttr.in 获取指定城市的天气信息。
    参数:
        city: 城市名称（英文或中文拼音）
        date: 日期，如 "today", "tomorrow", "2024-12-20"
    返回:
        天气信息字符串
    """
    city_map = {
        "北京": "Beijing",
        "上海": "Shanghai",
        "广州": "Guangzhou",
        "深圳": "Shenzhen",
        "杭州": "Hangzhou",
        "成都": "Chengdu",
        "南京": "Nanjing",
        "武汉": "Wuhan",
        "西安": "Xi'an",
    }
    city_en = city_map.get(city, city)

    if date.lower() in ("today", "今天"):
        url = f"https://wttr.in/{city_en}?format=%C+%t+%w+%h"
    else:
        url = f"https://wttr.in/{city_en}?format=%C+%t+%w+%h&date={date}"
    
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        return resp.text.strip()
    except Exception as e:
        return f"[天气查询失败: {e}]"


# ---------- 辅助函数：将 assistant message 对象转为字典（保留 reasoning_content）----------
def assistant_message_to_dict(msg):
    """
    将 openai 的 assistant message 对象转换为可放入 messages 列表的字典。
    保留所有必要字段，包括 reasoning_content（如果存在）。
    """
    msg_dict = {"role": "assistant"}
    
    # 保留内容（可能为 None）
    if msg.content is not None:
        msg_dict["content"] = msg.content
    
    # 保留 reasoning_content（DeepSeek 思考模式下需要）
    if hasattr(msg, "reasoning_content") and msg.reasoning_content is not None:
        msg_dict["reasoning_content"] = msg.reasoning_content
    
    # 处理 tool_calls
    if msg.tool_calls:
        tool_calls_list = []
        for tc in msg.tool_calls:
            tool_calls_list.append({
                "id": tc.id,
                "type": "function",
                "function": {
                    "name": tc.function.name,
                    "arguments": tc.function.arguments
                }
            })
        msg_dict["tool_calls"] = tool_calls_list
    
    return msg_dict


# ---------- Agent 核心 ----------
class WeatherAgent:
    def __init__(self):
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "查询指定城市在指定日期的天气。日期可以是 today, tomorrow 或具体日期 YYYY-MM-DD。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "city": {
                                "type": "string",
                                "description": "城市名称，如 北京、上海、Tokyo"
                            },
                            "date": {
                                "type": "string",
                                "description": "日期，可选值 today, tomorrow 或 YYYY-MM-DD，默认为 today"
                            }
                        },
                        "required": ["city"]
                    }
                }
            }
        ]
        self.messages = [
            {"role": "system", "content": "你是一个天气预报助手。根据用户的问题，使用天气查询工具获取信息，然后用自然语言回复用户。"}
        ]

    def chat(self, user_input: str) -> str:
        # 添加用户消息
        self.messages.append({"role": "user", "content": user_input})

        # 第一次调用 LLM，判断是否需要调用工具
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=self.messages,
            tools=self.tools,
            tool_choice="auto"
        )
        assistant_msg = response.choices[0].message

        # 如果 LLM 要求调用工具
        if assistant_msg.tool_calls:
            # 将助手消息转为字典并加入历史（包含 reasoning_content 和 tool_calls）
            self.messages.append(assistant_message_to_dict(assistant_msg))

            for tool_call in assistant_msg.tool_calls:
                func_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)
                city = arguments.get("city", "")
                date = arguments.get("date", "today")

                print(f"[Agent 调用工具] 查询 {city} {date} 的天气...")

                # 执行工具
                if func_name == "get_weather":
                    result = get_weather(city, date)
                else:
                    result = "未知工具"

                # 添加工具返回结果到历史
                self.messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result
                })

            # 第二次调用 LLM，生成最终回复
            final_response = client.chat.completions.create(
                model=LLM_MODEL,
                messages=self.messages
            )
            final_msg = final_response.choices[0].message
            final_content = final_msg.content

            # 将最终回复转为字典并加入历史（保留 reasoning_content）
            self.messages.append(assistant_message_to_dict(final_msg))
            return final_content

        else:
            # 不需要工具，直接返回文本
            # 也需将助手消息加入历史（可能包含 reasoning_content）
            self.messages.append(assistant_message_to_dict(assistant_msg))
            return assistant_msg.content if assistant_msg.content else ""


# ---------- 命令行入口 ----------
def main():
    print("=" * 40)
    print("  天气预报 Agent（基于 LLM）")
    print("  输入 'exit' 或 'quit' 退出")
    print("=" * 40)

    agent = WeatherAgent()

    while True:
        try:
            user_input = input("\n你：").strip()
            if user_input.lower() in ("exit", "quit", "退出"):
                print("再见！")
                break
            if not user_input:
                continue

            reply = agent.chat(user_input)
            print(f"Agent：{reply}")

        except KeyboardInterrupt:
            print("\n再见！")
            break
        except Exception as e:
            print(f"[错误] {e}")


if __name__ == "__main__":
    main()
