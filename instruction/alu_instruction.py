from . import Instruction


class AluInstruction(Instruction):
    def __init__(self, dst_reg):
        super().__init__()
        self.dst_reg = dst_reg


__all__ = ["AluInstruction"]
