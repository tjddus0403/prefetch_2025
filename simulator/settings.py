class Settings:
    def __init__(self, obj=None):
        if obj is None:
            # 데이터 수집용
            self.collect = True
            
            # 트레이스 설정
            TRACE = "sssp"
            self.dir = f"./traces/paddr/{TRACE}/"
            self.files = [f"{TRACE}_1m_tail"]
            self.trc = "paddr"
            
            self.clstm_result = f"../results/clstm_leap/{TRACE}_test_result_addr.csv"
            self.seq_result = f"../results/seq_leap/{TRACE}_test_result_addr.csv"
            self.only_clstm_result = f"../results/clstm_only/{TRACE}_test_result_addr.csv"
            self.only_seq_result = f"../results/seq_only/{TRACE}_test_result_addr.csv"
            self.delta_result = f"../results/delta/{TRACE}_test_result_addr.csv"

            # 단위 설정
            self.page_size = (1 << 14) # page size (16KB)
            self.line_size = (1 << 6) # line size
            self.cluster_size = (1 << 10) # 1024 pages

        else:
            self.dir = obj.dir
            self.files = obj.files
            self.trcs = obj.trcs
            
            self.page_size = obj.page_size
            self.line_size = obj.line_size
            self.cluster_size = obj.cluster_size