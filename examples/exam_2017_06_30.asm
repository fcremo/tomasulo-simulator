# Please consider the program in the table be executed on a CPU with dynamic scheduling based on TOMASULO algorithm with:
# 2 RESERVATION STATIONS (RS1, RS2) + 2 LOAD/STORE unit (LDU1, LDU2) with latency 4
# 2 RESERVATION STATIONS (RS3, RS4) + 2 ALU/BR FUs (ALU1, ALU2) with latency 2
# We assume 1 CDB for RF
# Static Branch Prediction ALWAYS TAKEN with Branch Target Buffer
# Please complete the TOMASULO TABLE by assuming all cache HITS and considering ONE ITERATION:
# Results differ from the exam because of the way memory consistency is guaranteed

.mem_rs 2
.mem_fu 2
.memrs_execution_latency 4
.alu_rs 2
.alu_fu 2
.alurs_execution_latency 2
.cdb_width 1

.const !VECTA 0
.const !VECTB 20

FOR:
    LD R1, [!VECTA + R6]
    ADD R1, R1, 4
    ST R1, [!VECTA + R6]
    LD R1, [!VECTB + R6]
    ADD R1, R1, 4
    ST R1, [!VECTB + R6]
    ADD R6, R6, 4
    BLT R6, R7, DUMMY
DUMMY:
HLT
