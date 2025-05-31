import pandas as pd
import numpy as np
import re
from datetime import datetime

df = pd.read_csv('wydarzenia_karnet_krakow_z_obrazkami_20250530-062133.csv')

# LOKALIZACJE
lok = pd.DataFrame()

lok['obiekty'] = df["lokalizacja_lista"].str.split(",").str[0].str.strip()
lok['ulice'] = df["lokalizacja_lista"].str.split(",").str[1].str.strip()
lok['miasta'] = df["lokalizacja_lista"].str.split(",").str[2].str.strip()

lok['miasta'] = lok['miasta'].fillna('Kraków')

df[['obiekty', 'ulice', 'miasta']] = lok[['obiekty', 'ulice', 'miasta']]
df = df.drop('lokalizacja_lista', axis=1)


# DATY
daty = pd.DataFrame()

daty['data_rozpoczecia'] = df['data_lista'].str.split("-").str[0].str.strip()
daty['data_zakonczenia'] = df['data_lista'].str.split("-").str[1].str.strip()

daty['godzina_rozpoczecia'] = daty['data_rozpoczecia'].str.split(",").str[1].str.strip()
daty['data_rozpoczecia'] = daty['data_rozpoczecia'].str.split(",").str[0].str.strip()

daty['czy_stale'] = np.nan

wanted_str = 'Wydarzenie stałe'
# Znajdź wiersze zawierające szukany string
mask = daty['data_rozpoczecia'].str.contains(wanted_str, na=False)

# Przenieś do kolumny docelowej i zastąp NULL
daty.loc[mask, 'czy_stale'] = daty.loc[mask, 'data_rozpoczecia']
daty.loc[mask, 'data_rozpoczecia'] = np.nan

df[['data_rozpoczecia',	'data_zakonczenia',	'godzina_rozpoczecia',	'czy_stale']] = daty[['data_rozpoczecia',	'data_zakonczenia',	'godzina_rozpoczecia',	'czy_stale']]
df = df.drop('data_lista', axis=1)



df['data_rozpoczecia'] = pd.to_datetime(df['data_rozpoczecia'], dayfirst=True, errors='coerce')
df['data_zakonczenia'] = pd.to_datetime(df['data_zakonczenia'], dayfirst=True, errors='coerce')

# Pobierz dzisiejszą datę
dzisiaj = datetime.now().date()

# Filtrowanie:
# 1. Wydarzenia, które się jeszcze nie rozpoczęły (data rozpoczęcia > dzisiaj)
# 2. LUB wydarzenia stałe (czy_stale == 'Wydarzenie stałe')
df_filtrowane = df[
    (df['data_rozpoczecia'].dt.date > dzisiaj) |
    (df['czy_stale'] == 'Wydarzenie stałe')
]

# Opcjonalnie: sortowanie po dacie rozpoczęcia
df = df_filtrowane.sort_values(by='data_rozpoczecia', na_position='last')





kategorie = df['typ_wydarzenia_lista']

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



df['czy_na_zewnatrz'] = np.random.randint(0, 2, size=len(df))


df.to_csv('wydarzenia_cleaned.csv', sep = ';', index=False)