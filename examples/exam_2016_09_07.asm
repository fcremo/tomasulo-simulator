; 2 RESERVATION STATIONS (RS1, RS2) + 2 LOAD/STORE unit (LDU1, LDU2) with latency 4
; 2 RESERVATION STATIONS (RS3, RS4) + 2 ALU/BR FUs (ALU1, ALU2) with latency 2
; Check STRUCTURAL hazards for RS in ISSUE phase
; Check RAW hazards and Check STRUCTURAL hazards for FUs in START EXECUTE phase
; WRITE RESULT in RESERVATION STATIONS and RF
; We assume 1 CDB for RF
; Static Branch Prediction ALWAYS TAKEN with Branch Target Buffer
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

FOR:
LD R1, [!VECTA + R6]
LD R2, [!VECTB + R6]
ADD R5, R2, R1
LD R3, [R5 + 0]
LD R4, [!VECTC + R6]
OR R3, R3, R4
ST R3, [R5 + 0]
ADD R6, R6, 4
BLT R6, R7, DUMMY

DUMMY:
HLT
