#!/usr/bin/env python3
"""Insere frontmatter YAML padronizado nos docs do SHERPI (idempotente).

Schema (consumido por agentes de IA para indexação/recuperação):
  title, description, doc_type, project, status, version, updated, language, tags
"""

from __future__ import annotations

from pathlib import Path

DOCS = Path(__file__).resolve().parent.parent / "docs"
UPDATED = "2026-06-18"

# filename (relativo a docs/) -> metadados
META: dict[str, dict[str, object]] = {
    "INDEX.md": {
        "title": "Índice da Documentação",
        "description": "Ponto de entrada da documentação do SHERPI, organizado por categoria.",
        "doc_type": "index",
        "status": "reference",
        "tags": ["index", "navegacao"],
    },
    "prd-sherpi.md": {
        "title": "Documento de Requisitos de Produto (PRD)",
        "description": "Visão, problema, personas, histórias de usuário, escopo e métricas do SHERPI.",
        "doc_type": "prd",
        "status": "approved",
        "version": "1.1",
        "tags": ["produto", "requisitos", "personas", "metricas"],
    },
    "tech-spec-sherpi.md": {
        "title": "Especificação Técnica",
        "description": "Arquitetura DDD/hexagonal, contratos, camada LLM, interpretabilidade, segurança e API.",
        "doc_type": "tech-spec",
        "status": "approved",
        "version": "1.1",
        "tags": ["arquitetura", "ddd", "hexagonal", "api", "llm", "interpretabilidade"],
    },
    "roadmap.md": {
        "title": "Roadmap do MVP (2 sprints)",
        "description": "Roadmap do MVP em 2 sprints (2 semanas), com Definition of Done, visão de futuro e marcos.",
        "doc_type": "roadmap",
        "status": "approved",
        "version": "1.1",
        "tags": ["roadmap", "sprints", "planejamento", "mvp"],
    },
    "agile-process.md": {
        "title": "Processo Ágil de Desenvolvimento",
        "description": "Papéis (8 integrantes), Design Sprint, Kanban, cerimônias e retrospectivas.",
        "doc_type": "process",
        "status": "approved",
        "version": "1.1",
        "tags": ["agil", "scrum", "kanban", "design-sprint", "papeis", "processo"],
    },
    "ddd-context-map.md": {
        "title": "Mapa de Contextos DDD",
        "description": "Bounded contexts, relações upstream/downstream e glossário da linguagem ubíqua.",
        "doc_type": "context-map",
        "status": "approved",
        "tags": ["ddd", "bounded-context", "linguagem-ubiqua"],
    },
    "threat-model.md": {
        "title": "Modelo de Ameaças",
        "description": "Ativos, atores e mitigações (STRIDE) do SHERPI.",
        "doc_type": "threat-model",
        "status": "approved",
        "tags": ["seguranca", "ameacas", "stride", "lgpd"],
    },
    "security.md": {
        "title": "Segurança e Confiabilidade",
        "description": "Controles de segurança e confiabilidade, separados em MVP e Fase 4.",
        "doc_type": "security",
        "status": "approved",
        "tags": ["seguranca", "confiabilidade", "lgpd", "observabilidade"],
    },
    "archive/sherpi-deep-research-v1.md": {
        "title": "Relatório de Pesquisa — SHERPI",
        "description": "Diagnóstico do Judiciário, gargalos, oportunidades de IA e proposta do MVP.",
        "doc_type": "research",
        "status": "reference",
        "tags": ["pesquisa", "judiciario", "peticoes", "ia", "mvp"],
    },
    "course-syllabus.md": {
        "title": "Ementa da Disciplina (DAIA)",
        "description": "Ementa de Desenvolvimento Ágil para Projetos de IA — contexto acadêmico.",
        "doc_type": "syllabus",
        "status": "reference",
        "tags": ["ementa", "academico", "agil"],
    },
    "adr/INDEX.md": {
        "title": "Índice de ADRs",
        "description": "Lista das decisões de arquitetura (Architecture Decision Records).",
        "doc_type": "adr-index",
        "status": "reference",
        "tags": ["adr", "arquitetura", "index"],
    },
    "pmp.md": {
        "title": "Plano de Gerenciamento do Projeto (PGP / PMP)",
        "description": "Escopo, tempo, custos, riscos, equipe, comunicação e qualidade do projeto SHERPI.",
        "doc_type": "pmp",
        "status": "approved",
        "tags": ["gerenciamento-de-projeto", "pgp", "pmp", "escopo", "riscos", "cronograma"],
    },
    "wbs.md": {
        "title": "Estrutura Analítica do Projeto (EAP / WBS)",
        "description": "Decomposição hierárquica do trabalho do SHERPI, com Gerenciamento de Projeto e Gestão e Rituais Ágeis.",
        "doc_type": "wbs",
        "status": "approved",
        "tags": ["eap", "wbs", "gerenciamento-de-projeto", "escopo"],
    },
    "demo-sprint-review.md": {
        "title": "Roteiro de Demo — Sprint Review",
        "description": "Runbook passo a passo para apresentar o MVP do SHERPI ao professor na Sprint Review.",
        "doc_type": "runbook",
        "status": "approved",
        "tags": ["demo", "sprint-review", "runbook", "apresentacao"],
    },
    "backlog.md": {
        "title": "Backlog do Produto e Sprint Backlog",
        "description": "Backlog do Produto (épicos e histórias, visão de futuro) e Sprint Backlog (tasks estimadas das 2 sprints).",
        "doc_type": "backlog",
        "status": "approved",
        "tags": ["backlog", "epicos", "historias-de-usuario", "sprint", "estimativas"],
    },
}

