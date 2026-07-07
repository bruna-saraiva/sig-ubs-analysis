import pandas as pd
from pathlib import Path
p=Path('Dados_Tratados')
df=pd.read_csv(p/'item2_ubs_inadequadas.csv', sep=';')
for c in ['POPULACAO','POPULACAO_INFANTIL','POPULACAO_IDOSA']:
    if c in df.columns:
        df[c]=pd.to_numeric(df[c], errors='coerce')

grp=df.groupby('CNES').agg(
    NOME_FANTASIA=('NOME_FANTASIA','first'),
    setores_criticos=('CD_SETOR', lambda x: x.nunique()),
    pop_infantil_sum=('POPULACAO_INFANTIL','sum'),
    pop_idosa_sum=('POPULACAO_IDOSA','sum')
).reset_index()

top5=grp.sort_values('setores_criticos', ascending=False).head(5)
print('CNES;NOME_FANTASIA;setores_criticos;pop_infantil_sum;pop_idosa_sum')
for _,r in top5.iterrows():
    cn=int(r['CNES'])
    name=str(r['NOME_FANTASIA'])
    s=int(r['setores_criticos'])
    pi=int(r['pop_infantil_sum']) if not pd.isna(r['pop_infantil_sum']) else 0
    pdv=int(r['pop_idosa_sum']) if not pd.isna(r['pop_idosa_sum']) else 0
    print(f"{cn};{name};{s};{pi};{pdv}")
