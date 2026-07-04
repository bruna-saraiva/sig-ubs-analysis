# Procedimento de análise no QGIS

Este documento descreve como reproduzir a preparação espacial das bases de setores censitários e unidades de saúde de São Luís. O método final associa cada setor à UBS mais próxima somente quando ela estiver a até 5 km do ponto representativo do setor. Os setores sem UBS nesse limite são classificados como descobertos.

Uma primeira versão do trabalho utilizou polígonos de Voronoi. Esse cenário foi preservado em arquivos iniciados por `voronoi_`, mas não representa a metodologia principal, pois o Voronoi atribui todo o território a alguma UBS e não permite identificar zonas descobertas.

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
- Remova geometrias duplicadas antes de calcular buffers e proximidade.

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

## 6. Criar um ponto representativo de cada setor

Para garantir uma única classificação por setor:

1. Procure **Ponto na superfície**;
2. Use `setores_sao_luis_utm` como entrada;
3. Salve como `pontos_setores_sao_luis`.

Foi utilizado **Ponto na superfície** em vez de centroide porque o ponto permanece dentro do setor, inclusive em polígonos irregulares.

## 7. Criar a cobertura de 5 km

Abra a ferramenta **Buffer** e configure:

```text
Camada de entrada: postos_saude_utm
Distância: 5000
Segmentos: 20
Dissolver resultado: não
```

Salve como `buffers_ubs_5km`. Essa camada preserva um polígono e o CNES de cada UBS.

Em seguida, use **Dissolver**, sem selecionar campos, para reunir todos os buffers. Salve como:

```text
cobertura_geral_5km
```

É esperado que a tabela da camada dissolvida possua apenas uma linha. Sua função é indicar se uma localização está dentro do alcance de pelo menos uma UBS, e não identificar qual UBS é responsável.

## 8. Criar o limite e as zonas descobertas

Use **Dissolver** em `setores_sao_luis_utm`, sem selecionar campos, e salve como `limite_sao_luis`.

Recorte `cobertura_geral_5km` por `limite_sao_luis` e salve como `cobertura_geral_5km_recortada`.

Depois use **Diferença**:

```text
Camada de entrada: limite_sao_luis
Camada de sobreposição: cobertura_geral_5km_recortada
```

Salve o resultado como `zonas_descobertas_5km`.

## 9. Associar cada setor à UBS mais próxima

Abra **Juntar atributos pela feição mais próxima**. O nome pode aparecer como **Unir atributos pela feição mais próxima** ou `native:joinbynearest`, conforme a versão do QGIS.

Configure:

```text
Camada de entrada: pontos_setores_sao_luis
Camada de união: postos_saude_utm
Número máximo de vizinhos: 1
Distância máxima: 5000
Descartar registros sem correspondência: não
```

Salve como:

```text
setores_cobertura_ubs_5km
```

A ferramenta adicionará os atributos da UBS e um campo numérico de distância, normalmente chamado `distance`. Se já existirem campos com os mesmos nomes, o QGIS poderá acrescentar sufixos como `_2`; no processamento deste projeto, os campos corretos da nova associação receberam esse sufixo.

## 10. Classificar os setores

Abra a calculadora de campos, escolha **Atualizar campo existente** ou crie `SITUACAO_COBERTURA` como texto. Use:

```qgis
CASE
    WHEN "distance" IS NULL THEN 'Descoberto'
    ELSE 'Coberto'
END
```

Como a própria busca foi limitada a 5.000 m, uma distância preenchida identifica setor coberto. Distância nula significa que nenhuma UBS foi encontrada no limite.

Não use uma classificação anterior obtida somente pela união com o buffer se ela divergir do campo `distance`. A distância gerada com os mesmos pontos e o mesmo limite é o critério final.

### Validação

- Deve existir uma linha por `CD_SETOR`;
- A camada deve conter os 1.736 setores;
- Nenhum setor coberto pode ficar sem o CNES novo;
- Nenhum setor descoberto deve ter distância preenchida;
- Todas as distâncias preenchidas devem ser menores ou iguais a 5.000 m;
- Inspecione visualmente os setores periféricos.

Se a exportação contiver duas linhas por setor, conserve a linha com `n = 1` e distância preenchida. Para setores descobertos, preserve uma única linha com distância e CNES nulos.

## 11. Exportar para processamento tabular

Clique com o botão direito em `setores_cobertura_ubs_5km` e escolha **Exportar → Salvar feições como...**.

Configure:

```text
Formato: CSV
Codificação: UTF-8
Geometria: sem geometria
Arquivo: setores_cobertura_ubs_5km.csv
```

Preserve pelo menos:

```text
CD_SETOR
SITUACAO_COBERTURA
CNES_2
NOME FANTASIA_2
NÍVEL DE ATENÇÃO_2
TURNO DE ATENDIMENTO_2
latitude_2
longitude_2
capacidade/mes_2
servicos_inferidos_2
n
distance
```

O arquivo bruto utilizado está preservado em `Dados_Intermediarios/setores_cobertura_ubs_5km_bruto.csv`. Fora do QGIS, ele foi consolidado por `CD_SETOR`, unido aos dados demográficos e utilizado para recalcular a população equivalente e o índice de sobrecarga.

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
- `Descoberto`: cinza.

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
cobertura_geral_5km_recortada
zonas_descobertas_5km
limite_sao_luis
```

Também podem ser mantidas as camadas intermediárias:

```text
setores_sao_luis_utm
buffers_ubs_5km
pontos_setores_sao_luis
setores_cobertura_ubs_5km
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
- Calcular buffers ou distâncias com pontos de UBS duplicados;
- Usar os polígonos dos setores na busca de proximidade, em vez de um único ponto representativo;
- Definir a situação de cobertura por um campo antigo quando a busca final já fornece `distance`;
- Contar duas vezes um setor duplicado na exportação;
- Remover o `P` do código preliminar e tratá-lo como se fosse definitivo;
- Fechar o QGIS mantendo resultados apenas como camadas temporárias;
- Sobrescrever o GeoPackage inteiro ao adicionar uma nova camada.

## 17. Observação metodológica

O limite de 5 km representa um cenário de cobertura por distância euclidiana. Ele não considera rede viária, tempo de deslocamento, barreiras físicas nem territórios administrativos oficiais das UBS.

Cada setor coberto foi atribuído à UBS mais próxima dentro desse limite. Setores sem UBS a até 5 km foram classificados como descobertos e não entraram na soma da população equivalente das UBS. O cenário anterior de Voronoi foi preservado somente para comparação, pois o Voronoi cobre todo o território e não produz áreas descobertas.
