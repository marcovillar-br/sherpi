---
title: "Relatório de Pesquisa — SHERPI"
description: "Diagnóstico do Judiciário, gargalos, oportunidades de IA e proposta do MVP."
doc_type: research
project: SHERPI
status: reference
version: 1.0
updated: 2026-06-18
language: pt-BR
tags: [pesquisa, judiciario, peticoes, ia, mvp]
---

# Relatório Técnico e Estratégico: Arquitetura e Implementação de Inteligência Artificial para Otimização do Fluxo de Petições no Judiciário Brasileiro

A transição digital do Poder Judiciário brasileiro, outrora focada de
maneira estrita na virtualização dos autos físicos para o formato
eletrônico, adentra agora uma fase incontornável de automação cognitiva
e reestruturação de fluxos operacionais. O cenário contemporâneo
exige que os tribunais adotem soluções que transcendam o mero
armazenamento digital em banco de dados, demandando arquiteturas de
sistemas capazes de processar, compreender, classificar e
estruturar o colossal volume de dados textuais não estruturados
que ingressam diariamente nas cortes. A implementação de soluções
baseadas em Inteligência Artificial (IA) não representa mais uma visão
futurista ou um luxo de modernização institucional; trata-se,
fundamentalmente, de uma necessidade premente de gestão pública,
governança e sobrevivência operacional, visando à garantia
constitucional da razoável duração do processo e à eficiência
jurisdicional.

Este relatório apresenta uma análise exaustiva e multidisciplinar dos
gargalos operacionais enfrentados pelos magistrados de primeiro e
segundo graus, mapeia o impacto direto e indireto da estrutura
redacional das petições judiciais nesse panorama sistêmico,
elabora um mapa de oportunidades tecnológicas alicerçado no estado da
arte da IA e, por fim, delineia o escopo técnico detalhado para o
desenvolvimento e a implementação de um Produto Mínimo Viável (MVP) em
um ciclo de desenvolvimento ágil de três semanas.

## 1. Diagnóstico do Judiciário: A Visão do Magistrado e os Gargalos Operacionais

A análise estrutural do Judiciário brasileiro revela um ecossistema
submetido a uma pressão de demanda sem paralelos no direito comparado
mundial. O magistrado, posicionado no ápice da cadeia decisória e
responsável pela chancela final da prestação jurisdicional, enfrenta
obstáculos diários e estruturais que reduzem significativamente o tempo
disponível para a sua atividade-fim fundamental: a análise aprofundada
de teses jurídicas complexas, a condução probatória e a prolação de
decisões justas e fundamentadas. A partir da compilação de dados
estatísticos recentes e das manifestações das corregedorias, destacam-se
três gargalos operacionais centrais que asfixiam a capacidade de
resposta das varas judiciais.

### 1.1. A Epidemia de Litigiosidade e a Sobrecarga Sistêmica de Casos Pendentes

O primeiro e mais evidente problema enfrentado pelos juízes no Brasil
hoje é o excesso de litigiosidade crônica, caracterizado por
volumes de ingresso de novos processos que superam sistematicamente a
capacidade humana de processamento e julgamento em tempo real. Os dados
extraídos do mais recente relatório *Justiça em Números 2025* (ano-base
2024), consolidado anualmente pelo Conselho Nacional de Justiça (CNJ)
por meio da Base Nacional de Dados do Poder Judiciário (DataJud),
evidenciam que a litigiosidade contra o Poder Público e grandes
corporações continua sendo o principal fator de sobrecarga das varas e
tribunais.^1^

A análise pormenorizada da composição do polo passivo das demandas
revela uma assimetria profunda e estrutural na distribuição processual
nacional. Dos vinte maiores réus do país, dez são entes públicos ou
autarquias estatais, os quais, em conjunto, respondem por 6,84 milhões
de ações pendentes, o que representa aproximadamente 8,5% de todos os
casos pendentes no acervo nacional no ano de 2024.^2^ O Instituto
Nacional do Seguro Social (INSS) lidera isoladamente e com larga margem
essa métrica, figurando no polo passivo de mais de 4,2 milhões de
processos, consolidando o que autoridades da cúpula do Judiciário
definem expressamente como uma verdadeira \"epidemia de
litigiosidade\".^2^ Apenas no último ano analisado, o INSS acumulou 227
mil novos processos, demonstrando que a curva de entrada permanece em
franca ascensão.^2^

A tabela a seguir demonstra a concentração de demandas nos maiores
litigantes públicos do país, evidenciando o peso que essas entidades
exercem sobre a máquina judiciária:

  ----------------------- ----------------------- -----------------------
  **Posição no Ranking    **Ente Público / Grande **Número de Casos
  Nacional**              Litigante**             Pendentes no Polo
                                                  Passivo (2024)**

  1º                      Instituto Nacional do   4.209.735
                          Seguro Social (INSS)    

  2º                      Estado de São Paulo     530.835

  3º                      Ministério da Fazenda   497.143

  4º                      Estado do Rio Grande do 362.166
                          Sul                     

  5º                      Advocacia-Geral da      285.220
                          União (AGU)             

  6º                      Estado da Bahia         239.826

  7º                      Estado de Minas Gerais  226.012

  8º                      Presidência da          194.053
                          República               

  9º                      Estado do Paraná        152.144

  10º                     Estado do Rio de        146.888
                          Janeiro                 
  ----------------------- ----------------------- -----------------------

Fonte: Dados consolidados do Justiça em Números 2025 (CNJ).^2^

Essa concentração brutal gera pautas massificadas de demandas
repetitivas (como revisões de benefícios previdenciários, execuções
fiscais, ações de saúde e contencioso bancário em massa), obrigando
juízes e seus quadros de assessores a dedicarem a maior parte de suas
jornadas de trabalho à análise mecânica e repetitiva de teses jurídicas
idênticas, em detrimento da dedicação intelectual a casos que exigem
maior densidade analítica e inovação jurisprudencial.

Para dimensionar de forma concreta o impacto dessa macroestrutura na
rotina diária da magistratura, os tribunais estaduais de médio e grande
porte enfrentam cargas de trabalho extenuantes e limítrofes. No Tribunal
de Justiça do Estado de Santa Catarina (TJSC), a título de
exemplificação de alta performance sob estresse, registraram-se 1,28
milhão de casos novos apenas em 2024.^3^ A carga de trabalho líquida por
magistrado nesse tribunal atingiu o assustador patamar de 8.011
processos sob a responsabilidade de um único julgador.^3^ Embora o
Índice de Produtividade dos Magistrados (IPM) tenha registrado aumentos
significativos --- chegando a 3.281 processos baixados por juiz, um
índice 27% acima da média nacional --- e o Índice de Produtividade dos
Servidores (IPS) tenha aumentado 16%, a manutenção desse cenário é
humanamente insustentável a longo prazo sem intervenção tecnológica.^3^
O TJSC logrou reduzir a sua taxa de congestionamento total para 66,1% e
a líquida para 58,8%, alcançando um Índice de Atendimento à Demanda
(IAD) de 114%, mas o esforço institucional e pessoal exigido para baixar
mais processos do que a entrada de novos casos (batendo as metas do CNJ)
expõe o limite físico e cognitivo da força de trabalho judiciária.^3^ A
continuidade dessa trajetória exige racionalidade algorítmica para
evitar que o sistema seja novamente sobrecarregado por demandas
automatizadas.^4^

### 1.2. O Gargalo da Triagem e a Ineficiência na Classificação Taxonômica (TPU)

O segundo problema operacional central reside na porta de entrada do
judiciário, no momento exato do ingresso da petição inicial ou de um
recurso incidente: a triagem, autuação e classificação do processo. Para
resolver problemas históricos de fragmentação de dados entre os estados,
o CNJ desenvolveu, desde 2007 (Resolução nº 46/2007, alterada pela
Resolução nº 326/2020), as Tabelas Processuais Unificadas (TPU).^5^ A
TPU tem a finalidade precípua de padronizar nacionalmente o
cadastramento das classes processuais, dos assuntos e das
movimentações.^6^

A estruturação da TPU é complexa e divide-se em seis níveis hierárquicos
(desde a grande área do direito até a minúcia procedimental), exigindo
extrema precisão e acurácia do advogado no momento em que realiza a
distribuição da petição inicial no sistema de Processo Judicial
Eletrônico (PJe, e-SAJ, Eproc, etc.).^6^ Por exemplo, uma autuação
escorreita exige transitar pelos níveis: *Nível 1 (Processo Cível) -\>
Nível 2 (Processo de Conhecimento) -\> Nível 3 (Procedimento de
Conhecimento) -\> Nível 4 (Procedimentos Especiais) -\> Nível 5 (Leis
Esparsas) -\> Nível 6 (Discriminatória)*.^6^

