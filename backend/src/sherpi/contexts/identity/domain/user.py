from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel


class Role(StrEnum):
    ADMIN = "ADMIN"
    REVISOR = "REVISOR"


class User(BaseModel):
    model_config = {"frozen": True}

    id: str
    email: str
    hashed_password: str
    role: Role = Role.REVISOR
    is_active: bool = True
