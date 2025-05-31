#!/usr/bin/env python3

import pandas as pd
import numpy as np
from lightgbm import LGBMRegressor
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers import SentenceTransformer
from sklearn.preprocessing import normalize

# === 1. Wczytanie danych ===
df = pd.read_csv("events_tiktak.csv")

# Przykładowe dane interakcji — jeśli nie masz, wygeneruj jak wcześniej
df["likes"] = np.random.poisson(50, len(df))
df["info_clicks"] = np.random.poisson(20, len(df))
df["shares"] = np.random.poisson(10, len(df))
df["watch_time"] = np.random.gamma(2, 30, len(df)).astype(int)
df["saves"] = np.random.poisson(5, len(df))

# Oblicz score
def compute_score(likes, info_clicks, shares, watch_time, saves):
    return (
        1.0 * likes +
        0.8 * info_clicks +
        0.6 * shares +
        0.4 * watch_time +
        0.2 * saves
    )

df["score"] = df.apply(lambda row: compute_score(
    row.likes, row.info_clicks, row.shares, row.watch_time, row.saves
), axis=1)

# === 2. Przygotowanie cech ===

# Model do embeddingu tekstu posta
text_model = SentenceTransformer('all-MiniLM-L6-v2')

# Zakładamy, że tekstem posta jest kolumna 'tytul'
df['post_embedding'] = df['tytul'].apply(lambda text: text_model.encode(text))

# Hashtagi są w formacie stringu "#a #b #c"
# Rozdziel na osobne hashtagi
df_exploded = df.copy()
df_exploded["hashtagi"] = df_exploded["hashtagi"].fillna("")
df_exploded = df_exploded.assign(hashtag=df_exploded["hashtagi"].str.split()).explode("hashtagi")
df_exploded["hashtag"] = df_exploded["hashtagi"]

# TF-IDF na hashtagach (proste podejście)
vectorizer = TfidfVectorizer(analyzer='char_wb', ngram_range=(2, 4))
vectorizer.fit(df_exploded["hashtag"])
hashtag_embeddings = vectorizer.transform(df_exploded["hashtag"])
hashtag_embeddings = normalize(hashtag_embeddings)

# Przekształć embeddingi do tablicy
post_embeddings = np.vstack(df_exploded["post_embedding"].values)

# Połącz cechy: [tekst posta | hashtag]
X = np.hstack((post_embeddings, hashtag_embeddings.toarray()))
y = df_exploded["score"].values

# === 3. Podział na zbiór treningowy/testowy ===
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# === 4. Trening modelu ===
model = LGBMRegressor()
model.fit(X_train, y_train)

# === 5. Rekomendacja hashtagów ===
def get_text_embedding(text):
    return text_model.encode(text)

def get_hashtag_embedding(tag):
    return vectorizer.transform([tag]).toarray()[0]

def combine_embeddings(post_emb, tag_emb):
    return np.hstack((post_emb, tag_emb))

def recommend_hashtags(post_text, candidate_hashtags, model, top_n=5):
    post_embedding = get_text_embedding(post_text)
    predictions = []
    for tag in candidate_hashtags:
        tag_embedding = get_hashtag_embedding(tag)
        features = combine_embeddings(post_embedding, tag_embedding)
        score = model.predict([features])[0]
        predictions.append((tag, score))
    return sorted(predictions, key=lambda x: x[1], reverse=True)[:top_n]
