# Análise da cobertura das UBS de São Luís

## Estrutura do projeto

### Fontes

- `Base_de_Dados.zip`: arquivos originais do IBGE e relatório de validação.
- `CNES_UBS_Sao-luis.csv`: cadastro original das unidades de saúde.

### Processamento

- `setores_censitarios.ipynb`: tratamento dos dados censitários.
- `ubs-slz.ipynb`: tratamento das unidades de saúde.
- `Dados_Intermediarios/juncao_setores_ubs.csv`: associação espacial do cenário anterior de Voronoi.
- `Dados_Intermediarios/setores_cobertura_ubs_5km_bruto.csv`: exportação bruta do QGIS para o cenário de cobertura limitada a 5 km.

### Dados tratados canônicos

- `Dados_Tratados/postos_de_saude.csv`: UBS tratadas, com capacidade estimada e serviços inferidos.
- `Dados_Tratados/setores_sao_luis.csv`: população, densidade e renda por setor.
- `Dados_Tratados/densidade_populacional_setores_censitarios.csv`: população total, infantil e idosa e densidade por setor.
- `Dados_Tratados/densidade_populacional_setores_join_ubs.csv`: base analítica completa por setor, com UBS associada e população equivalente.
- `Dados_Tratados/indice_sobrecarga_ubs.csv`: resultado agregado por UBS.
- `Dados_Tratados/indice_sobrecarga_com_setores.csv`: resultado por setor para união com a malha e elaboração dos mapas.
- `Dados_Tratados/zonas_descobertas_5km.csv`: setores localizados a mais de 5 km de qualquer UBS.
- Os arquivos iniciados por `voronoi_` preservam o cenário anterior em que fizemos a area de cobertura usando voronoi, mas é apenas para comparação metodológica.

### Documentação

- `Info/Acompanhamento.md`: andamento, fórmulas e decisões metodológicas.
- `Info/Procedimento_QGIS.md`: guia para reproduzir a preparação espacial, a cobertura limitada por distância e as uniões no QGIS.
- `Info/SIG_2026.1_Av3.pdf`: enunciado do trabalho.
- `Info/liv102136.pdf`: documentação do IBGE.
- `Info/Agregados_por_setores_demografia._info.png`: referência das variáveis demográficas.

## Arquivos recomendados para continuidade

Para as análises estatísticas, use `indice_sobrecarga_ubs.csv`. Para os mapas no QGIS, una `indice_sobrecarga_com_setores.csv` à malha definitiva pelo campo `CD_SETOR`.
