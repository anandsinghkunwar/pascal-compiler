import tacinstr, codegen, machine

# Class to define a basic block in IR code:
#  Structure:
#   - a list of instructions
#   - also store a set of variables in the bb
#  Methods:
#   - basic-block local register allocation function
#   - More?
class BasicBlock(object):
    def __init__(self, instrList):
        self.instrList = instrList
        self.varSet = set()
        for instr in instrList:
            self.varSet.update(instr.getVarSet())

    # Method: allocateRegisters
    #   Uses the NextUse heuristic to select the registers
    #   to be spilled.
    def allocateRegisters(self, numRegs):
        pass
