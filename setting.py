import torch
from argparse import Namespace
import numpy as np
import pandas as pd
import os

trace = "bc"

args = Namespace(
    # seed num
    seed = 1337,
    # cstate 파일의 라인 수를 Dataset클래스에서 사용 
    data_cstate_len = int(os.popen(f"wc -l ./data/raw/{trace}_4m.cstate").read().split()[0]),
    train_cstate_len = int(os.popen(f"wc -l ./data/raw/{trace}_3m.cstate").read().split()[0]),
    # 데이터셋 주소 설정
    dataset_csv = f"./data/csv/{trace}_train.csv",
    vocabset_csv = f"./data/csv/{trace}_vocab.csv",
    testset_csv = f"./data/csv/{trace}_test.csv",
    # model hyperparams
    batch_size = 64,
    lr = 5e-4,
    num_epoch = 20,
    embedding_size = 64,
    encoding_size = 32,
    max_len = 128,
    # env
    cuda = True,
    device = 'cuda'
)

def set_seed_everywhere(seed, cuda):
    np.random.seed(seed)
    torch.manual_seed(seed)
    if cuda:
        torch.cuda.manual_seed_all(seed)

def load_data(data):
    df = pd.DataFrame()
    if data == "train/val":
        df = pd.read_csv(args.dataset_csv)
    elif data == "vocab":
        df = pd.read_csv(args.vocabset_csv)
    elif data == "test":
        df = pd.read_csv(args.testset_csv)
    df['label'] = df['label'].astype(str)
    # train.py에서 데이터프레임 반환 받아서 사용해야 하므로 데이터프레임을 리턴
    return df