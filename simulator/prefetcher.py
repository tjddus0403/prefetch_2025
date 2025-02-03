import math
from prefetcher_info import *

class NonePrefetcher:
    def __init__(self, n = 3):
        self.code = NONE
        self.aggressiveness = n

    def prefetch(self, lpn: int):
        return []
    
class NLinePrefetcher:
    def __init__(self, n = 3):
        self.code = NLINE
        self.aggressiveness = n
        self.granularity = 1
        self.prefetch_offset = 1

    def prefetch(self, lpn: int):
        fetched_data = []
        _lpn = lpn + self.prefetch_offset
        for n in range(1, self.aggressiveness+1):
            fetched_data.append(_lpn)
            _lpn += self.granularity
        return fetched_data
    
class LeapPrefetcher:
    def __init__(self):
        self.code = LEAP
        self.aggressiveness = 1     # dynamic
        self.granularity = 1
        self.prefetch_offset = 1    # dynamic
        
        self.init_amount = 1
        self.lastprefetchamount = 0
        self.lastprefetchhit = 0
        self.last_offset = 1

        self.maxprefetchamount = 8
        self.maxbuffersize = 32
        self.splitvalue = 8

        self.hbuffer = []           # trend detect & aggressiveness

    # hbuffer에 기록
    def history_insert(self, addr):
        # hbuffer에 이전 기록이 없는 경우, 델타값 0 설정 후 hbuffer에 넣음
        if len(self.hbuffer) == 0:
            self.hbuffer.append([addr, 0])
            return
        # hbuffer에 이전 기록이 있는 경우, 직전 주소 꺼낸 후 현재 주소와의 델타값 계산
        prev = self.hbuffer[-1]
        delta = addr - prev[0]
        # 해당 델타값으로 hbuffer에 넣음
        self.hbuffer.append([addr, delta])
        # hbuffer size가 max를 넘은 경우, 가장 오래된 정보부터 삭제
        if len(self.hbuffer) > self.maxbuffersize:
            del self.hbuffer[0]

    # Trend detect
    def find_offset(self):
        wsize = int(len(self.hbuffer) / self.splitvalue)
        delta = 0

        while True:
            iter_idx = len(self.hbuffer) - (wsize+1)

            # boyer-moore algorithm
            candidate = 0
            vote = 0
            iter_idx2 = iter_idx
            while iter_idx2 != len(self.hbuffer)-1:
                if vote == 0:
                    candidate = self.hbuffer[iter_idx2][-1]
                if self.hbuffer[iter_idx2][-1] == candidate:
                    vote+=1
                else:
                    vote-=1
                iter_idx2+=1

            count = 0
            while iter_idx != len(self.hbuffer)-1:
                if self.hbuffer[iter_idx][-1] == candidate:
                    count+=1
                iter_idx+=1
            
            if count > int(wsize / 2):
                delta = candidate
            wsize = 2*wsize+1

            if delta != 0 or wsize > len(self.hbuffer) or wsize == 0:
                self.prefetch_offset = delta
                if self.prefetch_offset == 0:
                    self.prefetch_offset = self.last_offset
                return
            
    def set_aggressiveness(self, pref_hit_count):
        pref_amount = 0
        if pref_hit_count-self.lastprefetchhit == 0:
            pref_amount = self.init_amount
        else:
            pref_amount = 2**(math.ceil(math.log2(pref_hit_count-self.lastprefetchhit+1)))
        
        if pref_amount > self.maxprefetchamount:
            pref_amount = self.maxprefetchamount
        if pref_amount < int(self.lastprefetchamount / 2):
            pref_amount = int(self.lastprefetchamount / 2)

        self.lastprefetchhit = pref_hit_count
        self.lastprefetchamount = pref_amount
        self.aggressiveness = pref_amount

    def reset_(self):
        self.lastprefetchamount = 0
        self.lastprefetchhit = 0
        self.last_offset = 1
        self.prefetch_offset = 1
        self.aggressiveness = 1
        self.hbuffer = []

    def prefetch(self, lpn: int):
        fetched_data = []
        _lpn = lpn + self.prefetch_offset
        for n in range(1, self.aggressiveness+1):
            fetched_data.append(_lpn)
            _lpn += self.granularity * self.prefetch_offset
        return fetched_data

# class CLSTMPrefetcher:
#     def __init__(self):
#         self.code = CLSTM

#     def prefetch(self, lpn: int):
