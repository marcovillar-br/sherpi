from __future__ import annotations

import asyncio
from datetime import date

from synthetic.builder import build_clean, build_white_on_white

from sherpi.contexts.integration.domain.source import PetitionDoc
from sherpi.shared_kernel.value_objects import Rito


class SandboxSourceAdapter:
    """Adapter sandbox — gera petições sintéticas para demonstrar a ingestão.

    Em produção, substituir por PjeAdapter ou EprocAdapter com credenciais reais.
    """

    _SOURCE = "SANDBOX"

    @property
    def source_name(self) -> str:
        return self._SOURCE

    async def fetch(
        self, tribunal: str, date_from: date, date_to: date, *, limit: int = 50
    ) -> list[PetitionDoc]:
        await asyncio.sleep(0)
        docs: list[PetitionDoc] = []
        ritos = [Rito.CIVEL, Rito.TRABALHISTA, Rito.CIVEL]
        suffix = tribunal[-4:] if len(tribunal) >= 4 else "0100"
        for i in range(min(limit, 6)):
            is_injected = i % 3 == 2
            content = build_white_on_white() if is_injected else build_clean()
            rito = ritos[i % len(ritos)]
            docs.append(
                PetitionDoc(
                    process_number=f"{i + 1:07d}-00.{date_from.year}.8.26.{suffix}",
                    tribunal=tribunal,
                    source=self._SOURCE,
                    content=content,
                    rito=rito,
                )
            )
        return docs
