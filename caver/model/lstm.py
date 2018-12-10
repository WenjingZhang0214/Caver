import torch
from torch import nn

from .base import BaseModule
from ..config import ConfigLSTM
from ..utils import update_config


class LSTM(BaseModule):
    """
    :param hidden_dim: hidden layer dimension
    :type hidden_dim: int
    :param layer_num: num of hidden layer
    :type layer_num: int
    :param bidirectional: use bidirectional lstm layer?
    :type bidirectional: bool

    Simpole LSTM model

    text -> embedding -> lstm -> mlp -> sigmoid

    """
    def __init__(self, hidden_dim=100, embedding_dim=100, vocab_size=1000,
                 label_num=100, device="cpu", layer_num=1):
        super().__init__()
        # self.config = update_config(ConfigLSTM(), **kwargs)
        # self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.layer_num = layer_num
        self.bidirectional = True
        self.device = device
        self.hidden_dim = hidden_dim
        self.vocab_size = vocab_size
        self.embedding_dim = embedding_dim
        self.label_num = label_num
        self.embedding = nn.Embedding(self.vocab_size, self.embedding_dim)
        self.lstm = nn.LSTM(embedding_dim, hidden_dim, self.layer_num,
                            batch_first=True,
                            bidirectional=True)
        self.predictor = nn.Linear(hidden_dim*2, label_num)
        # self.sigmoid = nn.Sigmoid()


    def get_args(self):
        return vars(self)


    def update_args(self, args):
        for arg, value in args.items():
            vars(self)[arg] = value


    def init_hidden(self, batch_size):
        return (
            torch.zeros(
                self.layer_num * (2 if self.bidirectional else 1),
                batch_size, self.hidden_dim
            ).to(self.device),

            torch.zeros(
                self.layer_num * (2 if self.bidirectional else 1),
                batch_size, self.hidden_dim
            ).to(self.device)
        )

    def forward(self, sequence):
        # batch_size = sequence.size(0)
        # hidden = self.init_hidden(batch_size)
        embedded = self.embedding(sequence)

        self.lstm.flatten_parameters()
        output, (hidden, cell) = self.lstm(embedded)
        # output_feature = output[-1,:,:]
        output_feature = torch.cat((hidden[-2, :, :], hidden[-1, :, :]), dim=1)
        preds = self.predictor(output_feature)
        return preds
        # label = self.mlp(hidden[0].view(batch_size, -1))
        # return self.sigmoid(label)