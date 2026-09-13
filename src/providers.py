"""
🔌 MULTI-PROVIDER LLM ADAPTER (Google Gemini, OpenAI & Offline Mock)
Hỗ trợ Native Tool Calling và chuyển đổi linh hoạt qua biến môi trường LLM_PROVIDER.
"""

import os
import sys
import json
from typing import Dict, Any, List
from dotenv import load_dotenv

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

load_dotenv()

class BaseLLMProvider:
    """Interface cơ sở cho các LLM Provider hỗ trợ Native Tool Calling"""
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        raise NotImplementedError

    def generate_with_tools(self, prompt: str, tools_schema: List[Dict[str, Any]], system_prompt: str = "") -> Dict[str, Any]:
        raise NotImplementedError


class MockOfflineProvider(BaseLLMProvider):
    """Offline Mock Provider dùng để chạy thử mà không tốn API Key"""
    def __init__(self):
        self.model_name = "Offline-Mock-Model-2026"

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        return f"[Mock Chatbot Response]: Xin chào! Tôi đã nhận được câu hỏi '{prompt}'. (Chế độ Chatbot không có Tool tra cứu dữ liệu phòng họp theo thời gian thực)."

    def generate_with_tools(self, prompt: str, tools_schema: List[Dict[str, Any]], system_prompt: str = "") -> Dict[str, Any]:
        prompt_lower = prompt.lower()

        # Mô phỏng nhận diện intent đặt phòng
        if "a101" in prompt_lower and "đặt phòng" in prompt_lower:
            return {
                "type": "tool_call",
                "tool_name": "book_room",
                "arguments": {
                    "room_id": "A101",
                    "datetime_str": "14:00 15/09/2026",
                    "duration_hours": 2,
                    "equipment": ["Máy chiếu"]
                },
                "thought": "Người dùng yêu cầu đặt phòng A101. Tôi sẽ gọi tool book_room."
            }

        # Mô phỏng nhận diện intent kiểm tra phòng
        elif "a101" in prompt_lower and ("kiểm tra" in prompt_lower or "có trống" in prompt_lower):
            return {
                "type": "tool_call",
                "tool_name": "check_room_availability",
                "arguments": {
                    "room_id": "A101",
                    "datetime_str": "14:00 15/09/2026"
                },
                "thought": "Người dùng muốn kiểm tra tình trạng phòng A101. Tôi sẽ gọi tool check_room_availability."
            }

        # Edge case phòng không tồn tại
        elif "x999" in prompt_lower:
            return {
                "type": "tool_call",
                "tool_name": "check_room_availability",
                "arguments": {
                    "room_id": "X999",
                    "datetime_str": "10:00 16/09/2026"
                },
                "thought": "Người dùng muốn kiểm tra phòng X999. Tôi sẽ gọi tool check_room_availability."
            }

        else:
            return {
                "type": "text",
                "content": "[Mock Agent Response]: Xin chào! Tôi có thể hỗ trợ kiểm tra tình trạng phòng họp, thiết bị, đặt phòng và đề xuất phương án phù hợp.",
                "thought": "Đây là câu hỏi chung về Facilities Agent, trả lời trực tiếp không cần gọi Tool."
            }

