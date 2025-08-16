#lstm: reads embeddings sequentially
#forget gate: decides what to forget
#input gate: decides what to add to the cell state
#output gate: decides what to output
#cell state: carries information across time steps

#has a final hidden state that represents an entire sentence's meaning

#going to train it on a large labeled dataset (imdb reviews), then we can feed all of our articles and average them?
#or do we just want to train on the articles? won't be very accurate bc we dont have many

#pip install torch
import io
import os
from collections import Counter
import torch 
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

#we will used pretrained embeddings because we don't have enough data to train our own
#use GloVe
#potential homework: train your own embeddings with movie reviews dataset
#maybe even webscrape a review website like imdb/rottentomatoes to train your own embeddings

specials = ["<pad>", "<unk>"]
pad_idx = 0
unk_idx = 1


def build_vocab(tokenized_texts, max_vocab=30000, min_freq=1, lowercase=True):
    counter = Counter()
    for text in tokenized_texts:
        if lowercase:
            text = [word.lower() for word in text]
        counter.update(text)
    most_common = [w for w, c in counter.items() if c >= min_freq]
    most_common = sorted(most_common, key=lambda x: -counter[x])[:max_vocab-len(specials)]
    index_to_string = specials + most_common
    string_to_index = {s: i for i, s in enumerate(index_to_string)}
    return index_to_string, string_to_index

#make it into a txt to use in pytorch
def load_glove_txt(path, dim, lower_case=True):
    vecs={}
    with io.open(path, 'r', encoding='utf-8', newline='\n', errors='ignore') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) != dim + 1:
                continue
            word = parts[0]
            if lower_case:
                word = word.lower()
            vals = torch.tensor(list(map(float, parts[1:])), dtype=torch.float32)
            vecs[word]=vals
    return vecs

def make_embedding_matrix(itos, stoi, pretrained, dim, pad_idx=0, unk_idx=1):
    V=len(itos)
    embedding_matrix = torch.randn(V, dim) * 0.1
    embedding_matrix[pad_idx].zero_()
    hit = 0
    for w, i in stoi.items():
        if i in (pad_idx, unk_idx):
            continue
        if w in pretrained:
            embedding_matrix[i] = pretrained[w]
            hit += 1
    coverage = hit / (V - len(specials))
    if unk_idx is not None & len(pretrained) > 0:
        embedding_matrix[unk_idx] = torch.stack(list(pretrained.values)).mean(dim=0)
    return embedding_matrix, coverage

def ids_from_tokens(tokens, stoi, lowercase=True):
    if lowercase:
        tokens = [t.lower() for t in tokens]
    return [stoi.get(t, unk_idx) for t in tokens]

def pad_truncate(ids, L, pad_idx=0):
    if len(ids) > L:
        return ids[:L]
    else:
        return ids + [pad_idx] * (L - len(ids))
    
class SentDataset(Dataset):
    def __init__(self, tokenized_texts, labels, stoi, L=200):
        self.x=[pad_truncate(ids_from_tokens(text, stoi), L) for text in tokenized_texts]
        self.y = labels
        self.L = L

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, i):
        return torch.tensor(self.x[i], dtype=torch.long), torch.tensor(self.y[i], dtype=torch.float32)
    
class BiLSTMClassifier(nn.Module):
    def __init__(self, embedding_layer, hidden=128, num_layer=1, bidir=True, dropout=0.3):
        super().__init__()
        self.embedding = embedding_layer
        self.lstm = nn.LSTM(self.embedding.embedding_dim, hidden, num_layers=num_layer, batch_first=True, bidirectional=bidir)
        self.dropout = nn.Dropout(dropout)
        out_dim = hidden * 2 if bidir else hidden
        self.fc = nn.Linear(out_dim, 1)

    def forward(self, x):
        emb = self.embedding(x)
        out, (h, c) = self.lstm(emb)
        if self.lstm.bidirectional:
            h_last = torch.cat([h[-2], h[-1]], dim=1)
        else:
            h_last = h[-1]
        h_last = self.dropout(h_last)
        logit = self.fc(h_last).squeeze(1)
        return logit

def build_model_with_pretrained(train_tokens, val_tokens, y_train, y_val, glove_path, seq_len=200, dim=100,
                                batch_size=64, freeze_embeddings=True, device=None):
    device = device or ("cuda" if torch.cuda.is_available() else "cpu")
    #vocab
    itos, stoi = build_vocab(train_tokens, max_vocab=30000, min_freq=1, lowercase=True)
    #load vectors
    glove = load_glove_txt(glove_path, dim=dim, lower_case=True)
    #embedding matrix
    weight = make_embedding_matrix(itos, stoi, glove, dim, pad_idx=pad_idx, unk_idx=unk_idx)
    embedding = nn.Embedding.from_pretrained(weight, freeze=freeze_embeddings, padding_idx=pad_idx)
    #datasets
    train_dataset = SentDataset(train_tokens, y_train, stoi, L=seq_len)
    val_dataset = SentDataset(val_tokens, y_val, stoi, L=seq_len)
    train_dl = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_dl = DataLoader(val_dataset, batch_size=batch_size)
    #model
    model = BiLSTMClassifier(embedding_layer=embedding, hidden=128, num_layer=1, bidir=True, dropout=0.3).to(device)
    criterion = nn.BCEWithLogitsLoss() #loss function
    optimizer = torch.optim.Adam((filter(lambda p: p.requires_grad, model.parameters())), lr=2e-3)

    #training loop