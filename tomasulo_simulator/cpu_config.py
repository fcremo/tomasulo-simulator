DEFAULT_GP_REGISTERS = 16
DEFAULT_FP_REGISTERS = 8
DEFAULT_CDB_WIDTH = 1

DEFAULT_ALU_RS = 1
DEFAULT_ALU_FU = 1
DEFAULT_ALU_LATENCY = 1

DEFAULT_FPALU_RS = 1
DEFAULT_FPALU_FU = 1
DEFAULT_FPALU_LATENCY = 3

DEFAULT_MEM_RS = 1
DEFAULT_MEM_FU = 1
DEFAULT_MEM_LATENCY = 4
DEFAULT_MEM_ACCESS_QUEUE_SIZE = 2
DEFAULT_MEM_SIZE = 0x50

DEFAULT_FETCH_LATENCY = 1


class CpuConfig:
    def __init__(self, directives={}):
        # TODO: delete *rs_execution_latency
        self.gp_registers = DEFAULT_GP_REGISTERS
        self.fp_registers = DEFAULT_FP_REGISTERS
        self.cdb_width = DEFAULT_CDB_WIDTH
        self.alu_rs = DEFAULT_ALU_RS
        self.alu_fu = DEFAULT_ALU_FU
        self.alurs_execution_latency = DEFAULT_ALU_LATENCY
        self.alufu_execution_latency = DEFAULT_ALU_LATENCY
        self.fpalu_rs = DEFAULT_FPALU_RS
        self.fpalu_fu = DEFAULT_FPALU_FU
        self.fpalurs_execution_latency = DEFAULT_FPALU_LATENCY
        self.fpalufu_execution_latency = DEFAULT_FPALU_LATENCY
        self.mem_rs = DEFAULT_MEM_RS
        self.mem_fu = DEFAULT_MEM_FU
        self.memrs_execution_latency = DEFAULT_MEM_LATENCY
        self.memfu_execution_latency = DEFAULT_MEM_LATENCY
        self.mem_access_queue_size = DEFAULT_MEM_ACCESS_QUEUE_SIZE
        self.mem_size = DEFAULT_MEM_SIZE
        self.fetch_latency = DEFAULT_FETCH_LATENCY

        self.apply_config(directives)

    def apply_config(self, directives):
        for k, v in directives.items():
            if k not in self.__dict__:
                raise Exception("Unknown directive: {}".format(k))
            self.__dict__[k] = v

    def __getattr__(self, item):
        if item.endswith("_execution_latency"):
            return self.__dict__.get(item, None)
        else:
            return self.__dict__[item]

    def __getitem__(self, item):
        return self.__getattr__(item)
