# Contains all the global variables used in the code generator.

import tacinstr, codegen, machine, basicblock

# Variable to store the number of machine registers
numRegs = 6

# List of register names
regNames = ['eax', 'ebx', 'ecx', 'edx', 'esi', 'edi']

# Map from register names to register objects
registerMap = {}
for name in regNames:
    reg = Register(name)
    registerMap[name] = reg

# Object to instantiate the data section
data = Data()
