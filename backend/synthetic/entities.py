"""Catálogo de entidades **fake** — pessoas físicas e jurídicas com dados cadastrais
completos e coerentes (sem PII real; decisão *synthetic-first* / LGPD).

Gera entidades determinísticas a partir de uma seed, com CPF/CNPJ de checksum válido,
endereço coerente (logradouro + bairro + cidade/UF + CEP) e, para a PJ, um representante
legal que é uma `PessoaFisica` do mesmo catálogo. É a fonte única de identidades usada
pelo gerador de templates (`from_template`) e pelo corpus do zero (`builder`).

Uso (export opcional p/ inspeção humana):
    uv run python -m synthetic.entities --pf 30 --pj 15 --out data/fake_entities.json
"""

from __future__ import annotations

import argparse
import json
import random
from dataclasses import asdict, dataclass
from pathlib import Path

# --- Pools (fictícios) -----------------------------------------------------------

_PRENOMES = [
    "Ana",
    "Bruno",
    "Carla",
    "Daniel",
    "Eduardo",
    "Fernanda",
    "Gustavo",
    "Helena",
    "Igor",
    "Juliana",
    "Lucas",
    "Mariana",
    "Nelson",
    "Patrícia",
    "Rafael",
    "Sofia",
    "Thiago",
    "Vanessa",
    "André",
    "Beatriz",
]
_SOBRENOMES = [
    "Silva",
    "Souza",
    "Costa",
    "Pereira",
    "Almeida",
    "Ferreira",
    "Rodrigues",
    "Lima",
    "Gomes",
    "Carvalho",
    "Martins",
    "Rocha",
    "Ribeiro",
    "Alves",
    "Mendes",
    "Barbosa",
]
_PROFISSOES = [
    "autônomo(a)",
    "comerciante",
    "professor(a)",
    "motorista",
    "aposentado(a)",
    "analista de sistemas",
    "vendedor(a)",
    "servidor(a) público(a)",
    "engenheiro(a)",
    "enfermeiro(a)",
]
_ESTADO_CIVIL = ["solteiro(a)", "casado(a)", "divorciado(a)", "viúvo(a)", "em união estável"]
# (cidade, UF, prefixo de CEP) — fictício, mas plausível.
_CIDADES_UF = [
    ("Brasília", "DF", "70"),
    ("Goiânia", "GO", "74"),
    ("São Paulo", "SP", "01"),
    ("Campinas", "SP", "13"),
    ("Belo Horizonte", "MG", "30"),
    ("Curitiba", "PR", "80"),
    ("Rio de Janeiro", "RJ", "20"),
    ("Salvador", "BA", "40"),
]
_LOGRADOUROS = [
    "Rua das Acácias",
    "Avenida Central",
    "Quadra QNM {q}, Conjunto {c}",
    "Rua 15 de Novembro",
    "Avenida das Nações",
    "SQN {q}, Bloco {c}",
    "Rua dos Ipês",
    "Travessa São João",
]
_RAMOS = [
    "Comércio",
    "Serviços",
    "Tecnologia",
    "Logística",
    "Energia",
    "Telecomunicações",
    "Crédito e Financiamentos",
    "Varejo",
]
_PREFIXOS_PJ = ["Alfa", "Beta", "Gama", "Delta", "Ômega", "Sigma", "Vértice", "Horizonte"]
_SUFIXOS_PJ = ["LTDA.", "S/A", "ME", "EIRELI", "Comércio LTDA."]


# --- CPF / CNPJ com checksum válido ----------------------------------------------


def cpf_valido(rng: random.Random) -> str:
    digits = [rng.randint(0, 9) for _ in range(9)]
    for j in range(2):
        s = sum((10 + j - i) * digits[i] for i in range(9 + j))
        digits.append((s * 10 % 11) % 10)
    d = digits
    return f"{d[0]}{d[1]}{d[2]}.{d[3]}{d[4]}{d[5]}.{d[6]}{d[7]}{d[8]}-{d[9]}{d[10]}"


def cnpj_valido(rng: random.Random) -> str:
    base = [rng.randint(0, 9) for _ in range(8)] + [0, 0, 0, 1]  # filial 0001

    def dv(nums: list[int], weights: list[int]) -> int:
        r = sum(a * b for a, b in zip(nums, weights, strict=True)) % 11
        return 0 if r < 2 else 11 - r

    d1 = dv(base, [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])
    d2 = dv([*base, d1], [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])
    d = [*base, d1, d2]
    return f"{d[0]}{d[1]}.{d[2]}{d[3]}{d[4]}.{d[5]}{d[6]}{d[7]}/{d[8]}{d[9]}{d[10]}{d[11]}-{d[12]}{d[13]}"


# --- Entidades -------------------------------------------------------------------


@dataclass(frozen=True)
class Endereco:
    logradouro: str
    numero: int
    bairro: str
    cidade: str
    uf: str
    cep: str

    def __str__(self) -> str:
        return f"{self.logradouro}, nº {self.numero}, {self.bairro}, {self.cidade}/{self.uf}, CEP {self.cep}"


