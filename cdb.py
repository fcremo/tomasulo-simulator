import simpy


class CDB(simpy.Resource):
    def __init__(self, env, width):
        super().__init__(env, width)

    @property
    def busy(self):
        return self.count >= self.capacity
