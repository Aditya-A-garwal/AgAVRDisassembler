import sys

branchSetSpecialized        = True
branchClearSpecialized      = True
bitSetSpecialized           = True
bitClearSpecialized         = True

def getNibbles (pNum):
    return [pNum & 0b1111, (pNum >> 4) & 0b1111, (pNum >> 8) & 0b1111, (pNum >> 12) & 0b1111, (pNum >> 16) & 0b1111, (pNum >> 20) & 0b1111, (pNum >> 24) & 0b1111, (pNum >> 4) & 0b1111, (pNum >> 8) & 0b1111, (pNum >> 28) & 0b1111]

def bitMatch (pNum, pPattern):

    for c in pPattern[::-1]:

        x = ord (c) - 48

        if (pNum & 1) == x or (x != 0 and x != 1):
            pNum >>= 1
            continue
        else:
            return False

    return True

#! 32 bit functions

def avrCALL (pNum):
    # 1001  010k    kkkk    111k
    # kkkk  kkkk    kkkk    kkkk
    # set program counter to k
    k = pNum & 0b11111111111111111
    k |= ((pNum >> 20) & 0b11111) << 13
    return f"CALL    {k}\n"

def avrJMP (pNum):
    # 1001  010k    kkkk    110k
    # kkkk  kkkk    kkkk    kkkk
    k = (pNum & 0b11111111111111111) | (((pNum >> 20) & 0b11111) << 17)
    return f"JMP     {k}\n"

def avrLDS (pNum):
    # 1001  000d    dddd    0000
    # kkkk  kkkk    kkkk    kkkk
    d = (pNum >> 20) & 0b11111
    k = pNum & 0b1111111111111111
    return f"LDS     R{d}, {k}\n"

def avrSTS (pNum):
    # 1001  001d    dddd    0000
    # kkkk  kkkk    kkkk    kkkk
    d = (pNum >> 20) & 0b11111
    k = pNum & 0b1111111111111111
    return f"STS     {k}, R{d}\n"

#! first nibble not constant

def avrLDZ4 (pNum):
    # 10q0  qq0d    dddd    0qqq
    d = (pNum >> 4) & 0b11111
    q = (pNum & 0b111) | ((pNum >> 7) & 0b11000) | ((pNum >> 8) & 0b100000)

    if q == 0:
        return f"LD      R{d}, Z\n"

    return f"LDD     R{d}, Z+{q}\n"

def avrSTY4 (pNum):
    # 10q0  qq1r    rrrr    1qqq
    r = (pNum & 0b111110000) >> 4
    q = (pNum & 0b111)
    q |= (pNum & 0b110000000000) >> 7
    q |= (pNum & 0b10000000000000) >> 8

    if q == 0:
        return f"ST      Y, R{r}\n"

    return f"STD     Y+{q}, R{r}\n"

def avrSTZ4 (pNum):
    # 10q0  qq1r    rrrr    0qqq
    r = (pNum & 0b111110000) >> 4
    q = (pNum & 0b111)
    q |= (pNum & 0b110000000000) >> 7
    q |= (pNum & 0b10000000000000) >> 8

    if q == 0:
        return f"ST      Z, R{r}\n"

    return f"STD     Z+{q}, R{r}\n"

def avrLDY4 (pNum):
    # 10q0  qq0d    dddd    1qqq
    d = (pNum >> 4) & 0b11111
    q = (pNum & 0b111) | ((pNum >> 7) & 0b11000)

    if q == 0:
        return f"LD      R{d}, Y\n"

    return f"LDD     R{d}, Y+{q}\n"

#! 0000

def avrNOP (pNum):
    # 0000  0000    0000    0000
    return "NOP\n"

def avrADD (pNum):
    # 0000  11rd    dddd    rrrr
    # Rd = Rd + Rr
    d   = (pNum >> 4) & 0b11111
    r   = (pNum & 0b1111) | ((pNum >> 5) & 0b10000)

    if d == r:
        return f"LSL     R{d}\n"

    return f"ADD     R{d}, R{r}\n"

def avrFMUL (pNum):
    # 0000  0011    0ddd    1rrr
    # Rd * Rr = R1 (High) R0 (Low)
    d = ((pNum >> 4) & 0b111) + 16
    r = (pNum & 0b111) + 16
    return f"FMUL    R{d}, R{r}\n"

def avrFMULS (pNum):
    # 0000  0011    1ddd    0rrr
    # Rd * Rr = R1 (High) R0 (Low)
    d = ((pNum >> 4) & 0b111) + 16
    r = (pNum & 0b111) + 16
    return f"FMULS   R{d}, R{r}\n"

def avrFMULSU (pNum):
    # 0000  0011    1ddd    1rrr
    # Rd * Rr = R1 (High) R0 (Low)
    d = ((pNum & 4) & 0b111) + 16
    r = (pNum & 0b111) + 16
    return f"FMULSU  R{d}, R{r}\n"

def avrCPC (pNum):
    # 0000  01rd    dddd    rrrr
    # compare Rd with Rr + carry C
    d = (pNum & 0b111110000) >> 4
    r = pNum & 0b1111
    r |= ((pNum >> 9) & 0b1) << 4
    return f"CPC     R{d}, R{r}\n"

def avrMOVW (pNum):
    # 0000  0001    dddd    rrrr
    d = (pNum >> 4) & 0b1111
    d <<= 1
    r = pNum & 0b1111
    r <<= 1
    return f"MOVW    R{d}, R{r}\n"

def avrMULSU (pNum):
    # 0000  0011    0ddd    0rrr
    d = ((pNum >> 4) & 0b111) + 16
    r = (pNum & 0b111) + 16
    return f"MULSU   R{d}, R{r}\n"

