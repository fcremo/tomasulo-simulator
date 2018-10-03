from collections import namedtuple

import simpy

from tomasulo_simulator.execution_trace import CDBUnavailableHazard
from tomasulo_simulator.log_utils import get_logger


class CDB(simpy.Resource):
    def __init__(self, env, width):
        super().__init__(env, width)
        self.env = env
        self.waiting = {}

        self.id = "CDB"
        self._log = get_logger(env, self.id)

    def write(self, tag, value):
        """Returns a Simpy process that writes a value to the CDB."""
        return self.env.process(self._write(tag, value))

    def write_with_conflict_detection(self, tag, value, rs):
        """Returns a Simpy process that writes a value to the CDB.
        It also detects and logs a conflict if the CDB is not immediately available."""
        return self.env.process(self._write(tag, value, rs))

    def _write(self, tag, value, rs=None):
        req = self.request()
        res = yield req | self.env.timeout(0)
        if req not in res:
            if rs is not None:
                self._log("Conflict: not immediately available for writing result of {} ({})", rs, rs.instruction)
            detected_at = self.env.now
            yield req
            if rs is not None:
                rs.instruction.stats.hazards.append(CDBUnavailableHazard(detected_at, self.env.now))

        self._log("Writing {}: {}", tag, value)
        # TODO: make CDB latency configurable
        yield self.env.timeout(1)
        events = self.waiting.get(tag, [])
        for event in events:
            event.succeed(CDBWrite(tag, value))
        self.waiting[tag] = []

        self.release(req)

    def snoop(self, tag):
        """Returns a Simpy process that waits until a value with the given tag is written to the CDB.
        The returned process yields the value written to the CDB."""
        events = self.waiting.get(tag, [])
        event = simpy.Event(self.env)
        events.append(event)
        self.waiting[tag] = events

        def _snoop():
            write = yield event
            return write.value

        return self.env.process(_snoop())

    @property
    def busy(self):
        return self.count >= self.capacity


CDBWrite = namedtuple("CDBWrite", ["tag", "value"])
