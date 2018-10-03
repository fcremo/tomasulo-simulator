.mem_rs 2
.mem_fu 2
.memrs_execution_latency 4
.alu_rs 2
.alu_fu 2
.alurs_execution_latency 2
.cdb_width 1

LD R6, [R2 + 32]
FADD F2, F6, F4
FADD F3, F4, F2
FSUB F7, F2, F6
ADD R3, R7, R2