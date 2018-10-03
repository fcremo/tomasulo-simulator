from abc import ABC, abstractmethod

from .instruction import Instruction


class AluInstruction(Instruction, ABC):
    def __init__(self, dst_reg):
        super().__init__()
        self.dst_reg = dst_reg

    @property
    @abstractmethod
    def mnemonic(self):
        raise NotImplementedError()
