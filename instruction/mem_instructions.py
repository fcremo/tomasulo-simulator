from . import Instruction


class MemInstruction(Instruction):
    latency = 3

    def __init__(self, offset_reg, base):
        super().__init__()
        self.offset_reg = offset_reg
        self.base = base


class LoadInstruction(MemInstruction):
    mnemonic = "LD"

    def __init__(self, dst_reg, offset_reg, base):
        super().__init__(offset_reg, base)
        self.dst_reg = dst_reg

    @property
    def operands_str(self):
        return "{}, [{}+{}]".format(self.dst_reg, self.offset_reg, self.base)


class StoreInstruction(MemInstruction):
    mnemonic = "ST"

    def __init__(self, src_reg, offset_reg, base):
        super().__init__(offset_reg, base)
        self.src_reg = src_reg

    @property
    def operands_str(self):
        return "{}, [{}+{}]".format(self.src_reg, self.offset_reg, self.base)


__all__ = ["LoadInstruction", "StoreInstruction"]
