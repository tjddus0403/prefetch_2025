from prefetcher_info import *
import settings as st
import pandas as pd
import prefetcher as pf
import sys
import cache as cc

def get_pf(choice):
    if choice == PF_NONE:
        prefetcher = pf.NonePrefetcher()
    elif choice == PF_NLINE:
        prefetcher = pf.NLinePrefetcher()
    elif choice == PF_LEAP:
        prefetcher = pf.LeapPrefetcher()
    else:
        print("Wrong choice for prefetcher")
        sys.exit()
    
    return prefetcher

def _cache_sim(cache):
    choice = int(sys.argv[1])

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
    
    prefetcher = get_pf(choice)
    cache = cc.LRUCache(slots, conf.page_size, prefetcher, conf)
    _cache_sim(cache)

if __name__ == "__main__":
    cache_sim()
