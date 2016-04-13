# Module for IR code generation.
import symbol_table as ST
import globjects as G
import codegen as CG

# Global Variables
InstrList = [None]
tempCount = 0
nextQuad = 1

# Dummy class to enable parser to use attributes
class Node(object):
    def __init__(self):
        self.value = None
        self.code = []
        self.place = None
        self.items = []
        self.type = None
        self.arrayBeginList = []
        self.arrayEndList = []
        self.quad = None
        self.trueList = []
        self.falseList = []
        self.endList = []
        self.nextList = []

    def genCode(self, instr):
        self.code.append(instr)
        InstrList.append(instr)

# Class to support array dereferences in IR
class ArrayElement(object):
    def __init__(self, array, index):
        self.array = array
        self.index = index
        self.type = array.type.arrayBaseType

    def isInt(self):
        return self.type.type == ST.Type.INT
    def isBool(self):
        return self.type.type == ST.Type.BOOL
    def isChar(self):
        return self.type.type == ST.Type.CHAR
    def isString(self):
        return self.type.type == ST.Type.STRING
    def isArray(self):
        return self.type.type == ST.Type.ARRAY

# Function to generate temporary variables
def newTempInt():
    global tempCount
    tempVar = ST.currSymTab.addVar('.t'+str(tempCount), ST.Type('integer', ST.Type.TYPE), isTemp=True)
    tempCount += 1
    return tempVar

def newTempBool():
    global tempCount
    tempVar = ST.currSymTab.addVar('.t'+str(tempCount), ST.Type('boolean', ST.Type.TYPE), isTemp=True)
    tempCount += 1
    return tempVar

def newTempChar():
    global tempCount
    tempVar = ST.currSymTab.addVar('.t'+str(tempCount), ST.Type('char', ST.Type.TYPE), isTemp=True)
    tempCount += 1
    return tempVar

def newTempString():
    global tempCount
    tempVar = ST.currSymTab.addVar('.t'+str(tempCount), ST.Type('string', ST.Type.TYPE), isTemp=True)
    tempCount += 1
    return tempVar

def newTempArray():
    global tempCount
    tempVar = ST.currSymTab.addVar('.t'+str(tempCount), ST.Type('array', ST.Type.TYPE), isTemp=True)
    tempCount += 1
    return tempVar

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
            if self.operand in G.varMap.keys():
                self.addrDescEntry = G.varMap[self.operand]
            else:
                G.varMap[self.operand] = CG.AddrDescEntry(self.operand, isParam=varObj.isParameter, paramNum=varObj.paramNum, isLocal=varObj.isLocal, offset=varObj.offset)
                self.addrDescEntry = G.varMap[self.operand]
        elif type(varObj) is int:
            self.operand = varObj
            self.operandType = Operand.INT
        elif type(varObj) is str:
            self.operand = varObj
            if varObj == 'true' or varObj == 'false':
                self.operandType = Operand.BOOL
            else:
                self.operandType = Operand.STRING
        elif type(varObj) is bool:
            self.operand = varObj
            self.operandType = Operand.BOOL
        elif type(varObj) is ArrayElement:
            self.operand = varObj
            self.operandType = Operand.ARRAYELEMENT

    def isInt(self):
        return (self.operandType == Operand.INT) or self.isBool()
    def isString(self):
        return self.operandType == Operand.STRING
    def isBool(self):
        return self.operandType == Operand.BOOL
    def isChar(self):
        return (type(self.operand) == str) and (len(self.operand) == 1)
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
    def isVar(self):
        if self.isIntVar() or self.isStringVar() or self.isBoolVar() or self.isArray() or self.isArrayElement():
            return True
        else:
            return False

