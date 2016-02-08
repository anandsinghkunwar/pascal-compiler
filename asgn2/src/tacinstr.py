import machine, basicblock, codegen, re, globjects

# Class to define a symbol table entry (for variables).
# Member variables:
#   name - name of the variable
#   liveStatus - whether the the variable is live or not,
#                by default this is True as at the end of the
#                basic block the all variables are considered live
#   nextUse - next line number where the variable will be used
class SymTabEntry(object):
# For now, assume that all entries in the symbol table are integers.
    def __init__(self, name):
        self.name = name
        self.liveStatus = True
        self.nextUse = None
    def isLive(self):
        return self.liveStatus
# Class to define an address descriptor table entry (for variables).
# Member variables:
#   name - name of the variable
#   dataType - type of the variable (currently all integers)
#   reg - Register object where variable resides
#   memAddr - Memory Address where variable resides

class AddrDescEntry(object):
# For now, assume that all entries in the symbol table are integers.
    def __init__(self, name):
        self.name = name
        self.dataType = 'integer'
        self.reg = None
        self.memAddr = globjects.data.allocateMem(self.name)
        self.dirty = False

    def loadIntoReg(self, regName):
        self.removeReg()
        globjects.registerMap[regName].addVar(self.name)

    def removeReg(self):
        if self.reg:
            self.reg.removeVar(self.name)

# Class to handle instruction operands

class Operand(object):
    # Regular expressions to identify operand types
    reInt = r'^\d+$'
    reIdentifier = r'^[a-zA-Z_][a-zA-Z0-9_]*$'

    # Operand Types
    INT, VAR = range(2)

    def __init__(self, string):
        if re.match(Operand.reInt, string):
            self.operandType = Operand.INT
            self.operand = int(string)
        elif re.match(Operand.reIdentifier, string):
            self.operandType = Operand.VAR
            if not string in globjects.varMap.keys():
                globjects.varMap[string] = AddrDescEntry(string)
            self.operand = globjects.varMap[string]
        else:
            globjects.halt(-1, "unsupported operand type")

    def isInt(self):
        return self.operandType == Operand.INT
    def isVar(self):
        return self.operandType == Operand.VAR

