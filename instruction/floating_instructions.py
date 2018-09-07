from abc import ABC, abstractmethod

from .alu_instructions import AluInstruction


class FloatingInstruction(AluInstruction, ABC):
    def __init__(self, dst_reg, op1, op2):
        super().__init__(dst_reg)
        self.OP1 = op1
        self.OP2 = op2

    @property
    def operands_str(self):
        return "{}, {}, {}".format(self.dst_reg, self.OP1, self.OP2)

    @staticmethod
    @abstractmethod
    def result(op1, op2):
        raise NotImplementedError()

    @property
    @abstractmethod
    def mnemonic(self):
        raise NotImplementedError()


class FAddInstruction(FloatingInstruction):
    mnemonic = "FADD"

    @staticmethod
    def result(op1, op2):
        return op1 + op2


class FSubInstruction(FloatingInstruction):
    mnemonic = "FSUB"

    @staticmethod
    def result(op1, op2):
        return op1 - op2
