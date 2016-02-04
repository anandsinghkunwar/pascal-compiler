# Contains all the global variables used in the code generator.

import tacinstr, codegen, machine, basicblock

# Variable to store the number of machine registers
numRegs = 6

# List of register names
regNames = ['eax', 'ebx', 'ecx', 'edx', 'esi', 'edi']

# Map from register names to register objects
registerMap = {}

# Set of variables
variables = set()

# Map from variable names to variable objects
varMap = {}

# Object to instantiate the data section
data = machine.Data()
