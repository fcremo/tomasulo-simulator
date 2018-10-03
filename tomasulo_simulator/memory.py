import simpy

from tomasulo_simulator import execution_trace as etrace
from tomasulo_simulator.cpu_config import CpuConfig
from tomasulo_simulator.instruction import StoreInstruction
from tomasulo_simulator.log_utils import get_logger


class Memory:
    def __init__(self, env, config: CpuConfig, default_val=0):
        self.env = env
        self._access_queue = simpy.Store(env, config.mem_access_queue_size)
        self._access_queue_pop_event = simpy.Event(env)
        self._accesses_in_execution = simpy.FilterStore(env)
        self._accesses_in_execution_pop_event = simpy.Event(env)

        self.id = "MEM"
        self._memory = [default_val] * config.mem_size
        self._log = get_logger(env, self.id)

    def enqueue_memory_access(self, rs, instruction):
        # FIXME
        # this code sucks a bit, but it's necessary to detect
        # structural hazards immediately to print them in order.
        # Checking if fu_store.items is empty does not work, as
        # a FU may be be relased right after we yield so no conflict is happening
        # The idea is to check if the request is granted in zero time,
        # but any_of is not guaranteed to yield both the resource request and the timeout
        # at the same time (as in in a single call), even if they will trigger at the same
        # simulation time.
        # Possible definitive solutions:
        # 1) ignore the problem and not print conflicts in real time
        # 2) use a 0.1 clock-cycles timeout (so the resource request will be granted first if any is available)
        req_start = self.env.now
        req = self._access_queue.put(rs)
        results = yield self.env.any_of([req, self.env.timeout(0)])

        if req in results:
            hazard = False
        else:
            self._log("Structural hazard: no slots in the memory access queue available for {}", instruction)
            hazard = True
            yield req

        if hazard:
            self._log("Structural hazard solved, found a slot in the mem access queue")
            instruction.stats.hazards.append(etrace.MemQueueSlotUnavailableHazard(req_start, self.env.now))

    def wait_for_queue_turn(self, rs):
        current_rs = self._access_queue.items[0]
        while current_rs != rs:
            yield self._access_queue_pop_event
            current_rs = self._access_queue.items[0]

    def address_resolution_complete(self, rs):
        current_rs = yield self._access_queue.get()
        if rs != current_rs:
            raise Exception("Wrong order!")

        ev, self._access_queue_pop_event = self._access_queue_pop_event, simpy.Event(self.env)
        yield self._accesses_in_execution.put(rs)
        ev.succeed()

    def _has_to_wait_for_stores(self, rs):
        # FIXME: I suspect there's a potential deadlock if more than two dependent instructions get queued up
        # Should check only the addreses of reservation stations which had their instruction issued before ours
        for other_rs in self._accesses_in_execution.items:
            if (other_rs != rs and
                    isinstance(other_rs.instruction, StoreInstruction) and
                    other_rs.address == rs.address):
                return True
        return False

    def wait_for_other_stores(self, rs):
        # FIXME: I suspect there's a potential deadlock if more than two dependent instructions get queued up
        # Should check only the addreses of reservation stations which had their instruction issued before ours
        while self._has_to_wait_for_stores(rs):
            yield self._accesses_in_execution_pop_event

    def _has_to_wait_for_other_accesses(self, rs):
        for other_rs in self._accesses_in_execution.items:
            if other_rs != rs and other_rs.address == rs.address:
                return True
        return False

    def wait_for_other_accesses(self, rs):
        while self._has_to_wait_for_other_accesses(rs):
            yield self._accesses_in_execution_pop_event

    def memory_access_complete(self, rs):
        if rs not in self._accesses_in_execution.items:
            raise Exception("Something's wrong, please report this event as a bug")

        ev, self._accesses_in_execution_pop_event = self._accesses_in_execution_pop_event, simpy.Event(self.env)
        yield self._accesses_in_execution.get(lambda x: x == rs)
        ev.succeed()

    def __str__(self):
        return self.id

    def __repr__(self):
        return self.__str__()
