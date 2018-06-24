from abc import *

from simpy import Resource


class FunctionalUnit(Resource, ABC):
    def __init__(self, env):
        super().__init__(env)
        self.env = env

    @property
    def busy(self):
        return self.count > 0


class AluFU(FunctionalUnit):
    id_autoincrement = 1

    def __init__(self, env):
        super().__init__(env)
        self.id = "ALU" + str(AluFU.id_autoincrement)
        AluFU.id_autoincrement += 1


class MemFU(FunctionalUnit):
    id_autoincrement = 1

    def __init__(self, env):
        super().__init__(env)
        self.id = "MEM" + str(MemFU.id_autoincrement)
        MemFU.id_autoincrement += 1
