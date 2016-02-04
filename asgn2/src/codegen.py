# Main code generator module. Contains description of the
# symbol table, register descriptor, address descriptor.

import tacinstr, basicblock, machine

# Class to define the code generator
class Codegen(object):
    def __init__(self, program):
        self.program = program
        self.basicBlocks = []
    # Method to compute basic blocks from the IR program
    def getBasicBlocks(self):
        leaders = set()

        for instr in self.program:      #Yet to add for calling/return statements
            if instr.isIfGoto() or instr.isGoto():
                leaders.add(instr.Target)
                leaders.add(instr.LineNo + 1)
        basicBlocks = []
        prev = 0
        for l in leaders:
            basicBlocks.append(self.prog[prev:l-1])   #all this assuming program 
                                                    # is sorted acc. to line number
            prev = l-1
        basicBlocks.append(list(self.prog[prev:]))
        self.basicBlocks = basicBlocks
        return self.basicBlocks