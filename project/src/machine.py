import globjects as G

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
        G.varMap[varName].reg = self

    def removeVar(self, varName):
        self.varNames.remove(varName)
        G.varMap[varName].reg = None

    def spill(self):
        for varName in self.varNames:
            G.varMap[varName].reg = None
            if G.varMap[varName].isLocal:
                G.text.string += " "*4 + "movl %" + self.name + ", " + str(G.varMap[varName].offset) + '(%ebp)' + " "*4 + "#Spilling register\n"
            else:
                G.text.string += " "*4 + "movl %" + self.name + ", " + varName + " "*4 + "#Spilling register\n"
        self.varNames = set()

    def dump(self):
        for varName in self.varNames:
            G.text.string += " "*4 + "movl %" + self.name + ", " + varName + " "*4 + "#Dumping register\n"

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
        dataString = ".section .data\n"
        indent = " "*4
        for key in self.dataDict.keys():
            if key is not None:
                dataString += key + ":\n"
                if type(self.dataDict[key]) == int:
                    dataString += indent + ".long " + str(self.dataDict[key]) + "\n"
                elif type(self.dataDict[key]) == str:
                    fmtString = self.dataDict[key]
                    dataString += indent + ".ascii " + str(fmtString[:-1]) + "\\0\"\n"
        return dataString

    def printDataSection(self):
        print self.generate()

# Class to implement the text region.
class Text(object):
    def __init__(self):
        self.string = ''

    def generate(self):
        textString = ".section .text\n"
        indent = " "*4
        textString += indent + ".extern printf\n"
        textString += indent + ".extern scanf\n"
        textString += indent + ".extern malloc\n"
        textString += indent + ".globl main\n\n"
        textString += "main: \n"
        textString += indent + "pushl %ebp" + indent + "#treating main as a function\n"
        textString += indent + "movl %esp, %ebp" + indent + "#treating main as a function\n"
        textString += self.string
        return textString

    def printTextSection(self):
        print self.generate()