class GeminiProvider(BaseLLMProvider):
    """Google Gemini Provider (Native Tool Calling với Google GenAI SDK)"""
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = model or os.getenv("LLM_MODEL") or "gemini-2.5-flash"

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key or self.api_key == "your_gemini_api_key_here":
            return "[Gemini Error]: Chưa cấu hình GEMINI_API_KEY trong file .env!"

        try:
            from google import genai

            client = genai.Client(api_key=self.api_key)
            contents = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt

            response = client.models.generate_content(
                model=self.model_name,
                contents=contents
            )

            return response.text

        except Exception as e:
            error_text = str(e)

            if "429" in error_text or "RESOURCE_EXHAUSTED" in error_text:
                return (
                    "[Gemini API]: Hệ thống AI hiện đang tạm thời vượt giới hạn "
                    "sử dụng của Gemini API. Vui lòng thử lại sau."
                )

            return f"[Gemini Exception]: {error_text}"

    def generate_with_tools(
        self,
        prompt: str,
        tools_schema: List[Dict[str, Any]],
        system_prompt: str = ""
    ) -> Dict[str, Any]:

        if not self.api_key or self.api_key == "your_gemini_api_key_here":
            print(
                "ℹ️ [Gemini Provider]: Chưa tìm thấy GEMINI_API_KEY hợp lệ. "
                "Tự động chuyển sang Mock Offline."
            )
            return MockOfflineProvider().generate_with_tools(
                prompt,
                tools_schema,
                system_prompt
            )

        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=self.api_key)

            # Chuẩn hóa function declarations cho Gemini SDK
            function_declarations = []

            for tool in tools_schema:
                # Bỏ qua các tool schema chưa được định nghĩa hoàn chỉnh
                if not tool.get("name") or not tool.get("parameters"):
                    continue

                function_declarations.append({
                    "name": tool["name"],
                    "description": tool.get("description", ""),
                    "parameters": tool.get("parameters", {})
                })

            config = types.GenerateContentConfig(
                system_instruction=system_prompt if system_prompt else None,
                tools=[
                    {
                        "function_declarations": function_declarations
                    }
                ] if function_declarations else None,
                temperature=0.2
            )

            response = client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config
            )

            # Kiểm tra xem Gemini có trả về Tool Call không
            if response.function_calls:
                call = response.function_calls[0]

                args = (
                    dict(call.args)
                    if hasattr(call, "args") and call.args
                    else {}
                )

                return {
                    "type": "tool_call",
                    "tool_name": call.name,
                    "arguments": args,
                    "thought": (
                        f"Gemini quyết định gọi công cụ '{call.name}' "
                        f"với tham số: "
                        f"{json.dumps(args, ensure_ascii=False)}"
                    )
                }

            else:
                return {
                    "type": "text",
                    "content": response.text or "",
                    "thought": (
                        "Gemini phản hồi trực tiếp bằng văn bản "
                        "(không cần gọi công cụ)."
                    )
                }

        except Exception as e:
            error_text = str(e)

            # Xử lý riêng lỗi hết quota / rate limit
            if "429" in error_text or "RESOURCE_EXHAUSTED" in error_text:
                print(
                    "⚠️ [Gemini API Warning]: Gemini API đang vượt giới hạn quota. "
                    "Không fallback về Mock để tránh trả lời sai dữ liệu."
                )

                return {
                    "type": "text",
                    "content": (
                        "Hệ thống AI hiện đang tạm thời vượt giới hạn sử dụng "
                        "của Gemini API. Vui lòng thử lại sau. "
                        "Yêu cầu của bạn chưa được thực thi để tránh trả về "
                        "thông tin không chính xác."
                    ),
                    "thought": (
                        "Gemini API vượt giới hạn quota nên tạm dừng xử lý "
                        "yêu cầu và không sử dụng dữ liệu Mock."
                    )
                }

            # Các lỗi khác vẫn fallback Mock
            print(
                f"⚠️ [Gemini API Warning]: Không thể kết nối live API "
                f"({error_text}). Tự động fallback về Mock."
            )

            return MockOfflineProvider().generate_with_tools(
                prompt,
                tools_schema,
                system_prompt
            )


class OpenAIProvider(BaseLLMProvider):
    """OpenAI Provider (Native Tool Calling với OpenAI SDK)"""
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model_name = model or os.getenv("LLM_MODEL") or "gpt-4o-mini"

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key or self.api_key == "your_openai_api_key_here":
            return "[OpenAI Error]: Chưa cấu hình OPENAI_API_KEY trong file .env! Đang sử dụng chế độ Mock."
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            response = client.chat.completions.create(model=self.model_name, messages=messages)
            return response.choices[0].message.content or ""
        except Exception as e:
            return f"[OpenAI Exception]: {str(e)}"

    def generate_with_tools(self, prompt: str, tools_schema: List[Dict[str, Any]], system_prompt: str = "") -> Dict[str, Any]:
        if not self.api_key or self.api_key == "your_openai_api_key_here":
            print("ℹ️ [OpenAI Provider]: Chưa tìm thấy OPENAI_API_KEY hợp lệ. Tự động chuyển sang Mock Offline.")
            return MockOfflineProvider().generate_with_tools(prompt, tools_schema, system_prompt)

        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)

            tools = []
            for tool in tools_schema:
                if not tool.get("name"):
                    continue
                tools.append({
                    "type": "function",
                    "function": {
                        "name": tool["name"],
                        "description": tool.get("description", ""),
                        "parameters": tool.get("parameters", {})
                    }
                })

            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                tools=tools if tools else None,
                tool_choice="auto" if tools else None
            )

            msg = response.choices[0].message
            if msg.tool_calls:
                call = msg.tool_calls[0]
                args = json.loads(call.function.arguments) if call.function.arguments else {}
                return {
                    "type": "tool_call",
                    "tool_name": call.function.name,
                    "arguments": args,
                    "thought": f"OpenAI quyết định gọi công cụ '{call.function.name}' với tham số: {json.dumps(args, ensure_ascii=False)}"
                }
            else:
                return {
                    "type": "text",
                    "content": msg.content or "",
                    "thought": "OpenAI phản hồi trực tiếp bằng văn bản (không cần gọi công cụ)."
                }
        except Exception as e:
            print(f"⚠️ [OpenAI API Warning]: Không thể kết nối live API ({str(e)}). Tự động fallback về Mock.")
            return MockOfflineProvider().generate_with_tools(prompt, tools_schema, system_prompt)


def get_llm_provider() -> BaseLLMProvider:
    """Factory function khởi tạo Provider theo LLM_PROVIDER env variable"""
    provider_type = os.getenv("LLM_PROVIDER", "gemini").lower()
    
    if provider_type == "gemini":
        key = os.getenv("GEMINI_API_KEY")
        if key and key != "your_gemini_api_key_here":
            return GeminiProvider()
        else:
            return MockOfflineProvider()
    elif provider_type == "openai":
        key = os.getenv("OPENAI_API_KEY")
        if key and key != "your_openai_api_key_here":
            return OpenAIProvider()
        else:
            return MockOfflineProvider()
    elif provider_type == "mock":
        return MockOfflineProvider()
    else:
        return MockOfflineProvider()
