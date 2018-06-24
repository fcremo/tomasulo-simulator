from abc import *

from simpy import Resource


class FunctionalUnit(Resource, ABC):
    def __init__(self, env, id):
        super().__init__(env)
        self.env = env
        self.id = id

    @property
    def busy(self):
        return self.count > 0

    def __str__(self):
        return self.id

    def __repr__(self):
        return self.id


class AluFU(FunctionalUnit):
    id_autoincrement = 1

    def __init__(self, env):
        id = "ALU" + str(AluFU.id_autoincrement)
        AluFU.id_autoincrement += 1
        super().__init__(env, id)


class MemFU(FunctionalUnit):
    id_autoincrement = 1

    def __init__(self, env):
        id = "MEM" + str(MemFU.id_autoincrement)
        MemFU.id_autoincrement += 1
        super().__init__(env, id)
