from collections import namedtuple
from json import JSONEncoder

import functional_unit
import instruction

RSUnavailableHazard = namedtuple("RSUnavailableHazard", "detected_at solved_at assigned_rs")
FUUnavailableHazard = namedtuple("FUUnavailableHazard", "detected_at solved_at assigned_fu")
CDBUnavailableHazard = namedtuple("CDBUnavailableHazard", "detected_at solved_at")
MemQueueSlotUnavailableHazard = namedtuple("MemQueueSlotUnavailableHazard", "detected_at solved_at")
RAWHazard = namedtuple("RAWHazard", "detected_at solved_at register source_rs")


class ExecutionTrace:
    def __init__(self, instruction):
        super().__init__()
        self.instruction = instruction
        self.hazards = []
        self.issued = None
        self.start_execution = None
        self.write_result = None
        self.written_result = None
        self.rs = None
        self.fu = None

    def to_dict(self):
        import reservation_station
        d = {}
        for k, v in self.__dict__.items():
            if isinstance(v, (reservation_station.ReservationStation, functional_unit.FunctionalUnit)):
                d[k] = v.id
            elif isinstance(v, instruction.Instruction):
                d[k] = str(v)
            else:
                d[k] = v
        return d


class ExecutionTraceSerializer(JSONEncoder):
    def default(self, obj):
        return obj.__repr__()

