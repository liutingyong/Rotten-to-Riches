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
from torch.utils.data import DataSet, DataLoader

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
