from __future__ import annotations

from datetime import date
from typing import Protocol, runtime_checkable

from pydantic import BaseModel

from sherpi.shared_kernel.value_objects import Rito


class PetitionDoc(BaseModel):
    """Uma petição obtida de um sistema processual externo."""

    model_config = {"frozen": True}

    process_number: str
    tribunal: str
    source: str
    content: bytes
    rito: Rito


@runtime_checkable
class PetitionSource(Protocol):
    """Port de ingestão de petições de sistemas processuais."""

    async def fetch(
        self, tribunal: str, date_from: date, date_to: date, *, limit: int = 50
    ) -> list[PetitionDoc]: ...

    @property
    def source_name(self) -> str: ...
