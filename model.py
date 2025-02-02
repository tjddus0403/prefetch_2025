import torch.nn as nn
from torch.nn import functional as F
import torch

class Attention(nn.Module):
    def __init__(self, hidden_size):
        super(Attention, self).__init__()
        self.hidden_size = hidden_size
        self.attn_fc = nn.Linear(in_features=hidden_size, out_features=1)
    
    def forward(self, x):
        # print(x.shape)
        x = self.attn_fc(x)
        # print(x.shape)
        x = F.softmax(x, dim=1)
        # print(x.shape)
        return x
    
class Prefetcher(nn.Module):
    def __init__(self, args, vocab_size):
        super(Prefetcher, self).__init__()
        self.embedding = nn.Embedding(num_embeddings=vocab_size,
                                      embedding_dim=args.embedding_size)
        self.lstm = nn.LSTM(input_size = args.embedding_size,
                            hidden_size=args.encoding_size,
                            num_layers=2,
                            batch_first=True,
                            bidirectional=True,
                            dropout=0.1)
        self.attention = Attention(args.encoding_size*2)
        self.fc2 = nn.Linear(in_features=args.max_len, out_features=vocab_size)
        self.softmax = nn.LogSoftmax()

    def forward(self, x):
        # torchinfo summary 사용 시, long으로 직접 변경해주어야 함
        # x = x.long()
        # print("input :", x.shape)
        x = self.embedding(x)
        # print("after embbeding :", x.shape)
        output, hidden = self.lstm(x)
        # print("after lstm :", output.shape)
        attn_weights = self.attention(output)
        # print("attn weights :", attn_weights.shape)
        attn_output = output * attn_weights
        # print("after attention :", attn_output.shape)
        attn_output = torch.sum(attn_output, dim=-1)
        # print("after attention :", attn_output.shape)
        x = self.fc2(attn_output)
        # print("after fc :", x.shape)
        x = self.softmax(x)
        # print("after softmax :", x.shape)
        x = x.squeeze()
        # print("after sqz :", x.shape)
        return x