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

```bash
python3 simulation.py
```

## TODO
- document everything
- provide a better way to tune the CPU parameters then editing the `cpu.py` file
- provide a trace of the execution which resembles the ACA course exercises
- implement memory read/write instructions
- (maybe) move the execution of instructions to the functional units instead of the reservation stations
    - timings should not change, but it would better represent a real CPU
- lots and lots of other things
