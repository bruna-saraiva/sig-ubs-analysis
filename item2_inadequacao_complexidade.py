"""
Item 2 - Diagnóstico Espacial: Identificação de Postos com Inadequação de Complexidade
Análise de UBS Nível I que atendem setores com alta população infantil ou idosa
sem especialidades correspondentes.
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

import pandas as pd
import numpy as np
import os
from pathlib import Path

# ============================================================================
# ETAPA 1: CARREGAMENTO DOS ARQUIVOS
# ============================================================================

print("=" * 80)
print("ITEM 2 - DIAGNÓSTICO ESPACIAL")
print("Identificação de Postos com Inadequação de Complexidade")
print("=" * 80)
print("\n[ETAPA 1] Carregando arquivos...")

dados_dir = Path("./Dados_Tratados")
intermediario_dir = Path("./Dados_Intermediarios")

# Carregar os três arquivos principais
df_sobrecarga = pd.read_csv(dados_dir / "indice_sobrecarga_com_setores.csv", sep=";")
df_demografia = pd.read_csv(dados_dir / "densidade_populacional_setores_join_ubs.csv", sep=";")
df_especialidades = pd.read_csv(intermediario_dir / "juncao_setores_ubs.csv")

print(f"✓ Carregado: indice_sobrecarga_com_setores.csv ({len(df_sobrecarga)} linhas)")
print(f"✓ Carregado: densidade_populacional_setores_join_ubs.csv ({len(df_demografia)} linhas)")
print(f"✓ Carregado: juncao_setores_ubs.csv ({len(df_especialidades)} linhas)")

# Colunas importantes
print("\nColunas disponíveis:")
print(f"  - Sobrecarga: {list(df_sobrecarga.columns)[:10]}...")
print(f"  - Demografia: {list(df_demografia.columns)[:10]}...")
print(f"  - Especialidades: {list(df_especialidades.columns)}")

# ============================================================================
# ETAPA 2: UNIÃO DAS TABELAS
# ============================================================================

print("\n[ETAPA 2] Realizando merges...")

# Merge 1: Sobrecarga + Especialidades (por CNES)
df_merge1 = df_sobrecarga.merge(
    df_especialidades[["CNES", "servicos_inferidos"]],
    on="CNES",
    how="left"
)

# Usar dados de sobrecarga que já incluem população
df_merged = df_merge1.copy()

print(f"✓ Tabela unificada: {len(df_merged)} linhas")
print(f"✓ Colunas finais: {len(df_merged.columns)} colunas")

# Verificar se a coluna de complexidade existe
if "NIVEL_REFERENCIA" not in df_merged.columns:
    print("AVISO: coluna NIVEL_REFERENCIA não encontrada. Usando NÍVEL DE ATENÇÃO")
    if "NÍVEL DE ATENÇÃO" in df_merged.columns:
        df_merged["NIVEL_REFERENCIA"] = df_merged["NÍVEL DE ATENÇÃO"]

print(f"\nAmostra dos dados unificados:")
print(df_merged[["CNES", "CD_SETOR", "NIVEL_REFERENCIA", "POPULACAO_INFANTIL", 
                 "POPULACAO_IDOSA", "servicos_inferidos"]].head())

# ============================================================================
# ETAPA 3: DEFINIR "ALTA POPULAÇÃO" - PERCENTIL 75
# ============================================================================

print("\n[ETAPA 3] Definindo limites de 'alta população'...")

# Converter para numérico - usar ',' como separador decimal se necessário
df_merged["POPULACAO_INFANTIL"] = pd.to_numeric(
    df_merged["POPULACAO_INFANTIL"].astype(str).str.replace(",", "."), 
    errors="coerce"
)
df_merged["POPULACAO_IDOSA"] = pd.to_numeric(
    df_merged["POPULACAO_IDOSA"].astype(str).str.replace(",", "."), 
    errors="coerce"
)

# Remover valores NaN antes do cálculo
pop_infantil_valid = df_merged["POPULACAO_INFANTIL"].dropna()
pop_idosa_valid = df_merged["POPULACAO_IDOSA"].dropna()

p75_infantil = pop_infantil_valid.quantile(0.75)
p75_idosa = pop_idosa_valid.quantile(0.75)

print(f"Percentil 75 - População Infantil: {p75_infantil:.1f}")
print(f"Percentil 75 - População Idosa: {p75_idosa:.1f}")

print(f"\nEstatísticas de população infantil:")
print(pop_infantil_valid.describe())
print(f"\nEstatísticas de população idosa:")
print(pop_idosa_valid.describe())

# Marcar setores com alta população
df_merged["alta_infantil"] = df_merged["POPULACAO_INFANTIL"] >= p75_infantil
df_merged["alta_idosa"] = df_merged["POPULACAO_IDOSA"] >= p75_idosa
df_merged["alta_populacao"] = df_merged["alta_infantil"] | df_merged["alta_idosa"]

print(f"\n✓ Setores com alta população infantil: {df_merged['alta_infantil'].sum()}")
print(f"✓ Setores com alta população idosa: {df_merged['alta_idosa'].sum()}")
print(f"✓ Total de setores com alta população: {df_merged['alta_populacao'].sum()}")

# ============================================================================
# ETAPA 4: FILTRAR UBS NÍVEL I
# ============================================================================

print("\n[ETAPA 4] Filtrando UBS de Nível I...")

df_nivel_i = df_merged[df_merged["NIVEL_REFERENCIA"] == "I"].copy()

print(f"✓ UBS de Nível I encontradas: {df_nivel_i['CNES'].nunique()}")
print(f"✓ Linhas (setor-UBS) de Nível I: {len(df_nivel_i)}")

# Filtrar apenas Nível I com alta população
df_nivel_i_alta = df_nivel_i[df_nivel_i["alta_populacao"]].copy()

print(f"✓ UBS Nível I com setores de alta população: {df_nivel_i_alta['CNES'].nunique()}")
print(f"✓ Linhas de Nível I com alta população: {len(df_nivel_i_alta)}")

# ============================================================================
# ETAPA 5 & 6: VERIFICAR POPULAÇÃO E ESPECIALIDADES
# ============================================================================

print("\n[ETAPA 5 & 6] Verificando população atendida e especialidades...")

# Dicionários de serviços esperados
servicos_infantil = {
    "pediatria", "vacinação", "pré-natal", "infantil", "criança",
    "saúde da criança", "atenção infantil", "puericultura"
}

servicos_idoso = {
    "clínica ampliada", "idoso", "geriátrica", "geriatria", "ampliada",
    "saúde da família ampliada", "gerontologia", "atenção ao idoso"
}

def possui_servico(servicos_str, keywords):
    """Verifica se alguma palavra-chave está presente nos serviços"""
    if pd.isna(servicos_str):
        return False
    servicos_lower = str(servicos_str).lower()
    return any(keyword in servicos_lower for keyword in keywords)

# Adicionar colunas de verificação
df_nivel_i_alta["tem_servico_infantil"] = df_nivel_i_alta["servicos_inferidos"].apply(
    lambda x: possui_servico(x, servicos_infantil)
)
df_nivel_i_alta["tem_servico_idoso"] = df_nivel_i_alta["servicos_inferidos"].apply(
    lambda x: possui_servico(x, servicos_idoso)
)

# Identificar inadequações
inadequacoes = []

for _, row in df_nivel_i_alta.iterrows():
    motivos = []
    
    if row["alta_infantil"] and not row["tem_servico_infantil"]:
        motivos.append("Falta atendimento infantil")
    
    if row["alta_idosa"] and not row["tem_servico_idoso"]:
        motivos.append("Falta atendimento ao idoso")
    
    if motivos:
        inadequacoes.append({
            "CNES": row["CNES"],
            "NOME_FANTASIA": row["NOME FANTASIA"],
            "NIVEL_REFERENCIA": row["NIVEL_REFERENCIA"],
            "CD_SETOR": row["CD_SETOR"],
            "POPULACAO": row["POPULACAO"],
            "POPULACAO_INFANTIL": row["POPULACAO_INFANTIL"],
            "POPULACAO_IDOSA": row["POPULACAO_IDOSA"],
            "ALTA_INFANTIL": row["alta_infantil"],
            "ALTA_IDOSA": row["alta_idosa"],
            "SERVICOS_DISPONIVEL": row["servicos_inferidos"],
            "MOTIVO": "; ".join(motivos)
        })

df_inadequadas = pd.DataFrame(inadequacoes)

if len(df_inadequadas) > 0:
    print(f"\n✓ UBS inadequadas identificadas: {df_inadequadas['CNES'].nunique()}")
    print(f"✓ Setores inadequados: {len(df_inadequadas)}")
    print("\nAmostra de UBS inadequadas:")
    print(df_inadequadas[[
        "CNES", "NOME_FANTASIA", "CD_SETOR", 
        "POPULACAO_INFANTIL", "POPULACAO_IDOSA", "MOTIVO"
    ]].head(10))
else:
    print("\n⚠ Nenhuma UBS com inadequação de complexidade foi identificada.")

# ============================================================================
# ETAPA 7: PRODUZIR TABELA FINAL
# ============================================================================

print("\n[ETAPA 7] Produzindo tabela final...")

# Ordenar por CNES
df_inadequadas_sorted = df_inadequadas.sort_values(["CNES", "CD_SETOR"]).reset_index(drop=True)

# Salvar CSV
output_path = Path("./Dados_Tratados") / "item2_ubs_inadequadas.csv"
df_inadequadas_sorted.to_csv(output_path, sep=";", index=False, encoding="utf-8-sig")
print(f"✓ Salvo: {output_path}")

# Criar resumo de setores críticos
setores_criticos = df_inadequadas_sorted.groupby("CD_SETOR").agg({
    "POPULACAO_INFANTIL": "first",
    "POPULACAO_IDOSA": "first",
    "CNES": lambda x: "; ".join(x.astype(str).unique())
}).rename(columns={"CNES": "UBS_INADEQUADAS"}).reset_index()

setores_path = Path("./Dados_Tratados") / "item2_setores_criticos.csv"
setores_criticos.to_csv(setores_path, sep=";", index=False, encoding="utf-8-sig")
print(f"✓ Salvo: {setores_path}")

# ============================================================================
# ETAPA 8: ESTATÍSTICAS
# ============================================================================

print("\n[ETAPA 8] Gerando estatísticas...")

# Contar UBS Nível I
total_nivel_i = df_nivel_i['CNES'].nunique()

# Contar UBS inadequadas
ubs_inadequadas = df_inadequadas_sorted['CNES'].nunique()

# Total de UBS analisadas
total_ubs = df_merged['CNES'].nunique()

# Setores críticos
setores_afetados = df_inadequadas_sorted['CD_SETOR'].nunique()

# População afetada
populacao_afetada = df_inadequadas_sorted.groupby('CNES').agg({
    'POPULACAO_INFANTIL': 'sum',
    'POPULACAO_IDOSA': 'sum'
}).sum().sum()

# Porcentagem de inadequação
pct_inadequacao = (ubs_inadequadas / total_nivel_i * 100) if total_nivel_i > 0 else 0

print("\n" + "=" * 80)
print("ESTATÍSTICAS GERAIS")
print("=" * 80)
print(f"Total de UBS analisadas: {total_ubs}")
print(f"Total de UBS Nível I: {total_nivel_i}")
print(f"Total de UBS inadequadas (Nível I): {ubs_inadequadas}")
print(f"Percentual de inadequação: {pct_inadequacao:.2f}%")
print(f"Total de setores críticos: {setores_afetados}")
print(f"População infantil afetada: {df_inadequadas_sorted['POPULACAO_INFANTIL'].sum():.0f}")
print(f"População idosa afetada: {df_inadequadas_sorted['POPULACAO_IDOSA'].sum():.0f}")
print(f"Total de habitantes afetados: {populacao_afetada:.0f}")

# Motivos mais comuns
if len(df_inadequadas) > 0:
    print("\n" + "=" * 80)
    print("MOTIVOS DE INADEQUAÇÃO")
    print("=" * 80)
    motivos_count = df_inadequadas['MOTIVO'].value_counts()
    for motivo, count in motivos_count.items():
        print(f"  - {motivo}: {count} setor(es)")

# ============================================================================
# TABELA RESUMO PARA RELATÓRIO
# ============================================================================

print("\n[RELATÓRIO] Gerando tabela resumida...")

resumo_df = df_inadequadas_sorted[[
    "CNES", "NOME_FANTASIA", "NIVEL_REFERENCIA", "CD_SETOR",
    "POPULACAO", "POPULACAO_INFANTIL", "POPULACAO_IDOSA",
    "ALTA_INFANTIL", "ALTA_IDOSA", "SERVICOS_DISPONIVEL", "MOTIVO"
]].copy()

resumo_df.columns = [
    "CNES", "UBS", "Nível", "Setor", "Pop. Total",
    "Pop. Infantil", "Pop. Idosa", "Infantil↑", "Idosa↑", "Serviços", "Motivo"
]

resumo_path = Path("./Dados_Tratados") / "item2_tabela_resumo.csv"
resumo_df.to_csv(resumo_path, sep=";", index=False, encoding="utf-8-sig")
print(f"✓ Salvo: {resumo_path}")

# ============================================================================
# GRÁFICOS (opcional)
# ============================================================================

try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    
    print("\n[GRÁFICOS] Gerando visualizações...")
    
    plt.style.use('seaborn-v0_8-darkgrid')
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Item 2 - Inadequação de Complexidade de UBS', fontsize=16, fontweight='bold')
    
    # Gráfico 1: Distribuição de inadequações
    if len(df_inadequadas) > 0:
        motivos_data = df_inadequadas['MOTIVO'].value_counts()
        axes[0, 0].barh(motivos_data.index, motivos_data.values, color='steelblue')
        axes[0, 0].set_xlabel('Quantidade de Setores')
        axes[0, 0].set_title('Motivos de Inadequação')
        axes[0, 0].grid(axis='x', alpha=0.3)
    
    # Gráfico 2: População afetada por tipo
    pop_data = {
        'Infantil': df_inadequadas_sorted['POPULACAO_INFANTIL'].sum(),
        'Idosa': df_inadequadas_sorted['POPULACAO_IDOSA'].sum()
    }
    axes[0, 1].bar(pop_data.keys(), pop_data.values(), color=['#ff9999', '#66b3ff'])
    axes[0, 1].set_ylabel('População')
    axes[0, 1].set_title('População Afetada por Tipo')
    axes[0, 1].grid(axis='y', alpha=0.3)
    for i, v in enumerate(pop_data.values()):
        axes[0, 1].text(i, v + 50, f'{int(v)}', ha='center', fontweight='bold')
    
    # Gráfico 3: Estatísticas gerais
    stats_data = [total_ubs, total_nivel_i, ubs_inadequadas]
    stats_labels = [f'Total UBS\n({total_ubs})', 
                   f'Nível I\n({total_nivel_i})', 
                   f'Inadequadas\n({ubs_inadequadas})']
    axes[1, 0].bar(stats_labels, stats_data, color=['#66c2a5', '#fc8d62', '#8da0cb'])
    axes[1, 0].set_ylabel('Quantidade')
    axes[1, 0].set_title('Distribuição de UBS')
    axes[1, 0].grid(axis='y', alpha=0.3)
    
    # Gráfico 4: Percentual de inadequação
    if total_nivel_i > 0:
        pie_data = [ubs_inadequadas, total_nivel_i - ubs_inadequadas]
        pie_labels = [f'Inadequadas\n({pct_inadequacao:.1f}%)', 
                      f'Adequadas\n({100-pct_inadequacao:.1f}%)']
        axes[1, 1].pie(pie_data, labels=pie_labels, autopct='%1.1f%%',
                       colors=['#e78ac3', '#a6d854'], startangle=90)
        axes[1, 1].set_title('Proporção UBS Nível I')
    
    plt.tight_layout()
    graph_path = Path("./Dados_Tratados") / "item2_graficos.png"
    plt.savefig(graph_path, dpi=300, bbox_inches='tight')
    print(f"✓ Salvo: {graph_path}")
    plt.close()
    
except Exception as e:
    print(f"⚠ Erro ao gerar gráficos: {e}")

# ============================================================================
# RESUMO FINAL
# ============================================================================

print("\n" + "=" * 80)
print("ANÁLISE CONCLUÍDA")
print("=" * 80)
print("\nArquivos gerados:")
print(f"  ✓ {output_path}")
print(f"  ✓ {setores_path}")
print(f"  ✓ {resumo_path}")
if 'graph_path' in locals():
    print(f"  ✓ {graph_path}")

print("\nPróximos passos:")
print("  1. Revisar os arquivos CSV gerados")
print("  2. Elaborar proposta de intervenção com base nos resultados")
print("  3. Preparar mapas temáticos destacando as UBS inadequadas")
print("  4. Incluir análise no relatório final")

print("\n" + "=" * 80)
