# Contains all the global variables used in the code generator.

# Variable to store the number of machine registers
numRegs = 6

# List of register names
regNames = ['eax', 'ebx', 'ecx', 'edx', 'esi', 'edi']

# Map from register names to register objects
registerMap = {}

# Map from variable names to variable address descriptor
varMap = {}

# Object to instantiate the data section
data = None

# Object to instantiate the text section
text = None

# Current Instruction Variable
currInstr = None

# Set of Targets
targetSet = set()

# Set of Labels
labelSet = set()

# Error handling function
def halt(lineNo, errorMsg):
    print str(lineNo) + ": " + errorMsg + "\n"
    exit()
