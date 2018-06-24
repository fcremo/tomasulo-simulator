from . import ReservationStation


class MemReservationStation(ReservationStation):
    # TODO: finish implementing this

    def __init__(self, env, cpu):
        super().__init__(env, cpu)
        self.src_val = None
        self.src_rs = None
        self.addr = None

    def enqueue_instruction(self, instruction, lock_request):
        raise NotImplementedError()