Contudo, na prática da práxis forense diária, ocorre um severo
descompasso entre a norma e a realidade. A responsabilidade por essa
classificação inicial recai exclusivamente sobre o advogado, que,
frequentemente por desconhecimento técnico da taxonomia, por pressa, ou
até mesmo por estratégia (para burlar a prevenção de certos juízos),
cadastra os processos com classes ou assuntos absolutamente genéricos
(como selecionar \"Direito Civil - Obrigações\" no Nível 1 e parar a
classificação, em vez de especificar o Nível 6 detalhando tratar-se de
um contrato de empréstimo consignado fraudulento).

Quando a petição é distribuída de forma equivocada na árvore taxonômica
das TPU, ela burla a automação rudimentar baseada em regras (if-then)
dos sistemas judiciais.^6^ Como resultado pernicioso, as secretarias das
varas cíveis, dos juizados especiais e os gabinetes dos juízes precisam
gastar centenas de horas mensais executando a triagem analógica e
manual. Um servidor precisa abrir o arquivo PDF da petição inicial, ler
extensamente a narrativa dos fatos e os pedidos, inferir a real intenção
da parte, corrigir a taxonomia no sistema e, sobretudo, identificar se
há pedidos de tutela de urgência (liminares) ocultos no meio do texto
que justifiquem a inversão da fila cronológica de processos. Este tempo
gasto na triagem de peças rouba a força de trabalho que deveria ser
alocada na elaboração de minutas complexas.

### 1.3. O Avanço da Litigância Predatória e a Manipulação Artificial da Jurisdição

O terceiro grande gargalo operacional, que emergiu de forma
devastadora nos últimos cinco anos, é o avanço geométrico das demandas
abusivas e artificiais, conhecidas institucionalmente e doutrinariamente
como litigiosidade predatória (ou *sham litigation* no direito
comparado).^7^ Esse fenômeno nefasto é caracterizado pelo
ajuizamento massivo, sistemático e orquestrado de ações carentes de
lastro fático idôneo --- frequentemente baseadas em petições iniciais
integralmente padronizadas (método *copy-paste*), com intensa
fragmentação de demandas (o ajuizamento de cinco ou dez ações distintas
para o mesmo autor abordando questões derivadas de um mesmo contrato que
deveriam obrigatoriamente ser unificadas em litisconsórcio ou cúmulo de
pedidos).^9^ Em casos de maior gravidade investigados por corregedorias,
constata-se a utilização criminosa de documentação forjada, fraudes
documentais por alteração de data de comprovantes de residência e o
ajuizamento de litígios sem o pleno e real consentimento da parte
autora, recaindo estas ações frequentemente sobre idosos, analfabetos ou
pessoas em situação de hipervulnerabilidade social.^10^

A litigância predatória atua, na prática, como um ataque de negação de
serviço (DDoS - *Distributed Denial of Service*) analógico contra as
varas cíveis, as varas de fazenda pública e os juizados
especiais.^10^ Gico Jr. (2014) teoriza o sistema judicial como
um recurso comum de livre acesso que, por ser caracteristicamente rival,
tem sua utilidade diminuída para o cidadão legítimo quando inundado por
litigantes abusivos que parasitam a gratuidade de justiça.^10^ O tempo
consumido e o custo repassado ao Estado pela secretaria para expedir
ofícios, realizar citações por AR e processar contestações em dezenas de
milhares de processos desprovidos de viabilidade jurídica material
subtraem diretamente a celeridade e violam o direito fundamental
constitucional à duração razoável do processo dos jurisdicionados de
boa-fé.^8^

Para o magistrado, o grande obstáculo reside na extrema dificuldade de
identificar isoladamente essas demandas em meio ao volume regular e
esmagador de processos. Quando as petições iniciais predatórias são
lidas e analisadas de maneira isolada em um gabinete, elas
frequentemente parecem revestidas de toda a formalidade e aparência
legal exigidas pelo Código de Processo Civil.^10^ Apenas a adoção de uma
visão macroscópica e estatística, cruzando dados não estruturados de
milhões de documentos e rastreando padrões de repetição (mesmo advogado,
mesmos CEPs, mesmo núcleo de texto, mesma ausência de documentos
comprobatórios do nexo causal), permite identificar de fato o
comportamento predatório organizado.^9^ Este desafio monumental motivou
a criação do Tema 1.198 de Recursos Repetitivos pelo Superior Tribunal
de Justiça (STJ) e a promulgação da Recomendação nº 159/2024 pelo
Conselho Nacional de Justiça, impondo a adoção de estratégias
centralizadas e tecnológicas de controle.^7^

## 2. O Papel da Petição Judicial Nesse Gargalo

A petição inicial é o instrumento propulsor do exercício da jurisdição,
sem a qual a máquina judiciária, atrelada ao princípio da inércia, não
atua. Contudo, a cultura processual brasileira enraizada e o uso
inadequado das ferramentas de processamento de texto pelos operadores do
direito transformaram a peça vestibular, assim como as petições
interlocutórias e os recursos recursais, em alguns dos principais
fatores endógenos de agravamento da morosidade judicial e do esgotamento
da força de trabalho dos juízes.

### 2.1. A Prolixidade, o Excesso de Liturgia e a Sobrecarga Cognitiva

A estrutura redacional das petições brasileiras configura-se,
historicamente e estatisticamente, como um obstáculo severo à
celeridade. Em vez de privilegiar a objetividade dos fatos substanciais
e a precisão hermenêutica do pedido, consolidou-se uma cultura nociva de
valorização da erudição excessiva, do barroquismo retórico e da extensão
desproporcional do texto processual.^12^ É necessário analisar com
extrema cautela mesmo uma petição prolixa para evitar o risco de
prolatar uma decisão nula ou contrária ao direito invocado na miríade de
laudas, o que exige um consumo severo de tempo de gabinete.^14^

Existem múltiplos e frequentes registros de magistrados pelo país
determinando ativamente a emenda de petições iniciais com base única e
exclusivamente em sua extensão irrazoável e na falta de técnica. Em um
caso paradigmático ocorrido no Rio Grande do Norte (Processo
0100222-69.2014.8.20.0125), uma petição inicial composta por 49 páginas
foi formalmente classificada pelo julgador em seu despacho como um
\"livro\".^15^ O magistrado, fundamentando-se na premissa da Organização
das Nações Unidas para a Educação, a Ciência e a Cultura (UNESCO) de que
textos a partir de 49 páginas configuram um livro, forçou a redução
objetiva do documento sob a forte justificativa de que obrigar o
Judiciário e a outra parte a ler centenas de laudas configura \"uma
estratégia desleal para encurtar o prazo da defesa\".^15^ Outros relatos
colhidos no Judiciário mencionam e criticam abertamente advogados
peticionando em exorbitantes 116 laudas para o trato de questões de
baixa complexidade ou ritos sumários.^13^

A repetição massiva de ementas de jurisprudência há muito tempo
pacificada pelas cortes superiores, a exaustiva citação de conceitos
analíticos dogmáticos plenamente dominados pelo juízo (como despender
dezenas de páginas dissertando sobre o conceito tripartido de crime em
varas criminais ou delineando o que configura dano moral em varas
cíveis), e o uso de uma linguagem prolixa e rebuscada geram um ruído
informacional severo e desnecessário.^13^ Magistrados ressaltam
expressamente que petições com linguagem confusa, nas quais cinco
argumentos são apresentados --- sendo apenas um deles juridicamente
relevante e os outros quatro apenas exercícios estilísticos e inidôneos
--- geram o risco crítico de o argumento principal sequer ser
compreendido pela assessoria, culminando na rejeição dos pedidos.^13^

Da mesma forma, no âmbito de peças interlocutórias, como os embargos de
declaração, os tribunais de justiça e tribunais regionais federais
frequentemente enfrentam a prolixa problemática de advogados que
utilizam recursos que deveriam ser de integração (para suprir omissões,
contradições ou erros materiais) como instrumentos protelatórios
extensos para rediscutir o mérito da lide de forma ampla e descabida,
gerando reações legais e jurisdicionais punitivas para manutenção da
ordem processual (como a aplicação de multas do art. 1.026 do CPC).^16^

