from abc import ABC, abstractmethod

from .alu_instructions import AluInstruction


class ControlFlowInstruction(AluInstruction, ABC):
    def __init__(self, label=None, address=None):
        super().__init__("PC")
        self.label = label
        self.address = address

    @property
    @abstractmethod
    def mnemonic(self):
        raise NotImplementedError()


class JumpInstruction(ControlFlowInstruction):
    mnemonic = "JMP"

    @property
    def operands_str(self):
        return "{}({})".format(self.label, self.address)


class BranchInstruction(ControlFlowInstruction, ABC):
    def __init__(self, op1, op2, label=None, address=None):
        super().__init__(label, address)
        self.OP1 = op1
        self.OP2 = op2

    @staticmethod
    @abstractmethod
    def result(op1, op2, current_pc):
        raise NotImplementedError()

    @property
    def operands_str(self):
        return "{}, {}, {}({})".format(self.OP1, self.OP2, self.label, self.address)

    @property
    @abstractmethod
    def mnemonic(self):
        raise NotImplementedError()


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
