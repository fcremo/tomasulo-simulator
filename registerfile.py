class RegisterFile:
    """A CPU has N general purpose integer registers, R1-RN, and the progam counter (PC)"""
    def __init__(self, n_general_purpose):
        self.values = dict()
        self.n_general_purpose = n_general_purpose

        for reg_number in range(0, n_general_purpose):
            self.values["R"+str(reg_number)] = 0

        self.values["PC"] = 0

    def _is_valid_register(self, reg_name):
        return self._is_valid_integer_register(reg_name) or reg_name == "PC"

    def _is_valid_integer_register(self, reg_name):
        if not reg_name.startswith("R"):
            return False

        reg_number = int(reg_name[1:])
        if not 0 <= reg_number < self.n_general_purpose:
            return False

        return True

    def __getitem__(self, reg_name):
        if type(reg_name) is not str:
            raise KeyError("Register name must be a string")

        regname = reg_name.upper()
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
