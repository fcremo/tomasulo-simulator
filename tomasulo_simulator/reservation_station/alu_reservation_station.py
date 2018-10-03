from ..instruction import AluInstruction
from ..instruction import BitwiseInstruction
from ..instruction import BranchInstruction
from ..instruction import ControlFlowInstruction
from ..instruction import FloatingInstruction
from ..instruction import IntegerInstruction
from ..instruction import JumpInstruction
from ..instruction import LogicInstruction
from .reservation_station import ReservationStation


class ALUReservationStation(ReservationStation):
    kind = "AluRS"
    incremental_id = 1

    def __init__(self, env, cpu, fu_store, rs_store):
        super().__init__(env, cpu, fu_store, rs_store)
        self.OP1_read = None
        self.OP2_read = None
        self.OP1_val = None
        self.OP2_val = None

    def _decode_operands(self):
        if isinstance(self.instruction, (IntegerInstruction, LogicInstruction, BitwiseInstruction,
                                         BranchInstruction, FloatingInstruction)):
            self.OP1_read = self._read_operand(self.instruction.OP1)
            self.OP2_read = self._read_operand(self.instruction.OP2)

        # Associate destination register with this reservation station in the RF
        if isinstance(self.instruction, (IntegerInstruction, LogicInstruction, BitwiseInstruction, FloatingInstruction)):
            self.cpu.reg_file.associate_rs_with_reg(self, self.instruction.dst_reg)

    def _wait_for_dependencies(self):
        dependencies = []

        if self.OP1_read is not None:
            dependencies.append(self.OP1_read)
        if self.OP2_read is not None:
            dependencies.append(self.OP2_read)

        fu_request = self.env.process(self._get_functional_unit())
        dependencies.append(fu_request)

        # Wait for dependencies to be ready
        results = yield self.env.all_of(dependencies)

        if self.OP1_read in results:
            self.OP1_val = results[self.OP1_read]
        if self.OP2_read in results:
            self.OP2_val = results[self.OP2_read]

        self.FU = results[fu_request]

    def _execute(self):
        if isinstance(self.instruction, ControlFlowInstruction):
            yield self.env.process(self._execute_control_flow_instruction())
        elif isinstance(self.instruction, AluInstruction):
            yield self.env.process(self._execute_alu_instruction())
        else:
            raise ValueError("Instruction type unsupported: {}".format(type(self.instruction)))

    def _execute_alu_instruction(self):
        yield self.env.timeout(self._execution_latency())
        self.result = self.instruction.result(self.OP1_val, self.OP2_val)

    def _execute_control_flow_instruction(self):
        if isinstance(self.instruction, JumpInstruction):
            yield self.env.process(self._execute_jump_instruction())
        elif isinstance(self.instruction, BranchInstruction):
            yield self.env.process(self._execute_branch_instruction())
        else:
            raise NotImplementedError()

    def _execute_jump_instruction(self):
        # TODO: support indirect jumps like JMP R1
        yield self.env.timeout(self._execution_latency())
        self.result = self.instruction.address

    def _execute_branch_instruction(self):
        yield self.env.timeout(self._execution_latency())
        self.result = self.instruction.result(self.OP1_val, self.OP2_val, self.cpu.reg_file["PC"])
        if self.result != self.cpu.reg_file["PC"]:
            self._log("{} TAKEN, new PC is {}", self.instruction, self.result)
        else:
            self._log("{} NOT TAKEN", self.instruction)

    def _reset(self):
        super()._reset()
        self.OP1_read = None
        self.OP2_read = None
        self.OP1_val = None
        self.OP2_val = None