# Class to define a Three Address Code Instruction (TACInstr).
class TACInstr(object):
    def __init__(self, instrTuple):
        self.InstrType = None
        self.Target = None
        self.Op = None
        self.Src1 = None
        self.Src2 = None
        self.Dest = None
        self.SymTable = None
        self.Label = None
        self.TargetLabel = None
        self.LineNo = int(instrTuple[0])
        self.IOFmtStringAddr = None
        self.IOArgList = []

        # Process the instrTuple to populate the member fields
        self.InstrType = TACInstr.InstrMap[instrTuple[1]]
        # Now, the parsing diverges for each type
        if self.isAssign():
            if len(instrTuple) == 4:   # Basic assignment: 1, =, a, b
                dest = Operand(instrTuple[2])
                src1 = Operand(instrTuple[3])
                if not dest.isVar():
                    globjects.halt(self.LineNo, instrTuple[2] + " is not a variable")
                else:
                    self.Dest = dest
                    self.Src1 = src1
            elif len(instrTuple) == 5:
                dest = Operand(instrTuple[3])
                if not dest.isVar():
                    globjects.halt(self.LineNo, instrTuple[3] + " is not a variable")
                else:
                    self.Dest = dest
                    self.Op = TACInstr.OpMap[instrTuple[2]]
                    if self.Op == TACInstr.CALLOP:         # Special unary op: 9, =, call, a, foo
                        self.TargetLabel = instrTuple[4]
                    else:               # Assignment with unary op: 2, =, -, g, f
                        src1 = Operand(instrTuple[4])
                        self.Src1 = src1
            elif len(instrTuple) == 6:   # Assignment with binary op: 3, =, +, a, b, c
                dest = Operand(instrTuple[3])
                src1 = Operand(instrTuple[4])
                src2 = Operand(instrTuple[5])
                if not dest.isVar():
                    globjects.halt(self.LineNo, instrTuple[3] + " is not a variable")
                else:
                    self.Dest = dest
                    self.Src1 = src1
                    self.Src2 = src2
                    self.Op = TACInstr.OpMap[instrTuple[2]]
            else:
                globjects.halt(self.LineNo, "unsupported format for assignment instruction")
        elif self.isIfGoto():
            if len(instrTuple) == 6:    # Tuple: 4, ifgoto, relop, i, j, L
                self.Target = int(instrTuple[5])
                globjects.targetSet.add(self.Target)
                self.Op = TACInstr.OpMap[instrTuple[2]]
                self.Src1 = Operand(instrTuple[3])
                self.Src2 = Operand(instrTuple[4])
            else:
                globjects.halt(self.LineNo, "unsupported format for IfGoto instruction")
        elif self.isGoto():
            if len(instrTuple) == 3:    # Tuple: 5, goto, L1
                self.Target = int(instrTuple[2])
                globjects.targetSet.add(self.Target)
            else:
                globjects.halt(self.LineNo, "unsupported format for Goto instruction")
        elif self.isCall():
            if len(instrTuple) == 3:    # Tuple: 6, call, foo
                self.TargetLabel = instrTuple[2]
            else:
                globjects.halt(self.LineNo, "unsupported format for call instruction")
        elif self.isReturn():
            if len(instrTuple) == 3:    # Tuple: 7, ret, retval
                self.Src1 = Operand(instrTuple[2])
            elif len(instrTuple) == 2:    # Tuple: 8, ret
                pass
            else:
                globjects.halt(self.LineNo, "unsupported format for return instruction")
        elif self.isLabel():
            if len(instrTuple) == 3:    # Tuple: 9, label, name
                self.Label = instrTuple[2]
            else:
                globjects.halt(self.LineNo, "unsupported format for label instruction")
        elif self.isPrintf():           # Tuple: 10, printf, fmt_string, args...
            if len(instrTuple) >= 3:
                self.IOFmtStringAddr = globjects.data.allocateMem('.STR'+str(self.LineNo), instrTuple[2])
                self.IOArgList = [Operand(arg) for arg in instrTuple[3:]]
            else:
                globjects.halt(self.LineNo, "unsupported format for printf instruction")
        elif self.isScanf():            # Tuple: 11, scanf, fmt_string, args...
            if len(instrTuple) >= 3:
                self.IOFmtStringAddr = globjects.data.allocateMem('.STR'+str(self.LineNo), instrTuple[2])
                self.IOArgList = [Operand(arg) for arg in instrTuple[3:]]
                for arg in self.IOArgList:
                    if arg.isInt():
                        globjects.halt(self.LineNo, "integer argumnet instead of memory address in scanf instruction")
            else:
                globjects.halt(self.LineNo, "too few arguments for scanf instruction")
        else:
            globjects.halt(self.LineNo, "unsupported instruction")

    # Types of operations
    ADD, SUB, MULT, DIV, EQ, GT, LT, GEQ, LEQ, NEQ, SHL, SHR, AND, NOT, OR, MOD, XOR, CALLOP = range(18)

    # Operation map
    OpMap = {
                "+"     : ADD,      "-"     : SUB,      "*"     : MULT,
                "/"     : DIV,      ">"     : GT,       "<"     : LT,
                ">="    : GEQ,      "<="    : LEQ,      "<>"    : NEQ,
                "<<"    : SHL,      ">>"    : SHR,      "and"   : AND,
                "not"   : NOT,      "or"    : OR,       "mod"   : MOD,
                "xor"   : XOR,      "=="    : EQ,       "call"  : CALLOP
            }

    # Types of instructions
    ASSIGN, IFGOTO, GOTO, CALL, RETURN, LABEL, PRINTF, SCANF = range(8)

    # Instruction map
    InstrMap = {
                "="     : ASSIGN,      "ifgoto"     : IFGOTO,      "goto"     : GOTO,
                "call"  : CALL,        "ret"        : RETURN,      "label"    : LABEL,
                "printf": PRINTF,      "scanf"      : SCANF
               }

    # Methods to check type of the instruction 
    def isAssign(self):
        return self.InstrType == TACInstr.ASSIGN
    def isIfGoto(self):
        return self.InstrType == TACInstr.IFGOTO
    def isGoto(self):
        return self.InstrType == TACInstr.GOTO
    def isCall(self):
        return self.InstrType == TACInstr.CALL
    def isReturn(self):
        return self.InstrType == TACInstr.RETURN
    def isLabel(self):
        return self.InstrType == TACInstr.LABEL
    def isTarget(self):
        return self.LineNo in globjects.targetSet
    def isPrintf(self):
        return self.InstrType == TACInstr.PRINTF
    def isScanf(self):
        return self.InstrType == TACInstr.SCANF
    def isExit(self):
        return self.InstrType == TACInstr.EXIT
    def isJump(self):
        return self.isGoto() or self.isIfGoto() or self.isCall() or self.isReturn()

    # Auxiliary methods
    def getVarSet(self):
        varSet = set()
        for var in (self.Src1, self.Src2, self.Dest):
            if var and var.isVar():
                varSet.update([var.operand.name])
        for arg in self.IOArgList:
            if arg and arg.isVar():
                varSet.update([arg.operand.name])
        return varSet
