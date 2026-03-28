"""Domestic Chinese model adapters."""

import os
import requests

from .base import BaseModel


class DoubaoModel(BaseModel):
    """ByteDance Doubao model adapter using Volcengine SDK."""

    def __init__(self, model_id: str, api_key: str | None = None):
        super().__init__(model_id)
        self.api_key = api_key or os.getenv("DOUBAO_API_KEY")
        if not self.api_key:
            raise ValueError("DOUBAO_API_KEY is required")
        # 导入volcengine模块
        from volcenginesdkarkruntime import Ark

        # 初始化客户端
        self.client = Ark(api_key=self.api_key)

    def generate(self, prompt: str) -> str:
        # 使用火山引擎SDK调用豆包API
        response = self.client.chat.completions.create(
            model=self.model_id,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        return response.choices[0].message.content or ""

    @property
    def name(self) -> str:
        return f"doubao/{self.model_id}"


class QwenModel(BaseModel):
    """Alibaba Qwen model adapter using OpenAI-compatible API."""

    def __init__(self, model_id: str, api_key: str | None = None):
        super().__init__(model_id)
        self.api_key = api_key or os.getenv("QWEN_API_KEY")
        if not self.api_key:
            raise ValueError("QWEN_API_KEY is required")
        self.base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"

    def generate(self, prompt: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model_id,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
        }
        response = requests.post(self.base_url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"] or ""

    @property
    def name(self) -> str:
        return f"qwen/{self.model_id}"