def avrMULS (pNum):
    # 0000  0010    dddd    rrrr
    d = ((pNum >> 4) & 0b1111) + 16
    r = (pNum & 0b1111) + 16
    return f"MULS    R{d}, R{r}\n"

def avrSBC (pNum):
    # 0000  10rd    dddd    rrrr
    d = (pNum >> 4) & 0b11111
    r = (pNum & 0b1111) | ((pNum >> 5) & 0b10000)
    return f"SBC     R{d}, R{r}\n"

#! 0001

def avrADC (pNum):
    # 0001  11rd    dddd    rrrr
    # Rd = Rd + Rr + C
    d   = (pNum >> 4) & 0b11111
    r   = (pNum & 0b1111) | ((pNum >> 5) & 0b10000)

    if d == r:
        return f"ROL     R{d}\n"

    return f"ADC     R{d}, R{r}\n"

def avrROL (pNum):
    # ADC Rd, Rd
    return f"\n"

def avrCPSE (pNum):
    # 0001  00rd    dddd    rrrr
    # If Rd == Rr then increment program counter by 2 (or 3) else by 1
    d = (pNum & 0b111110000) >> 4
    r = (pNum & 0b1111)
    r |= (((pNum >> 9) & 0b1) << 4)
    return f"CPSE    R{d}, R{r}\n"

def avrCP (pNum):
    # 0001  01rd    dddd    rrrr
    # compares Rd with Rr
    d = (pNum >> 4) & 0b1111
    r = (pNum & 0b1111) | (((pNum >> 9) & 0b1) << 4)
    return f"CP      R{d}, R{r}\n"

def avrSUB (pNum):
    # 0001  10rd    dddd    rrrr
    r = (pNum & 0b1111) | ((pNum >> 5) & 0b10000)
    d = (pNum >> 4) & 0b11111
    return f"SUB     R{d}, R{r}\n"

#! 0010

def avrAND (pNum):
    # 0010  00rd    dddd    rrrr
    # Rd = Rd & Rr
    d   = (pNum & 0b111110000) >> 4
    r   = (pNum & 0b1111)
    r   |= (pNum & 0b1000000000) >> 5
    return f"AND     R{d}, R{r}\n"

# def avrCLR (pNum):
#     # EOR Rd, Rd
#     return f""

def avrEOR (pNum):
    # 0010  01rd    dddd    rrrr
    # Rd = Rd xor Rr
    d   = (pNum & 0b111110000) >> 4
    r   = (pNum & 0b1111)
    r   |= (pNum & 0b1000000000) >> 5

    if d == r:
        return f"CLR     R{d}\n"
    return f"EOR     R{d}, R{r}\n"

def avrMOV (pNum):
    # 0010  11rd    dddd    rrrr
    d = (pNum >> 4) & 0b11111
    r = (pNum & 0b1111) | ((pNum >> 5) & 0b10000)
    return f"MOV     R{d}, R{r}\n"

def avrOR (pNum):
    # 0010  10rd    dddd    rrrr
    d = (pNum >> 4) & 0b11111
    r = (pNum & 0b1111) | ((pNum >> 5) & 0b10000)
    return f"OR      R{d}, R{r}\n"

def avrTST (pNum):
    # 0010  00dd    dddd    dddd
    # AND Rd, Rd
    return f""

#! 0011

def avrCPI (pNum):
    # 0011  KKKK    dddd    KKKK
    # compare Rd with constant K
    d = ((pNum >> 4) & 0b1111) + 16
    K = (pNum & 0b1111) | (((pNum >> 8) & 0b1111) << 4)
    return f"CPI     R{d}, {K}\n"

#! 0100

def avrSBCI (pNum):
    # 0100  KKKK    dddd    KKKK
    d = ((pNum >> 4) & 0b1111) + 16
    K = (pNum & 0b1111) | (((pNum >> 8) & 0b1111) << 4)
    return f"SBCI    R{d}, {K}\n"

#! 0101

def avrSUBI (pNum):
    # 0101  KKKK    dddd    KKKK
    d = ((pNum >> 4) & 0b1111) + 16
    K = (pNum & 0b1111) | (((pNum >> 8) & 0b1111) << 4)
    return f"SUBI    R{d}, {K}\n"

#! 0110

def avrORI (pNum):
    # 0110  KKKK    dddd    KKKK
    d = ((pNum >> 4) & 0b1111) + 16
    K = (pNum & 0b1111) | (((pNum >> 8) & 0b1111) << 4)
    return f"ORI     R{d}, {K}\n"

# def avrSBR (pNum):
#     # 0110  KKKK    dddd    KKKK
#     d   = ((pNum >> 4) & 0b1111) + 16
#     K1  = pNum & 0b1111
#     K2  = (pNum >> 8) & 0b1111
#     K   = (K2 << 4) | K1
#     return f"SBR     R{d}, {K}\n"

#! 0111

def avrANDI (pNum):
    # 0111  KKKK dddd KKKK
    # Rd = Rd & K
    d   = ((pNum >> 4) & 0b1111) + 16
    K1  = pNum & 0b1111
    K2  = (pNum >> 8) & 0b1111
    K   = (K2 << 4) | K1
    return f"ANDI    R{d}, {K}\n"

def avrCBR (pNum):
    # ANDI with k complemented
    return f"\n"

#! 1000

# def avrLDZ1 (pNum):
#     # 1000  000d    dddd    0000
#     d = (pNum >> 4) & 0b11111
#     return f"LD      R{d}, Z\n"

# def avrSTY1 (pNum):
#     # 1000  001r    rrrr    1000
#     r = (pNum >> 4) & 0b11111
#     return f"ST      Y, R{r}\n"

