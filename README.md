# Tomasulo simulator
This is a project for the ACA course of Politecnico di Milano.
It simulates a CPU at the functional-unit level, in order to test how the Tomasulo algorithm works, 
improving throughput while avoiding hazards.

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
First, edit `simulation.py` to include the assembly code you want to run and to tweak the CPU structure. 
See `cpu.py` for the possible parameters.
You also might want to modify the latency of some instructions, and should do that by modifying the relevant file in the `instruction` folder.
Then run with: 

```bash
python3 simulation.py
```

## Example run
The following assembly and parameters
```python
def print_cpu(cpu):
    print(cpu)
    
assembler = Assembler()
assembler += AddInstruction("R1", "R0", 1)
assembler += AddInstruction("R2", "R0", 1)
assembler += AddInstruction("R1", "R1", 1)
assembler += AddInstruction("R2", "R1", 1)
assembler += BreakpointInstruction(handler=print_cpu)
assembler += HaltInstruction()

DEFAULT_MEM_SIZE = 0x1000
DEFAULT_INT_REGS = 8
DEFAULT_CDB_WIDTH = 1
DEFAULT_ALU_RS = 2
DEFAULT_MEM_RS = 2
DEFAULT_ALU_FU = 1
DEFAULT_MEM_FU = 2
DEFAULT_FETCH_LATENCY = 1
``` 
produce this output:
```
CLK     0 | CPU | Fetching instruction at PC 0
CLK     1 | CPU | Fetched instruction ADD R1, R0, 1
CLK     1 | CPU | Issuing ADD R1, R0, 1 to RS1
CLK     1 | CPU | Fetching instruction at PC 1
CLK     1 | RS1 | Operands already available
CLK     1 | RS1 | Using ALU1
CLK     2 | CPU | Fetched instruction ADD R2, R0, 1
CLK     2 | CPU | Issuing ADD R2, R0, 1 to RS2
CLK     2 | CPU | Fetching instruction at PC 2
CLK     2 | RS2 | Operands already available
CLK     2 | RS2 | Structural hazard: no FU free for RS2
CLK     3 | RS1 | End execution of ADD R1, R0, 1
CLK     3 | CPU | Fetched instruction ADD R1, R1, 1
CLK     3 | CPU | Structural hazard: no RS found for ADD R1, R1, 1
CLK     3 | RS1 | Broadcasting result on CDB
CLK     3 | RS1 | Writing back result to R1 in the RF (no WAW detected)
CLK     3 | RS2 | Structural hazard solved, obtained ALU1
CLK     4 | CPU | Issuing ADD R1, R1, 1 to RS1
CLK     4 | CPU | Fetching instruction at PC 3
CLK     4 | RS1 | Operands already available
CLK     4 | RS1 | Structural hazard: no FU free for RS1
CLK     5 | RS2 | End execution of ADD R2, R0, 1
CLK     5 | CPU | Fetched instruction ADD R2, R1, 1
CLK     5 | CPU | Structural hazard: no RS found for ADD R2, R1, 1
CLK     5 | RS2 | Broadcasting result on CDB
CLK     5 | RS2 | Writing back result to R2 in the RF (no WAW detected)
CLK     5 | RS1 | Structural hazard solved, obtained ALU1
CLK     6 | CPU | Issuing ADD R2, R1, 1 to RS2
CLK     6 | CPU | Fetching instruction at PC 4
CLK     6 | RS2 | RAW: ADD R2, R1, 1 waiting for R1 from RS1
CLK     6 | RS2 | Structural hazard: no FU free for RS2
CLK     7 | RS1 | End execution of ADD R1, R1, 1
CLK     7 | CPU | Fetched instruction BREAK 
CLK     7 | CPU Registers: R0: 0, R1: RS1, R2: RS2, R3: 0, R4: 0, R5: 0, R6: 0, R7: 0, PC: 5
CLK     7 | CPU | Breakpoint hit
CLK     7 | CPU | Fetching instruction at PC 5
CLK     7 | RS1 | Broadcasting result on CDB
CLK     7 | RS1 | Writing back result to R1 in the RF (no WAW detected)
CLK     7 | RS2 | Structural hazard solved, obtained ALU1
CLK     7 | RS2 | Operands of ADD R2, R1, 1 are now ready
CLK     8 | CPU | Fetched instruction HLT 
CLK     8 | CPU | HLT found, stopping the issue of new instructions
CLK     9 | RS2 | End execution of ADD R2, R1, 1
CLK     9 | RS2 | Broadcasting result on CDB
CLK     9 | RS2 | Writing back result to R2 in the RF (no WAW detected)
CLK     9 | CPU Registers: R0: 0, R1: 2, R2: 3, R3: 0, R4: 0, R5: 0, R6: 0, R7: 0, PC: 6
```

## TODO
- document everything
- provide a better way to tune the CPU parameters then editing the `cpu.py` file
- provide a trace of the execution which resembles the ACA course exercises
- implement memory read/write instructions
- (maybe) move the execution of instructions to the functional units instead of the reservation stations
    - timings should not change, but it would better represent a real CPU
- lots and lots of other things
