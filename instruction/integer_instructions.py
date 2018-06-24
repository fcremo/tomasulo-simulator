from .alu_instruction import AluInstruction


class IntegerInstruction(AluInstruction):
    latency = 2

    def __init__(self, dst_reg, OP1, OP2):
        super().__init__(dst_reg)
        self.OP1 = OP1
        self.OP2 = OP2

    @property
    def operands_str(self):
        return "{}, {}, {}".format(self.dst_reg, self.OP1, self.OP2)

    @staticmethod
    def result(op1, op2):
        raise NotImplementedError()


class AddInstruction(IntegerInstruction):
    mnemonic = "ADD"

    @staticmethod
    def result(op1, op2):
        return (op1 + op2) % 0x100


class SubInstruction(IntegerInstruction):
    mnemonic = "SUB"

    @staticmethod
    def result(op1, op2):
        return (op1 - op2) % 0x100


__all__ = ["IntegerInstruction", "AddInstruction", "SubInstruction"]
