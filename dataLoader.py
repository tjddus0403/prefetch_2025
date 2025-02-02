from torch.utils.data import Dataset, DataLoader
from vectorizer import *

class CstateDataset(Dataset):
    def __init__(self, cstate_df, vectorizer, vocabset_df, testset_df, train_sz, val_sz):
        self.cstate_df = cstate_df
        self.vectorizer = vectorizer

        self.train_size = train_sz
        self.train_df = self.cstate_df.loc[:self.train_size]

        self.val_size = val_sz
        self.val_df = self.cstate_df.loc[self.train_size:self.train_size+self.val_size] # 일단 tr_sz+vl_sz 해두긴 했는데, 사실상 끝 아닌가
        
        self.test_size = len(testset_df)
        self.test_df = testset_df

        self.vocab_size = len(vocabset_df)
        self.vocab_df = vocabset_df
        
        self._lookup_dict = {'train' : (self.train_df, self.train_size),
                             'val' : (self.val_df, self.val_size),
                             'test' : (self.test_df, self.test_size),
                             'vocab' : (self.vocab_df, self.vocab_size)}
        
        self.set_split('vocab')

    @classmethod
    def load_dataset_and_make_vectorizer(cls, cstate_df, vocabset_df, testset_df, train_sz, val_sz):
        vectorizer = PAVectorizer.from_dataframe(vocabset_df)
        return cls(cstate_df, vectorizer, vocabset_df, testset_df, train_sz, val_sz)
    
    def get_vectorizer(self):
        return self.vectorizer
    
    def set_split(self, split='train'):
        self._target_df, self._target_size = self._lookup_dict[split]

    def __getitem__(self, index):
        row = self._target_df.iloc[index]
        pa_vector = self.vectorizer.vectorize(row.pa)
        label_vector = self.vectorizer.vectorize(row.label)

        return {'x_data':pa_vector['pa_vector'],
                'y_target':label_vector['pa_vector'],
                'x_data_length':pa_vector['pa_length']}
    
    def get_num_batches(self, batch_size):
        return len(self) // batch_size
    
    def __len__(self):
        return self._target_size

def generate_batches(dataset, batch_size, shuffle=False, drop_last=True, device='cpu'):
    dataloader = DataLoader(dataset=dataset, batch_size=batch_size, shuffle=shuffle, drop_last=drop_last)
    for data_dict in dataloader:
        out_data_dict={}
        for name, tensor in data_dict.items():
            out_data_dict[name] = data_dict[name].to(device)
        yield out_data_dict