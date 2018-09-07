from abc import ABC


class FunctionalUnit(ABC):
    def __init__(self, id):
        self.id = id

    def __str__(self):
        return self.id

    def __repr__(self):
        return self.id


class AluFU(FunctionalUnit):
    id_autoincrement = 1

    def __init__(self):
        id = "ALU" + str(AluFU.id_autoincrement)
        AluFU.id_autoincrement += 1
        super().__init__(id)


class MemFU(FunctionalUnit):
    id_autoincrement = 1

    def __init__(self):
        id = "MEM" + str(MemFU.id_autoincrement)
        MemFU.id_autoincrement += 1
        super().__init__(id)
