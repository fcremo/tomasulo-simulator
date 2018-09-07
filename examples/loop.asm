; equivalent to
; int c = 0;
; for(int i=3; i>0; i--) c+=2;

ADD R1, R0, 3
LOOP:
    BLE R1, R0, END
    ADD R2, R2, 2
    SUB R1, R1, 1
    JMP LOOP
END:
    HLT
