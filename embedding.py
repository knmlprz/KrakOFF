import pandas as pd
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModel

# Wczytaj dane
df = pd.read_csv('./data_events/events_tiktak.csv', sep=';')
df['hashtagi'] = df['hashtagi'].astype(str).fillna('')

# Sparsuj hashtagi do listy słów (usunąć # i podzielić po spacji)
df['hashtag_list'] = df['hashtagi'].apply(lambda x: x.strip().replace('#', '').split())

# Wczytaj tokenizer i model
model_name = 'sentence-transformers/paraphrase-multilingual-mpnet-base-v2'
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)
model.eval()  # wyłącz dropout
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model.to(device)

# Mean pooling function
def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output.last_hidden_state  # [batch, seq_len, hidden_size]
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, dim=1) / torch.clamp(input_mask_expanded.sum(dim=1), min=1e-9)

# Funkcja: embedding średni z listy hashtagów
def get_avg_embedding(hashtags):
    if not hashtags:
        return np.zeros(model.config.hidden_size)
    text_batch = hashtags
    inputs = tokenizer(
        text_batch,
        padding=True,
        truncation=True,
        return_tensors='pt'
    ).to(device)

    with torch.no_grad():
        model_output = model(**inputs)
        embeddings = mean_pooling(model_output, inputs['attention_mask'])
    
    return embeddings.mean(dim=0).cpu().numpy()  # średnia embeddingów hashtagów

# Zastosuj dla każdego wiersza
df['embedding'] = df['hashtag_list'].apply(get_avg_embedding)

# Sprawdź wynik
print(df[['hashtagi', 'embedding']].head())
