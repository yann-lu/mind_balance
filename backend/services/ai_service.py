"""
AI服务集成模块
支持 DeepSeek、千问(Qwen)等多种大模型
"""
import os
import json
import httpx
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta


class AIService:
    """AI服务基类"""

    def __init__(self, api_key: str, api_base: str = None, model: str = None):
        self.api_key = api_key
        self.api_base = api_base
        self.model = model
        self.client = httpx.AsyncClient(timeout=60.0)

    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """发送聊天请求"""
        raise NotImplementedError

    async def close(self):
        """关闭客户端"""
        await self.client.aclose()


class DeepSeekService(AIService):
    """DeepSeek AI服务"""

    def __init__(self, api_key: str, model: str = "deepseek-chat"):
        api_base = "https://api.deepseek.com/v1"
        super().__init__(api_key, api_base, model)

    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """调用DeepSeek API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": self.model,
            "messages": messages,
            **kwargs
        }

        response = await self.client.post(
            f"{self.api_base}/chat/completions",
            headers=headers,
            json=data
        )

        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]


class QwenService(AIService):
    """千问(Qwen) AI服务"""

    def __init__(self, api_key: str, model: str = "qwen-turbo"):
        api_base = "https://dashscope.aliyuncs.com/api/v1"
        super().__init__(api_key, api_base, model)

    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """调用千问API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": self.model,
            "input": {
                "messages": messages
            },
            **kwargs
        }

        response = await self.client.post(
            f"{self.api_base}/services/aigc/text-generation/generation",
            headers=headers,
            json=data
        )

        response.raise_for_status()
        result = response.json()
        return result["output"]["text"]


class OpenAIService(AIService):
    """OpenAI兼容的服务(包括其他兼容OpenAI API的服务)"""

    def __init__(self, api_key: str, api_base: str, model: str = "gpt-3.5-turbo"):
        super().__init__(api_key, api_base, model)

    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """调用OpenAI兼容API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": self.model,
            "messages": messages,
            **kwargs
        }

        response = await self.client.post(
            f"{self.api_base}/chat/completions",
            headers=headers,
            json=data
        )

        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]


def get_ai_service(provider: str, api_key: str, api_base: str = None, model: str = None) -> AIService:
    """工厂函数:根据provider返回对应的AI服务实例"""
    services = {
        'deepseek': DeepSeekService,
        'qwen': QwenService,
        'openai': OpenAIService,
    }

    service_class = services.get(provider.lower())
    if not service_class:
        raise ValueError(f"Unsupported AI provider: {provider}")

    if provider.lower() == 'openai':
        return service_class(api_key, api_base, model)
    else:
        return service_class(api_key, model or service_class.__init__.__defaults__[0])