Para o magistrado e o analista judiciário que processam mentalmente
dezenas de casos complexos todos os dias, a extração dos requisitos
fundamentais e inegociáveis previstos no artigo 319 do Código de
Processo Civil de 2015 (fatos articulados, fundamentos jurídicos
específicos, valor da causa e pedidos claros e delimitados) ^17^ dentro
de um oceano de textos copiados de bancos de modelos genéricos de
procedência duvidosa na internet consome uma energia cognitiva
incomensurável.^12^ Essa sobrecarga degrada a acurácia, eleva
drasticamente o tempo de processamento por feito e contribui intimamente
com o esgotamento funcional.

### 2.2. Omissões, Defeitos Estruturais e a Indústria do Retrabalho Processual

Em oposição polar ao excesso de texto inútil, as petições
contemporâneas sofrem gravemente com a escassez de materialidade
probatória e falhas nos requisitos essenciais mínimos previstos em
lei. Dados e levantamentos estatísticos indicam que, em
determinadas varas cíveis e juizados especiais pelo país, o índice de
falha é calamitoso: até seis de cada dez (60%) petições iniciais
distribuídas apresentam problemas estruturais impeditivos de pronto
julgamento.^18^ Essas falhas generalizadas incluem a ausência
de instrumentos de procuração válidos e atualizados, a falta de
comprovantes de residência idôneos, a omissão na juntada de memória de
cálculo detalhada em ações de cobrança e execuções, e, frequentemente, a
formulação de pedidos lógicos que são manifestamente incompatíveis com a
narração dos fatos.^17^ Modelos genéricos baixados na internet,
não adaptados ao caso concreto, são a gênese de grande parte dessa
deficiência técnica.^17^

Essas falhas geram um fluxo processual altamente ineficiente e
burocraticamente redundante, criando a indústria do retrabalho endógeno:

1.  O processo é autuado e ingressa na fila de conclusão. O juiz ou
    assessor dedica tempo para ler a petição e percebe o vício
    estrutural;

2.  É proferido um despacho fundamentado determinando a emenda da
    inicial, estabelecendo o prazo improrrogável de 15 dias úteis,
    conforme determina imperativamente o artigo 321 do CPC/15
    ^17^;

3.  A secretaria do juízo procede com os atos de intimação via diário
    oficial ou portal eletrônico;

4.  O advogado peticiona novamente no prazo legal, contudo, muitas
    vezes incorrendo em novos erros ou respondendo de maneira
    insatisfatória;

5.  O processo retorna à mesma fila de conclusão, exigindo uma nova
    leitura integral de resgate e recontextualização por parte do
    gabinete.

Caso o vício seja insanável ou a ordem não seja cumprida adequadamente,
o desfecho processual resulta no indeferimento preliminar da petição
inicial, nos termos do art. 330 do CPC/15, com a extinção prematura do
processo sem resolução de mérito, movimentando toda a estrutura
jurisdicional sem entregar qualquer resultado palpável e efetivo ao
tecido social.^17^ Esse ciclo de retrabalho oculto é um dos
principais vetores da elevada taxa de congestionamento, transformando um
ato que deveria ser único, contínuo e célere (a admissibilidade
positiva) em um procedimento cartorário fragmentado que se arrasta por
várias semanas e onera o erário.^14^

### 2.3. A Nova Ameaça Tecnológica: *Prompt Injection* e a Falsificação Direcionada à Inteligência Artificial

A implementação de soluções de tecnologia também carrega o ônus de
introduzir novos vetores de ataque processual. Com a adoção crescente
e, por vezes, informal de ferramentas de inteligência artificial
generativa de leitura de PDFs por magistrados, assessores e secretarias,
surgiu um fenômeno gravíssimo, sub-reptício e altamente lesivo: a
manipulação intencional e codificada do texto processual com o objetivo
direto de corromper a análise e as inferências automatizadas dos
algoritmos judiciais. A técnica, conhecida cientificamente e no
escopo de segurança da informação como *prompt injection* (injeção de
comando ou instrução), consiste na inserção de comandos imperativos
ocultos diretamente na estrutura do corpo ou dos metadados da petição em
formato PDF. O objetivo malicioso dessa injeção é induzir os
Modelos de Linguagem de Grande Escala (LLMs) adotados pelo juízo a
ignorarem os fatos reais do documento e gerarem resumos mentirosos
favoráveis à parte ou a concederem benefícios e pedidos liminares (como
justiça gratuita ou tutelas de urgência inaudita altera parte) de
maneira indevida.^20^

Casos emblemáticos e recentes no Judiciário brasileiro demonstraram que
essa ameaça é concreta. Em 13 de maio de 2026, na 3ª Vara do Trabalho de
Parauapebas (Pará), ocorreu o primeiro registro documentado de punição
judicial para essa prática. Advogadas inseriram comandos imperativos
ocultos contra a IA no bojo da petição, formatando a fonte na cor branca
sobre o fundo branco, tornando o conteúdo plenamente invisível à leitura
de qualquer humano (seja o magistrado, o promotor ou a parte contrária),
mas perfeitamente extraível e legível pelo extrator algorítmico
(*parser*) que realiza o *scraping* do texto e alimenta os sistemas
processuais de IA.^20^ Essa manobra culminou na aplicação de multa por
litigância de má-fé por violação dos arts. 5º e 77º do CPC.^21^ Pouco
depois, cenário similar ocorreu no Foro Central Cível de São Paulo
(Processo nº 4050201-45.2025.8.26.0100), no qual o juiz detectou que a
petição de um banco réu continha instruções ocultas diretas para
eventuais sistemas automáticos, exigindo explicações formais sob pena de
acionamento do núcleo disciplinar da Ordem dos Advogados do Brasil (OAB)
e da Corregedoria.^21^

