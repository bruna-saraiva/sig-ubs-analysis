## Acompanhamento do Projeto
Precisamos de 3 camadas para o trabalho:
- postos de saude
- setores censitarios
- cobertura dos postos
  
A seguir o que temos e o que não temos de cada camada:
### Postos:
Fonte:
[x] - id_posto(CNES)
[x] - nome(nome fantasia)
[x] - capacidade/mes (fiz um mapeamento estimado, utilizando nivel de atencao como base para quantidade de atendimentos)
[x] - complexidade (nível de atencao)
[x] - especialidades_disponiveis (inferi apenas servicoes prestados como atençao basica, clinica geral,enfermagem)

### Areas de cobertura:
[x] - id_posto(CNES)
[] - area_km2

### Setores censitários
Fonte: https://www.ibge.gov.br/estatisticas/sociais/saude/22827-censo-demografico-2022.html?edicao=41852&t=resultados
[x] - id_setor
[x] - area_km2
[x] - populacao
[x] - densidade_hab_km2
[x] - populacao_idosa
[x] - populacao_infatil 
[x] - renda_media (utilizei renda do responsavel e usei a variavel V06004, nao achei um dicionario de variaveis, mas é o que mais parece ser uma media da renda)

*1.736 setores preservados
1.716 com renda encontrada
20 sem correspondência, mantidos com valor vazio*


#### Sobre capacidade/mes
Podemos usar nivel de atencao e mapear:
- 1 -> 3.000 atendimentos/mes
- 2 -> 6.000
- 3 -> 12.000

### Sequência de tarefas:
[x] - Finalizar Setores
[x] - Finalizar UBS
[x] - Gerar poligonos de Voronoi para estimar area de cobertura 
[x] - Recortar o Voronoi pelo limite de São Luís 
[x] - Intersectar Voronoi × Setores: assim descobriremos quais setores pertencem a cobertura de cada UBS

[x] - Calcular a populacao equivalente de cada setor contemplado pela UBS
  - Fórmula: `PEQ = população adulta + 1,5 × população infantil + 1,8 × população idosa`
  - População adulta: `população total - população infantil - população idosa`
  - Resultado: 1.663 setores calculados e 53 mantidos sem PEQ por possuírem valores suprimidos (`X`) pelo IBGE
[x] - Calcular indice de sobrecarga
  - Fórmula: `Is = ΣPeq / (capacidade_mes × wc)`
  - Peso de complexidade (`wc`): Nível I = 0,8; Nível II = 1,0; Nível III = 1,3
  - Para unidades com mais de um nível, foi considerado o maior nível informado
  - Classificação: Adequado (`Is < 0,90`), Em risco (`0,90 ≤ Is ≤ 1,10`) e Sobrecarregado (`Is > 1,10`)
  - Resultado: índice calculado para 63 UBS; 6 adequadas, 3 em risco e 54 sobrecarregadas
  - Os setores com valores demográficos suprimidos (`X`) não entraram na soma de PEQ e foram contabilizados na coluna `SETORES_SEM_PEQ`
  - O índice e a classificação de cada UBS foram associados aos respectivos `CD_SETOR` em `Dados_Tratados/indice_sobrecarga_setores.csv`, permitindo a junção com a malha no QGIS
[] - Mapear setores de alta densidade fora de qualquer area de cobertura (zonas descobertas)
[] - Identificar postos com inadequacao de complexidade: nivel 1 cobrindo setor com alta populacao_idosa ou populacao_infatil sem as
especicialidades necessarias
[] - Produzir mapa por diagnóstico: Is por cor, complexidade por símbolo, zonas descobertas e gradiente de densidade
[] - Elaborar proposta
