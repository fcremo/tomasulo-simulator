from abc import *


class Instruction(ABC):
    incremental_id = 1

    def __init__(self):
        self.id = Instruction.incremental_id
        Instruction.incremental_id += 1

    @property
    @abstractmethod
    def latency(self):
        raise NotImplementedError()

    @property
    @abstractmethod
    def mnemonic(self):
        raise NotImplementedError()

    @property
    def operands_str(self):
        return ""

    @property
    def mnemonic_full(self):
        return "{} {}".format(self.mnemonic, self.operands_str)

    def __repr__(self):
        return "INS #{}: {}".format(self.id, self.mnemonic_full)

    def __str__(self):
        return self.mnemonic_full


class HaltInstruction(Instruction):
    latency = 0

    @property
    def mnemonic(self):
        return "HLT"


class BreakpointInstruction(Instruction):
    latency = 0

    def __init__(self, handler=None):
        super().__init__()
        self.handler = handler

    @property
    def mnemonic(self):
        return "BREAK"


# TODO: importing stuff not at the top of the file was done to solve circular dependencies and
# provide the possibility to do "from instruction import *"
# There has to be a better way
from .alu_instructions import *
from .integer_instructions import *
from .control_flow_instructions import *
from .mem_instructions import *


__all__ = ["HaltInstruction", "BreakpointInstruction"]
__all__ += alu_instructions.__all__
__all__ += integer_instructions.__all__
__all__ += control_flow_instructions.__all__
__all__ += mem_instructions.__all__
