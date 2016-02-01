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


class Data(object):
    def __init__(self):
        self.dataDict = {}

    def allocateMem(self, name):
        self.dataDict["mem_" + name] = 0
        return "mem_" + name

    def isAllocated(self, name):
        return self.dataDict.get("mem_" + name) != None

    def assignVal(self, name, value):
        if self.isAllocated(self, name):
            self.dataDict["mem_" + name] = value
        else:
            pass    #handle error
    def getVal(self, name):
        if self.isAllocated(self, name):
            return self.dataDict["mem_" + name]
        else:
            pass    #handle error

    def generate(self):
        text = ".section .data\n"
        align = " "*4
        for key in self.dataDict.keys():
            text += key + ":\n" + align + ".long " + str(self.dataDict[key]) + "\n"
        return text
