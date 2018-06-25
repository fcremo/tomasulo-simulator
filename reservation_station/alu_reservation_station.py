import simpy

from . import ReservationStation, RSResult
from instruction import *


class ALUReservationStation(ReservationStation):
    def __init__(self, env, cpu):
        super().__init__(env, cpu)
        self.OP1_val = None
        self.OP2_val = None
        self.OP1_source_rs = None
        self.OP2_source_rs = None
        self.result = None
        self.result_broadcast_event = None

    def enqueue_instruction(self, instruction, lock_request):
        self.instruction = instruction
        self.lock_req = lock_request

        # Create a new event that will be triggered when the result is written to the CDB
        self.result_broadcast_event = simpy.Event(self.env)

        self.env.process(self._run_instruction())

    def _run_instruction(self):
        # Execute the required computation
        if isinstance(self.instruction, IntegerInstruction):
            yield self.env.process(self._enqueue_integer_instruction())
        elif isinstance(self.instruction, ControlFlowInstruction):
            yield self.env.process(self._enqueue_control_flow_instruction())
        else:
            raise ValueError("Instruction type unsupported: {}".format(type(self.instruction)))

        # Broadcast the result on the cdb
        if self.CDB.busy:
            self._log("Struct hazard: CDB is busy")
        with self.CDB.request() as CDB_req:
            yield CDB_req
            self._log("Broadcasting result on CDB")
            self.result_broadcast_event.succeed(RSResult(rs=self, result=self.result))
            # Write back the result to the register file if no WAW is detected
            if self.reg_file[self.instruction.dst_reg] is self:
                self._log("Writing back result to {} in the RF (no WAW detected)", self.instruction.dst_reg)
                self.reg_file[self.instruction.dst_reg] = self.result
            else:
                self._log("WAW detected and avoided for reg {}", self.instruction.dst_reg)

        # Release the functional unit
        yield self.alu_FU.put(self.FU)

        # Reset RS status
        self.reset()

        # Finally, release the RS
        yield self.release(self.lock_req)

    def _enqueue_integer_instruction(self):
        # Decode the operands
        self._decode_operands()

        # Associate destination register with this reservation station in the RF
        self.reg_file[self.instruction.dst_reg] = self

        # Wait for the operands to be ready
        yield self.env.process(self._wait_for_dependencies())

        # Execute the instruction
        self.execution_process = self.env.timeout(self.instruction.latency)
        yield self.execution_process
        self._log("End execution of {}", self.instruction)
        self.result = self.instruction.result(self.OP1_val, self.OP2_val)

    def _decode_operands(self):
        instruction = self.instruction

        # Read immediate operand
        if isinstance(instruction.OP1, int):
            self.OP1_val = instruction.OP1
        # Read concrete operand (register value)
        elif isinstance(self.reg_file[instruction.OP1], int):
            self.OP1_val = self.reg_file[instruction.OP1]
        # Associate source RS with operand
        else:
            self.OP1_source_rs = self.reg_file[instruction.OP1]

        # Read immediate operand
        if isinstance(instruction.OP2, int):
            self.OP2_val = instruction.OP2
        # Read concrete operand (register value)
        elif isinstance(self.reg_file[instruction.OP2], int):
            self.OP2_val = self.reg_file[instruction.OP2]
        # Associate source RS with operand
        else:
            self.OP2_source_rs = self.reg_file[instruction.OP2]

    def _wait_for_dependencies(self):
        dependencies = []
        pending_operands = {}
        OP1_broadcast_event, OP2_broadcast_event = None, None
        if self.OP1_source_rs is not None:
            OP1_broadcast_event = self.OP1_source_rs.result_broadcast_event
            dependencies.append(OP1_broadcast_event)
            pending_operands[self.instruction.OP1] = self.OP1_source_rs
        if self.OP2_source_rs is not None:
            OP2_broadcast_event = self.OP2_source_rs.result_broadcast_event
            dependencies.append(OP2_broadcast_event)
            pending_operands[self.instruction.OP2] = self.OP2_source_rs

        fu_request = self.env.process(self._reserve_functional_unit())
        dependencies.append(fu_request)

        if pending_operands:
            pending_str = ", ".join([str(reg) + " from " + str(rs) for reg, rs in pending_operands.items()])
            self._log("RAW: {} waiting for {}", self.instruction, pending_str)
        else:
            self._log("Operands already available")

        # Wait for operands to be ready
        results = yield self.env.all_of(dependencies)
        if OP1_broadcast_event in results:
            self.OP1_val = results[OP1_broadcast_event].result
        if OP2_broadcast_event in results:
            self.OP2_val = results[OP2_broadcast_event].result

        self.FU = results[fu_request]

        if pending_operands:
            self._log("Operands of {} are now ready", self.instruction)

    def _reserve_functional_unit(self):
        struct_hazard = False
        if not self.cpu.alu_FU.items:
            self._log("Structural hazard: no FU free for {}", self)
            struct_hazard = True

        fu = yield self.cpu.alu_FU.get()

        if struct_hazard:
            self._log("Structural hazard solved, obtained {}", fu)
        else:
            self._log("Using {}", fu)

        return fu

    def _enqueue_control_flow_instruction(self):
        if isinstance(self.instruction, JumpInstruction):
            yield self.env.process(self._execute_jump_instruction())
        elif isinstance(self.instruction, BranchInstruction):
            yield self.env.process(self._execute_branch_instruction())
        else:
            raise NotImplementedError()

    def _execute_jump_instruction(self):
        # TODO: support indirect jumps like JMP R1
        self.FU = yield self.env.process(self._reserve_functional_unit())
        self._log("Starting execution of {}", self.instruction)
        yield self.env.timeout(self.instruction.latency)
        self._log("End execution of {}", self.instruction)
        self.result = self.instruction.address

    def _execute_branch_instruction(self):
        self._decode_operands()
        yield self.env.process(self._wait_for_dependencies())
        yield self.env.timeout(self.instruction.latency)
        self.result = self.instruction.result(self.OP1_val, self.OP2_val, self.reg_file["PC"])
        if self.result != self.reg_file["PC"]:
            self._log("End execution of {}, TAKEN, new PC is {}", self.instruction, self.result)
        else:
            self._log("End execution of {}, NOT TAKEN", self.instruction)

    def reset(self):
        super().reset()
        self.OP1_val = None
        self.OP2_val = None
        self.OP1_source_rs = None
        self.OP2_source_rs = None
        self.result = None
        self.result_broadcast_event = None
