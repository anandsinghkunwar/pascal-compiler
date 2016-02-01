# Contains a model of the machine assembly code
#   - a class to implement machine registers
#   - a class to implement the (global) data region
#   - a class to implement the code section

import tacinstr, basicblock

# Global variable to store number of general purpose registers
numRegs = 6

# Global list of register names
registers = ['eax', 'ebx', 'ecx', 'edx', 'edi', 'esi']

# Class to implement machine registers.
class Register(object):
    def __init__(self, name):
        self.name = name
        self.value = 0
        self.empty = True
    
    def value(self):
        return self.value

    def isEmpty(self):
        return self.empty

    def spill(self):
        pass
