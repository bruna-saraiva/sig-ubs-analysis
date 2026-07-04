# Procedimento de análise no QGIS

Este documento descreve como reproduzir a preparação espacial das bases de setores censitários e unidades de saúde de São Luís. O objetivo é associar cada setor à UBS de referência estimada por proximidade, usando polígonos de Voronoi, e preparar as camadas para os mapas do trabalho.

## 1. Arquivos necessários

- Malha de Setores Censitários definitiva do Censo 2022;
- `Dados_Tratados/postos_de_saude.csv`;
- `Dados_Tratados/indice_sobrecarga_com_setores.csv`, após os cálculos realizados fora do QGIS.

Neste documento, a expressão **malha definitiva** significa especificamente a **Malha de Setores Censitários definitiva do Censo Demográfico 2022**, disponibilizada pelo IBGE. Não se trata da malha municipal, da malha de bairros ou de outra divisão territorial.

Os valores de `CD_SETOR` dessa malha devem ter 15 algarismos e não podem terminar com `P`. A letra `P` identifica a Malha de Setores Censitários preliminar, que não é compatível com os agregados definitivos utilizados no trabalho.

## 2. Criar o GeoPackage do projeto

Recomenda-se armazenar todas as camadas permanentes no mesmo arquivo:

```text
trabalho_saude_slz.gpkg
```

Ao salvar novas camadas, selecione sempre esse arquivo e informe um nome diferente para a camada interna. Escolha **adicionar nova camada** quando o GeoPackage já existir. Não escolha **sobrescrever arquivo**, pois isso pode apagar as demais camadas.

## 3. Selecionar somente os setores de São Luís

1. Adicione a malha definitiva ao QGIS.
2. Abra a tabela de atributos.
3. Clique em **Selecionar feições usando uma expressão**.
4. Use:

```qgis
"CD_MUN" = '2111300'
```

5. Clique em **Selecionar feições**.
6. Exporte em **Exportar → Salvar feições selecionadas como...**.
7. Configure:

```text
Formato: GeoPackage
Arquivo: trabalho_saude_slz.gpkg
Camada: setores_sao_luis
```

8. Marque **Salvar somente feições selecionadas**.

### Validação

- Todos os registros devem ter `CD_MUN = 2111300`;
- Todos devem apresentar `NM_MUN = São Luís`;
- Nenhum `CD_SETOR` deve terminar com `P`;
- A camada definitiva utilizada no projeto possui 1.736 setores de São Luís.

## 4. Adicionar os pontos das UBS

1. Acesse **Camada → Adicionar camada → Adicionar camada de texto delimitado**.
2. Selecione `Dados_Tratados/postos_de_saude.csv`.
3. Configure:

```text
Campo X: longitude
Campo Y: latitude
Geometria: coordenadas de ponto
```

4. Informe o SRC correspondente às coordenadas geográficas, normalmente SIRGAS 2000 (`EPSG:4674`).
5. Adicione a camada.

### Validação

- Confira visualmente se os pontos aparecem em São Luís;
- Verifique se `CNES`, `NOME FANTASIA` e `capacidade/mes` estão preenchidos;
- Cada CNES deve aparecer apenas uma vez;
- Remova geometrias duplicadas antes de criar o Voronoi.

Para remover pontos exatamente repetidos:

```text
Processamento → Caixa de ferramentas → Excluir geometrias duplicadas
```

## 5. Reprojetar as camadas

Os cálculos de distância não devem ser realizados diretamente em latitude e longitude. Exporte os setores e as UBS para:

```text
SIRGAS 2000 / UTM zona 23S
EPSG:31983
```

Use **Exportar → Salvar feições como...** e grave as camadas reprojetadas no GeoPackage:

```text
setores_sao_luis_utm
postos_saude_utm
```

## 6. Criar as áreas de cobertura por Voronoi

1. Abra **Processamento → Caixa de ferramentas**.
2. Procure **Polígonos de Voronoi**.
3. Configure:

```text
Camada de entrada: postos_saude_utm
Região de buffer: aproximadamente 10%
```

4. Salve no GeoPackage:

```text
cobertura_voronoi
```

Cada polígono representa a área geometricamente mais próxima de uma UBS. Os campos do ponto original, como CNES, nome e capacidade, devem permanecer associados ao polígono.

O Voronoi representa uma aproximação de cobertura por proximidade euclidiana. Ele não corresponde necessariamente às áreas administrativas oficiais das UBS.

## 7. Criar o limite de São Luís

1. Procure a ferramenta **Dissolver**.
2. Use `setores_sao_luis_utm` como entrada.
3. Não selecione campo de dissolução, para reunir todos os setores.
4. Salve como:

```text
limite_sao_luis
```

O resultado será um único limite formado pela união dos setores.

## 8. Recortar o Voronoi pelo município

1. Abra a ferramenta **Recortar**.
2. Configure:

```text
Camada de entrada: cobertura_voronoi
Camada de sobreposição: limite_sao_luis
```

3. Salve como:

```text
cobertura_voronoi_sao_luis
```

Esse procedimento impede que os polígonos de cobertura avancem para fora do recorte estudado.

## 9. Criar um ponto representativo de cada setor

Não se deve unir diretamente os polígonos dos setores aos polígonos de Voronoi usando o predicado `intersecta`. Um setor pode atravessar mais de uma área de Voronoi e produzir linhas duplicadas.

