"""Restauração (des-anonimização) dos valores reais após a extração.

A anonimização protege o **LLM externo** (LGPD); o **revisor humano autorizado**
deve ver os dados reais. Como a extração roda sobre o texto anonimizado, o resumo
volta com placeholders (`[CPF_1]`, `[NOME_1]`…) — aqui os substituímos de volta
pelos valores originais usando o mapa produzido na anonimização reversível.

O prompt persistido para auditoria **continua anonimizado** (é o que o LLM viu).
"""

from __future__ import annotations

import re

from pydantic import BaseModel


def restore_text(text: str, mapping: dict[str, str]) -> str:
    """Substitui cada placeholder pelo valor original. Chaves mais longas primeiro
    (evita que `[CPF_1]` corrompa `[CPF_11]`)."""
    if not mapping:
        return text
    pattern = re.compile("|".join(re.escape(k) for k in sorted(mapping, key=len, reverse=True)))
    return pattern.sub(lambda m: mapping[m.group()], text)


def _walk(obj: object, mapping: dict[str, str]) -> object:
    if isinstance(obj, str):
        return restore_text(obj, mapping)
    if isinstance(obj, list):
        return [_walk(x, mapping) for x in obj]
    if isinstance(obj, dict):
        return {k: _walk(v, mapping) for k, v in obj.items()}
    return obj


def deanonymize_model[TModel: BaseModel](model: TModel, mapping: dict[str, str]) -> TModel:
    """Restaura os valores reais em todos os campos string de um modelo Pydantic."""
    if not mapping:
        return model
    restored = _walk(model.model_dump(), mapping)
    return type(model).model_validate(restored)
