.mem_rs 2
.mem_fu 2
.memrs_execution_latency 4
.alu_rs 2
.alu_fu 2
.alurs_execution_latency 2
.cdb_width 1

LD R6, [R2 + 32]
FADD R2, R6, R4
FADD R0, R4, R2
FSUB R7, R2, R6
ADD R0, R7, R2