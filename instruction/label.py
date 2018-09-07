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
