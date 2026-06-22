from __future__ import annotations

from datetime import date

from sherpi.contexts.integration.infrastructure.sandbox_adapter import SandboxSourceAdapter
from sherpi.shared_kernel.value_objects import Rito


async def test_fetch_returns_docs() -> None:
    adapter = SandboxSourceAdapter()
    docs = await adapter.fetch("TJSP", date(2024, 1, 1), date(2024, 1, 7), limit=4)
    assert len(docs) == 4
    assert all(d.source == "SANDBOX" for d in docs)
    assert all(len(d.content) > 0 for d in docs)
    assert all(d.tribunal == "TJSP" for d in docs)


async def test_fetch_limit() -> None:
    adapter = SandboxSourceAdapter()
    docs = await adapter.fetch("TRT2", date(2024, 1, 1), date(2024, 1, 7), limit=2)
    assert len(docs) == 2


async def test_fetch_max_capped_at_6() -> None:
    adapter = SandboxSourceAdapter()
    docs = await adapter.fetch("TJSP", date(2024, 1, 1), date(2024, 1, 7), limit=100)
    assert len(docs) == 6  # sandbox caps at 6


async def test_fetch_includes_both_ritos() -> None:
    adapter = SandboxSourceAdapter()
    docs = await adapter.fetch("TJSP", date(2024, 1, 1), date(2024, 1, 7), limit=6)
    ritos = {d.rito for d in docs}
    assert Rito.CIVEL in ritos
    assert Rito.TRABALHISTA in ritos


def test_source_name() -> None:
    assert SandboxSourceAdapter().source_name == "SANDBOX"
