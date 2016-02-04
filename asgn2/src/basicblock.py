import tacinstr, codegen, machine, copy

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
        self.computeNextUses()
    # Method: allocateRegisters
    #   Uses the NextUse heuristic to select the registers
    #   to be spilled.
    def allocateRegisters(self, numRegs):
        pass
    # Method: computeNextUses
    # Uses to initialise Symbol Table of all instructions in
    # the basic block and compute next uses for all variables
    # in the basic block
    def computeNextUses():
        prev = None
        for instr in self.instrList.reverse():
            if prev:
                instr.SymTable = copy.deepcopy(prev.SymTable)
            else:
                instr.SymTable = dict([varName, SymTabEntry(varName)] for varName in self.varSet)
            if instr.Dest:
                instr.SymTable[instr.Dest.operand.name].liveStatus = False
                instr.SymTable[instr.Dest.operand.name].nextUse = None
            if instr.Src1 and instr.Src1.isVar():
                instr.SymTable[instr.Src1.operand.name].liveStatus = True
                instr.SymTable[instr.Src1.operand.name].nextUse = instr.LineNo
            if instr.Src2 and instr.Src2.isVar():
                instr.SymTable[instr.Src2.operand.name].liveStatus = True
                instr.SymTable[instr.Src2.operand.name].nextUse = instr.LineNo
            prev = instr.SymTable