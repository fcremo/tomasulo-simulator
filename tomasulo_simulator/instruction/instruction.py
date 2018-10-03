from abc import ABC, abstractmethod

from ..cpu_config import CpuConfig


class Instruction(ABC):
    incremental_id = 1

    def __init__(self):
        from ..execution_trace import ExecutionTrace

        self.id = Instruction.incremental_id
        Instruction.incremental_id += 1

        # Variables used for execution tracing
        self.stats = ExecutionTrace(self)

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

    def latency(self, config: CpuConfig):
        for c in self.__class__.__mro__:
            if c is Instruction:
                return None
            latency = config[self.mnemonic.lower() + "_execution_latency"]
            if latency is not None:
                return latency
        return None

    def __repr__(self):
        return "INS #{}: {}".format(self.id, self.mnemonic_full)

    def __str__(self):
        return self.mnemonic_full


class HaltInstruction(Instruction):
    @property
    def mnemonic(self):
        return "HLT"


class BreakpointInstruction(Instruction):
    def __init__(self, handler=None):
        super().__init__()
        self.handler = handler

    @property
    def mnemonic(self):
        return "BREAK"
