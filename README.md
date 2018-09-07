# Tomasulo simulator
This is a project for the Advanced Computer Architectures course of Politecnico di Milano.
It simulates the Tomasulo algorithm which is used in CPUs to improve throughput while avoiding hazards.
It was implemented following the course slides and also [this document](https://cseweb.ucsd.edu/classes/fa07/cse240a/Papers/tomasulo.pdf),
but changes were made where appropriate for simplicity.

## How to run
**This project requires python 3.6+**

### Virtualenv (optional)
I highly suggest creating a virtualenv in order to keep your system clean.
You can do it in many ways, my preferred is using virtualenvwrapper.
Follow [this guide](http://docs.python-guide.org/en/latest/dev/virtualenvs/#virtualenvwrapper) to install it, then create and activate the virtualenv with
```bash
mkvirtualenv tomasulo-simulator
workon tomasulo-simulator
```

You can exit the virtualenv with `deactivate`, and delete the virtualenv with `rmvirtualenv tomasulo-simulator`

### Installing required libraries
```bash
pip install -r requirements.txt
```

### Running
```
usage: simulation.py [-h] [--output OUTPUT] [--no-stats] [--interactive]
                     [--step-by-step] [--dump-assembled-instructions]
                     [--quiet]
                     program

Tomasulo algorithm simulator

positional arguments:
  program               the assembly file to execute

optional arguments:
  -h, --help            show this help message and exit
  --output OUTPUT, -o OUTPUT
                        Output statistics to json
  --no-stats, -n        Don't output statistics on STDOUT
  --interactive, -i     Spawn IPython shell during the simulation
  --step-by-step, -s    Execute the simulation step by step
  --dump-assembled-instructions, -d
                        Print the assembled instructions
  --quiet, -q           Don't print the program logo
```

See the `examples` directory for examples on how to write assembly for the machine.

## TODO
- document everything
- (maybe) move the execution of instructions to the functional units instead of the reservation stations
    - timings should not change, but it would better represent a real CPU
- implement reorder buffer
- implement speculation (issue-wise and execution-wise)
- write tests and a way to run them
- implement NOT instruction
- finish implementing floating point instructions
- indirect jumps (e.g. `JMP R1`)
- allow load/stores like `LD R1, [R2]`
