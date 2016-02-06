import tacinstr, codegen, machine, copy
import globjects as G

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
    def getReg(self):
        if G.currInstr.Src1 and G.currInstr.Src1.isVar():
            varName = G.currInstr.Src1.operand.name
            if (G.currInstr.SymTable[varName].liveStatus == False and
                G.currInstr.SymTable[varName].liveStatus == None and
                G.varMap[varName].reg and
                len(G.varMap[varName].reg.varNames) == 1):
                regName = G.varMap[varName].reg.name
                G.varMap[varName].reg.spill()
                return G.registerMap[regName]

        if G.currInstr.Src2 and G.currInstr.Src2.isVar():
            varName = G.currInstr.Src2.operand.name
            if (G.currInstr.SymTable[varName].liveStatus == False and
                G.currInstr.SymTable[varName].liveStatus == None and
                G.varMap[varName].reg and
                len(G.varMap[varName].reg.varNames) == 1):
                regName = G.varMap[varName].reg.name
                G.varMap[varName].reg.spill()
                return G.registerMap[regName]

        reg = self.getEmptyRegister()
        if reg:
            return reg

        if G.currInstr.Dest:
            varName = G.currInstr.Dest.operand.name
            if G.currInstr.SymTable[varName].nextUse:
                return getOccupiedRegister()
            else:
                pass #return memory

    def getEmptyRegister():
        for regName in G.regNames:
            if G.registerMap[regName].isEmpty():
                return G.registerMap[regName]
        return None
    def getOccupiedRegister():
        maxNextUse = 0
        for regName in G.regNames:
            if not G.registerMap[regName].isEmpty():
                nextUseList = [G.currInstr.SymTable[varName].nextUse
                    for varName in G.registerMap[regName].varNames
                    if G.currInstr.SymTable[varName].nextUse != 0]

                if nextUseList:
                    minNextUseReg = min(nextUseList)
                else:
                    G.registerMap[regName].spill()
                    return G.registerMap[regName]

                if maxNextUse < minNextUseReg:
                    maxNextRegName = regName
                    maxNextUse = minNextUseReg
        G.registerMap[maxNextRegName].spill()
        return G.registerMap[maxNextRegName]
    # Method: computeNextUses
    # Uses to initialise Symbol Table of all instructions in
    # the basic block and compute next uses for all variables
    # in the basic block
    def computeNextUses(self):
        prev = None
        instrList = list(self.instrList)
        instrList.reverse()
        for instr in instrList:
            if prev:
                instr.SymTable = copy.deepcopy(prev)
            else:
                instr.SymTable = dict([varName, tacinstr.SymTabEntry(varName)] for varName in self.varSet)
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