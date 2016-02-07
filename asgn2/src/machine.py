import globjects

# Contains a model of the machine assembly code
#   - a class to implement machine registers
#   - a class to implement the (global) data region
#   - a class to implement the code section

# Class to implement machine registers.
# The member variable varNames acts as a register descriptor,
# which keeps track of the set of variable names that the
# register holds.
class Register(object):
    def __init__(self, name):
        self.name = name
        self.varNames = set()

    def isEmpty(self):
        return len(self.varNames) == 0

    def addVar(self, varName):
        self.varNames.add(varName)
        globjects.varMap[varName].reg = self

    def removeVar(self, varName):
        self.varNames.remove(varName)
        globjects.varMap[varName].reg = None

    def spill(self):
        for varName in self.varNames:
            globjects.varMap[varName].reg = None
        self.varNames = set()
        # TODO :add mov instruction


# Class to implement the global data region. For now, we allow
# only integers to be allocated.
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
