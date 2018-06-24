#!/usr/bin/env python3

import simpy

from instruction import *
from cpu import CPU
from assembler import Assembler, Label
import IPython

INTERACTIVE = False
STEP_BY_STEP = False


def print_cpu(cpu):
    print(cpu)


def spawn_ipython(cpu):
    header = "The cpu variable contains a reference to the CPU instance.\nUse 'quit' to exit."
    IPython.embed(header=header)


def main():
    env = simpy.Environment()

    assembler = Assembler()
    assembler += AddInstruction("R1", "R0", 3)
    assembler += Label("LOOP")
    assembler += BLEInstruction("R1", 0, "END")
    assembler += AddInstruction("R2", "R2", 2)
    assembler += SubInstruction("R1", "R1", 1)
    assembler += BreakpointInstruction(handler=print_cpu)
    assembler += JumpInstruction("LOOP")
    assembler += Label("END")
    assembler += HaltInstruction()

    code = assembler.get_assembled_code()

    # cpu = CPU(env, code, breakpoint_handler=spawn_ipython)
    # cpu = CPU(env, code, breakpoint_handler=print_cpu)
    cpu = CPU(env, code)

    env.process(cpu.run())

    if STEP_BY_STEP:
        while True:
            try:
                env.step()
            except simpy.core.EmptySchedule:
                break
            finally:
                print(cpu)

            if INTERACTIVE:
                try:
                    spawn_ipython(cpu)
                except Exception as e:
                    print(e)
    else:
        env.run()
        print(cpu)

    if INTERACTIVE:
        spawn_ipython(cpu)


if __name__ == "__main__":
    main()