# def avrSTZ1 (pNum):
#     # 1000  001r    rrrr    0000
#     r = (pNum >> 4) & 0b11111
#     return f"ST      Z, R{r}\n"

#! 1001

def avrLDZ2 (pNum):
    # 1001  000d    dddd    0001
    d = (pNum >> 4) & 0b11111
    return f"LD      R{d}, Z+\n"

def avrADIW (pNum):
    # 1001  0110    KKdd    KKKK
    # Rd:Rd+1 = Rd:Rd+1 + K
    d   = (pNum >> 4) & 0b11
    d   = list([24, 26, 28, 30])[d]
    k   = (pNum & 0b1111) | ((pNum >> 2) & 0b110000)
    return f"ADIW    R{d + 1}:R{d}, {k}\n"

def avrASR (pNum):
    # 1001  010d    dddd    0101
    # Rd = Rd >> 1 (The rightmost bit goes into the C flag of the SREG)
    d   = (pNum >> 4) & 0b11111
    return f"ASR     R{d}\n"

def avrBCLR (pNum):
    # 1001  0100    1sss    1000
    # Bit s of SREG = 0
    s   = (pNum >> 4) & 0b111

    if not bitClearSpecialized:
        return f"BCLR    {s}\n"

    if s == 0b000:
        return f"CLC\n"

    if s == 0b001:
        return f"CLZ\n"

    if s == 0b010:
        return f"CLN\n"

    if s == 0b011:
        return f"CLV\n"

    if s == 0b100:
        return f"CLS\n"

    if s == 0b101:
        return f"CLH\n"

    if s == 0b110:
        return f"CLT\n"

    if s == 0b111:
        return f"CLI\n"

def avrBREAK (pNum):
    # 1001  0101    1001    1000
    # Used by the on chip debug system, usually not used by program
    return f"BREAK\n"

def avrCBI (pNum):
    # 1001  1000    AAAA    Abbb
    # clear the b-th bit in the Ath IO register
    b = pNum & 0b111
    A = (pNum & 0b11111000) >> 3
    return f"CBI     {A}, {b}\n"

# def avrCLC (pNum):
#     # 1001  0100    1000    1000
#     # clears the carry flag
#     return f"CLC\n"

# def avrCLH (pNum):
#     # 1001  0100    1101    1000
#     # clears the half carry flah
#     return f"CLH\n"

# def avrCLI (pNum):
#     # 1001  0100    1111    1000
#     # clear global interrupt fla in SREG
#     return f"CLI\n"

# def avrCLN (pNum):
#     # 1001  0100    1010    1000
#     # clears the negative flag in SREG
#     return f"CLN\n"

# def avrCLS (pNum):
#     # 1001  0100    1100    1000
#     # clears signed flag in SREG
#     return f"CLS\n"

# def avrCLT (pNum):
#     # 1001  0100    1110    1000
#     # clears the t flag in SREG
#     return f"CLT\n"

# def avrCLV (pNum):
#     # 1001  0100    1011    1000
#     # clears the overflow flag in SREG
#     return f"CLV\n"

# def avrCLZ (pNum):
#     # 1001  0100    1001    1000
#     # clears the zero flag in SREG
#     return f"CLZ\n"

def avrCOM (pNum):
    # 1001  010d    dddd    0000
    # Rd = 0xFF - Rd
    d = (pNum >> 4) & 0b11111
    return f"COM     R{d}\n"

def avrDEC (pNum):
    # 1001  010d    dddd    1010
    # Rd -= 1
    d = (pNum >> 4) & 0b11111
    return f"DEC     R{d}\n"

def avrDES (pNum):
    # 1001  0100    KKKK    1011
    K = (pNum >> 4) & 0b1111
    return f"DES     {hex (K)}\n"

def avrEICALL (pNum):
    # 1001  0101    0001    1001
    # sets the first 16 bits of the program counter equal to teh first 16 bits of the Z pointer register
    # sets the second 16 bits of the program counter equal to the EIND register
    return f"EICALL\n"

def avrEIJMP (pNum):
    # 1001  0100    0001    1001
    # sets the first 16 bits of the program counter equal to teh first 16 bits of the Z pointer register
    # sets the second 16 bits of the program counter equal to the EIND register
    return f"EIJMP\n"

def avrELPM1 (pNum):
    # 1001  0101    1101    1000
    # Load the value of RAMPZ:Z to R0
    return f"ELPM\n"

def avrELPM2 (pNum):
    # 1001  000d    dddd    0110
    # Load the value of RAMPZ:Z to Rd and leave Z unchanged
    d = (pNum >> 4) & 0b11111
    return f"ELPM    R{d}, Z\n"

def avrELPM3 (pNum):
    # 1001  000d    dddd    0111
    # Load the value of RAMPZ:Z to Rd and increment Z
    d = (pNum >> 4) & 0b11111
    return f"ELPM    R{d}, Z+\n"

def avrICALL (pNum):
    # 1001  0101    0000    1001
    return f"ICALL\n"

def avrIJMP (pNum):
    # 1001  0100    0000    1001
    return f"IJMP\n"

def avrIN (pNum):
    # 1011  0AAd    dddd    AAAA
    d = (pNum >> 4) & 0b11111
    A = (pNum & 0b1111) | (((pNum >> 9) & 0b11) << 4)
    return f"IN      R{d}, {A}\n"

def avrINC (pNum):
    # 1001  010d    dddd    0011
    d = (pNum >> 4) & 0b11111
    return f"INC     R{d}\n"

def avrLAC (pNum):
    # 1001  001r    rrrr    0110
    d = (pNum >> 4) & 0b11111
    return f"LAC     Z, R{d}\n"

