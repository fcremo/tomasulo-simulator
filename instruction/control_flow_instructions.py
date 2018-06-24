from abc import *

from .alu_instruction import AluInstruction


class ControlFlowInstruction(AluInstruction):
    def __init__(self, label=None, address=None):
        super().__init__("PC")
        self.label = label
        self.address = address


class JumpInstruction(ControlFlowInstruction):
    mnemonic = "JMP"
    latency = 1

    @property
    def operands_str(self):
        return "{}({})".format(self.label, self.address)


class BranchInstruction(ControlFlowInstruction):
    latency = 2

    def __init__(self, OP1, OP2, label=None, address=None):
        super().__init__(label, address)
        self.OP1 = OP1
        self.OP2 = OP2

    @staticmethod
    def result(op1, op2, current_pc):
        raise NotImplementedError()

    @property
    def operands_str(self):
        return "{}, {}, {}({})".format(self.OP1, self.OP2, self.label, self.address)


class BEQInstruction(BranchInstruction):
    mnemonic = "BEQ"

    def result(self, op1, op2, current_pc):
        if op1 == op2:
            return self.address
        else:
            return current_pc


class BNEInstruction(BranchInstruction):
    mnemonic = "BNE"

    def result(self, op1, op2, current_pc):
        if op1 != op2:
            return self.address
        else:
            return current_pc


class BLTInstruction(BranchInstruction):
    mnemonic = "BLT"

    def result(self, op1, op2, current_pc):
        if op1 < op2:
            return self.address
        else:
            return current_pc


class BLEInstruction(BranchInstruction):
    mnemonic = "BLE"

    def result(self, op1, op2, current_pc):
        if op1 <= op2:
            return self.address
        else:
            return current_pc


class BGTInstruction(BranchInstruction):
    mnemonic = "BGT"

    def result(self, op1, op2, current_pc):
        if op1 > op2:
            return self.address
        else:
            return current_pc


class BGEInstruction(BranchInstruction):
    mnemonic = "BGE"

    def result(self, op1, op2, current_pc):
        if op1 >= op2:
            return self.address
        else:
            return current_pc


__all__ = [
    "ControlFlowInstruction", "JumpInstruction", "BranchInstruction",
    "BEQInstruction", "BNEInstruction",
    "BLTInstruction", "BLEInstruction",
    "BGEInstruction", "BGTInstruction"
]
