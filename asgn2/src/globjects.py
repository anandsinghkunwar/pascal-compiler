# Contains all the global variables used in the code generator.

import machine

# Variable to store the number of machine registers
numRegs = 6

# List of register names
regNames = ['eax', 'ebx', 'ecx', 'edx', 'esi', 'edi']

# Map from register names to register objects
registerMap = {}

# Map from variable names to variable address descriptor
varMap = {}

# Object to instantiate the data section
data = machine.Data()