def avrLAS (pNum):
    # 1001  001r    rrrr    0101
    d = (pNum >> 4) & 0b11111
    return f"LAS     Z, R{d}\n"

def avrLAT (pNum):
    # 1001  001r    rrrr    0111
    d = (pNum >> 4) & 0b11111
    return f"LAT     Z, R{d}\n"

def avrLDX1 (pNum):
    # 1001  000d    dddd    1100
    d = (pNum >> 4) & 0b11111
    return f"LD      R{d}, X\n"

def avrLDX2 (pNum):
    # 1001  000d    dddd    1101
    d = (pNum >> 4) & 0b11111
    return f"LD      R{d}, X+\n"

def avrLDX3 (pNum):
    # 1001  000d    dddd    1110
    d = (pNum >> 4) & 0b11111
    return f"LD      R{d}, -X\n"

def avrBSET (pNum):
    # 1001  0100    0sss    1000
    # sets bit s in SREG
    s   = (pNum >> 4) & 0b111

    if not bitSetSpecialized:
        return f"BSET    {s}\n"

    if s == 0b000:
        return f"SEC\n"

    if s == 0b001:
        return f"SEZ\n"

    if s == 0b010:
        return f"SEN\n"

    if s == 0b011:
        return f"SEV\n"

    if s == 0b100:
        return f"SES\n"

    if s == 0b101:
        return f"SEH\n"

    if s == 0b110:
        return f"SET\n"

    if s == 0b111:
        return f"SEI\n"

# def avrLDY1 (pNum):
#     # 1001  000d    dddd    1000
#     d = (pNum >> 4) & 0b11111
#     return f"LD      R{d}, Y\n"

def avrLDY2 (pNum):
    # 1001  000d    dddd    1001
    d = (pNum >> 4) & 0b11111
    return f"LD      R{d}, Y+\n"

def avrLDY3 (pNum):
    # 1001  000d    dddd    1010
    d = (pNum >> 4) & 0b11111
    return f"LD      R{d}, -Y\n"

def avrLDZ3 (pNum):
    # 1001  000d    dddd    0100
    d = (pNum >> 4) & 0b11111
    return f"LD      R{d}, -Z\n"

def avrLPM1 (pNum):
    # 1001  0101    1100   1000
    return f"LPM\n"

def avrLPM2 (pNum):
    # 1001  000d    dddd   0100
    d = (pNum >> 4) & 0b11111
    return f"LPM     R{d}, Z\n"

def avrLPM3 (pNum):
    # 1001  010d    dddd   0101
    d = (pNum >> 4) & 0b11111
    return f"LPM     R{d}, Z+\n"

# def avrLSL (pNum):
#     # ADD Rd, Rd
#     return f""

def avrLSR (pNum):
    # 1001  010d    dddd    0110
    d = (pNum >> 4) & 0b11111
    return f"LSR     R{d}\n"

def avrNEG (pNum):
    # 1001  010d    dddd    0001
    d = (pNum >> 4) & 0b11111
    return f"NEG     R{d}\n"

def avrMUL (pNum):
    # 1001  11rd    dddd    rrrr
    d = (pNum >> 4) & 0b11111
    r = (pNum & 0b1111) | ((pNum >> 5) & 0b10000)
    return f"MUL     R{d}, R{r}\n"

def avrPOP (pNum):
    # 1001  000d    dddd    1111
    d = (pNum >> 4) & 0b11111
    return f"POP     R{d}\n"

def avrPUSH (pNum):
    # 1001  001d    dddd    1111
    d = (pNum >> 4) & 0b11111
    return f"PUSH   R{d}\n"

def avrRET (pNum):
    # 1001  0101    0000    1000
    return f"RET\n"

def avrRETI (pNum):
    # 1001  0101    0001    1000
    return f"RETI\n"

def avrROR (pNum):
    # 1001  010d    dddd    0111
    d = (pNum >> 4) & 0b11111
    return f"ROR     R{d}\n"

def avrSBI (pNum):
    # 1001  1010    AAAA    Abbb
    b = pNum & 0b111
    A = (pNum >> 3) & 0b11111
    return f"SBI    {A}, {b}\n"

def avrSBIC (pNum):
    # 1001  1001    AAAA    Abbb
    b = pNum & 0b111
    A = (pNum >> 3) & 0b11111
    return f"SBIC   {A}, {b}\n"

def avrSBIS (pNum):
    # 1001  1011    AAAA    Abbb
    A   = (pNum >> 3) & 0b11111
    b   = pNum & 0b111
    return f"SBIS    {A}, {b}\n"

def avrSBIW (pNum):
    # 1001  0111    KKdd    KKKK
    d   = list (24, 26, 28, 30)[(pNum >> 4)]
    K   = (pNum & 0b1111) | ((pNum >> 2) & 0b110000)
    return f"SBIW    R{d}, {K}\n"

# def avrSEC (pNum):
#     # 1001  0100    0000    1000
#     return f"SEC\n"

# def avrSEH (pNum):
#     # 1001  0100    0101    1000
#     return f"SEH\n"

# def avrSEI (pNum):
#     # 1001  0100    0111    1000
#     return f"SEI\n"

# def avrSEN (pNum):
#     # 1001  0100    0010    1000
#     return f"SEH\n"

# # def avrSES (pNum):
# #     # 1001  0100    0100    1000
# #     return f"SES\n"

# def avrSET (pNum):
#     # 1001  0100    0110    1000
#     return f"SET\n"

# def avrSEV (pNum):
#     # 1001  0100    0011    1000
#     return f"SEV\n"

# def avrSEZ (pNum):
#     # 1001  0100    0001    1000
#     return f"SEI\n"

def avrSLEEP (pNum):
    # 1001  0101    1000    1000
    return f"SLEEP\n"

