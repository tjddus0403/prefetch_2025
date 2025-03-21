from prefetcher_info import *
import settings as st
import pandas as pd
import prefetcher as pf
import sys
import cache as cc

def get_pf(choice, conf):
    if choice == PF_NONE:
        prefetcher = pf.NonePrefetcher()
    elif choice == PF_NLINE:
        prefetcher = pf.NLinePrefetcher()
    elif choice == PF_LEAP:
        prefetcher = pf.LeapPrefetcher()
    elif choice == PF_CLSTM:
        prefetcher = pf.CLSTMPrefetcher(conf.clstm_result)
    elif choice == PF_BO:
        prefetcher = pf.BestOffsetPrefetcher()
    elif choice == PF_RA:
        prefetcher = pf.LinuxReadAhead()
    elif choice == PF_ONLYC:
        prefetcher = pf.OnlyCstateOrSeq(conf.only_clstm_result)
    elif choice == PF_ONLYS:
        prefetcher = pf.OnlyCstateOrSeq(conf.only_seq_result)
    elif choice == PF_DELTA:
        prefetcher = pf.DeltaLSTM(conf.delta_result)
    elif choice == PF_SEQ:
        prefetcher = pf.SeqPrefetcher(conf.seq_result)
    else:
        print("Wrong choice for prefetcher")
        sys.exit()
    
    return prefetcher

def _cache_sim(cache):
    for f in cache.conf.files:
        filename = cache.conf.dir + f + "." + cache.conf.trc
        cache.reset()
        
        with open(filename, 'r') as df:
            addr = df.readline()
            while addr:
                cache.access(addr)
                addr = df.readline()
        
        print("prefetcher :", cache.pf.code, "\ntrace :", f)
        cache.stats()

def cache_sim():
    if len(sys.argv) > 1:
        choice = int(sys.argv[1])
    else:
        choice = PF_NONE
    
    # Cache settings
    conf = st.Settings()
    capacity = 1 << 21      # 2MB
    slots = capacity / conf.page_size
    
    prefetcher = get_pf(choice, conf)
    cache = cc.LRUCache(slots, conf.page_size, prefetcher, conf)
    _cache_sim(cache)

if __name__ == "__main__":
    cache_sim()
