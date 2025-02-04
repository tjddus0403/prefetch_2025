import pandas as pd
import numpy as np
import random
import lzma
import os

random.seed(1234)

PAGE_SIZE = 1 << 21

folder_path = "./ChampSim_trace/"

trace_list = ['astar']

def make_pagetable(unique_vn, pp_num):
    pn_candidate = random.sample(range(pp_num), len(unique_vn))
    page_table=pd.DataFrame({'vn':list(unique_vn), 'pn':pn_candidate})
    return page_table

def v2p(page_table, va_trace):
    trace_list = []
    trace_df = pd.DataFrame()
    for i, va in enumerate(va_trace):
        vpn = va // PAGE_SIZE
        idx = va % PAGE_SIZE
        ppn = page_table[page_table['vn']==vpn].iloc[0]['pn']
        pa = ppn * PAGE_SIZE + idx
        trace_list.append({'va':va, 'pa':pa})
    trace_df = pd.DataFrame(trace_list)
    return trace_df

def get_vaddr(file_path):
    addrs = []
    if file_path.endswith('.txt.xz'):
        with lzma.open(file_path, mode='rt', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if i == 5000000:
                    break
                if line.startswith('***') or line.startswith('Read'):
                    continue
                split = line.strip().split(', ')
                inst_id, pc, addr = int(split[0]), int(split[3], 16), int(split[2], 16)
                addrs.append(addr)
    return addrs

for trace in trace_list:
    prefix = trace+"-"
    for file in os.listdir(folder_path):
        if file.startswith(prefix):  
            file_path = os.path.join(folder_path, file)
            va_df = pd.DataFrame({'va':get_vaddr(file_path)})
            va_df.to_csv("./vaddr/"+trace+"_5m.vaddr", index=False, header=False)
            va_trace = va_df['va']
            va_range = {"min":va_df.min()['va'], "max":va_df.max()['va']}
            VIRTUAL_ADDRESS_SPACE_SIZE = va_range['max'] - va_range['min'] + 1
            PHYSICAL_ADDRESS_SPACE_SIZE = VIRTUAL_ADDRESS_SPACE_SIZE * 4
            V_PAGE_NUM = VIRTUAL_ADDRESS_SPACE_SIZE // PAGE_SIZE
            P_PAGE_NUM = PHYSICAL_ADDRESS_SPACE_SIZE // PAGE_SIZE

            unique_va = list(set(va_trace))
            ununique_vn = list(x//PAGE_SIZE for x in unique_va)
            unique_vn = set(ununique_vn)

            pg_tb = make_pagetable(unique_vn, P_PAGE_NUM)
            v2p_result = v2p(pg_tb, va_trace)

            paddr_file = "./paddr/"+trace+"/"+trace+"_5m.paddr"
            v2p_result['pa'].to_csv(paddr_file, index=False, header=False)
            print("Finished v2p : ", paddr_file)