# Main code generator module. Contains description of the
# symbol table, register descriptor, address descriptor.
import basicblock, machine, globjects, translate
import ircodegen as IG
from itertools import tee, izip

# Class to define the code generator
class Codegen(object):
    def __init__(self, program):
        self.program = program
        self.basicBlocks = []
        for regName in globjects.regNames:
            globjects.registerMap[regName] = machine.Register(regName)
        self.computeBasicBlocks()
        globjects.data.printDataSection()
        print "\n"
        globjects.text.printTextSection()

    # Method to compute basic blocks from the IR program
    def computeBasicBlocks(self):
        leaders = set([1, len(self.program)+1])
        for instr in self.program:
            if instr.isIfGoto() or instr.isGoto():
                leaders.add(instr.Target)
                leaders.add(instr.LineNo + 1)
            if instr.isCall() or instr.isReturn():
                leaders.add(instr.LineNo + 1)
            if instr.isLabel():
                leaders.add(instr.LineNo)
            if instr.isAssign() and instr.Op == IG.TACInstr.CALLOP:
                leaders.add(instr.LineNo + 1)
        for leaderPair in pairwise(leaders):
            bb = basicblock.BasicBlock(self.program[leaderPair[0]-1:leaderPair[1]-1])
            self.basicBlocks.append(bb)
        for basicBlock in self.basicBlocks:
            translate.translateBlock(basicBlock)

# Class to implement address descriptor table entry for variables
class AddrDescEntry(object):
    def __init__(self, name, type):
        self.name = name
        self.dataType = type
        self.reg = None
        self.memAddr = globjects.data.allocateMem(self.name)
        self.dirty = False

    def loadIntoReg(self, regName):
        self.removeReg()
        globjects.registerMap[regName].addVar(self.name)

    def removeReg(self):
        if self.reg:
            self.reg.removeVar(self.name)

# Auxiliary function
def pairwise(iterable):
    a, b = tee(iterable)
    next(b, None)
    return izip(a, b)
