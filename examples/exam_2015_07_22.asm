.mem_rs 2
.mem_fu 2
.memrs_execution_latency 4
.alu_rs 2
.alu_fu 2
.alurs_execution_latency 2
.cdb_width 1

.const !VECTA 0
.const !VECTB 20
.const !VECTC 40
.const !VECTD 60

FOR:
LD R2, [!VECTA + R6]
LD R3, [!VECTB + R6]
LD R4, [!VECTC + R6]
ADD R3, R2, R3
ADD R4, R3, R4
ST R4, [!VECTC + R6]
ST R0, [!VECTD + R6]
ADD R6, R6, 4
BLT R6, R7, DUMMY
DUMMY:
HLT