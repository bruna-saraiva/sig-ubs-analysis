# Item 2 - Diagnóstico Espacial
## Identificação de Postos com Inadequação de Complexidade

---

## Resumo Executivo

Esta análise identifica **Unidades Básicas de Saúde (UBS) de Nível I que atendem setores com alta população infantil ou idosa, mas não possuem as especialidades correspondentes**.

### Descobertas Principais

- **15 UBS de Nível I analisadas**
- **15 UBS inadequadas identificadas (100%)**
- **6.948 setor-UBS em situação inadequada**
- **208 setores críticos afetados**
- **1.026.933 habitantes em risco** (população combinada de infantil + idosa)

---

## Metodologia

### 1. Definição de "Alta População" — Percentil 75

O critério de alta população foi estabelecido estatisticamente, evitando arbitrariedade:

| Métrica | Percentil 75 |
|---------|-------------|
| População Infantil | 46 pessoas/setor |
| População Idosa | 109 pessoas/setor |

**Justificativa:** A escolha do percentil 75 é amplamente utilizada em epidemiologia e planejamento de saúde como ponto de corte para identificar áreas de alta concentração.

### 2. Critérios de Inadequação

Uma UBS Nível I é considerada **inadequada** quando:

- Atende um setor com **alta população infantil** (≥46 crianças) MAS não oferece:
  - Pediatria
  - Vacinação
  - Pré-natal
  - Atenção infantil
  - Puericultura
  
**OU**

- Atende um setor com **alta população idosa** (≥109 idosos) MAS não oferece:
  - Clínica ampliada
  - Geriatria / Gerontologia
  - Atendimento ao idoso
  - Saúde da família ampliada

---

## Resultados Detalhados

### Estatísticas Gerais

```
Total de UBS analisadas:           63
Total de UBS Nível I:              15
Total de UBS inadequadas (Nível I): 15
Percentual de inadequação:         100%

Total de setores críticos:          208
População infantil afetada:     359.271
População idosa afetada:        667.662
Total de habitantes afetados: 1.026.933
```

### Motivos de Inadequação

| Motivo | Setores Afetados |
|--------|------------------|
| Falta atendimento infantil | 3.669 |
| Falta atendimento ao idoso | 1.964 |
| Falta ambos (infantil + idoso) | 1.315 |
| **TOTAL** | **6.948** |

### Achado Crítico

**100% das UBS de Nível I em São Luís apresentam inadequação de complexidade.**

Isso significa que todas as UBS de menor complexidade estão atendendo populações cuja demanda (alta proporção de crianças e/ou idosos) indicaria a necessidade de serviços mais especializados.

---

## UBS Inadequadas Identificadas

As 15 UBS inadequadas são:

| CNES | Nome Fantasia | Nível | Motivo Principal | Setores Afetados |
|------|---------------|-------|-----------------|------------------|
| 666394 | CENTRO DE SAUDE BARRETO | I | Falta atendimento ao idoso | Múltiplos |
| 2876175 | [UBS] | I | Falta atendimento ao idoso | Múltiplos |
| [Outras 13 UBS] | ... | I | ... | ... |

*(Ver arquivo `item2_ubs_inadequadas.csv` para lista completa)*

---

## Distribuição de Inadequação

### Por Tipo de Demanda

- **População infantil:** 3.669 setores (52,8%) com demanda não atendida
- **População idosa:** 1.964 setores (28,3%) com demanda não atendida
- **Ambas:** 1.315 setores (18,9%) com dupla carência

### Concentração Geográfica

Os **208 setores críticos** estão distribuídos entre todas as 15 UBS Nível I, indicando que o problema é **generalizado e não localizado**.

---

## Implicações

### Risco à Saúde

1. **Crianças:** Falta de pediatria, vacinação e pré-natal compromete:
   - Cobertura vacinal
   - Diagnóstico precoce
   - Acompanhamento do desenvolvimento

2. **Idosos:** Falta de serviços geriátricos compromete:
   - Controle de doenças crônicas
   - Prevenção de quedas
   - Atendimento integrado

### Sobrecarga do Sistema

UBS Nível I foram dimensionadas para atenção básica genérica, não para populações com demandas especializadas. Isso gera:
- Encaminhamentos inadequados
- Vazios assistenciais
- Iniquidade em saúde

---

## Recomendações

### Curto Prazo (0-6 meses)

1. **Capacitação:** Treinar equipes das 15 UBS Nível I em:
   - Protocolo de atendimento geriátrico
   - Protocolo de atendimento infantil
   - Vacinação avançada

2. **Referenciação:** Estabelecer fluxos claros de encaminhamento para UBS Nível II/III quando necessário

3. **Monitoramento:** Acompanhar qualidade de vida em setores críticos

### Médio Prazo (6-18 meses)

1. **Elevação de Complexidade:** Considerar upgrade de 5-7 UBS de maior demanda para Nível II

2. **Redistribuição de Áreas:** Reorganizar territórios para melhor distribuição de demanda

3. **Investimento em Infraestrutura:**
   - Ampliar espaço físico
   - Adquirir equipamentos de diagnóstico
   - Aumentar quadro de especialistas

### Longo Prazo (18+ meses)

1. **Reorganização da Rede:**
   - Estruturar rede com hierarquização adequada
   - UBS Nível I para áreas de baixa demanda
   - UBS Nível II/III para áreas de alta demanda

2. **Matriz de Oferta:**
   - Mapeamento de especialidades por nível
   - Protocolo de referência e contrarreferência

---

## Arquivos Gerados

1. **`item2_ubs_inadequadas.csv`** — Lista completa de todas as combinações setor-UBS inadequadas
2. **`item2_setores_criticos.csv`** — Resumo de setores com população infantil/idosa elevada
3. **`item2_tabela_resumo.csv`** — Tabela formatada para relatório
4. **`item2_graficos.png`** — Visualizações dos resultados

---

## Próximos Passos

1. ✅ **Análise concluída** — Item 2 do diagnóstico espacial
2. ⏳ **Mapa temático** — Localizar UBS inadequadas em mapa de São Luís
3. ⏳ **Proposta de intervenção** — Detalhar ações recomendadas
4. ⏳ **Integração com outros items** — Correlacionar com densidade de cobertura (Item 1)

---

## Referências Metodológicas

- **Percentil 75:** Utilizado para identificar valores anormalmente altos em distribuições normais
- **Especialidades esperadas:** Baseadas em protocolos do CONASS (Conselho Nacional de Secretários de Saúde) e MS
- **Classificação de UBS:** NÍVEL I (atenção básica) vs NÍVEL II/III (maior complexidade)

---

**Data da Análise:** 2025-07-06  
**Ferramenta:** Python com Pandas/NumPy  
**Área de Estudo:** São Luís, Maranhão  
**Total de Setores Analisados:** 1.736  
**Total de Registros:** 78.948 (setor × UBS)

---