# ADRs: título derivado, doc_type=adr, status=accepted
_ADRS = {
    "adr/0001-ddd-hexagonal.md": "ADR-0001: DDD modular monolith + hexagonal",
    "adr/0002-explicit-orchestrator-vs-langgraph.md": "ADR-0002: Orquestrador explícito vs. LangGraph",
    "adr/0003-llm-agnostic-via-port.md": "ADR-0003: Camada LLM-agnóstica via port",
    "adr/0004-postgres-pgvector.md": "ADR-0004: PostgreSQL + pgvector",
    "adr/0005-gemini-flash-default.md": "ADR-0005: Gemini Flash como LLM default",
    "adr/0006-docker-db-only.md": "ADR-0006: Docker apenas para o banco",
    "adr/0007-auth-jwt-single-profile.md": "ADR-0007: Autenticação JWT com perfil único",
    "adr/0008-multi-dominio-rito-aware.md": "ADR-0008: Arquitetura multi-domínio (rito-aware)",
}
for rel, title in _ADRS.items():
    META[rel] = {
        "title": title,
        "description": title.split(": ", 1)[1] + " — contexto, decisão e consequências.",
        "doc_type": "adr",
        "status": "accepted",
        "tags": ["adr", "arquitetura", "decisao"],
    }


def _yaml_list(items: list[str]) -> str:
    return "[" + ", ".join(items) + "]"


def _q(value: object) -> str:
    """Escapa e aspas um escalar (valores podem conter ':' — ex.: títulos de ADR)."""
    s = str(value).replace("\\", "\\\\").replace('"', '\\"')
    return f'"{s}"'


def build_frontmatter(meta: dict[str, object]) -> str:
    lines = ["---"]
    lines.append(f"title: {_q(meta['title'])}")
    lines.append(f"description: {_q(meta['description'])}")
    lines.append(f"doc_type: {meta['doc_type']}")
    lines.append("project: SHERPI")
    lines.append(f"status: {meta['status']}")
    lines.append(f"version: {meta.get('version', '1.0')!s}")
    lines.append(f"updated: {UPDATED}")
    lines.append("language: pt-BR")
    lines.append(f"tags: {_yaml_list(list(meta['tags']))}")  # type: ignore[arg-type]
    lines.append("---")
    return "\n".join(lines)


def main() -> None:
    changed, skipped = 0, 0
    for rel, meta in META.items():
        path = DOCS / rel
        if not path.exists():
            print(f"!! ausente: {rel}")
            continue
        text = path.read_text(encoding="utf-8")
        # Remove frontmatter existente (substituição idempotente).
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) == 3:
                text = parts[2].lstrip("\n")
        path.write_text(build_frontmatter(meta) + "\n\n" + text, encoding="utf-8")
        changed += 1
        print(f"++ frontmatter: {rel}")
    print(f"\n{changed} atualizados, {skipped} ignorados.")


if __name__ == "__main__":
    main()
