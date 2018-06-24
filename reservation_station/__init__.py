import simpy
from abc import *
from collections import namedtuple

from log_utils import get_logger

RSResult = namedtuple("RSResult", ["rs", "result"])


class ReservationStation(simpy.Resource, ABC):
    incremental_id = 1

    def __init__(self, env, cpu):
        super().__init__(env, capacity=1)
        self.env = env
        self.cpu = cpu
        self.reg_file = cpu.reg_file
        self.CDB = cpu.CDB
        self.alu_FU = cpu.alu_FU
        self.mem_FU = cpu.mem_FU

        self.instruction = None
        self.execution_process = None
        self.lock_req = None

        self.FU = None

        self.id = "RS" + str(self.incremental_id)
        ReservationStation.incremental_id += 1
        self._log = get_logger(env, self.id)

    def enqueue_instruction(self, instruction, lock_request):
        raise NotImplementedError()

    def reset(self):
        self.instruction = None
        self.execution_process = None
        self.FU = None

    @property
    def busy(self):
        return self.count > 0

    def __str__(self):
        return self.id

    def __repr__(self):
        return self.__str__()


# module level imports not at the beginning of the file to allow
# easier imports from outside the package while avoiding circular dependencies
from .alu_reservation_station import ALUReservationStation
from .mem_reservation_station import MemReservationStation
