import instruction


class Assembler:
    def __init__(self):
        self.code = []
        self.labels = {}

    def get_assembled_code(self):
        assembled = []
        for i in self.code:
            if isinstance(i, instruction.ControlFlowInstruction):
                try:
                    i.address = self.labels.get(i.label)
                except KeyError:
                    raise RuntimeError("Label {} is not declared".format(i.label))

            assembled.append(i)

        return assembled

    def __add__(self, code):
        if isinstance(code, Label):
            self.labels[code.id] = len(self.code)

        elif isinstance(code, instruction.Instruction):
            self.code.append(code)

        return self


class Label:
    def __init__(self, id):
        self.id = id

    def __repr__(self):
        return "LAB {}".format(self.id)

    def __str__(self):
        return str(self.id)

    def __hash__(self):
        return self.id.__hash__()

    def __eq__(self, other):
        if isinstance(other, Label):
            return self.id == other.id

        return other == self.id
