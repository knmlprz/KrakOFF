import pandas as pd
import numpy as np
import os
from pathlib import Path
import re


folder = Path('.\\filmiki')  # np. Path('./dane')
files = [str(p) for p in folder.rglob('*') if p.is_file()]

df = pd.read_csv('wydarzenia_krakow.csv', sep=';')

#df[['data_rozpoczecia', 'data_zakonczenia']] = pd.to_datetime(df[['data_rozpoczecia', 'data_zakonczenia']], errors='coerce').dt.normalize()
df['czy_na_zewnatrz'] = np.random.randint(0, 2, size=len(df))


# Przypisanie ścieżek
if len(files) >= len(df):
    df['sciezka_do_filmiku'] = files[:len(df)]
else:
    df['sciezka_do_filmiku'] = files + [np.nan] * (len(df) - len(files))

# Podgląd
print(df[['tytul', 'sciezka_do_filmiku']])



kategorie = df['typ_wydarzenia']

def generuj_hashtagi(nazwa):
    if nazwa == 'W gminach Metropolii':
        return '#WGminach #Metropolii'

    nazwa = nazwa.replace(',', ' i')

    czesci = [cz.strip() for cz in re.split(r'\bi\b', nazwa, flags=re.IGNORECASE)]

    # generuj hashtagi
    hashtagi = []
    for cz in czesci:
        if cz:
            slowa = cz.lower().split()
            if len(slowa) == 1:
                hashtagi.append(f'#{slowa[0]}')
            else:
                hashtagi.extend([f'#{s}' for s in slowa])
    return ' '.join(hashtagi)

df1 = pd.DataFrame({'kategoria': kategorie})

df['hashtagi'] = df1['kategoria'].apply(generuj_hashtagi)

df.to_csv('data\\events_tiktak.csv', sep =';', index=False)