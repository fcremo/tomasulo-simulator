from abc import ABC, abstractmethod
from collections import namedtuple

import execution_trace as etrace
from log_utils import get_logger


class ReservationStation(ABC):
    kind = "RS"
    incremental_id = 1

    def __init__(self, env, cpu, fu_store, rs_store):
        self.id = self.__class__.kind + str(self.__class__.incremental_id)
        self.__class__.incremental_id += 1

        self.env = env
        self.cpu = cpu

        self.instruction = None
        self.FU = None
        self.result = None

        self.fu_store = fu_store
        self.rs_store = rs_store

        self._log = get_logger(env, self.id)

    def issue(self, instruction):
        """Issues an instruction to the reservation station,
        and returns a process which terminates when execution is complete"""
        self.instruction = instruction

        # Log instruction issue
        instruction.stats.issued = self.env.now
        instruction.stats.rs = self

        # Immediately decode the operands
        self._decode_operands()

        return self._execution_process()

    @abstractmethod
    def _decode_operands(self):
        """This method must be implemented by every reservation station.
        It should immediately decode the operands of the instruction."""
        raise NotImplementedError()

    def _read_operand(self, operand):
        """Helper method which returns a process that will wait until the operand is ready and return it"""
        # If the operand is an immediate value then return it after a timeout to simulate decode times.
        if isinstance(operand, int):
            def process():
                # TODO: make immediate operand read _execution_latency configurable
                yield self.env.timeout(1)
                return operand
            return self.env.process(process())
        # Otherwise the operand must be a register name,
        # so ask the register file for the register value
        elif isinstance(operand, str):
            return self.cpu.reg_file.read_register_with_raw_detection(operand, self)
        else:
            raise Exception("Operand type incorrect")

    def _execution_process(self):
        yield self.env.process(self._wait_for_dependencies())
        self._log("All dependencies for {} are ready (using {})", self.instruction, self.FU)

        # Log start of execution
        self._log("Starting execution phase of {}", self.instruction)
        self.instruction.stats.start_execution = self.env.now
        self.instruction.stats.fu = self.FU
        yield self.env.process(self._execute())

        self._log("End execution of {}, starting writeback phase", self.instruction)
        yield self.env.process(self._writeback())

        self.instruction.stats.written_result = self.env.now

        # Append the instruction to the execution trace list
        self.cpu.executed_instructions.append(self.instruction)

        fu = self.FU
        # Reset RS before releasing it
        self._reset()

        # return the FU and RS to the CPU
        yield self._return_to_cpu(fu)

    def _get_functional_unit(self):
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
        store_req_start = self.env.now
        req = self.fu_store.get()
        results = yield self.env.any_of([req, self.env.timeout(0)])

        if req in results:
            hazard = False
            obtained_fu = req.value
        else:
            self._log("Structural hazard: no FU available for {}", self.instruction)
            hazard = True
            obtained_fu = yield req

        if hazard:
            self._log("Structural hazard solved: obtained {} for {}", obtained_fu, self.instruction)
            self.instruction.stats.hazards.append(etrace.FUUnavailableHazard(store_req_start, self.env.now, obtained_fu))

        return obtained_fu

    @abstractmethod
    def _wait_for_dependencies(self):
        """This method must be implemented by all reservation stations.
        It should wait for all dependencies necessary before executing the instruction (operands, FU, and others)"""
        raise NotImplementedError()

    @abstractmethod
    def _execute(self):
        """This method must be implemented by all reservation stations.
        It should execute the instruction and save the result in self.result"""
        raise NotImplementedError()

    def _writeback(self):
        self.instruction.stats.write_result = self.env.now
        if self.result is not None:
            yield self.cpu.CDB.write_with_conflict_detection(self, self.result, self)
        else:
            yield self.env.timeout(1)

    def _execution_latency(self):
        instruction_latency = self.instruction.latency(self.cpu.config)
        if instruction_latency is not None:
            return instruction_latency

        for c in self.__class__.__mro__:
            if c is ReservationStation:
                raise Exception("Latency not defined for instruction {}".format(self.instruction.mnemonic))

            latency = self.cpu.config[self.kind.lower() + "_execution_latency"]
            if latency is not None:
                return latency

        raise Exception("Latency not defined for instruction {}".format(self.instruction.mnemonic))

    def _return_to_cpu(self, fu):
        """Returns itself and the functional unit to the CPU after execution is complete"""
        return self.env.all_of([self.fu_store.put(fu), self.rs_store.put(self)])

    @abstractmethod
    def _reset(self):
        self.instruction = None
        self.FU = None
        self.result = None

    def __str__(self):
        return self.id

    def __repr__(self):
        return self.__str__()


RegReadResult = namedtuple("RegReadResult", ["rs", "result"])
