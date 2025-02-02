
# 제일 의문의 부분... 왜 이렇게 해놨을까... 우리꺼에선 이렇게까지 설정할 필요가 없을텐데...
# 우선 vocab이 바뀌면 실험 결과가 혹시 달라질 수 있으니까 그대로 놔둬보기..
# 가능하다면 mask, unk 설정 수정하기
class PAVocabulary(object):
    def __init__(self, token_to_idx = None, add_unk = True, mask_token = "<MASK>", unk_token = "<UNK>"):
        if token_to_idx is None:
            token_to_idx = {}
        self._token_to_idx = token_to_idx
        self._idx_to_token = {idx:token for token, idx in self._token_to_idx.items()}
        
        self._add_unk = add_unk
        self._mask_token = mask_token
        self._unk_token = unk_token
        
        self.mask_index = self.add_token(self._mask_token)
        self.unk_index = -1
        if add_unk:
            self.unk_index = self.add_token(self._unk_token)


    def lookup_token(self, token):
        if self.unk_index >= 0:
            return self._token_to_idx.get(token, self.unk_index)
        else:
            return self._token_to_idx[token]

    def lookup_index(self, index):
        if index not in self._idx_to_token:
            raise KeyError("the index (%d) is not in the Vocabulary" %index)
        return self._idx_to_token[index]
    
    def add_token(self, token):
        if token in self._token_to_idx:
            index = self._token_to_idx[token]
        else:
            index = len(self._token_to_idx)
            self._token_to_idx[token] = index
            self._idx_to_token[index] = token
        return index

    def __len__(self):
        return len(self._token_to_idx)