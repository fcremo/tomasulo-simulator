from tomasulo_simulator import execution_trace as etrace
from tomasulo_simulator.log_utils import get_logger
from tomasulo_simulator.reservation_station import ReservationStation


class RegisterFile:
    """A CPU has N general purpose integer registers (R1-RN)
    M floating point registers (F1-FM) and the progam counter (PC)"""
    def __init__(self, env, cpu, general_purpose_regs, floating_point_regs):
        self.cpu = cpu
        self.general_purpose_regs = general_purpose_regs
        self.floating_point_regs = floating_point_regs

        self.values = {}
        for reg_number in range(general_purpose_regs):
            self.values["R"+str(reg_number)] = 0
        for reg_number in range(floating_point_regs):
            self.values["F" + str(reg_number)] = 0
        self.values["PC"] = 0

        self.env = env
        self.id = "RF"
        self._log = get_logger(env, self.id)

    def associate_rs_with_reg(self, rs, reg_name):
        self[reg_name] = rs
        self.env.process(self._wait_for_result_to_update_register(rs, reg_name))

    def read_register(self, reg_name):
        src = self[reg_name]

        def _read_register():
            if isinstance(src, int):
                yield self.env.timeout(1)
                return src
            elif isinstance(src, ReservationStation):
                value = yield self.cpu.CDB.snoop(src)
                return value

        return self.env.process(_read_register())

    def read_register_with_raw_detection(self, reg_name, rs):
        src = self[reg_name]

        if isinstance(src, int):
            def _read_register():
                yield self.env.timeout(1)
                return src

            return self.env.process(_read_register())
        elif isinstance(src, ReservationStation):
            detected_at = self.env.now
            process = self.cpu.CDB.snoop(src)

            def _read_register():
                value = yield process
                rs.instruction.stats.hazards.append(etrace.RAWHazard(detected_at, self.env.now, reg_name, rs))
                return value

            return self.env.process(_read_register())

    def _wait_for_result_to_update_register(self, rs, reg_name):
        instruction = rs.instruction
        value = yield self.cpu.CDB.snoop(rs)
        self._log("Got result of {} ({}) from CDB ({})", instruction, value, rs)
        if self[reg_name] is rs:
            self._log("Writing back the result to the RF")
            self[reg_name] = value
        else:
            self._log("Not writing back result (another RS is associated to the register)")

    def _is_valid_register(self, reg_name):
        return self._is_valid_integer_register(reg_name) \
               or self._is_valid_floating_point_register(reg_name) \
               or reg_name == "PC"

    def _is_valid_integer_register(self, reg_name):
        if not reg_name.startswith("R"):
            return False

        reg_number = int(reg_name[1:])
        if not 0 <= reg_number < self.general_purpose_regs:
            return False

        return True

    def _is_valid_floating_point_register(self, reg_name):
        if not reg_name.startswith("F"):
            return False

        reg_number = int(reg_name[1:])
        if not 0 <= reg_number < self.floating_point_regs:
            return False

        return True

    def __getitem__(self, reg_name):
        if type(reg_name) is not str:
            raise KeyError("Register name must be a string")

        reg_name = reg_name.upper()
        if not self._is_valid_register(reg_name):
            raise KeyError("Register {} is not valid".format(reg_name))

        return self.values.get(reg_name)

    def __setitem__(self, reg_name, value):
        if type(reg_name) is not str:
            raise KeyError("Register name must be a string")

        reg_name = reg_name.upper()
        if not self._is_valid_register(reg_name):
            raise KeyError("Register {} is not valid".format(reg_name))

        if reg_name == "R0":
            raise KeyError("Cannot write register R0")

        self.values[reg_name] = value

    def __repr__(self):
        return ", ".join(["{}: {}".format(name, val) for name, val in self.values.items()])
