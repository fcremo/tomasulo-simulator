from .instruction import Instruction, BreakpointInstruction, HaltInstruction
from .alu_instructions import AluInstruction
from .bitwise_instructions import BitwiseInstruction, AndInstruction, OrInstruction
from .control_flow_instructions import (
    ControlFlowInstruction, JumpInstruction, BranchInstruction,
    BEQInstruction, BLEInstruction, BGTInstruction,
    BGEInstruction, BNEInstruction, BLTInstruction)
from .floating_instructions import FloatingInstruction, FAddInstruction, FSubInstruction
from .integer_instructions import IntegerInstruction, AddInstruction, SubInstruction
from .label import Label
from .logic_instructions import LogicInstruction, AndlInstruction, OrlInstruction
from .mem_instructions import MemInstruction, LoadInstruction, StoreInstruction
