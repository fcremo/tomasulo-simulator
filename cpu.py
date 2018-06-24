import simpy

from instruction import *
from registerfile import RegisterFile
from reservation_station import ALUReservationStation, MemReservationStation
from functionalunit import AluFU, MemFU
from log_utils import get_logger

from cdb import CDB


class CPU:
    DEFAULT_MEM_SIZE = 0x1000
    DEFAULT_INT_REGS_NUMBER = 8
    DEFAULT_CDB_WIDTH = 1
    DEFAULT_ALU_RS = 2
    DEFAULT_MEM_RS = 2
    DEFAULT_ALU_FU = 2
    DEFAULT_MEM_FU = 2
    DEFAULT_FETCH_CLOCKS = 1

    def __init__(self, env: simpy.Environment, instructions,
                 memory=bytearray(DEFAULT_MEM_SIZE),
                 reg_file=RegisterFile(DEFAULT_INT_REGS_NUMBER),
                 CDB_width=DEFAULT_CDB_WIDTH, fetch_clocks=DEFAULT_FETCH_CLOCKS,
                 alu_RS=DEFAULT_ALU_RS, mem_RS=DEFAULT_MEM_RS,
                 alu_FU=DEFAULT_ALU_FU, mem_FU=DEFAULT_MEM_FU,
                 breakpoint_handler=None
                 ):
        self.instructions = instructions
        self.next_instruction = None

        self.memory = memory
        self.reg_file = reg_file

        # Common data bus
        self.CDB = CDB(env, CDB_width)

        self.fetch_clocks = fetch_clocks

        self.alu_FU = [AluFU(env) for _ in range(alu_FU)]
        self.mem_FU = [MemFU(env) for _ in range(mem_FU)]

        self.alu_RS = [ALUReservationStation(env, self) for _ in range(alu_RS)]
        self.mem_RS = [MemReservationStation(env, self) for _ in range(mem_RS)]

        self.env = env

        if breakpoint_handler is None:
            self.breakpoint_handler = self._default_breakpoint_handler
        else:
            self.breakpoint_handler = breakpoint_handler

        self._log = get_logger(env, "CPU")

    def issue(self):
        while True:
            if self.can_fetch():
                self._log("Fetching instruction at PC {}", self.reg_file["PC"])
                self.next_instruction = self.instructions[self.reg_file["PC"]]
                yield self.env.timeout(self.fetch_clocks)
                self._log("Fetched instruction {}", self.next_instruction)
                self.reg_file["PC"] += 1
            else:
                self._log("Stall while fetching instruction")
                yield self.env.timeout(1)
                continue

            ni, self.next_instruction = self.next_instruction, None

            if isinstance(ni, HaltInstruction):
                self._log("HLT found, stopping the issue of new instructions")
                return

            if isinstance(ni, BreakpointInstruction):
                if ni.handler is not None:
                    ni.handler(self)
                self.breakpoint_handler(self)
                continue

            rs = self.find_free_reservation_station(ni)
            while rs is None:
                self._log("Structural conflict: no RS found for {}", ni)
                yield self.env.timeout(1)
                rs = self.find_free_reservation_station(ni)

            self._log("Issuing {} to {}", ni, rs)

            # Lock the reservation station
            rs_lock = rs.request()
            yield rs_lock
            # Send the instruction to the reservation station
            rs.enqueue_instruction(ni, rs_lock)

            if isinstance(ni, ControlFlowInstruction):
                self._log("Stalling fetches until the new PC is available")
                broadcast = yield rs.result_broadcast_event
                self.reg_file.values["PC"] = broadcast.result

    def find_free_reservation_station(self, instruction):
        if isinstance(instruction, AluInstruction):
            rs_list = self.alu_RS
        elif isinstance(instruction, MemInstruction):
            rs_list = self.mem_RS
        else:
            raise Exception("Unrecognized instruction: {}".format(instruction))

        for rs in rs_list:
            if rs.busy:
                continue
            else:
                return rs

        return None

    def run(self):
        yield self.env.process(self.issue())

    def can_fetch(self):
        return self.next_instruction is None

    @staticmethod
    def _default_breakpoint_handler(cpu):
        cpu._log("Breakpoint hit")

    def __repr__(self):
        return "CLK {:>5n} | CPU Registers: {}".format(self.env.now, self.reg_file)

