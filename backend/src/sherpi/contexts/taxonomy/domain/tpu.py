from __future__ import annotations

from pydantic import BaseModel

from sherpi.shared_kernel.value_objects import Rito


class TpuSuggestion(BaseModel):
    model_config = {"frozen": True}

    tpu_code: str
    description: str
    confidence: float
    anchor_excerpt: str


class TpuEntry(BaseModel):
    model_config = {"frozen": True}

    id: str
    tpu_code: str
    description: str
    rito: Rito
    text_excerpt: str