# Class to define a Three Address Code Instruction (TACInstr).
class TACInstr(object):
    def __init__(self, instrType, op=None, target=None, src1=None, src2=None,
                 dest=None, label=None, targetLabel=None, lineNo=None, ioArgList=None,
                 paramList=None, ioFmtString=None, symTableParser=None):
        self.InstrType = instrType
        self.Target = target
        self.Op = op
        self.Src1 = None
        self.Src2 = None
        self.Dest = None
        self.SymTable = None
        self.SymTableParser = symTableParser
        self.Label = label
        self.TargetLabel = targetLabel
        self.LineNo = lineNo
        self.IOFmtString = ioFmtString
        self.IOFmtStringAddr = None
        self.IOArgList = ioArgList
        self.ParamList = paramList

        if src1 is not None:
            self.Src1 = Operand(src1)
        if src2 is not None:
            self.Src2 = Operand(src2)
        if dest is not None:
            self.Dest = Operand(dest)

        if self.isScanf() or self.isPrintf():
            self.IOFmtStringAddr = G.data.allocateMem('.STR'+str(self.LineNo), ioFmtString)

    # Types of operations
    ADD, SUB, MULT, DIV, EQ, GT, LT, GEQ, LEQ, NEQ, \
    SHL, SHR, AND, NOT, OR, MOD, XOR, CALLOP, \
    LOGICAND, LOGICNOT, LOGICXOR, LOGICOR = range(22)

    # Operation map
    OpMap = {
                "+"     : ADD,          "-"     : SUB,      "*"     : MULT,
                "/"     : DIV,          ">"     : GT,       "<"     : LT,
                ">="    : GEQ,          "<="    : LEQ,      "<>"    : NEQ,
                "<<"    : SHL,          ">>"    : SHR,      "and"   : LOGICAND,
                "shl"   : SHL,          "shr"   : SHR,      "|"     : OR,
                "&"     : AND,          "^"     : XOR,      "~"     : NOT,
                "not"   : LOGICNOT,     "or"    : LOGICOR,  "mod"   : MOD,
                "xor"   : LOGICXOR,     "=="    : EQ,       "call"  : CALLOP,
                "="     : EQ
            }

    # Types of instructions
    ASSIGN, IFGOTO, GOTO, CALL, RETURN, LABEL, PRINTF, SCANF, NOP, DECLARE = range(10)

    # Instruction map
    InstrMap = {
                "="       : ASSIGN,      "ifgoto"     : IFGOTO,      "goto"     : GOTO,
                "call"    : CALL,        "ret"        : RETURN,      "label"    : LABEL,
                "printf"  : PRINTF,      "scanf"      : SCANF,       "nop"      : NOP,
                "declare" : DECLARE
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
    def isNop(self):
        return self.InstrType == TACInstr.NOP
    def isDeclare(self):
        return self.InstrType == TACInstr.DECLARE

    # Auxiliary methods
    def getVarSet(self):
        varSet = set()
        for var in (self.Src1, self.Src2, self.Dest):
            if var and var.isVar():
                varSet.update([var.operand])
        if self.IOArgList is not None:
            for arg in self.IOArgList:
                if arg and arg.isVar():
                    varSet.update([arg.operand])
        return varSet

def getLexeme(obj): #for getting lexeme from Operand object or constant
    if isinstance(obj, Operand):
        if obj.isArrayElement():
            arrayName = obj.operand.array.name
            if isinstance(obj.operand.index, ST.SymTabEntry):
                return arrayName + '[' + obj.operand.index.name + ']'
            elif type(obj.operand.index) is int:
                return arrayName + '[' + str(obj.operand.index) + ']'
            elif type(obj.operand.index) is str:
                return arrayName + '[' + obj.operand.index + ']'
        else:
            return str(obj.operand)
    else:
        return str(obj)

def getName(obj):   #for getting lexeme from SymTabEntry or constant
    if isinstance(obj, ST.SymTabEntry):
        return obj.name
    else:
        return str(obj)

def generateIr(irList):
    if len(irList) > 0:
        text = ''
        ir = irList[0]
        text += str(ir.LineNo) + ", "
        rev_InstrMap = {v:k for k, v in TACInstr.InstrMap.items()}
        rev_OpMap = {v:k for k, v in TACInstr.OpMap.items()}
        if ir.isIfGoto():
            text += "ifgoto, " + rev_OpMap[ir.Op] + ", " + getLexeme(ir.Src1) + ", " + getLexeme(ir.Src2) + ", " + str(ir.Target)
        elif ir.isGoto():
            text += "goto, " + str(ir.Target)
        elif ir.isCall():
            text += "call, " + ir.TargetLabel
            if ir.ParamList:
                args = [getName(arg) for arg in ir.ParamList]
                text += ", " + ", ".join(args)
        elif ir.isReturn():
            text += "ret"
            if ir.Src1:
                text += ", " + getLexeme(ir.Src1)
        elif ir.isLabel():
            text += "label, " + ir.Label
            if ir.ParamList:
                args = [getName(arg) for arg in ir.ParamList]
                text += ", " + ", ".join(args)
        elif ir.isPrintf():
            text += "printf, " + ir.IOFmtString
            args = [getLexeme(arg) for arg in ir.IOArgList]
            text += ", " + ", ".join(args)
        elif ir.isScanf():
            text += "scanf, " + ir.IOFmtString
            args = [getLexeme(arg) for arg in ir.IOArgList]
            text += ", " + ", ".join(args)
        elif ir.isNop():
            text += "nop"
        elif ir.isAssign():
            text += "=, "
            if ir.Op is None:   #basic assignment
                text += getLexeme(ir.Dest) + ", " + getLexeme(ir.Src1)
            elif ir.Op is TACInstr.CALLOP:  #assignment with call
                text += "call, " + getLexeme(ir.Dest) + ", " + ir.TargetLabel
                if ir.ParamList:
                    args = [getName(arg) for arg in ir.ParamList]
                    text += ", " + ", ".join(args)
            elif ir.Src2: #binary operator
                text += rev_OpMap[ir.Op]  + ", "+ getLexeme(ir.Dest) + ", " + getLexeme(ir.Src1) + ", " + getLexeme(ir.Src2)
            else:   #unary operators except call
                text += rev_OpMap[ir.Op] + ", " + getLexeme(ir.Dest) + ", " + getLexeme(ir.Src1)
        elif ir.isDeclare():
            text += "declare, " + getLexeme(ir.Dest) + ", " + getLexeme(ir.Src1) + ", " + getLexeme(ir.Src2)
        return text + "\n" + generateIr(irList[1:])
    else:
        return ""