def avrSPM1 (pNum):
    # 1001  0101    1110    1000
    return f"SPM\n"

def avrSPM2 (pNum):
    # 1001  0101    1111    1000
    return f"SPM    Z+\n"

def avrSTX1 (pNum):
    # 1001  001r    rrrr    1100
    r = (pNum >> 4) & 0b11111
    return f"ST      X, R{r}\n"

def avrSTX2 (pNum):
    # 1001  001r    rrrr    1101
    r = (pNum >> 4) & 0b11111
    return f"ST      X+, R{r}\n"

def avrSTX3 (pNum):
    # 1001  001r    rrrr    1110
    r = (pNum >> 4) & 0b11111
    return f"ST      -X, R{r}\n"

def avrSTY2 (pNum):
    # 1001  001r    rrrr    1001
    r = (pNum >> 4) & 0b11111
    return f"ST      Y+, R{r}\n"

def avrSTY3 (pNum):
    # 1001  001r    rrrr    1010
    r = (pNum >> 4) & 0b11111
    return f"ST      -Y, R{r}\n"

def avrSTZ2 (pNum):
    # 1001  001r    rrrr    0001
    r = (pNum >> 4) & 0b11111
    return f"ST      Y, R{r}\n"

def avrSTZ3 (pNum):
    # 1001  001r    rrrr    0010
    r = (pNum >> 4) & 0b11111
    return f"ST      Y, R{r}\n"

def avrSTS16 (pNum):
    # 1001  1kkk    dddd    kkkk
    d = ((pNum >> 4) & 0b1111) + 16
    k = (pNum & 0b1111) | ((pNum >> 4) & 0b1110000)
    return f"\n"

def avrSWAP (pNum):
    # 1001  010d    dddd    0010
    d = (pNum >> 4) & 0b11111
    return f"SWAP    R{d}\n"

def avrWDR (pNum):
    # 1001  0101    1010    1000
    return f"WDR\n"

def avrXCH (pNum):
    # 1001  001r    rrrr    0100
    r = (pNum >> 4) & 0b11111
    return f"SCH     R{r}\n"

#! 1010

def avrLDS16 (pNum):
    # 1010  0kkk    dddd    kkkk
    d = (pNum >> 4) & 0b1111
    k = (pNum & 0b1111) | ((pNum >> 4) & 0b01110000)
    return f"LDS     R{d}, {k}\n"

#! 1011

def avrOUT (pNum):
    # 1011  1AAr    rrrr    AAAA
    A = (pNum & 0b1111) | ((pNum >> 5) & 0b110000)
    r = (pNum >> 4) & 0b11111
    return f"OUT     {A}, R{r}\n"

#! 1100

def avrRJMP (pNum):
    # 1100  kkkk    kkkk    kkkk
    k   = pNum & 0b111111111111
    if (k >> 11) & 1:
        k -= 4096
    return f"RJMP    {k}\n"

#! 1101

def avrRCALL (pNum):
    # 1101  kkkk    kkkk    kkkk
    k   = pNum & 0b111111111111
    if (k >> 11) & 1:
        k -= 4096
    return f"RCALL   {k}\n"

#! 1110

def avrLDI (pNum):
    # 1110  KKKK    dddd    KKKK
    d = ((pNum >> 4) & 0b1111) + 16
    K = (pNum & 0b1111) | ((pNum >> 4) & 0b11110000)
    return f"LDI     R{d}, {K}\n"

def avrSER (pNum):
    # 1110  1111    dddd    1111
    d = (pNum >> 4) & 0b1111
    return f"SER     R{d}\n"

#! 1111

def avrBLD (pNum):
    # 1111  100d    dddd    0bbb
    # Bit b of Rd = T flag of SREG
    d   = (pNum >> 4) & 0b11111
    b   = pNum & 0b111
    return f"BLD     R{d}, {b}\n"

def avrBRBC (pNum):
    # 1111  01kk    kkkk    ksss
    # If bit s of sreg is not set, increment program counter by k+1 else 1
    s   = pNum & 0b111
    k   = (pNum >> 3) & 0b1111111
    k   -= (1 << 7)

    #! branchClearSpecialized should be user defined
    if not branchClearSpecialized:
        return f"BRBC    {s}, {k}\n"

    if (s == 0b000):
        return f"BRCC    {k}\n" # same as BRSH

    if (s == 0b001):
        return f"BRNE    {k}\n"

    if (s == 0b010):
        return f"BRPL    {k}\n"

    if (s == 0b011):
        return f"BRVC    {k}\n"

    if (s == 0b100):
        return f"BRGE    {k}\n"

    if (s == 0b101):
        return f"BRHC    {k}\n"

    if (s == 0b110):
        return f"BRTC    {k}\n"

    if (s == 0b111):
        return f"BRID    {k}\n"

def avrBRBS (pNum):
    # 1111  00kk    kkkk    ksss
    # If bit s of sreg is set, increment program counter by k+1 else 1
    s   = pNum & 0b111
    k   = (pNum >> 3) & 0b1111111
    k   -= (1 << 7)

    #! branchSetSpecialized should be user defined
    if not branchSetSpecialized:
        return f"BRBS    {s}, {k}\n"

    if (s == 0b000):
        return f"BRCS    {k}\n" # same as BRLO

    if (s == 0b001):
        return f"BREQ    {k}\n"

    if (s == 0b010):
        return f"BRMI    {k}\n"

    if (s == 0b011):
        return f"BRVS    {k}\n"

    if (s == 0b100):
        return f"BRLT    {k}\n"

    if (s == 0b101):
        return f"BRHS    {k}\n"

    if (s == 0b110):
        return f"BRTS    {k}\n"

    if (s == 0b111):
        return f"BRIE    {k}\n"

