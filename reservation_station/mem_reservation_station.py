from instruction.mem_instructions import StoreInstruction, LoadInstruction
from .reservation_station import ReservationStation


class MemReservationStation(ReservationStation):
    kind = "MemRS"
    incremental_id = 1

    def __init__(self, env, cpu, fu_store, rs_store):
        super().__init__(env, cpu, fu_store, rs_store)
        self.offset_read = None
        self.src_read = None
        self.offset_val = None
        self.src_val = None
        self.address = None

    def _decode_operands(self):
        if isinstance(self.instruction, StoreInstruction):
            self.src_read = self._read_operand(self.instruction.src_reg)

        self.offset_read = self._read_operand(self.instruction.offset_reg)

        # Associate destination register with this reservation station in the RF
        if isinstance(self.instruction, LoadInstruction):
            self.cpu.reg_file.associate_rs_with_reg(self, self.instruction.dst_reg)

    def _wait_for_dependencies(self):
        dependencies = []

        if self.src_read is not None:
            dependencies.append(self.src_read)
        dependencies.append(self.offset_read)

        fu_request = self.env.process(self._get_functional_unit())
        dependencies.append(fu_request)

        dependencies.append(self.env.process(self.cpu.memory.wait_for_queue_turn(self)))

        results = yield self.env.all_of(dependencies)

        self.offset_val = results[self.offset_read]
        if self.src_read is not None:
            self.src_val = results[self.src_read]

        self.FU = results[fu_request]

        self.address = self.offset_val + self.instruction.base
        yield self.env.process(self.cpu.memory.address_resolution_complete(self))

        if isinstance(self.instruction, LoadInstruction):
            yield self.env.process(self.cpu.memory.wait_for_other_stores(self))
        else:
            yield self.env.process(self.cpu.memory.wait_for_other_accesses(self))

    def _execute(self):
        yield self.env.timeout(self._execution_latency())

        if isinstance(self.instruction, LoadInstruction):
            self.result = self.cpu.memory._memory[self.address]
        elif isinstance(self.instruction, StoreInstruction):
            self.cpu.memory._memory[self.address] = self.src_val
        else:
            raise ValueError("Unrecognized instruction")

        yield self.env.process(self.cpu.memory.memory_access_complete(self))

    def _writeback(self):
        return super()._writeback()

    def _reset(self):
        super()._reset()
        self.offset_read = None
        self.src_read = None
        self.offset_val = None
        self.src_val = None
        self.address = None
