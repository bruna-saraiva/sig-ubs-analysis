import pandas as pd
from pathlib import Path
p=Path('Dados_Tratados')
df=pd.read_csv(p/'item2_setores_criticos.csv', sep=';')
# ensure numeric
for c in ['POPULACAO_INFANTIL','POPULACAO_IDOSA']:
    if c in df.columns:
        df[c]=pd.to_numeric(df[c], errors='coerce')
# UBS_INADEQUADAS may be numeric or string; convert
if 'UBS_INADEQUADAS' in df.columns:
    df['UBS_INADEQUADAS']=df['UBS_INADEQUADAS'].astype(str)
# group
grp=df.groupby('UBS_INADEQUADAS').agg(
    setores_criticos=('CD_SETOR', 'nunique'),
    pop_infantil_sum=('POPULACAO_INFANTIL','sum'),
    pop_idosa_sum=('POPULACAO_IDOSA','sum')
).reset_index()
# sort
top5=grp.sort_values('setores_criticos', ascending=False).head(5)
print('UBS_INADEQUADAS;setores_criticos;pop_infantil_sum;pop_idosa_sum')
for _,r in top5.iterrows():
    print(f"{r['UBS_INADEQUADAS']};{int(r['setores_criticos'])};{int(r['pop_infantil_sum'])};{int(r['pop_idosa_sum'])}")