# def avrBRCC (pNum):
#     # 1111  01kk    kkkk    k000
#     # If bit C of carry flag is not set, increment program counter by k+1 else 1
#     k   = (pNum >> 3) & 0b1111111
#     k   -= (1 << 7)
#     return f"BRCC    {k}\n"

# def avrBRCS (pNum):
#     # 1111  00kk    kkkk    k000
#     # If C is 1, then increment program counter by k+1 else 1
#     k   = (pNum >> 3) & 0b1111111
#     return f"BRCS    {k}\n"

# def avrBREQ (pNum):
#     # 1111  00kk    kkkk    k001
#     # If the zero flag is set, then increment program counter by k+1 else 1
#     k   = (pNum >> 3) & 0b1111111
#     return f"BREQ    {k}\n"

# def avrBRGE (pNum):
#     # 1111  01kk    kkkk    k100
#     # If the signed flag is cleared, increment program counter by k+1 else 1
#     k   = (pNum >> 3) & 0b1111111
#     return f"BRGE    {k}\n"

# def avrBRHC (pNum):
#     # 1111  01kk    kkkk    k101
#     # If the half carry flag is cleared, increment program counter by k+1 else 1
#     k   = (pNum >> 3) & 0b1111111
#     return f"BRHC    {k}\n"

# def avrBRHS (pNum):
#     # 1111  00kk    kkkk    k101
#     # If the half carry flag is set, increment program counter by k+1 else 1
#     k   = (pNum >> 3) & 0b1111111
#     return f"BRHS    {k}\n"

# def avrBRID (pNum):
#     # 1111  01kk    kkkk    k111
#     # If the global interrupt is disabled, then increment program counter by k+1 else 1
#     k   = (pNum >> 3) & 0b1111111
#     return f"BRID    {k}\n"

# def avrBRIE (pNum):
#     # 1111  00kk    kkkk    k111
#     # If the global interrupt is enabled, then increment program counter by k+1 else 1
#     k   = (pNum >> 3) & 0b1111111
#     return f"BRIE    {k}\n"

# def avrBRLO (pNum):
#     # 1111  00kk    kkkk    k000
#     # If the carry flag is set, then increment program counter by k+1 else 1
#     k   = (pNum >> 3) & 0b1111111
#     return f"BRLO    {k}\n"

# def avrBRLT (pNum):
#     # 1111  00kk    kkkk    k100
#     # If the signed flag is set, then increment program counter by k+1 else 1
#     k   = (pNum >> 3) & 0b1111111
#     return f"BRLT    {k}\n"

# def avrBRMI (pNum):
#     # 1111  00kk    kkkk    k010
#     # If the negative flag is set, then increment program counter by k+1 else 1
#     k   = (pNum >> 3) & 0b1111111
#     return f"BRMI    {k}\n"

# def avrBRNE (pNum):
#     # 1111  01kk    kkkk    k001
#     # If the zero flag is cleared, then increment program counter by k+1 else 1
#     k   = (pNum >> 3) & 0b1111111
#     return f"BRNE    {k}\n"

# def avrBRPL (pNum):
#     # 1111  01kk    kkkk    k010
#     # If the negative flag is cleared, then increment program counter by k+1 else 1
#     k   = (pNum >> 3) & 0b1111111
#     return f"BRPL    {k}\n"

# def avrBRSH (pNum):
#     # 1111  01kk    kkkk    k000
#     # If the carry flag is cleared, then increment program counter by k+1 else 1
#     k   = (pNum >> 3) & 0b1111111
#     k   -= (1 << 7)
#     return f"BRSH    {k}\n"

# def avrBRTC (pNum):
#     # 1111  01kk    kkkk    k110
#     # If the T flag is cleared, then increment program counter by k+1 else 1
#     k   = (pNum >> 3) & 0b1111111
#     return f"BRTC    {k}\n"

# def avrBRTS (pNum):
#     # 1111  01kk    kkkk    k000
#     # If the T flag is set, then increment program counter by k+1 else 1
#     k   = (pNum >> 3) & 0b1111111
#     return f"BRTS    {k}\n"

# def avrBRVC (pNum):
#     # 1111  01kk    kkkk    k000
#     # If the overflow flag is cleared, then increment program counter by k+1 else 1
#     k   = (pNum >> 3) & 0b1111111
#     return f"BRVC    {k}\n"

# def avrBRVS (pNum):
#     # 1111  01kk    kkkk    k000
#     # If the overflow flag is set, then increment program counter by k+1 else 1
#     k   = (pNum >> 3) & 0b1111111
#     return f"BRVS    {k}\n"

def avrBST (pNum):
    # 1111  101d    dddd    0bbb
    # stored bit b from Td to the T flag in SREG
    d   = (pNum >> 4) & 0b11111
    b   = pNum & 0b111
    return f"BST     R{d}, {b}\n"

def avrSBRC (pNum):
    # 1111  110r    rrrr    0bbb
    r = (pNum >> 4) & 0b11111
    b = pNum & 0b111
    return f"SBRC    R{r}, {b}\n"

def avrSBRS (pNum):
    # 1111  111r    rrrr    0bbb
    r = (pNum >> 4) & 0b11111
    b = pNum & 0b111
    return f"SBRS    R{r}, {b}\n"


f       = open (sys.argv[1], "r")
dat     = list (map (int, f.read ().split (',')))
f.close ()