Para garantir uma única UBS por setor:

1. Procure **Ponto na superfície**.
2. Use `setores_sao_luis_utm` como entrada.
3. Salve como:

```text
pontos_setores_sao_luis
```

Foi utilizado **Ponto na superfície** em vez de centroide porque o ponto gerado permanece dentro do setor, inclusive em polígonos de formato irregular.

## 10. Associar cada setor à cobertura de uma UBS

1. Abra **Unir atributos pela localização**.
2. Configure:

```text
Camada de entrada: pontos_setores_sao_luis
Camada de união: cobertura_voronoi_sao_luis
Predicado: dentro de
Tipo de união: utilizar apenas a primeira feição correspondente
```

3. Adicione pelo menos os campos:

```text
CNES
NOME FANTASIA
NÍVEL DE ATENÇÃO
TURNO DE ATENDIMENTO
latitude
longitude
capacidade/mes
servicos_inferidos
```

4. Salve como:

```text
setores_ubs_associados
```

### Validação

- Deve existir uma linha por `CD_SETOR`;
- Não pode haver `CD_SETOR` duplicado;
- Todos os registros devem pertencer a São Luís;
- A quantidade de registros deve corresponder aos 1.736 setores da malha;
- Verifique registros sem CNES;
- Inspecione visualmente alguns setores periféricos e suas UBS associadas.

Um ponto exatamente sobre uma fronteira ou lacuna pode ficar sem associação. Nesse caso, selecione o setor e associe-o à UBS mais próxima, registrando o ajuste.

## 11. Exportar a associação para processamento tabular

Clique com o botão direito em `setores_ubs_associados` e escolha **Exportar → Salvar feições como...**.

Configure:

```text
Formato: CSV
Delimitador: vírgula
Arquivo: juncao_setores_ubs.csv
```

O arquivo utilizado neste projeto está preservado em:

```text
Dados_Intermediarios/juncao_setores_ubs.csv
```

Esse CSV foi unido às informações demográficas por `CD_SETOR`. Os cálculos de população equivalente e índice de sobrecarga foram realizados fora do QGIS.

## 12. Adicionar o índice calculado ao mapa

1. Adicione `Dados_Tratados/indice_sobrecarga_com_setores.csv` como camada de texto delimitado.
2. Escolha **Sem geometria**.
3. Abra as propriedades de `setores_sao_luis_utm`.
4. Entre em **Uniões** e clique em `+`.
5. Configure:

```text
Camada de união: indice_sobrecarga_com_setores
Campo de união: CD_SETOR
Campo alvo: CD_SETOR
```

6. Adicione os campos necessários, incluindo:

```text
POPULACAO_EQUIVALENTE
CNES
NOME FANTASIA
INDICE_SOBRECARGA
CLASSIFICACAO
```

Essa união é inicialmente virtual. Para torná-la permanente:

1. Clique com o botão direito na camada unida;
2. Selecione **Exportar → Salvar feições como...**;
3. Salve no GeoPackage como:

```text
setores_indicadores
```

## 13. Aplicar a classificação do índice

Abra **Propriedades → Simbologia** e selecione **Categorizado**.

Use o campo:

```text
CLASSIFICACAO
```

Sugestão de cores:

- `Adequado`: verde;
- `Em risco`: amarelo;
- `Sobrecarregado`: vermelho;
- `Sem associação`: cinza.

Os limites adotados são:

```text
Adequado: Is < 0,90
Em risco: 0,90 ≤ Is ≤ 1,10
Sobrecarregado: Is > 1,10
```

## 14. Camadas que devem ser preservadas

O GeoPackage final deve conter, no mínimo:

```text
setores_indicadores
postos_saude_utm
cobertura_voronoi_sao_luis
limite_sao_luis
```

Também podem ser mantidas as camadas intermediárias:

```text
setores_sao_luis_utm
cobertura_voronoi
pontos_setores_sao_luis
setores_ubs_associados
```

## 15. Salvar o projeto

Salve o projeto do QGIS como arquivo `.qgz`. O projeto guarda organização, estilos e referências às camadas, mas não preserva resultados temporários.

Antes de fechar:

1. Identifique camadas temporárias;
2. Use **Tornar permanente** ou exporte-as para o GeoPackage;
3. Salve o projeto com `Ctrl + S`;
4. Reabra o projeto e confira se nenhuma camada aparece como indisponível.

## 16. Erros que devem ser evitados

- Usar a malha preliminar, identificada pelo sufixo `P`;
- Filtrar por um campo regional como `NM_RGI` em vez de `CD_MUN`;
- Exportar todas as feições quando somente São Luís estava selecionado;
- Calcular distâncias em coordenadas geográficas;
- Criar Voronoi com pontos de UBS duplicados;
- Unir polígonos dos setores ao Voronoi por interseção, gerando mais de uma linha por setor;
- Remover o `P` do código preliminar e tratá-lo como se fosse definitivo;
- Fechar o QGIS mantendo resultados apenas como camadas temporárias;
- Sobrescrever o GeoPackage inteiro ao adicionar uma nova camada.

## 17. Observação metodológica

As áreas de Voronoi cobrem todo o recorte municipal e representam apenas a UBS geometricamente mais próxima. Para identificar zonas descobertas, será necessário estabelecer uma distância máxima aceitável de acesso e comparar essa distância com a localização dos setores. O Voronoi, isoladamente, não produz áreas sem cobertura.
