from collections import Counter
from vocabulary import *
import numpy as np

class PAVectorizer(object):
    def __init__(self, pa_vocab):
        self.pa_vocab = pa_vocab

    def _get_pa_indices(self, pa_list):
        indices = [self.pa_vocab.lookup_token(token) for token in pa_list.split(" ")]
        return indices
    
    def _vectorize(self, indices):
        vector_len = len(indices)
        vector = np.zeros(vector_len, dtype=np.int64)
        vector[:len(indices)] = indices
        return vector

    def vectorize(self, cstate):
        pa_indices = self._get_pa_indices(cstate)
        pa_vector = self._vectorize(indices=pa_indices)
        return {'pa_vector':pa_vector,
                'pa_length':len(pa_indices)}

    @classmethod
    def from_dataframe(cls, cstate_df):
        pa_vocab = PAVocabulary()
        pa_counts = Counter()
        for cstate in cstate_df.pa:
            for pa in cstate.split(" "):
                pa_counts[pa] += 1
        for cstate in cstate_df.label:
            pa_counts[cstate] += 1

        for pa, count in pa_counts.items():
            if count >= 1 : # cufoff = 1
                pa_vocab.add_token(pa)
        
        print("Size of vocab:", len(pa_vocab))
        return cls(pa_vocab)