@dataclass(frozen=True)
class PessoaFisica:
    nome: str
    cpf: str
    rg: str
    orgao_expedidor: str
    data_nascimento: str
    nacionalidade: str
    estado_civil: str
    profissao: str
    nome_pai: str
    nome_mae: str
    endereco: Endereco
    telefone: str
    email: str

    @property
    def filiacao(self) -> str:
        return f"{self.nome_pai} e {self.nome_mae}"


@dataclass(frozen=True)
class PessoaJuridica:
    razao_social: str
    nome_fantasia: str
    cnpj: str
    inscricao_estadual: str
    endereco: Endereco
    telefone: str
    email: str
    representante: PessoaFisica


# --- Fábricas (determinísticas por rng) ------------------------------------------


def _nome_completo(rng: random.Random) -> str:
    sobrenomes = rng.sample(_SOBRENOMES, 2)  # distintos → evita "Silva Silva"
    return f"{rng.choice(_PRENOMES)} {sobrenomes[0]} {sobrenomes[1]}"


def _endereco(rng: random.Random) -> Endereco:
    cidade, uf, cep_pref = rng.choice(_CIDADES_UF)
    logradouro = rng.choice(_LOGRADOUROS).format(q=rng.randint(1, 40), c=rng.choice("ABCDEF"))
    return Endereco(
        logradouro=logradouro,
        numero=rng.randint(1, 1999),
        bairro=rng.choice(["Centro", "Jardim América", "Setor Sul", "Vila Nova", "Bela Vista"]),
        cidade=cidade,
        uf=uf,
        cep=f"{cep_pref}{rng.randint(0, 9)}{rng.randint(10, 99)}-{rng.randint(100, 999)}",
    )


def make_pessoa_fisica(rng: random.Random, *, nome: str | None = None) -> PessoaFisica:
    nome = nome or _nome_completo(rng)
    primeiro = nome.split()[0].lower()
    return PessoaFisica(
        nome=nome,
        cpf=cpf_valido(rng),
        rg=f"{rng.randint(1, 9)}.{rng.randint(100, 999)}.{rng.randint(100, 999)}",
        orgao_expedidor=f"SSP/{rng.choice(['DF', 'SP', 'GO', 'MG', 'RJ'])}",
        data_nascimento=f"{rng.randint(1, 28):02d}/{rng.randint(1, 12):02d}/{rng.randint(1960, 2002)}",
        nacionalidade="brasileiro(a)",
        estado_civil=rng.choice(_ESTADO_CIVIL),
        profissao=rng.choice(_PROFISSOES),
        nome_pai=_nome_completo(rng),
        nome_mae=_nome_completo(rng),
        endereco=_endereco(rng),
        telefone=f"(61) 9{rng.randint(1000, 9999)}-{rng.randint(1000, 9999)}",
        email=f"{primeiro}.{rng.randint(1, 999)}@exemplo.com",
    )


def make_pessoa_juridica(rng: random.Random) -> PessoaJuridica:
    fantasia = f"{rng.choice(_PREFIXOS_PJ)} {rng.choice(_RAMOS)}"
    return PessoaJuridica(
        razao_social=f"{fantasia} {rng.choice(_SUFIXOS_PJ)}",
        nome_fantasia=fantasia,
        cnpj=cnpj_valido(rng),
        inscricao_estadual=f"{rng.randint(100, 999)}.{rng.randint(100, 999)}.{rng.randint(100, 999)}",
        endereco=_endereco(rng),
        telefone=f"(61) 3{rng.randint(100, 999)}-{rng.randint(1000, 9999)}",
        email=f"contato@{rng.choice(_PREFIXOS_PJ).lower()}.com.br",
        representante=make_pessoa_fisica(rng),
    )


def make_distinct_pessoas(rng: random.Random, n: int) -> list[PessoaFisica]:
    """`n` pessoas físicas com **prenomes distintos** — evita repetição visível
    entre as partes de uma mesma peça (ex.: dois autores com o mesmo primeiro nome)."""
    prenomes = rng.sample(_PRENOMES, n)
    return [
        make_pessoa_fisica(rng, nome=f"{pre} {' '.join(rng.sample(_SOBRENOMES, 2))}")
        for pre in prenomes
    ]


def build_catalog(
    *, seed: int = 42, n_pf: int = 30, n_pj: int = 15
) -> tuple[list[PessoaFisica], list[PessoaJuridica]]:
    """Catálogo determinístico de `n_pf` pessoas físicas e `n_pj` jurídicas."""
    rng = random.Random(seed)
    return (
        [make_pessoa_fisica(rng) for _ in range(n_pf)],
        [make_pessoa_juridica(rng) for _ in range(n_pj)],
    )


# --- CLI: exporta o catálogo p/ JSON (inspeção humana) ---------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description="Exporta um catálogo de entidades fake (JSON).")
    parser.add_argument("--pf", type=int, default=30, help="quantas pessoas físicas")
    parser.add_argument("--pj", type=int, default=15, help="quantas pessoas jurídicas")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--out", type=Path, default=Path("data/fake_entities.json"))
    args = parser.parse_args()

    pf, pj = build_catalog(seed=args.seed, n_pf=args.pf, n_pj=args.pj)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(
            {
                "pessoas_fisicas": [asdict(p) for p in pf],
                "pessoas_juridicas": [asdict(p) for p in pj],
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    print(f"{len(pf)} PF + {len(pj)} PJ exportadas em {args.out}")


if __name__ == "__main__":
    main()
