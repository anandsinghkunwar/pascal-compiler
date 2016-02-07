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
            print " "*4 + "movl %" + self.name + "," + varname + " "*4 + ";Spilling register\n"
        self.varNames = set()


# Class to implement the global data region. For now, we allow
# only integers to be allocated.
class Data(object):
    def __init__(self):
        self.dataDict = {}

    def allocateMem(self, name, value=0):
        self.dataDict[name] = value
        return name

    def isAllocated(self, name):
        return self.dataDict.get(name) != None

    def generate(self):
        text = ".section .data\n"
        indent = " "*4
        for key in self.dataDict.keys():
            text += key + ":\n"
            if type(self.dataDict[key]) == int:
                text += indent + ".long " + str(self.dataDict[key]) + "\n"
            elif type(self.dataDict[key]) == str:
                text += indent + ".ascii" + str(self.dataDict[key]) + "\n"
        return text

    def printDataSection(self):
        print self.generate()
