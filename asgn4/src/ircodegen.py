# Module for IR code generation.
import symbol_table as ST

# Dummy class to enable parser to use attributes
class Node(object):
    def __init__(self):
        self.value = None
        self.code = ''
        self.place = None
        self.items = []
        self.type = None
        self.arrayBeginList = []
        self.arrayEndList = []
        self.quad = None
        self.trueList = []
        self.falseList = []

# Class to handle instruction operands
class Operand(object):
    # Operand Types
    INT, STRING, BOOL, INTVAR, STRINGVAR, BOOLVAR, ARRAY, ARRAYELEMENT = range(8)

    def __init__(self, varObj):
        if isinstance(varObj, ST.SymTabEntry):
            self.operand = varObj.name
            if varObj.type.type == ST.Type.INT:
                self.operandType = Operand.INTVAR
            elif varObj.type.type == ST.Type.STRING:
                self.operandType = Operand.STRINGVAR
            elif varObj.type.type == ST.Type.BOOL:
                self.operandType = Operand.BOOLVAR
            else:
                self.operandType = Operand.ARRAY
        elif type(varObj) is int:
            self.operand = varObj
            self.operandType = Operand.INT
        elif type(varObj) is str:
            self.operand = varObj
            self.operandType = Operand.STRING
        elif type(varObj) is bool:
            self.operand = varObj
            self.operandType = Operand.BOOL
        else:   #ARRAYELEMENT
            # TODO
            pass

    def isInt(self):
        return self.operandType == Operand.INT
    def isString(self):
        return self.operandType == Operand.STRING
    def isBool(self):
        return self.operandType == Operand.BOOL
    def isIntVar(self):
        return self.operandType == Operand.INTVAR
    def isStringVar(self):
        return self.operandType == Operand.STRINGVAR
    def isBoolVar(self):
        return self.operandType == Operand.BOOLVAR
    def isArray(self):
        return self.operandType == Operand.ARRAY
    def isArrayElement(self):
        return self.operandType == Operand.ARRAYELEMENT

# Class to define a Three Address Code Instruction (TACInstr).
class TACInstr(object):
    def __init__(self, instrType, op, target=None, src1=None, src2=None, dest=None, label=None, targetLabel=None, lineNo=None, ioArgList=None):
        self.InstrType = None
        self.Target = None
        self.Op = None
        self.Src1 = None
        self.Src2 = None
        self.Dest = None
        #self.SymTable = None
        self.Label = None
        self.TargetLabel = None
        self.LineNo = None
        self.IOFmtStringAddr = None
        self.IOArgList = []

        self.InstrType = instrType
        if target:
            self.Target = int(target)
        self.Op = op
        if src1:
            self.Src1 = Operand(src1)
        if src2:
            self.Src2 = Operand(src2)
        if dest:
            self.Dest = Operand(dest)
        if label:
            self.Label = label
        if targetLabel:
            self.TargetLabel = targetLabel
        if lineNo:
            self.LineNo = int(lineno)
        if ioArgList:
            self.IOArgList = ioArgList

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
