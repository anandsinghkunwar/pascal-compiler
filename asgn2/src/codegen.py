# Main code generator module. Contains description of the
# symbol table, register descriptor, address descriptor.
import tacinstr, basicblock, machine, globjects
from itertools import tee, izip

# Class to define the code generator
class Codegen(object):
    def __init__(self, program):
        self.program = program
        self.basicBlocks = []
        for regName in globjects.regNames:
            globjects.registerMap[regName] = machine.Register(regName)
        globjects.data = machine.Data()
        self.computeBasicBlocks()

    # Method to compute basic blocks from the IR program
    def computeBasicBlocks(self):
        leaders = set([1, len(self.program)+1])
        for instr in self.program:      #Yet to add for calling/return statements
            if instr.isIfGoto() or instr.isGoto():
                leaders.add(instr.Target)
                leaders.add(instr.LineNo + 1)
        for leaderPair in pairwise(leaders):
            bb = basicblock.BasicBlock(self.program[leaderPair[0]-1:leaderPair[1]-1])
            self.basicBlocks.append(bb)

# Auxiliary function
def pairwise(iterable):
    a, b = tee(iterable)
    next(b, None)
    return izip(a, b)
