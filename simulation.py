#!/usr/bin/env python3
import argparse
import json
import time
import IPython
import pandas as pd
import simpy

from parser import Parser
from assembler import assemble
from cpu_config import CpuConfig
from cpu import CPU
from execution_trace import ExecutionTraceSerializer


def main():
    print_figlet()

    with open(args.program) as f:
        program = f.read()

    directives, code = Parser().parse_code(program)
    instructions = assemble(code)
    config = CpuConfig(directives)

    if args.dump_assembled_instructions:
        print("Assembled instructions:")
        print(dump_instructions(instructions))

    env = simpy.Environment()
    # cpu = CPU(env, code, breakpoint_handler=spawn_ipython_handler)
    # cpu = CPU(env, code, breakpoint_handler=lambda cpu: print(cpu))
    cpu = CPU(env, instructions, config)

    run_simulation(env, cpu)
    collect_statistics(cpu)


def print_figlet():
    if not args.quiet:
        from pyfiglet import Figlet
        f = Figlet(font="nancyj-improved")
        print(f.renderText("Tomasulo simulator"))


def run_simulation(env, cpu):
    env.process(cpu.run())

    if args.step_by_step:
        while True:
            try:
                env.step()
            except simpy.core.EmptySchedule:
                break
            finally:
                print(cpu)

            if args.interactive:
                try:
                    spawn_ipython_handler(cpu)
                except Exception as e:
                    print(e)
    else:
        env.run()
        print(cpu)


def collect_statistics(cpu):
    stats = [i.stats.to_dict() for i in cpu.executed_instructions]
    if not args.no_stats:
        print_stats(stats)

    if args.output:
        filename = "./outputs/out_{:.0f}.json".format(time.time())
        with open(filename, "x") as f:
            json.dump(stats, f, cls=ExecutionTraceSerializer)


def print_stats(stats):
    columns = ["Instruction", "Issue", "Start exec.", "Write res.", "Written res.", "Hazards", "RS", "FU"]
    col_order = ["instruction", "issued", "start_execution", "write_result", "written_result", "hazards", "rs", "fu"]
    df = pd.DataFrame(stats).sort_values(by="issued")[col_order]
    pd.set_option('display.max_colwidth', -1)
    formatters = {
        "hazards": lambda hazards: " ".join([hazard.__repr__() for hazard in hazards])
    }
    print("\n")
    print(df.to_string(header=columns, justify="end", formatters=formatters))
    # TODO: print ClockPerInstruction/InstructionsPerClock


def spawn_ipython_handler(cpu):
    header = "The cpu variable contains a reference to the CPU instance.\nUse 'quit' to exit."
    IPython.embed(header=header)


def dump_instructions(instructions):
    return "\n".join([str(i) for i in instructions]) + "\n"


argparser = argparse.ArgumentParser(description="Tomasulo algorithm simulator")
argparser.add_argument("program", help="the assembly file to execute")
argparser.add_argument("--output", "-o", help="Output statistics to json")
argparser.add_argument("--no-stats", "-n", help="Don't output statistics on STDOUT", action="store_true")
argparser.add_argument("--interactive", "-i", help="Spawn IPython shell during the simulation", action="store_true")
argparser.add_argument("--step-by-step", "-s", help="Execute the simulation step by step", action="store_true")
argparser.add_argument("--dump-assembled-instructions", "-d", help="Print the assembled instructions", action="store_true")
argparser.add_argument("--quiet", "-q", help="Don't print the program logo", action="store_true")


if __name__ == "__main__":
    args = argparser.parse_args()
    main()
