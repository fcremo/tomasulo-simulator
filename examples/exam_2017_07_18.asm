; 2 RESERVATION STATIONS (RS1, RS2) + 1 LOAD/STORE unit (LDU1) with latency 4
; 2 RESERVATION STATIONS (RS3, RS4) + 1 ALU/BR FU (ALU1) with latency 2
; We assume 1 Common Data Bus
; Static Branch Prediction ALWAYS TAKEN with Branch Target Buffer
.mem_rs 2
.mem_fu 1
.alu_rs 2
.alu_fu 1
.memrs_execution_latency 4
.alurs_execution_latency 2
.cdb_width 1

LD R1, [0 + R6]
LD R2, [20 + R6]
ADD R1, R1, 5
ADD R2, R2, 5
ST R1, [0]
ST R2, [20]
ADD R6, R6, 4
BLT R6, R7, DUMMY
DUMMY:
HLT
