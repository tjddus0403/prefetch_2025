from abc import abstractmethod
import bitarray
import util as ut
import sys
from prefetcher_info import *

class Cache:
    def __init__(self, capacity: int, unit, conf):
        self.slots = capacity
        # print("cache slots :", self.slots)
        self.unit = unit # 캐쉬 내 데이터 관리 단위
        self.hits = 0
        self.refs = 0
        self.conf = conf

        # for clstm
        self.prev_miss_cs = []
    
    @abstractmethod
    def access(self, line):
        pass

class LRUCache(Cache):
    def __init__(self, capacity: int, unit, pf, conf):
        super().__init__(capacity, unit, conf)

        # cached data
        self.dlist = []         # LRU list
        self.sorted_dlist = []  # Sorted list

        # prefetch settings
        self.pf = pf
        # self.pf_n = pf.aggressiveness
        self.pf_buff = []       # prefetced data list
        self.pf_buff_slots = int(self.slots * 0.2)
        # print("prefetch buffer slots :", self.pf_buff_slots)
        self.pf_hits = 0

        # bitmap
        self.bitmap = {}
        self.touched_list = []

        # distance
        self.distance = []
        self.pf_hit_distance = []
        self.pf_miss_distance = []
        self.miss_lpn = []
        self.closest_rank = []
        self.miss_closest_rank = []

    def reset(self):
        self.hits = 0
        self.refs = 0

        self.dlist.clear()
        self.sorted_dlist.clear()
        
        self.pf_buff.clear()
        self.pf_hits = 0

        self.distance.clear()
        self.pf_hit_distance.clear()
        self.pf_miss_distance.clear()
        self.miss_lpn.clear()
        self.closest_rank.clear()
        self.miss_closest_rank.clear()

        # leap의 경우, 이전 기록을 가지고 있기 때문에 trace가 바뀔 때, 초기화 필요
        if self.pf.code == LEAP:
            self.pf.reset_()

    def stats(self):
        stat = f"cache_size = {self.slots} \npf_buff_size = {self.pf_buff_slots} \ntotal_refs = {self.refs} \nhits = {self.hits} \npf_hits = {self.pf_hits} \nhit_ratio = {self.hits/self.refs} \nhit_ratio_pf = {(self.hits+self.pf_hits)/self.refs}"
        print(stat)
        return
    
    def access(self, addr):
        self.refs += 1
        addr = int(addr)
        # is_hit = 0
        # is_pf_hit = 0

        lpn = addr // self.unit # 16KB 페이지 단위로 프리페치
        
        # best offset
        if self.pf.code == BO:
            self.pf.learn(lpn)

        # clstm
        if self.pf.code == CLSTM:
            pf_clstm = self.pf.prefetch(int(lpn))
            for pd in pf_clstm:
                pd = int(pd)
                if pd not in self.pf_buff and pd not in self.dlist:
                    self.pf_buff.append(pd)
                if len(self.pf_buff) > self.pf_buff_slots:
                    self.pf_buff.pop(0)
        # read-ahead
        if self.pf.code == RA:
            # 저장된 마지막 접근 page가 없을 경우 
            if self.pf.prev_page < 0:
                self.pf.readahead_on = 1
                self.pf.prev_page = lpn # 마지막 접근 page 저장

            # 마지막으로 접근했던 page가 있을 경우
            else:
                # sequential access -> read-ahead on 상태.
                # agressiveness 증가
                # random->sequential인 경우
                # agressiveness 4에서 시작
                if lpn == self.pf.prev_page + 1:
                    if self.pf.readahead_on:
                        self.pf.aggressControl("seq")
                    
                    else:
                        self.pf.readahead_on = 1
                    
                # random access -> read-ahead off
                else:
                    self.pf.readaheadOff()

        # hit
        if lpn in self.dlist:
            self.dlist.remove(lpn)
            self.dlist.insert(0, lpn) # MRU position: head
            self.hits += 1

            if self.pf.code == RA:
                self.pf.hit_counter += 1
                # 연속해서 hit 256번 발생했을 때 read-ahead 끔
                if self.pf.hit_counter == 256:
                    self.pf.readaheadOff() 
        
        # miss
        else:
            # prefetch hit
            if lpn in self.pf_buff:
                self.pf_buff.remove(lpn)
                self.pf_hits += 1
            
                if self.pf.code == RA:
                    self.pf.hit_counter += 1
                    # 연속해서 hit 256번 발생했을 때 read-ahead 끔
                    if self.pf.hit_counter == 256:
                        self.pf.readaheadOff()

            # # prefetch miss
            else:
                if self.pf.code == RA:
                    # dlist, pf_buff 모두 miss일 때 hit counter = 0
                    self.pf.hit_counter = 0

            self.miss_lpn.append(lpn)
            # replacement
            if len(self.dlist) == self.slots:
                evicted_lpn = self.dlist.pop(-1)
                
            # insert accessed data into cache
            self.dlist.insert(0, lpn)

            if self.pf.code == LEAP:
                self.pf.history_insert(lpn)
                self.pf.find_offset()
                self.pf.set_aggressiveness(self.pf_hits)

            if self.pf.code == RA:
                self.pf.prev_page = lpn
            
            if self.pf.code == CLSTM:
                self.pf.leap.history_insert(lpn)
                self.pf.leap.find_offset()
                self.pf.leap.set_aggressiveness(self.pf_hits)
                pf_data = self.pf.leap.prefetch(int(lpn))
            else:
                pf_data = self.pf.prefetch(int(lpn))

            for pd in pf_data:
                if pd not in self.pf_buff and pd not in self.dlist:
                    self.pf_buff.append(pd)
                if len(self.pf_buff) > self.pf_buff_slots:
                    self.pf_buff.pop(0) # FIFO

                    # memory pressure 시, read-ahead 크기 조절
                    if self.pf.code == RA:
                        self.pf.aggressControl("mp")

        return