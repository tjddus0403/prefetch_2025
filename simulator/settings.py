class Settings:
    def __init__(self, obj=None):
        if obj is None:
            # 트레이스 설정
            self.dir = "./traces/paddr/bc/"
            self.files = ["bc_1m_tail"]
            self.trc = "paddr"
            
            self.clstm_result = "../results/bc_test_result_addr.csv"

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
            self.cluster_size = obj.cluster_sifze