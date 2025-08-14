#lstm: reads embeddings sequentially
#forget gate: decides what to forget
#input gate: decides what to add to the cell state
#output gate: decides what to output
#cell state: carries information across time steps

#has a final hidden state that represents an entire sentence's meaning

#going to train it on a large labeled dataset (imdb reviews), then we can feed all of our articles and average them?
#or do we just want to train on the articles? won't be very accurate bc we dont have many

#pip install torch
import torch 
import torch.nn as nn
from torch.utils.data import DataSet, DataLoader

#we will used pretrained embeddings because we don't have enough data to train our own
#use GloVe
#potential homework: train your own embeddings with movie reviews dataset
#maybe even webscrape a review website like imdb/rottentomatoes to train your own embeddings