f       = open (sys.argv[2], "w")
cur     = 0
buf     = [0 for i in range (len (dat) // 2)]

for i, e in enumerate (dat):
    if i&1:
        cur         |= e << 8
        buf [i//2]  = cur
    else:
        cur         = e

dat     = buf

skip    = False
for i, e in enumerate (dat):

    if skip:
        skip    = False
        continue

    # first check for 32 bit instruction pattern matches
    # Matches CALL
    if bitMatch (e, "1001010kkkkk111k"):
        e       = (e << 16) | dat[i + 1]
        skip    = True
        f.write (avrCALL (e))
        continue

    # Matches JMP
    if bitMatch (e, "1001010kkkkk110k"):
        e       = (e << 16) | dat[i + 1]
        skip    = True
        f.write (avrJMP (e))
        continue

    # Matches LDS
    if bitMatch (e, "1001000ddddd0000"):
        e       = (e << 16) | dat[i + 1]
        skip    = True
        f.write (avrLDS (e))
        continue

    # Matches STS
    if bitMatch (e, "1001001ddddd0000"):
        e       = (e << 16) | dat[i + 1]
        skip    = True
        f.write (avrSTS (e))
        continue

    # check if the first nibble is not constant
    if bitMatch (e, "10q0qq0ddddd0qqq"):
        f.write (avrLDZ4 (e))
        continue

    if bitMatch (e, "10q0qq1rrrrr1qqq"):
        f.write (avrSTY4 (e))
        continue

    if bitMatch (e, "10q0qq1rrrrr0qqq"):
        f.write (avrSTZ4 (e))
        continue

    if bitMatch (e, "10q0qq0ddddd1qqq"):
        f.write (avrLDY4 (e))
        continue

    # 0000

    if e == 0:
        f.write (avrNOP (e))
        continue

    if bitMatch (e, "000011rdddddrrrr"):
        f.write (avrADD (e))
        continue

    if bitMatch (e, "000000110ddd1rrr"):
        f.write (avrFMUL (e))
        continue

    if bitMatch (e, "000000111ddd0rrr"):
        f.write (avrFMULS (e))
        continue

    if bitMatch (e, "000000111ddd1rrr"):
        f.write (avrFMULSU (e))
        continue

    if bitMatch (e, "000001rdddddrrrr"):
        f.write (avrCPC (e))
        continue

    if bitMatch (e, "00000001ddddrrrr"):
        f.write (avrMOVW (e))
        continue

    if bitMatch (e, "000000110ddd0rrr"):
        f.write (avrMULSU (e))
        continue

    if bitMatch (e, "00000010ddddrrrr"):
        f.write (avrMULS (e))
        continue

    if bitMatch (e, "000010rdddddrrrr"):
        f.write (avrSBC (e))
        continue

    # 0001

    if bitMatch (e, "000111rdddddrrrr"):
        f.write (avrADC (e))
        continue

    if bitMatch (e, "000100rdddddrrrr"):
        f.write (avrCPSE (e))
        continue

    if bitMatch (e, "000101rdddddrrrr"):
        f.write (avrCP (e))
        continue

    if bitMatch (e, "000110rdddddrrrr"):
        f.write (avrSUB (e))
        continue

    # 0010

    if bitMatch (e, "001000rdddddrrrr"):
        f.write (avrAND (e))
        continue

    if bitMatch (e, "001001rdddddrrrr"):
        f.write (avrEOR (e))
        continue

    if bitMatch (e, "001011rdddddrrrr"):
        f.write (avrMOV (e))
        continue

    if bitMatch (e, "001010rdddddrrrr"):
        f.write (avrOR (e))
        continue

    # 0011

    if bitMatch (e, "0011KKKKddddKKKK"):
        f.write (avrCPI (e))
        continue

    # 0100

    if bitMatch (e, "0100KKKKddddKKKK"):
        f.write (avrSBCI (e))
        continue

    # 0101

    if bitMatch (e, "0101KKKKddddKKKK"):
        f.write (avrSUBI (e))
        continue

    # 0110

    if bitMatch (e, "0110KKKKddddKKKK"):
        f.write (avrORI (e))
        continue

    # 0111

    if bitMatch (e, "0111KKKKddddKKKK"):
        f.write (avrANDI (e))
        continue

    # 1001

    if bitMatch (e, "1001000ddddd0001"):
        f.write (avrLDZ2 (e))
        continue

    if bitMatch (e, "10010110KKddKKKK"):
        f.write (avrADIW (e))
        continue

    if bitMatch (e, "1001010ddddd0101"):
        f.write (avrASR (e))
        continue

    if bitMatch (e, "100101001sss1000"):
        f.write (avrBCLR (e))
        continue

    if bitMatch (e, "1001010110011000"):
        f.write (avrBREAK (e))
        continue

    if bitMatch (e, "10011000AAAAAbbb"):
        f.write (avrCBI (e))
        continue

    if bitMatch (e, "1001010ddddd0000"):
        f.write (avrCOM (e))
        continue

    if bitMatch (e, "1001010ddddd1010"):
        f.write (avrDEC (e))
        continue

    if bitMatch (e, "10010100KKKK1011"):
        f.write (avrDES (e))
        continue

    if bitMatch (e, "1001010100011001"):
        f.write (avrEICALL (e))
        continue

    if bitMatch (e, "1001010000011001"):
        f.write (avrEIJMP (e))
        continue

    if bitMatch (e, "1001010111011000"):
        f.write (avrELPM1 (e))
        continue

    if bitMatch (e, "1001000ddddd0110"):
        f.write (avrELPM2 (e))
        continue

    if bitMatch (e, "1001000ddddd0111"):
        f.write (avrELPM3 (e))
        continue

    if bitMatch (e, "1001010100001001"):
        f.write (avrICALL (e))
        continue

    if bitMatch (e, "1001010000001001"):
        f.write (avrIJMP (e))
        continue

    if bitMatch (e, "10110AAdddddAAAA"):
        f.write (avrIN (e))
        continue

    if bitMatch (e, "1001010ddddd0011"):
        f.write (avrINC (e))
        continue

    if bitMatch (e, "1001001rrrrr0110"):
        f.write (avrLAC (e))
        continue

    if bitMatch (e, "1001001rrrrr0101"):
        f.write (avrLAS (e))
        continue

    if bitMatch (e, "1001001rrrrr0111"):
        f.write (avrLAT (e))
        continue

    if bitMatch (e, "1001000ddddd1100"):
        f.write (avrLDX1 (e))
        continue

    if bitMatch (e, "1001000ddddd1101"):
        f.write (avrLDX2 (e))
        continue

    if bitMatch (e, "1001000ddddd1110"):
        f.write (avrLDX3 (e))
        continue

    if bitMatch (e, "100101000sss1000"):
        f.write (avrBSET (e))
        continue

    if bitMatch (e, "1001000ddddd1001"):
        f.write (avrLDY2 (e))
        continue

    if bitMatch (e, "1001000ddddd1010"):
        f.write (avrLDY3 (e))
        continue

    if bitMatch (e, "1001000ddddd0100"):
        f.write (avrLDZ3 (e))
        continue

    if bitMatch (e, "1001010111001000"):
        f.write (avrLPM1 (e))
        continue

    if bitMatch (e, "1001000ddddd0100"):
        f.write (avrLPM2 (e))
        continue

    if bitMatch (e, "1001010ddddd0101"):
        f.write (avrLPM3 (e))
        continue

    if bitMatch (e, "1001010ddddd0110"):
        f.write (avrLSR (e))
        continue

    if bitMatch (e, "1001010ddddd0001"):
        f.write (avrNEG (e))
        continue

    if bitMatch (e, "100111rdddddrrrr"):
        f.write (avrMUL (e))
        continue

    if bitMatch (e, "1001000ddddd1111"):
        f.write (avrPOP (e))
        continue

    if bitMatch (e, "1001001ddddd1111"):
        f.write (avrPUSH (e))
        continue

    if bitMatch (e, "1001010100001000"):
        f.write (avrRET (e))
        continue

    if bitMatch (e, "1001010100011000"):
        f.write (avrRETI (e))
        continue

    if bitMatch (e, "1001010ddddd0111"):
        f.write (avrROR (e))
        continue

    if bitMatch (e, "10011010AAAAAbbb"):
        f.write (avrSBI (e))
        continue

    if bitMatch (e, "10011001AAAAAbbb"):
        f.write (avrSBIC (e))
        continue

    if bitMatch (e, "10011011AAAAAbbb"):
        f.write (avrSBIS (e))
        continue

    if bitMatch (e, "10010111KKddKKKK"):
        f.write (avrSBIW (e))
        continue

    if bitMatch (e, "1001010110001000"):
        f.write (avrSLEEP (e))
        continue

    if bitMatch (e, "1001010111101000"):
        f.write (avrSPM1 (e))
        continue

    if bitMatch (e, "1001010111111000"):
        f.write (avrSPM2 (e))
        continue

    if bitMatch (e, "1001001rrrrr1100"):
        f.write (avrSTX1 (e))
        continue

    if bitMatch (e, "1001001rrrrr1101"):
        f.write (avrSTX2 (e))
        continue

    if bitMatch (e, "1001001rrrrr1110"):
        f.write (avrSTX3 (e))
        continue

    if bitMatch (e, "1001001rrrrr1001"):
        f.write (avrSTY2 (e))
        continue

    if bitMatch (e, "1001001rrrrr1010"):
        f.write (avrSTY3 (e))
        continue

    if bitMatch (e, "1001001rrrrr0001"):
        f.write (avrSTZ2 (e))
        continue

    if bitMatch (e, "1001001rrrrr0010"):
        f.write (avrSTZ3 (e))
        continue

    if bitMatch (e, "10011kkkddddkkkk"):
        f.write (avrSTS16 (e))
        continue

    if bitMatch (e, "1001010ddddd0010"):
        f.write (avrSWAP (e))
        continue

    if bitMatch (e, "1001010110101000"):
        f.write (avrWDR (e))
        continue

    if bitMatch (e, "1001001rrrrr0100"):
        f.write (avrXCH (e))
        continue

    # 1010

    if bitMatch (e, "10100kkkddddkkkk"):
        f.write (avrLDS16 (e))
        continue

    # 1011

    if bitMatch (e, "10111AArrrrrAAAA"):
        f.write (avrOUT (e))
        continue

    # 1100

    if bitMatch (e, "1100kkkkkkkkkkkk"):
        f.write (avrRJMP (e))
        continue

    # 1101

    if bitMatch (e, "1101kkkkkkkkkkkk"):
        f.write (avrRCALL (e))
        continue

    # 1110

    if bitMatch (e, "1110KKKKddddKKKK"):
        f.write (avrLDI (e))
        continue

    if bitMatch (e, "11101111dddd1111"):
        f.write (avrSER (e))
        continue

    # 1111

    if bitMatch (e, "1111100ddddd0bbb"):
        f.write (avrBLD (e))
        continue

    if bitMatch (e, "111100kkkkkkksss"):
        f.write (avrBRBS (e))
        continue

    if bitMatch (e, "111101kkkkkkksss"):
        f.write (avrBRBC (e))
        continue

    if bitMatch (e, "1111101ddddd0bbb"):
        f.write (avrBST (e))
        continue

    if bitMatch (e, "1111110rrrrr0bbb"):
        f.write (avrSBRC (e))
        continue

    if bitMatch (e, "1111111rrrrr0bbb"):
        f.write (avrSBRS (e))
        continue

f.close ()
