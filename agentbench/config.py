"""Configuration management — environment variables and model registry."""

import os

from dotenv import load_dotenv

from agentbench.models.base import BaseModel
from agentbench.models.domestic_models import DoubaoModel, QwenModel

load_dotenv()

# Default model IDs for domestic Chinese models
DOMESTIC_MODEL_IDS: dict[str, str] = {
    "doubao": "doubao-seed-2-0-pro-260215",  # Doubao Seed 2.0 Pro (Volcengine supported model)
    "qwen": "qwen3.5-plus",  # Alibaba Qwen 3.5 Plus (latest version)
}

# Model registry: short name -> factory class
MODEL_REGISTRY: dict[str, type[BaseModel]] = {
    "doubao": DoubaoModel,
    "qwen": QwenModel,
}


def get_model(name: str) -> BaseModel:
    """Create a model instance by short name.

    Args:
        name: One of 'doubao', 'qwen'.

    Returns:
        A configured model instance.
    """
    name = name.strip().lower()
    if name not in MODEL_REGISTRY:
        raise ValueError(f"Unknown model: {name!r}. Available: {list(MODEL_REGISTRY)}")

    # Domestic Chinese models
    model_id = DOMESTIC_MODEL_IDS[name]
    if name == "doubao":
        return DoubaoModel(model_id=model_id)
    elif name == "qwen":
        return QwenModel(model_id=model_id)
    else:
        raise ValueError(f"Unknown model: {name!r}")
