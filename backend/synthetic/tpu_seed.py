"""Seed rotulado de TPU (Tabela Processual Única — CNJ) para a Sprint 5.

Contém 30 entradas sintéticas (15 cível + 15 trabalhista) usadas para popular
o índice k-NN e para o eval de acurácia top-1/top-3.
"""

from __future__ import annotations

from sherpi.contexts.taxonomy.domain.tpu import TpuEntry
from sherpi.shared_kernel.value_objects import Rito

_RAW: list[dict[str, str]] = [
    # ── Cível ──────────────────────────────────────────────────────────────────
    {
        "id": "civel-001",
        "tpu_code": "1116",
        "description": "Indenização por Dano Moral",
        "rito": "CIVEL",
        "text_excerpt": (
            "O requerente pleiteia indenização por danos morais decorrentes de inscrição "
            "indevida nos cadastros de inadimplentes (SPC e Serasa) sem que houvesse débito "
            "legítimo. A conduta da requerida causou constrangimento, abalo à honra e "
            "reflexos negativos na vida pessoal e profissional do autor, configurando dano "
            "moral presumido (in re ipsa), nos termos da jurisprudência consolidada do STJ. "
            "Requer condenação ao pagamento de indenização por danos morais, a ser arbitrada "
            "por este Juízo."
        ),
    },
    {
        "id": "civel-002",
        "tpu_code": "1116",
        "description": "Indenização por Dano Moral",
        "rito": "CIVEL",
        "text_excerpt": (
            "A parte autora postula reparação por danos morais em razão de falha na prestação "
            "de serviços bancários, incluindo saques não autorizados em sua conta corrente. "
            "A instituição financeira requerida não adotou as medidas de segurança adequadas, "
            "causando prejuízo material e moral ao consumidor. A responsabilidade é objetiva "
            "por força do Código de Defesa do Consumidor, art. 14. Requer indenização "
            "correspondente ao dano sofrido."
        ),
    },
    {
        "id": "civel-003",
        "tpu_code": "11176",
        "description": "Cobrança",
        "rito": "CIVEL",
        "text_excerpt": (
            "Trata-se de ação de cobrança referente a débito oriundo de contrato de prestação "
            "de serviços firmado entre as partes. A requerida deixou de efetuar o pagamento "
            "das parcelas contratadas, totalizando o valor descrito na inicial. Apesar das "
            "notificações extrajudiciais, o débito permanece em aberto, razão pela qual a "
            "autora busca a condenação ao pagamento do principal acrescido de juros de mora "
            "e correção monetária desde o inadimplemento."
        ),
    },
    {
        "id": "civel-004",
        "tpu_code": "11176",
        "description": "Cobrança",
        "rito": "CIVEL",
        "text_excerpt": (
            "A autora pleiteia a cobrança de valores devidos em decorrência de locação "
            "comercial, incluindo aluguéis vencidos e encargos contratuais não pagos pelo "
            "réu. O contrato previa reajuste anual pelo IGPM e multa por inadimplemento. "
            "Notificado extrajudicialmente, o locatário quedou-se inerte. Requer-se a "
            "condenação ao pagamento dos aluguéis em atraso, multa contratual e honorários."
        ),
    },
    {
        "id": "civel-005",
        "tpu_code": "10398",
        "description": "Rescisão do Contrato",
        "rito": "CIVEL",
        "text_excerpt": (
            "O autor pleiteia a rescisão do contrato de compra e venda de imóvel celebrado "
            "com a requerida, em razão de inadimplemento contratual consistente na não "
            "entrega do bem no prazo estipulado. A construtora descumpriu o cronograma "
            "de obras por mais de 24 meses, configurando mora contumaz. Requer rescisão "
            "com devolução integral dos valores pagos corrigidos, além de indenização "
            "por lucros cessantes e danos morais."
        ),
    },
    {
        "id": "civel-006",
        "tpu_code": "10398",
        "description": "Rescisão do Contrato",
        "rito": "CIVEL",
        "text_excerpt": (
            "Postula-se a rescisão de contrato de prestação de serviços de internet por "
            "falha reiterada no fornecimento do serviço contratado. A operadora não "
            "cumpriu o prazo de velocidade mínima garantida, tampouco solucionou as "
            "reclamações do consumidor no prazo legal. Requer rescisão sem multa, "
            "restituição dos valores pagos no período de inadimplemento e indenização "
            "por danos morais."
        ),
    },
    {
        "id": "civel-007",
        "tpu_code": "10674",
        "description": "Obrigação de Fazer",
        "rito": "CIVEL",
        "text_excerpt": (
            "A parte autora requer a condenação da requerida à obrigação de fazer consistente "
            "em concluir as obras de reforma do imóvel objeto do contrato de empreitada "
            "firmado entre as partes. A ré paralisou os serviços sem justificativa após "
            "receber 70% do valor contratado. Requer tutela de urgência para retomada "
            "imediata das obras, sob pena de multa diária, além de indenização pelos "
            "danos causados pela paralisação."
        ),
    },
    {
        "id": "civel-008",
        "tpu_code": "10674",
        "description": "Obrigação de Fazer",
        "rito": "CIVEL",
        "text_excerpt": (
            "O autor postula obrigação de fazer consistente na entrega dos documentos de "
            "transferência do veículo adquirido do réu há mais de noventa dias. O comprador "
            "pagou integralmente o preço ajustado, porém o vendedor não providenciou a "
            "documentação necessária junto ao DETRAN, impedindo a regularização do bem. "
            "Requer tutela antecipada para compelir a entrega dos documentos sob pena "
            "de astreintes."
        ),
    },
    {
        "id": "civel-009",
        "tpu_code": "10531",
        "description": "Revisional de Aluguel",
        "rito": "CIVEL",
        "text_excerpt": (
            "O locatário pleiteia a revisão judicial do valor do aluguel do imóvel residencial "
            "que ocupa, sob o fundamento de que o valor praticado distancia-se em mais de 20% "
            "do preço de mercado para imóveis similares na mesma região. Laudo de avaliação "
            "imobiliária instrui a inicial demonstrando a defasagem. Requer fixação de "
            "aluguel conforme valor de mercado apurado em perícia, retroagindo à data da "
            "citação."
        ),
    },
    {
        "id": "civel-010",
        "tpu_code": "10531",
        "description": "Revisional de Aluguel",
        "rito": "CIVEL",
        "text_excerpt": (
            "O locador postula revisão judicial do aluguel comercial com fulcro no art. 19 "
            "da Lei de Locações, por verificar que o valor corrente está abaixo do preço "
            "de mercado após período de três anos sem revisão. A localização privilegiada "
            "do ponto comercial e a valorização da região justificam o reajuste. Requer "
            "perícia para apuração do valor justo de mercado e condenação ao pagamento "
            "da diferença."
        ),
    },
    {
        "id": "civel-011",
        "tpu_code": "6230",
        "description": "Despejo por Falta de Pagamento",
        "rito": "CIVEL",
        "text_excerpt": (
            "O locador propõe ação de despejo por falta de pagamento de aluguéis, "
            "encargos e IPTU referentes aos últimos seis meses, totalizando valor "
            "indicado na inicial. O locatário foi notificado e não purgou a mora nem "
            "desocupou o imóvel voluntariamente. Requer liminar de desocupação em "
            "quinze dias, nos termos do art. 59, §1º, IX da Lei 8.245/91, além da "
            "condenação ao pagamento dos valores em atraso."
        ),
    },
    {
        "id": "civel-012",
        "tpu_code": "7619",
        "description": "Usucapião",
        "rito": "CIVEL",
        "text_excerpt": (
            "O autor postula o reconhecimento da usucapião especial urbana do imóvel "
            "que ocupa com animus domini há mais de cinco anos, de forma mansa, pacífica "
            "e ininterrupta, utilizando-o como sua moradia habitual junto à sua família. "
            "O imóvel possui área inferior a 250m² e o possuidor não é proprietário de "
            "outro bem imóvel. Preenchidos os requisitos do art. 183 da Constituição "
            "Federal e art. 1.240 do Código Civil."
        ),
    },
    {
        "id": "civel-013",
        "tpu_code": "10786",
        "description": "Responsabilidade Civil do Fornecedor",
        "rito": "CIVEL",
        "text_excerpt": (
            "O consumidor requer indenização em razão de defeito no produto adquirido "
            "que causou dano material e pessoal. O produto apresentou vício oculto "
            "que a fornecedora não sanou no prazo de 30 dias previsto no CDC. A "
            "responsabilidade é objetiva nos termos do art. 12 do Código de Defesa "
            "do Consumidor. Requer a restituição do valor pago, ressarcimento dos "
            "danos materiais comprovados e indenização por danos morais."
        ),
    },
    {
        "id": "civel-014",
        "tpu_code": "10004",
        "description": "Execução de Título Extrajudicial",
        "rito": "CIVEL",
        "text_excerpt": (
            "O exequente propõe execução de título extrajudicial com base em nota "
            "promissória emitida pelo executado, líquida, certa e exigível, vencida "
            "e não paga. O título preenche todos os requisitos do art. 783 do CPC. "
            "Requer citação do executado para pagar ou oferecer bens à penhora, sob "
            "pena de expropriação, acrescidos de juros de mora, correção monetária "
            "e honorários advocatícios."
        ),
    },
    {
        "id": "civel-015",
        "tpu_code": "11185",
        "description": "Ação Monitória",
        "rito": "CIVEL",
        "text_excerpt": (
            "O autor propõe ação monitória com base em cheque prescrito e documentos "
            "que comprovam a relação negocial e a dívida do réu. Embora o título esteja "
            "prescrito para execução direta, conserva sua força probante para a via "
            "monitória nos termos da Súmula 299 do STJ. Requer a expedição de mandado "
            "de pagamento para que o réu pague o valor indicado em quinze dias, sob "
            "pena de constituição de título judicial."
        ),
    },
    # ── Trabalhista ────────────────────────────────────────────────────────────
    {
        "id": "trab-001",
        "tpu_code": "9583",
        "description": "Verbas Rescisórias",
        "rito": "TRABALHISTA",
        "text_excerpt": (
            "O reclamante postula o pagamento das verbas rescisórias não quitadas na "
            "rescisão do contrato de trabalho, incluindo saldo de salário, aviso prévio "
            "indenizado proporcional, férias proporcionais com 1/3, décimo terceiro "
            "salário proporcional e multa de 40% sobre o FGTS. A reclamada homologou "
            "a rescisão sem efetuar o correto pagamento de todos os direitos. Os valores "
            "estão discriminados na planilha de cálculo que instrui a inicial."
        ),
    },
    {
        "id": "trab-002",
        "tpu_code": "9583",
        "description": "Verbas Rescisórias",
        "rito": "TRABALHISTA",
        "text_excerpt": (
            "O empregado dispensado sem justa causa requer o pagamento integral das "
            "verbas rescisórias, pois o TRCT foi homologado com valores incorretos. "
            "A reclamada calculou o aviso prévio proporcional de forma equivocada, "
            "reduziu indevidamente as férias vencidas e não depositou a multa fundiária "
            "integral. O pedido é certo, determinado e com valor indicado por rubrica "
            "na planilha de liquidação anexa."
        ),
    },
    {
        "id": "trab-003",
        "tpu_code": "9624",
        "description": "Horas Extras",
        "rito": "TRABALHISTA",
        "text_excerpt": (
            "O reclamante laborou habitualmente além da jornada legal de 8 horas diárias "
            "e 44 horas semanais, sem a devida contraprestação. Os registros de ponto "
            "anexados demonstram a prestação de horas extras por todo o período contratual. "
            "Requer o pagamento das horas extraordinárias acrescidas do adicional de 50%, "
            "reflexos em DSR, férias, décimo terceiro e FGTS. O pedido é líquido conforme "
            "planilha de cálculo. Valor total: R$ 28.500,00."
        ),
    },
    {
        "id": "trab-004",
        "tpu_code": "9624",
        "description": "Horas Extras",
        "rito": "TRABALHISTA",
        "text_excerpt": (
            "A reclamante pleiteia o reconhecimento e pagamento de horas extras decorrentes "
            "do trabalho em regime de sobreaviso não remunerado, por estar obrigada a "
            "permanecer de plantão com celular corporativo ligado fora do horário de "
            "expediente. Conforme súmula 428 do TST, o sobreaviso equivale a 1/3 da hora "
            "normal. O pedido totalizando R$ 15.200,00 está discriminado na planilha de "
            "liquidação que instrui esta reclamação trabalhista."
        ),
    },
    {
        "id": "trab-005",
        "tpu_code": "9619",
        "description": "Assédio Moral",
        "rito": "TRABALHISTA",
        "text_excerpt": (
            "O reclamante foi vítima de assédio moral sistemático praticado por seu "
            "superior hierárquico, consistente em humilhações públicas, metas "
            "sabidamente inatingíveis, isolamento e ameaças de demissão reiteradas. "
            "A conduta degradou as condições de trabalho e causou dano psicológico "
            "comprovado por laudo médico. Requer indenização por danos morais no valor "
            "de R$ 30.000,00, além das verbas rescisórias decorrentes de rescisão "
            "indireta por culpa do empregador."
        ),
    },
    {
        "id": "trab-006",
        "tpu_code": "9619",
        "description": "Assédio Moral",
        "rito": "TRABALHISTA",
        "text_excerpt": (
            "A reclamante sofreu assédio moral por parte da supervisora, que a humilhava "
            "perante colegas, atribuía tarefas excessivas e fazia comentários depreciativos "
            "sobre seu desempenho. As testemunhas presenciarão os episódios. A conduta "
            "causou síndrome de burnout diagnosticada por médico psiquiatra, conforme "
            "atestado anexo. Requer indenização por danos morais no valor de R$ 25.000,00 "
            "e indenização por danos materiais relativos ao tratamento médico."
        ),
    },
    {
        "id": "trab-007",
        "tpu_code": "9573",
        "description": "FGTS",
        "rito": "TRABALHISTA",
        "text_excerpt": (
            "O reclamante constata que a reclamada não efetuou os depósitos mensais do "
            "FGTS durante todo o período do contrato de trabalho, o que configura "
            "infração à Lei 8.036/90. Os extratos da conta vinculada do FGTS demonstram "
            "ausência de recolhimentos. Requer a condenação ao pagamento dos depósitos "
            "omitidos com a multa de 40%, correção pelo TRMC e juros de mora, "
            "totalizando R$ 18.750,00 conforme planilha de cálculo."
        ),
    },
    {
        "id": "trab-008",
        "tpu_code": "9573",
        "description": "FGTS",
        "rito": "TRABALHISTA",
        "text_excerpt": (
            "A reclamante requer o levantamento das diferenças de FGTS decorrentes do "
            "pagamento informal de parte do salário fora do contracheque (salário por "
            "fora), base de cálculo que deveria ter sido considerada para os depósitos "
            "fundiários. Havendo sonegação do salário real, os cálculos do FGTS foram "
            "feitos a menor. O pedido totaliza R$ 12.300,00 e está liquidado na "
            "planilha que instrui a inicial."
        ),
    },
    {
        "id": "trab-009",
        "tpu_code": "9581",
        "description": "Adicional de Insalubridade",
        "rito": "TRABALHISTA",
        "text_excerpt": (
            "O reclamante laborou exposto a agentes insalubres sem o fornecimento de "
            "EPIs adequados ou com EPIs ineficazes, em atividade enquadrada no Anexo "
            "14 da NR-15 (agentes biológicos). Laudo pericial deverá confirmar o "
            "enquadramento no grau máximo (40%). Requer o pagamento do adicional de "
            "insalubridade de 40% sobre o salário mínimo durante todo o contrato, "
            "com reflexos em DSR, férias e décimo terceiro. Valor: R$ 22.100,00."
        ),
    },
    {
        "id": "trab-010",
        "tpu_code": "9581",
        "description": "Adicional de Insalubridade",
        "rito": "TRABALHISTA",
        "text_excerpt": (
            "A reclamante exercia função de auxiliar de limpeza hospitalar, exposta a "
            "agentes biológicos de forma habitual sem a devida proteção, em "
            "enquadramento no grau máximo da NR-15. A reclamada não pagou o adicional "
            "de insalubridade durante todo o contrato. O pedido de adicional de 40% "
            "sobre o salário mínimo, com reflexos e integrações, totaliza R$ 19.800,00 "
            "conforme demonstrativo de cálculo."
        ),
    },
    {
        "id": "trab-011",
        "tpu_code": "9582",
        "description": "Adicional de Periculosidade",
        "rito": "TRABALHISTA",
        "text_excerpt": (
            "O eletricista reclamante exercia atividades em condições de periculosidade "
            "por trabalhar com eletricidade em alta tensão, nos termos do Anexo 4 da "
            "NR-16, sem receber o adicional de periculosidade de 30% sobre o salário "
            "base. Requer o pagamento do adicional por todo o período contratual, "
            "com os devidos reflexos em DSR, férias e décimo terceiro salário. "
            "Valor total do pedido: R$ 35.600,00."
        ),
    },
    {
        "id": "trab-012",
        "tpu_code": "9598",
        "description": "Equiparação Salarial",
        "rito": "TRABALHISTA",
        "text_excerpt": (
            "O reclamante exerce função idêntica à do paradigma indicado na inicial, "
            "com a mesma produtividade e perfeição técnica, trabalhando no mesmo "
            "estabelecimento e não tendo o paradigma vantagem pessoal. O salário do "
            "reclamante é R$ 1.500,00 inferior ao do paradigma, sem justificativa "
            "legítima. Requer o reconhecimento da equiparação salarial com pagamento "
            "das diferenças por todo o período, totalizando R$ 27.000,00."
        ),
    },
    {
        "id": "trab-013",
        "tpu_code": "9610",
        "description": "Reconhecimento de Vínculo Empregatício",
        "rito": "TRABALHISTA",
        "text_excerpt": (
            "O reclamante prestou serviços à reclamada de forma pessoal, onerosa, "
            "não eventual e com subordinação jurídica durante dois anos, sob o rótulo "
            "de pessoa jurídica (pejotização). Preenchidos os requisitos do art. 3º "
            "da CLT, impõe-se o reconhecimento do vínculo empregatício com o registro "
            "em CTPS e pagamento de todas as verbas trabalhistas devidas no período, "
            "incluindo FGTS, férias, décimo terceiro e verbas rescisórias."
        ),
    },
    {
        "id": "trab-014",
        "tpu_code": "9612",
        "description": "Rescisão Indireta",
        "rito": "TRABALHISTA",
        "text_excerpt": (
            "O reclamante requer o reconhecimento da rescisão indireta do contrato de "
            "trabalho por falta grave cometida pela empregadora, consistente em atraso "
            "reiterado no pagamento de salários por mais de três meses consecutivos, "
            "em descumprimento do art. 483, d, da CLT. A falta patronal é incontroversa "
            "e os extratos bancários comprovam o inadimplemento. Requer todas as verbas "
            "como se demissão sem justa causa fosse. Valor: R$ 42.800,00."
        ),
    },
    {
        "id": "trab-015",
        "tpu_code": "9625",
        "description": "Intervalo Intrajornada",
        "rito": "TRABALHISTA",
        "text_excerpt": (
            "O reclamante não usufruiu do intervalo intrajornada mínimo de uma hora "
            "previsto no art. 71 da CLT, sendo obrigado a realizar refeições no "
            "próprio posto de trabalho por determinação da chefia. Os registros de "
            "ponto demonstram a supressão habitual do intervalo. Requer o pagamento "
            "do período suprimido acrescido de 50%, com natureza salarial e reflexos "
            "em parcelas que integram a remuneração. Valor: R$ 9.800,00."
        ),
    },
]


def load_seed() -> list[TpuEntry]:
    """Retorna as entradas do seed TPU para popular o índice e o eval."""
    return [
        TpuEntry(
            id=r["id"],
            tpu_code=r["tpu_code"],
            description=r["description"],
            rito=Rito(r["rito"]),
            text_excerpt=r["text_excerpt"],
        )
        for r in _RAW
    ]
