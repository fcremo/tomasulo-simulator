from copy import deepcopy

import simpy

import execution_trace as etrace
from cpu_config import CpuConfig
from cdb import CDB
from functional_unit import AluFU, MemFU
from instruction import (
    HaltInstruction, BreakpointInstruction,
    ControlFlowInstruction, MemInstruction,
    AluInstruction, FloatingInstruction
)
from log_utils import get_logger
from memory import Memory
from registerfile import RegisterFile
from reservation_station import ALUReservationStation, MemReservationStation


class CPU:
    def __init__(self, env: simpy.Environment, instructions, config: CpuConfig, breakpoint_handler=None):
        self._instructions = instructions
        self.config = config

        self.memory = Memory(env, config)
        self.reg_file = RegisterFile(env, self, config.gp_registers, config.fp_registers)

        # Common data bus
        self.CDB = CDB(env, config.cdb_width)

        # TODO: distinguish ALU from FPALU
        self.alu_FU = simpy.Store(env)
        [self.alu_FU.put(AluFU()) for _ in range(config.alu_fu)]
        self.fpalu_FU = simpy.Store(env)
        [self.fpalu_FU.put(AluFU()) for _ in range(config.fpalu_fu)]
        self.mem_FU = simpy.Store(env)
        [self.mem_FU.put(MemFU()) for _ in range(config.mem_fu)]

        self.alu_RS = simpy.Store(env)
        [self.alu_RS.put(ALUReservationStation(env, self, self.alu_FU, self.alu_RS)) for _ in range(config.alu_rs)]
        self.fpalu_RS = simpy.Store(env)
        [self.fpalu_RS.put(ALUReservationStation(env, self, self.fpalu_FU, self.fpalu_RS)) for _ in range(config.fpalu_rs)]
        self.mem_RS = simpy.Store(env)
        [self.mem_RS.put(MemReservationStation(env, self, self.mem_FU, self.mem_RS)) for _ in range(config.mem_rs)]

        # This list will hold the executed instructions
        self.executed_instructions = []

        self.env = env

        if breakpoint_handler is None:
            self.breakpoint_handler = self._default_breakpoint_handler
        else:
            self.breakpoint_handler = breakpoint_handler

        self._log = get_logger(env, "CPU")

    def _dispatch(self):
        while True:
            self._log("Fetching instruction at PC {}", self.reg_file["PC"])
            yield self.env.timeout(self.config.fetch_latency)

            # TODO: find a better way to log execution traces without deepcopying the instruction object
            # Right now the object is copied so stats can be saved directly into it, and it works even for
            # tight loops where the same instruction may be executing many times simultaneously
            try:
                next_instruction = deepcopy(self._instructions[self.reg_file["PC"]])
            except IndexError:
                self._log("WARNING: PC {} is out of range", self.reg_file["PC"])
                self._log("Use HLT instructions")
                return

            self._log("Fetched {}", next_instruction)
            self.reg_file["PC"] += 1

            if isinstance(next_instruction, HaltInstruction):
                return

            if isinstance(next_instruction, BreakpointInstruction):
                if next_instruction.handler is not None:
                    next_instruction.handler(self)
                self.breakpoint_handler(self)
                continue

            # Get an appropriate reservation station
            rs = yield self.env.process(self.get_reservation_station(next_instruction))

            # Loads and stores also need a spot in the memory access queue
            if isinstance(rs, MemReservationStation):
                yield self.env.process(self.memory.enqueue_memory_access(rs, next_instruction))

            # Issue the instruction to the reservation station
            self._log("Issuing {} to {}", next_instruction, rs)
            self.env.process(rs.issue(next_instruction))

            # TODO: log fetch stall (as conflict)
            # TODO: implement speculative execution
            if isinstance(next_instruction, ControlFlowInstruction):
                self._log("Stalling fetches until the new PC is available")
                self.reg_file.values["PC"] = yield self.CDB.snoop(rs)

    def get_reservation_station(self, instruction):
        if isinstance(instruction, AluInstruction):
            if isinstance(instruction, FloatingInstruction):
                rs_store = self.fpalu_RS
            else:
                rs_store = self.alu_RS
        elif isinstance(instruction, MemInstruction):
            rs_store = self.mem_RS
        else:
            raise Exception("Unrecognized instruction: {}".format(instruction))

        # FIXME
        # this code sucks a bit, but it's necessary to detect
        # structural hazards immediately to print them in order.
        # Checking if rs_store.items is empty does not work, as
        # an RS may be be relased right after we yield so no conflict is happening
        # The idea is to check if the request is granted in zero time,
        # but any_of is not guaranteed to yield both the resource request and the timeout
        # at the same time (as in in a single call), even if they will trigger at the same
        # simulation time.
        # Possible definitive solutions:
        # 1) ignore the problem and not print conflicts in real time
        # 2) use a 0.1 clock-cycles timeout (so the resource request will be granted first if any is available)
        store_req_start = self.env.now
        rs_req = rs_store.get()
        res = yield self.env.any_of([rs_req, self.env.timeout(0)])

        if rs_req in res:
            hazard = False
            obtained_rs = rs_req.value
        else:
            self._log("Structural hazard: no RS available for {}", instruction)
            hazard = True
            obtained_rs = yield rs_req

        if hazard:
            self._log("Structural hazard solved: obtained {} for {}", obtained_rs, instruction)
            instruction.stats.hazards.append(etrace.RSUnavailableHazard(store_req_start, self.env.now, obtained_rs))

        return obtained_rs

    def run(self):
        self._log("Starting instruction dispatch")
        yield self.env.process(self._dispatch())
        self._log("Stopped instruction dispatch")

    def dump_memory(self):
        for addr in range(0, len(self.memory._memory), 4):
            contents = ["0x{:0>2x}".format(m) for m in self.memory._memory[addr:addr + 4]]
            print("0x{:x}: ".format(addr).ljust(6) + " ".join(contents))

    @staticmethod
    def _default_breakpoint_handler(cpu):
        cpu._log("Breakpoint hit, registers: {}", cpu.reg_file)

    def __repr__(self):
        return "CLK {:>3n} | CPU Registers: {}".format(self.env.now, self.reg_file)
