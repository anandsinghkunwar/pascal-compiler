# Main code generator module. Contains description of the
# symbol table, register descriptor, address descriptor.

import tacinstr, basicblock, machine

# Register descriptor: Modelled as a dictionary where each
# key is a register name and each corresponding value is
# varname where varname is the name of the
# variable contained in the register.

class RegDescriptor(object):
    def __init__(self):
        self.regDict = {}

    def addReg(self, regName):
        self.regDict[regName] = ''

    def allocateReg(self, regName, varName):
        self.regDict[regName] = varName

# Address descriptor: Modelled as a dictionary where each
# key is a variable name and each corresponding value is a
# set of all the locations where this variable's value can
# be found, e.g. register(s), memory address.

class AddrDescriptor(object):
    def __init__(self):
        self.addrDict = {}

    def addVar(self, varName, addr):
        self.addrDict[varName] = set([addr])

    def addLoc(self, varName, location):
        self.addrDict[varName].update([location])