A literatura contemporânea de segurança da informação e jurimetria
aponta que o formato digital PDF permite esconder conteúdo em dezenas de
camadas lógicas diferentes. Esses ataques de injeção direta frustram
severamente as garantias do devido processo legal e são mapeados da
seguinte forma ^21^:

  ----------------- ------------------ ------------------- -----------------
  **Nível de        **Forma e Vetor de **Visibilidade para **Impacto
  Sofisticação      Ataque (Prompt     Leitor Humano       Esperado e Risco
  Técnica**         Injection em       (Juiz/Assessor)**   à IA Judicial**
                    PDFs)**                                

  **Mínima**        Fonte microscópica Invisível ou        Alto. A extração
                    (tamanho \< 1pt)   confundível com     óptica e lógica
                    ou Cor idêntica ao ruído e sujeira de  do texto ocorre
                    fundo da página    digitalização.      de forma contínua
                    (Branco no                             e a instrução
                    Branco).                               atinge
                                                           diretamente o
                                                           prompt primário
                                                           do modelo de IA.

  **Baixa**         Manipulação de     Invisível na        Médio/Alto. O
                    Metadados XMP e    renderização do     modelo absorve os
                    Dicionários do     PDF, necessita      metadados
                    arquivo (campos    inspeção forense de maliciosos como
                    /Info, /Subject,   metadados.          contexto fatual
                    /Keywords).                            irrefutável antes
                                                           da leitura do
                                                           corpo.^21^

  **Baixa**         Uso de Caracteres  Totalmente          Alto. Os
                    Unicode invisíveis Invisível ao leitor extratores
                    (U+200B) e         nativo do Adobe     algorítmicos
                    inserção de texto  Reader ou PJe.      ignoram
                    além das                               coordenadas de
                    coordenadas de                         tela e capturam
                    borda limites                          todo o texto
                    (fora da                               serializado da
                    \"CropBox\").                          *stream* de
                                                           dados.

  **Média**         Ocultação via      Invisível. O leitor Muito Alto.
                    dicionário de      visual enxerga o    Modelos priorizam
                    Acessibilidade     texto regular, mas  os fluxos de
                    (Atributo          o leitor de máquina texto acessível
                    /ActualText        captura a instrução em suas leituras
                    divergente da      oculta.             por questões de
                    camada de                              padronização
                    renderização).                         W3C.^21^

  **Média/Alta**    Uso de Camadas de  Invisível. Exige    Alto. Sem filtros
                    PDF                manipulação das     avançados,
                    propositadamente   propriedades de     *parsers*
                    desativadas (OCG   visibilidade do     primitivos
                    /OFF) ou Campos    leitor.             extraem o
                    AcroForm ocultos                       conteúdo da
                    não preenchíveis.                      camada
                                                           invisível.^21^
  ----------------- ------------------ ------------------- -----------------

Se a arquitetura de IA elabora um sumário analítico contaminado por
essas diretrizes indevidas, o preceito do contraditório é sumariamente
aniquilado, pois a contraparte não pode impugnar o que não consegue
enxergar. Adicionalmente, essa fraude frustra diretamente os
mandamentos da Resolução CNJ nº 615/2025 (e equivalentes éticos da OAB),
que impõe a obrigatoriedade absoluta de supervisão humana criteriosa
sobre os resultados e minutas gerados por sistemas de inteligência
artificial no âmbito do Judiciário.^21^ A referida supervisão humana
torna-se um paradoxo impraticável: o magistrado não dispõe de meios
materiais para supervisionar, validar ou corrigir o viés cognitivo
gerado no algoritmo por um código técnico ou texto liminar que ele,
fisiologicamente, sequer consegue visualizar na tela limpa do processo
eletrônico.^21^

## 3. Mapa de Oportunidades Tecnológicas para a Inteligência Artificial

O avanço exponencial da inteligência artificial aplicada ao Direito
(*Legaltech* e *Lawtech*) apresenta um potencial incomparável de
mitigar, de forma substantiva e escalável, as ineficiências
identificadas. Com o amadurecimento e a democratização global das
arquiteturas de aprendizado profundo baseadas em *Transformers*,
tornou-se perfeitamente exequível intervir com alta precisão matemática
e semântica nos gargalos processuais da triagem, da análise de
prolixidade textual e na blindagem de segurança das cortes. A seguir,
propõe-se a análise fundamentada de três casos de uso focais e práticos
aplicáveis imediatamente à rotina contenciosa e judiciária
brasileira.

### 3.1. Processamento de Linguagem Natural (NLP) para Classificação Taxonômica (TPU) e Agrupamento Semântico

O primeiro e fundamental caso de uso de IA atua diretamente no gargalo
analógico da autuação e na distribuição processual. Modelos estáticos de
Processamento de Linguagem Natural (NLP), especificamente aqueles
baseados na robusta arquitetura *Encoder* (como a grande família de
variantes do modelo BERT - *Bidirectional Encoder Representations from
Transformers*), podem e devem ser submetidos a ciclos rigorosos de
reajuste fino (*fine-tuning*) para classificar automaticamente e de modo
probabilístico as petições iniciais de acordo com as centenas de
ramificações das Tabelas Processuais Unificadas do CNJ.^6^

A literatura técnica computacional nacional já dispõe de modelos
vetoriais de código aberto e livre acesso altamente especializados no
domínio jurídico. Exemplifica-se esta vanguarda com o desenvolvimento do
*LegalBert-pt*, um modelo avançado que foi pré-treinado em um
*corpus* monstruoso de mais de 1,5 milhão de documentos processuais
originados e coletados de 10 tribunais de justiça brasileiros distintos,
conferindo-lhe uma compreensão semântica ímpar do vocabulário jurídico
pátrio.^27^ Adicionalmente, destaca-se o *JurisBERT*, que
aplicou técnicas avançadas em bases de Similaridade Textual Semântica
(STS), alimentado exaustivamente com 24.000 pares de ementas
jurisprudenciais, apresentando níveis de precisão formidáveis e
reduzindo significativamente a necessidade de hardwares computacionais
(GPGPU) caros para sua inferência contínua se comparado a modelos
gigantes multilíngues.^28^ A aplicação cirúrgica dessas tecnologias
permite que um microsserviço leia densamente a fundamentação fática e os
pedidos das iniciais e infira --- com índices de confiabilidade
superiores a 90% --- os códigos processuais e de assuntos
correspondentes na árvore da TPU. Essa implementação neutraliza
inteiramente a carga de erro advinda do peticionamento deficiente do
advogado, isenta definitivamente a secretaria da tarefa massante de
revisão corretiva e padroniza a produção estatística nacional.

Ademais, essas redes geram *embeddings* (representações vetoriais de
altíssima dimensionalidade do texto legal), que possibilitam o cálculo
algébrico instantâneo de grau de similaridade semântica (como a
distância cosseno) entre milhares de petições que ingressam a cada
hora.^28^ Experiências consolidadas e extremamente bem-sucedidas na
vanguarda tecnológica dos Tribunais Superiores evidenciam a solidez
incontestável dessa abordagem teórica. O Supremo Tribunal Federal (STF),
operando em nuvem própria sob o projeto STF Digital, construiu em 2018
sua primeira iniciativa de IA pública, o *Victor*, desenvolvido
primariamente para mapear e apoiar ativamente a triagem de milhares de
Recursos Extraordinários e vinculá-los preditivamente a temas de
Repercussão Geral, reduzindo anos de acervo para minutos de
processamento.^29^ Em 2023, o STF alavancou essa tecnologia lançando o
sistema *VitorIA*, focado exclusivamente no agrupamento em *clusters* de
processos dotados de enorme similaridade textual sistêmica, revelando
casos materialmente idênticos aptos a receberem julgamento conjunto.^30^
Por seu turno, o Superior Tribunal de Justiça (STJ) gerencia o vigoroso
sistema *Athos*, que se utiliza da métrica padronizada CRISP-DM (*Cross
Industry Standard Process for Data Mining*) em parceria com
núcleos de inteligência para promover a afetação massiva de
controvérsias em sede de Recursos Repetitivos.^31^ No contexto
pulverizado do 1º Grau estadual e federal, essa mesma arquitetura de
*clustering* (que já encontrou sucesso em Juizados Especiais Cíveis,
identificando lotes em que grupos predatórios concentram até 53% das
ações idênticas em uma única comarca) ^33^ pode perfeitamente ser
instalada para agrupar centenas de ações versando sobre um mesmo evento
lesivo de um banco, empresa aérea ou concessionária de telecomunicações.
Isso empodera o juiz a sentenciar processos em lote, multiplicando seu
rendimento exponencialmente. Além disso, a iniciativa da Plataforma
Sinapses do CNJ já tem trabalhado na catalogação de mais de 150 modelos
construídos por diversos tribunais para compartilhar essas inovações por
todo o país e integrar de forma interoperável ao PJe.^34^

### 3.2. Inteligência Artificial Generativa (LLMs) para Extração de Entidades, Resumo Estruturado e Controle Preambular de Admissibilidade

Para mitigar a dor operacional crítica gerada pelas ineficiências na
forma das petições prolixas que atingem de 50 a 116 páginas sem
necessidade material, a Inteligência Artificial Generativa, impulsionada
e alicerçada pelas robustas e revolucionárias arquiteturas de Modelos de
Linguagem de Grande Escala (LLMs), oferece um retorno sobre o
investimento e usabilidade imediatos.^13^ Diferentemente da IA
classificatória clássica (que lida com vetores fixos para encontrar
probabilidades limitadas), a IA Generativa possui uma complexa e
profunda capacidade semântica para executar rotinas de compressão,
síntese textual argumentativa e tradução simplificada de contextos
herméticos. O STF também avança aceleradamente nessa frente exploratória
com o uso interno da plataforma *Maria*, projetada sob rígidos
protocolos de supervisão humana para executar correções textuais em
relatórios da Corte, gerar ementas judiciais alinhadas aos rigorosos
padrões do CNJ e produzir consultas de jurisprudência correlatas de modo
integrado no ato de construção das decisões monocráticas.^30^

A aplicação direta dessa frente nas varas cíveis, juizados especiais e
juizados da fazenda pública consiste fundamentalmente em submeter o
inteiro teor da petição inicial, independentemente de sua prolixidade ou
extensão formidável, à interface de um LLM devidamente calibrado (com
parâmetros específicos como baixa \'temperatura\' para mitigar riscos de
\"alucinações algorítmicas\") para produzir instantaneamente um
documento denominado \"Sumário Executivo Estruturado de
Gabinete\". Essa IA deverá varrer a petição, extrair os
principais nodos de entidades processuais essenciais e mapear, de forma
determinística, tabular e lógica, a presença ou ausência dos requisitos
vinculantes de admissibilidade e mérito. Os outputs gerados forneceriam
imediatamente à equipe do juiz:

-   **Qualificação Objetiva e Polos Ação:** Identificação estruturada
    do CPF/CNPJ, endereços e validação formal de partes.

-   **Fato Gerador Sintetizado:** Redução cognitiva de 10 ou mais
    páginas exaustivas de repetições literais de trocas de e-mails para
    um único parágrafo central e estruturado resumindo objetivamente a
    lide.

-   **Fundamentação Jurídica Invocada:** Extração cirúrgica do exato
    embasamento normativo invocado, expurgando automaticamente a cópia
    inútil de jurisprudência que já é do conhecimento do
    julgador.^13^

-   **Pedidos Listados, Liminares e Valor da Causa:** Extração direta
    do rol processual de pedidos da exordial, formatação destes em
    *bullet points* objetivos (incluindo destaque vital e prioritário em
    alerta vermelho para qualquer existência de requerimentos de
    antecipação de tutela cautelar, sob risco de perecimento de
    direito), além de realizar o confronto sistêmico com a razoabilidade
    do valor da causa pleiteado.

Para o denso e intrincado contexto jurídico brasileiro --- notório pelo
uso frequente de \"juridiquês\", expressões idiomáticas em latim e ritos
processuais complexos ---, a utilização intensiva de grandes modelos
parametrizados e nacionalizados de processamento representa uma vantagem
técnica e qualitativa abissal em face de APIs generalistas
estrangeiras. Destaca-se a excelência dos LLMs especializados em
português, especialmente a família de modelos Sabiá (em suas versões
sucessivas Sabiá-3 e o contemporão Sabiá-4), desenvolvidos com rigor
acadêmico pelo laboratório *Maritaca AI*.^38^ Este arcabouço
tecnológico nacional demonstrou capacidades e métricas estelares de
desempenho nos mais variados *benchmarks* e testes padronizados
brasileiros.^39^ Nos cenários experimentais de validação, os modelos da
arquitetura Sabiá alcançaram resultados impactantes: aprovações teóricas
que superaram 87% de aproveitamento quantitativo na difícil 1ª Fase do
Exame da Ordem dos Advogados do Brasil (OAB) e cravando a nota de 7.5 na
avaliação escrita discursiva referente à 2ª Fase do rigoroso
certame.^42^ Adicionalmente, registram rendimentos na casa dos 88% no
ENEM e excelência no teste OAB-Bench voltado para a redação de cunho
jurídico e no Magis-Bench voltado ao conhecimento prático
processual.^39^ O uso preferencial de LLMs com essa estirpe e
*fine-tuning* local garante ao tribunal e aos desenvolvedores públicos
que o modelo atuante não sofra lapsos ou alucinações cognitivas baseadas
no sistema de *Common Law* norte-americano tampouco produza falhas
interpretativas elementares sobre institutos intrinsecamente
brasileiros, como o mandado de segurança, agravos de instrumento, regras
de impenhorabilidade de bens ou preceitos peculiares dos ritos
sumariíssimos.^38^

### 3.3. IA Defensiva, Visão Computacional e Monitoramento Ativo para Detecção de Litigância Predatória e Manipulação

O terceiro imperativo e caso de uso proeminente afasta-se
momentaneamente do escopo cognitivo jurídico interpretativo e adentra
nas esferas críticas da perícia forense, segurança cibernética judicial
e jurimetria punitiva: o emprego maciço de ferramentas da ciência de
dados para blindar ativamente a jurisdição nacional contra o assédio
agressivo da Litigância Predatória e o parasitismo cibernético das
injeções de comandos ocultos (*prompt injection*). Ferramentas
combinadas que integram *pipelines* de Visão Computacional (para análise
gráfica, biométrica e topológica do documento em pixel) com a mineração
aprofundada de metadados binários atuarão como um cinturão de segurança
prévio; uma parede de defesa (um *Firewall* jurisdicional) que purifica
o documento antes mesmo de permitir que ele chegue à análise final
cognitiva do juízo de admissibilidade, da equipe de servidores, ou de um
LLM gerador de resumos.^10^

Como exaustiva e brilhantemente demonstrado pela experiência judiciária
de ponta liderada pelo \"Projeto Bastião\" --- ferramenta construída no
âmbito de tecnologia e inteligência pelo Tribunal de Justiça de
Pernambuco (TJPE) --- os modelos orquestrados de aprendizado de máquina
supervisionado provaram capacidade incomparável de traçar malhas
algorítmicas, identificar comportamentos anômalos e mapear o *modus
operandi* de esquemas delitivos complexos que são, por premissa
biológica, indetectáveis ao controle do julgamento humano solitário.^10^
Entre os achados documentados nas recomendações, esses modelos analisam
os fluxos de rede para detectar ações ajuizadas sistematicamente pelo
mesmo endereço de IP (provando centralização), mapeiam o fracionamento
suspeito (centenas de demandas da mesma vara ajuizadas em minutos),
utilizam OCR (*Optical Character Recognition*) para evidenciar que as
procurações anexadas são digitalmente idênticas até mesmo na mesma
posição milimétrica da assinatura e na exata angulação do escaner
(sinalizando clara reprodução mecânica artificial de firmas e
adulteração em massa para a captação de clientela irregular) e cruzam
metadados que indicam o não consentimento da parte vulnerável
supostamente lesada.^9^

No nicho de extrema relevância operacional para inibir fraudes
emergentes que atentam de forma inédita e grave contra os pilares
tecnológicos do contraditório judicial --- como o supramencionado
*prompt injection* de \"texto branco\" ou manipulação profunda dos
dicionários criptografados de acessibilidade em arquivos PDF --- é
impositiva a implementação de uma IA eminentemente defensiva. A
solução deverá promover uma agressiva \"engenharia reversa\" estrutural
nos laudos de recepção do documento: assim que o arquivo submetido
alcança os servidores primários do tribunal pelo barramento do PJe ou
E-Proc, aciona-se um extrator de fluxo de texto (*stream parser*)
associado à inspeção óptica dos glifos (*font rendering*) em busca
sistemática de anomalias cromáticas e invisibilidade tática. O
código fonte buscará proativamente dissonâncias evidentes entre o que é
visível rasterizado (em imagem) e o texto binário legível que é
alimentado nos conectores do sistema de IA. Em sendo detectada
manipulação, o sistema deverá estagnar permanentemente a tramitação
algorítmica, sinalizando uma enorme *flag* de alerta cor escarlate
indicando \"Risco Grave: Tentativa de Fraude Algorítmica Processual -
Quebra Implícita da Boa-Fé\" no cabeçalho do painel do julgador,
subsidiando de forma direta e insofismável o magistrado para a imposição
célere de multas de litigância de má-fé e provocando os deveres
disciplinares obrigatórios estatuídos pelas Corregedorias.^21^

## 4. Proposta de Solução: Desenvolvimento e Implementação do MVP (Case Técnico de 3 Semanas)

Para materializar todo o potencial das oportunidades técnicas
previamente discutidas, enfrentar com robustez a crise de triagem
sistêmica e, simultaneamente, atender de forma peremptória à contagem
regressiva da urgência estipulada em três semanas letivas para a entrega
da prova de conceito (POC) da pós-graduação, submete-se à aprovação o
escopo de desenvolvimento integral do projeto **SHERPI** (Sistema
Híbrido de Extração e Resumo Estruturado de Petições Iniciais).

O SHERPI concebe-se essencialmente como um Produto Mínimo Viável (MVP)
delineado, projetado e desenvolvido de forma altamente coesa utilizando
metodologias ágeis. A arquitetura de implantação foi montada sobre um
conglomerado de bibliotecas de código-fonte aberto, protocolos
consolidados em Python e o uso inteligente de APIs de IA generativa de
baixo custo, eliminando a necessidade de infraestrutura local cara e
viabilizando perfeitamente o seu uso no escopo acadêmico.

### 4.1. Escopo Técnico da Arquitetura do Sistema e Pilha Tecnológica (Tech Stack)

A arquitetura do SHERPI implementará um fluxo de RAG
(*Retrieval-Augmented Generation*) agentil moderno. A matriz
arquitetônica adotará a seguinte configuração de sistema, com foco em
ferramentas públicas e modelos acessíveis:

1.  **Linguagem Base e Framework de Backend:** A fundação algorítmica e
    o roteamento da infraestrutura dar-se-ão inteiramente via **Python**
    (versão \>=3.10), utilizando o *microframework* **FastAPI**. O
    FastAPI assegura o suporte nativo a rotinas assíncronas lidando em
    alta performance e garantindo o provisionamento via rotas HTTP
    padrão.

2.  **Camada de Ingestão e O Firewall Óptico:** Como núcleo para
    leitura do PDF, utilizaremos a biblioteca de código aberto
    **PyMuPDF** (a *wrapper* de bindings em C/Python do Mupdf).
    Diferentemente de extratores simples, o PyMuPDF concede total acesso
    às matrizes topológicas e atributos visuais (cores, tamanho de
    escala da fonte, campos ocultos). Isso permite criar uma função
    defensiva que detecta *prompt injection* (como fontes com contraste
    de cor zero em relação ao fundo) em uma fração de milissegundo,
    antes de qualquer envio de dados para as APIs dos LLMs.^21^

3.  **Orquestração Agentil com LangGraph:** Em substituição ao
    LangChain tradicional (que é focado em pipelines lineares - DAGs
    simples), a arquitetura adotará o **LangGraph**. O LangGraph é o
    estado da arte open-source para a construção de sistemas
    multi-agentes e fluxos de trabalho completos baseados em grafos. Ao
    utilizar a estrutura nativa de StateGraph, permitiremos que a IA
    gerencie o estado dos dados ativamente, suportando *loops*,
    ramificações e decisões condicionais. Isso é vital: se o agente
    perceber que a petição está incompleta ou manipulada, o LangGraph
    permite rotear o processo para um \"nó de falha\" imediatamente, sem
    seguir cegamente um pipeline linear ineficiente.

4.  **Motor de Inferência Computacional Semântica (APIs de Baixo
    Custo):** Considerando o cenário de pós-graduação e a viabilidade
    orçamentária do MVP, adotaremos o uso de APIs comerciais de entrada
    extremamente eficientes e de baixíssimo custo (dispensando GPUs
    caras locais ou o uso pesado do Ollama). Recomendam-se duas opções
    que se integram perfeitamente aos *nodes* do LangGraph:

    -   **OpenAI API (gpt-4o-mini):** O modelo *mini* da OpenAI
        apresenta métricas estelares de compreensão do português e
        estruturação JSON, custando menos de 15 centavos de dólar por
        milhão de tokens de entrada.

    -   **Google Gemini API (Gemini 1.5 Flash):** Possui uma janela de
        contexto colossal, ideal para ler 100 páginas de petição de uma
        só vez, e oferece níveis gratuitos de desenvolvimento para
        testes acadêmicos (*free tier* para requisições limitadas por
        minuto).

5.  **Microsserviço de Classificação Taxonômica (Sugestão de TPU):**
    Consolidando-se um arranjo tecnológico complementar totalmente
    gratuito, propõe-se um motor inferior de Inteligência Artificial que
    roda puramente em CPU/RAM. Adotando a inferência preditiva leve de
    *Transformers*, hospeda-se localmente mediante a biblioteca do
    *HuggingFace* o já treinado modelo vetorial nacional **JurisBERT**
    ou **LegalBert-pt**.^27^ Este algoritmo confrontará as narrativas
    com a base de dados pública do CNJ para sugerir a taxonomia TPU da
    classe e do assunto.^5^

6.  **Desenvolvimento e Entrega da Interface Gráfica (GUI):** Pelo
    cronograma de três semanas corridas, a implementação será feita com
    o *framework* open-source **Streamlit**. O Streamlit permite erguer
    uma *Dashboard* web cristalina escrita inteiramente em Python. Ela
    permitirá que os avaliadores submetam PDFs e visualizem os alertas e
    o resumo em tempo real, atendendo ao princípio do
    *human-in-the-loop* (supervisão humana indispensável).^21^

### 4.2. Funcionamento Empírico do Produto Operacional (Visão de Gabinete do MVP)

No fluxo temporal do MVP SHERPI, a jornada operacional validada pelo
*StateGraph* (LangGraph) consistirá em quatro etapas sequenciais
automáticas:

1.  **Nó 1: Ação Prévia de Firewall (Sanitarização via PyMuPDF):** O
    arquivo é decifrado pelas raízes lexicais. Se o PyMuPDF detectar
    manipulação cromática (texto branco oculto) ou metadados XMP
    maliciosos, o fluxo de estado do LangGraph direciona imediatamente
    para o Fim da execução e exibe uma tarja vermelha na tela: \"Risco
    Eminente --- Probabilidade de *Prompt Injection*\".^21^ Não há gasto
    de tokens de API.

2.  **Nó 2: Compressão Estrutural e Destilação Extrativa (API LLM):**
    Atestada a segurança óptica do documento, o texto limpo é enviado à
    API (GPT-4o-mini ou Gemini Flash). Pautado pelo LangGraph, o LLM
    ignora citações doutrinárias prolixas e devolve um formulário
    pragmático formatado em JSON contendo: Partes, Fatos Concretos,
    Fundamentação Invocada e Pedidos Finais atrelados ao Valor da Causa.

3.  **Nó 3: Checagem de Regras de Admissibilidade:** Simultaneamente,
    regras simples baseadas em *Regular Expressions* no Python verificam
    na listagem extraída a presença dos comprovantes básicos (RG, CPF,
    Comprovante de Residência). Um semáforo visual (verde/vermelho)
    alerta a necessidade de emenda à inicial (art. 321 do CPC).^18^

4.  **Nó 4: Inferência Taxonômica (Sugestão de TPU):** Uma interface
    interativa flutuante apresenta o cálculo matemático local efetuado
    pelo JurisBERT, listando o top 3 das classes TPU mais adequadas para
    o caso, mitigando erros humanos da autuação.^6^

### 4.3. Cronograma Ágil de Desenvolvimento Iterativo Contínuo (3 Semanas Intensivas)

A viabilização deste escopo em três semanas (ideal para a disciplina de
pós-graduação) ocorrerá na seguinte divisão ágil de *sprints*:

#### Semana 1: Estruturação, Implantação do Framework e Escudos de Defesa (Data & Parsing)

-   **Dia 1 e Dia 2:** Definição do escopo da prova de conceito (POC) e
    obtenção dos dados. Coleta de 50 a 100 petições cíveis de acesso
    público, anonimizadas, para servirem como base material de teste.

-   **Dia 3 e Dia 4:** Codificação do *parser* em **PyMuPDF**.
    Programação da heurística defensiva (o *Firewall*) que inspeciona a
    cor da fonte, as marcações ocultas /ActualText e o tamanho dos
    glifos para identificar ativamente injecões de *prompt*
    processuais.^21^

-   **Dia 5:** Construção e indexação vetorial da base de TPU,
    vinculando o ambiente local ao modelo *JurisBERT* baixado pelo
    HuggingFace Hub para as predições estáticas das tabelas do CNJ.^5^

#### Semana 2: Core Engineering Cognitiva e Orquestração do Agente (LangGraph + API LLM)

-   **Dia 6 e Dia 7:** Edificação da arquitetura estrutural de fluxos
    usando **LangGraph**. A definição do StateGraph em Python que
    governará as rotas lógicas da leitura do documento e o roteamento de
    erros (condicionais). A engenharia do *System Prompt* restritivo
    obrigando a geração da resposta em JSON.

-   **Dia 8 e Dia 9:** Integração com as APIs externas escolhidas
    (**OpenAI ou Google**). Implementação dos conectores de rede
    seguros, configurando a \"temperatura\" da chamada da API para 0.0
    (garantindo respostas determinísticas e extirpando alucinações
    criativas) e realizando as primeiras inferências sobre o *corpus*
    documental sanitizado.

-   **Dia 10:** Testes unitários iterativos do fluxo. Validação do
    roteamento do LangGraph: garantir que se a petição apresentar mais
    de 100 páginas, a IA acione a rotina de *chunking* (fatiamento de
    contexto) sem estourar o limite econômico da API.

#### 

#### Semana 3: Design Interface, Validação Acadêmica e Fechamento (Testes A/B e *Deploy*)

-   **Dia 11 e Dia 12:** Edificação gráfica da interface limpa e
    intuitiva em **Streamlit**. Criação de um *Dashboard* interativo,
    com o PDF renderizado visualmente em um painel e, ao lado, as
    extrações das entidades feitas pela IA e os laudos de auditoria de
    segurança antifraude.

-   **Dia 13 e Dia 14:** Sessão de experimentação empírica (Testes A/B).
    O pesquisador e colegas compararão o tempo médio gasto por um humano
    para ler as extensas páginas de doutrina da inicial e extrair os
    pedidos, versus o tempo do modelo computacional. Levantamento das
    métricas qualitativas e de precisão (F1 Score da extração do
    LangGraph).

-   **Dia 15:** Encerramento metodológico programado. Fechamento da
    Prova de Conceito, empacotamento do código em repositório GitHub e
    compilação do material estatístico comprobatório para a defesa e
    entrega do trabalho final da pós-graduação.

## Conclusão Estratégica

A saturação crônica vivenciada na base operacional do Poder Judiciário
brasileiro, agravada anualmente por volumes desproporcionais de
peticionamento prolixo, falhas estruturais massivas de admissibilidade e
por inovações parasitárias maliciosas --- a exemplo da fraude
algorítmica caracterizada pela técnica de *prompt injection* injetada em
arquivos PDF ---, atesta de forma inequívoca o esgotamento dos
paradigmas organizacionais puramente analógicos.

O desenho tecnológico estruturado neste documento para a construção
acadêmica do MVP **SHERPI** evidencia que a solução não requer
investimentos astronômicos em infraestrutura e em plataformas fechadas
(vendor lock-in) ou mesmo manutenções e configurações complexas e de
alto custo computacional local de hardware. Com a adoção cirúrgica de
metodologias e ecossistemas abertos e maduros (como o **LangGraph** para
o roteamento escalável de decisões agentais) e o aproveitamento
inteligente de **APIs comerciais eficientes e de custo baixíssimo**
(como os modelos de entrada do Google e OpenAI), é perfeitamente
exequível criar uma ferramenta funcional, segura e altamente precisa no
prazo otimizado de três semanas.

A proposta, que resguarda princípios imutáveis como a transparência
cibernética por meio de triagem prévia e a obrigatoriedade impositiva da
supervisão humana (*human-in-the-loop*), demonstra cabalmente o
potencial de absorção inovadora e racional do Estado. A automação
cognitiva guiada por ferramentas enxutas é o caminho irrefutável para
devolver aos juízes e aos seus analistas o insumo mais valioso para a
concretização de uma jurisdição de excelência: o tempo intelectual livre
de demandas repetitivas.

#### Referências citadas

1.  Justiça em números, acessado em junho 13, 2026,
    https://justica-em-numeros.cnj.jus.br/]{.underline}](https://justica-em-numeros.cnj.jus.br/)

2.  CNJ: Dos 20 réus mais demandados na Justiça, 10 são entes públicos -
    Migalhas, acessado em junho 13, 2026,
    https://www.migalhas.com.br/quentes/441129/cnj-dos-20-reus-mais-demandados-na-justica-10-sao-entes-publicos]{.underline}](https://www.migalhas.com.br/quentes/441129/cnj-dos-20-reus-mais-demandados-na-justica-10-sao-entes-publicos)

3.  Relatório Justiça em Números, do CNJ, aponta TJSC com desempenho
    acima da média nacional - Imprensa - Poder Judiciário de Santa
    Catarina, acessado em junho 13, 2026,
    https://www.tjsc.jus.br/web/imprensa/-/relatorio-justica-em-numeros-do-cnj-aponta-tjsc-com-desempenho-acima-da-media-nacional]{.underline}](https://www.tjsc.jus.br/web/imprensa/-/relatorio-justica-em-numeros-do-cnj-aponta-tjsc-com-desempenho-acima-da-media-nacional)

4.  Justiça em Números 2025: A revolução silenciosa do Judiciário
    brasileiro - Migalhas, acessado em junho 13, 2026,
    https://www.migalhas.com.br/depeso/441595/justica-em-numeros-2025-revolucao-silenciosa-do-judiciario-brasileiro]{.underline}](https://www.migalhas.com.br/depeso/441595/justica-em-numeros-2025-revolucao-silenciosa-do-judiciario-brasileiro)

5.  Tabela processuais unificadas - Portal CNJ, acessado em junho 13,
    2026,
    https://www.cnj.jus.br/programas-e-acoes/tabela-processuais-unificadas/]{.underline}](https://www.cnj.jus.br/programas-e-acoes/tabela-processuais-unificadas/)

6.  TABELAS PROCESSUAIS UNIFICADAS -- TPU\'S - TJGO, acessado em junho
    13, 2026,
    https://www.tjgo.jus.br/images/img/CCS/docs2/TPU\_-\_advogados.pdf]{.underline}](https://www.tjgo.jus.br/images/img/CCS/docs2/TPU_-_advogados.pdf)

7.  litigância predatória nos processos de execução: o uso abusivo do
    requerimento de falência pelo credor - Civil Procedure Review,
    acessado em junho 13, 2026,
    https://www.civilprocedurereview.com/revista/article/download/391/263/1221]{.underline}](https://www.civilprocedurereview.com/revista/article/download/391/263/1221)

8.  LITIGÂNCIA PREDATÓRIA (SHAM LITIGATION) - Revista da Seção
    Judiciária de Alagoas, acessado em junho 13, 2026,
    https://revista.jfal.jus.br/RJSJAL/article/download/47/38/173]{.underline}](https://revista.jfal.jus.br/RJSJAL/article/download/47/38/173)

9.  2247 O PAPEL DO CNJ NO COMBATE À LITIGÂNCIA PREDATÓRIA RESUMO,
    acessado em junho 13, 2026,
    https://periodicorease.pro.br/rease/article/download/21507/13178/60369]{.underline}](https://periodicorease.pro.br/rease/article/download/21507/13178/60369)

10. direito, governança e novas tecnologias ii - conpedi, acessado em
    junho 13, 2026,
    http://site.conpedi.org.br/publicacoes/v38r977z/a8g25p9g/LHppXpr9QAlHRcP4.pdf]{.underline}](http://site.conpedi.org.br/publicacoes/v38r977z/a8g25p9g/LHppXpr9QAlHRcP4.pdf)

11. os desafios na aplicação de inteligência artificial para
    identificação de demandas predatórias no - SEMINÁRIO DIREITO PRIVADO
    E TECNOLOGIA RESUMO EXPANDIDO, acessado em junho 13, 2026,
    https://periodicos.uni7.edu.br/index.php/sdptec/article/download/1831/1075]{.underline}](https://periodicos.uni7.edu.br/index.php/sdptec/article/download/1831/1075)

12. Os maiores erros na Petição Inicial - Questão de Direito 452 -
    YouTube, acessado em junho 13, 2026,
    https://www.youtube.com/watch?v=ebgvojEYeWo]{.underline}](https://www.youtube.com/watch?v=ebgvojEYeWo)

13. Confira 5 dicas para sua petição inicial ser acolhida - Migalhas,
    acessado em junho 13, 2026,
    https://www.migalhas.com.br/quentes/348996/confira-5-dicas-para-sua-peticao-inicial-ser-acolhida]{.underline}](https://www.migalhas.com.br/quentes/348996/confira-5-dicas-para-sua-peticao-inicial-ser-acolhida)

14. UNIVERSIDADE DE MARÍLIA CLÁUDIO MARQUES ALVES O PROCESSO ELETRÔNICO
    E SEUS REFLEXOS NA ATIVIDADE JURISDICIONAL DO ESTADO BRAS, acessado
    em junho 13, 2026,
    https://portal.unimar.br/site/public/pdf/dissertacoes/CCC9E6C791097A2A07405B7FAC647B53.pdf]{.underline}](https://portal.unimar.br/site/public/pdf/dissertacoes/CCC9E6C791097A2A07405B7FAC647B53.pdf)

15. Juiz critica prolixidade de petição e manda parte emendar inicial -
    Migalhas, acessado em junho 13, 2026,
    https://www.migalhas.com.br/quentes/198659/juiz-critica-prolixidade-de-peticao-e-manda-parte-emendar-inicial]{.underline}](https://www.migalhas.com.br/quentes/198659/juiz-critica-prolixidade-de-peticao-e-manda-parte-emendar-inicial)

16. Ponderações acerca da prolixidade das petições e a garantia da
    celeridade da tramitação processual - Revista do Tribunal Regional
    Federal da 3ª Região - TRF3, acessado em junho 13, 2026,
    https://revista.trf3.jus.br/index.php/rtrf3/article/download/253/235/582]{.underline}](https://revista.trf3.jus.br/index.php/rtrf3/article/download/253/235/582)

17. Petição Inicial: guia completo com 5 dicas para elaborar - Projuris,
    acessado em junho 13, 2026,
    https://www.projuris.com.br/blog/peticao-inicial/]{.underline}](https://www.projuris.com.br/blog/peticao-inicial/)

18. Juízes pedem emenda de inicial em até 60% de casos cíveis - JOTA,
    acessado em junho 13, 2026,
    https://www.jota.info/advocacia/juizes-pedem-emenda-de-inicial-em-ate-60-de-casos-civeis]{.underline}](https://www.jota.info/advocacia/juizes-pedem-emenda-de-inicial-em-ate-60-de-casos-civeis)

19. Petição inicial: como fazer, requisitos + MODELO - Aurum, acessado
    em junho 13, 2026,
    https://www.aurum.com.br/blog/peticao-inicial/]{.underline}](https://www.aurum.com.br/blog/peticao-inicial/)

20. Prompt injection no processo: multa, OAB e inquérito do \... -
    JusDocs, acessado em junho 13, 2026,
    https://jusdocs.com/blog/prompt-injection-processo-multa-oab-stj-inquerito-ia]{.underline}](https://jusdocs.com/blog/prompt-injection-processo-multa-oab-stj-inquerito-ia)

21. Prompt injection em documentos judiciais: Conceito, vetores e
    riscos, acessado em junho 13, 2026,
    https://www.migalhas.com.br/depeso/455924/prompt-injection-em-documentos-judiciais-conceito-vetores-e-riscos]{.underline}](https://www.migalhas.com.br/depeso/455924/prompt-injection-em-documentos-judiciais-conceito-vetores-e-riscos)

22. Prompt injection e integridade processual: o paradoxo da \... -
    JOTA, acessado em junho 13, 2026,
    https://www.jota.info/opiniao-e-analise/artigos/prompt-injection-em-peticoes-e-o-paradoxo-da-integridade-processual]{.underline}](https://www.jota.info/opiniao-e-analise/artigos/prompt-injection-em-peticoes-e-o-paradoxo-da-integridade-processual)

23. Juiz identifica comando oculto para IA em petição e cobra
    explicações de advogado, acessado em junho 13, 2026,
    https://justicapotiguar.com.br/index.php/2026/05/21/juiz-identifica-comando-oculto-para-ia-em-peticao-e-cobra-explicacoes-de-advogado/]{.underline}](https://justicapotiguar.com.br/index.php/2026/05/21/juiz-identifica-comando-oculto-para-ia-em-peticao-e-cobra-explicacoes-de-advogado/)

24. Juiz manda advogado explicar comando oculto para IA em petição -
    Migalhas, acessado em junho 13, 2026,
    https://www.migalhas.com.br/quentes/456548/juiz-manda-advogado-explicar-comando-oculto-para-ia-em-peticao]{.underline}](https://www.migalhas.com.br/quentes/456548/juiz-manda-advogado-explicar-comando-oculto-para-ia-em-peticao)

25. Juiz De SP Manda Advogado Explicar Comando Oculto Em Petição Que
    Poderia Influenciar IA \| Juristas, acessado em junho 13, 2026,
    https://juristas.com.br/noticias/juiz-de-sp-manda-advogado-explicar-comando-oculto-em-peticao-que-poderia-influenciar-ia/]{.underline}](https://juristas.com.br/noticias/juiz-de-sp-manda-advogado-explicar-comando-oculto-em-peticao-que-poderia-influenciar-ia/)

26. Prompt injection oculto em petição inicial: O caso de Parauapebas -
    Migalhas, acessado em junho 13, 2026,
    https://www.migalhas.com.br/depeso/455925/prompt-injection-oculto-em-peticao-inicial-o-caso-de-parauapebas]{.underline}](https://www.migalhas.com.br/depeso/455925/prompt-injection-oculto-em-peticao-inicial-o-caso-de-parauapebas)

27. LegalBert-pt: A Pretrained Language Model for the Brazilian
    Portuguese Legal Domain \| Request PDF - ResearchGate, acessado em
    junho 13, 2026,
    https://www.researchgate.net/publication/374645610_LegalBert-pt_A_Pretrained_Language_Model_for_the_Brazilian_Portuguese_Legal_Domain]{.underline}](https://www.researchgate.net/publication/374645610_LegalBert-pt_A_Pretrained_Language_Model_for_the_Brazilian_Portuguese_Legal_Domain)

28. JurisBERT: Transformer-based model for embedding legal texts,
    acessado em junho 13, 2026,
    https://repositorio.ufms.br/bitstream/123456789/5119/1/JurisBERT\_\_Transformer_based_model_for_embedding_legal_texts.pdf]{.underline}](https://repositorio.ufms.br/bitstream/123456789/5119/1/JurisBERT__Transformer_based_model_for_embedding_legal_texts.pdf)

29. STF finaliza testes de nova ferramenta de Inteligência Artificial,
    acessado em junho 13, 2026,
    https://portal.stf.jus.br/noticias/verNoticiaDetalhe.asp?idConteudo=507120&ori=1]{.underline}](https://portal.stf.jus.br/noticias/verNoticiaDetalhe.asp?idConteudo=507120&ori=1)

30. STF amplia uso de inteligência artificial em apoio à atividade \...,
    acessado em junho 13, 2026,
    https://noticias.stf.jus.br/postsnoticias/stf-amplia-uso-de-inteligencia-artificial-em-apoio-a-atividade-jurisdicional/]{.underline}](https://noticias.stf.jus.br/postsnoticias/stf-amplia-uso-de-inteligencia-artificial-em-apoio-a-atividade-jurisdicional/)

31. PROJETO ATHOS: Um Estudo de Caso sobre a inserção do Superior
    Tribunal de Justiça na Era da Inteligência Artificial. - CNJ,
    acessado em junho 13, 2026,
    https://www.cnj.jus.br/wp-content/uploads/2022/11/projeto-athos.pdf]{.underline}](https://www.cnj.jus.br/wp-content/uploads/2022/11/projeto-athos.pdf)

32. Decisão judicial assistida por inteligência artificial e o Sistema
    Victor do Supremo Tribunal Federal - SciELO, acessado em junho 13,
    2026,
    https://www.scielo.br/j/rinc/a/YKZfQPLJqT7F3P445KkmwnC/?lang=pt]{.underline}](https://www.scielo.br/j/rinc/a/YKZfQPLJqT7F3P445KkmwnC/?lang=pt)

33. ARTIGOS - Biblioteca digital do CNJ, acessado em junho 13, 2026,
    https://bibliotecadigital.cnj.jus.br/jspui/bitstream/123456789/185/1/Aplica%C3%A7%C3%A3o%20da%20Intelig%C3%AAncia%20Artificial%20na%20identifica%C3%A7%C3%A3o%20de%20conex%C3%B5es.pdf]{.underline}](https://bibliotecadigital.cnj.jus.br/jspui/bitstream/123456789/185/1/Aplica%C3%A7%C3%A3o%20da%20Intelig%C3%AAncia%20Artificial%20na%20identifica%C3%A7%C3%A3o%20de%20conex%C3%B5es.pdf)

34. Serviço Sinapses - Inteligência Artificial \| Documentação PJe,
    acessado em junho 13, 2026,
    https://docs.pje.jus.br/servicos-auxiliares/servico-sinapses-inteligencia-artificial/]{.underline}](https://docs.pje.jus.br/servicos-auxiliares/servico-sinapses-inteligencia-artificial/)

35. Plataforma Sinapses / Inteligência Artificial - Portal CNJ, acessado
    em junho 13, 2026,
    https://www.cnj.jus.br/sistemas/plataforma-sinapses/]{.underline}](https://www.cnj.jus.br/sistemas/plataforma-sinapses/)

36. Estrutura Tecnológica - Portal CNJ, acessado em junho 13, 2026,
    https://www.cnj.jus.br/programas-e-acoes/processo-judicial-eletronico-pje/inovapje/estrutura-tecnologica/]{.underline}](https://www.cnj.jus.br/programas-e-acoes/processo-judicial-eletronico-pje/inovapje/estrutura-tecnologica/)

37. Plataforma Sinapses reúne 150 modelos de inteligência artificial,
    acessado em junho 13, 2026,
    https://www.undp.org/pt/brazil/news/plataforma-sinapses-reune-150-modelos-de-inteligencia-artificial]{.underline}](https://www.undp.org/pt/brazil/news/plataforma-sinapses-reune-150-modelos-de-inteligencia-artificial)

38. Maritaca AI --- Inteligência artificial para o Brasil, acessado em
    junho 13, 2026,
    https://www.maritaca.ai/]{.underline}](https://www.maritaca.ai/)

39. Pesquisa --- Maritaca AI, acessado em junho 13, 2026,
    https://www.maritaca.ai/research/]{.underline}](https://www.maritaca.ai/research/)

40. Research - Maritaca AI, acessado em junho 13, 2026,
    https://www.maritaca.ai/en/research/]{.underline}](https://www.maritaca.ai/en/research/)

41. Sabiá-4 Technical Report - arXiv, acessado em junho 13, 2026,
    https://arxiv.org/html/2603.10213v1]{.underline}](https://arxiv.org/html/2603.10213v1)

42. AI for Brazil - Maritaca AI, acessado em junho 13, 2026,
    https://www.maritaca.ai/en/]{.underline}](https://www.maritaca.ai/en/)

43. CHATGPT nacional treinado em português do Brasil do Brasil. -
    YouTube, acessado em junho 13, 2026,
    https://www.youtube.com/watch?v=G6vmZ0S2h0I]{.underline}](https://www.youtube.com/watch?v=G6vmZ0S2h0I)
