from tomasulo_simulator import instruction


class Assembler:
    def __init__(self):
        self.code = []
        self.labels = {}

    def get_assembled_code(self):
        assembled = []
        for i in self.code:
            if isinstance(i, instruction.ControlFlowInstruction):
                try:
                    i.address = self.labels[i.label]
                except KeyError:
                    raise RuntimeError("Label {} is not declared".format(i.label))

            assembled.append(i)

        return assembled

    def set_code(self, code):
        for c in code:
            self.__add__(c)

    def __add__(self, code):
        if isinstance(code, instruction.Label):
            self.labels[code.id] = len(self.code)

        elif isinstance(code, instruction.Instruction):
            self.code.append(code)

        return self


def assemble(instructions):
    assembler = Assembler()
    assembler.set_code(instructions)
    return assembler.get_assembled_code()
