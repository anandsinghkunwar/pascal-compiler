import machine, basicblock, codegen, re

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

# Class to define an address descriptor table entry (for variables).
# Member variables:
#   name - name of the variable
#   dataType - type of the variable (currently all integers)
#   addr - set of locations (e.g. reg, memory, stack) where the
#          value of the variable can be found.
class AddrDescEntry(object):
# For now, assume that all entries in the symbol table are integers.
    def __init__(self, name):
        self.name = name
        self.dataType = 'integer'
        self.addr = set()

    def memAlloc(self):
        memAddr = machine.data.allocateMem(self.name)
        self.addr.add(memAddr)

    def loadIntoReg(self, regName):
        reg = machine.registerMap[regName]
        reg.addVar(self.name)

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
            self.operand = string
        else:
            # Error
            pass

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
        self.LineNo = instrTuple[0]

        # Process the instrTuple to populate the member fields
        self.InstrType = TACInstr.InstrMap[instrTuple[1]]
        # Now, the parsing diverges for each type
        if self.isAssign():
            if   len(instrTuple) == 4:   # Basic assignment: 1, =, a, b
                dest = Operand(instrTuple[2])
                src1 = Operand(instrTuple[3])
                if not dest.isVar():
                    # Error
                    pass
                else:
                    self.Dest = dest
                    self.Src1 = src1
            elif len(instrTuple) == 5:   # Assignment with unary op: 2, =, -, g, f
                dest = Operand(instrTuple[3])
                src1 = Operand(instrTuple[4])
                if not dest.isVar():
                    # Error
                    pass
                else:
                    self.Dest = dest
                    self.Src1 = src1
                    self.Op = TACInstr.OpMap[instrTuple[2]]
            elif len(instrTuple) == 6:   # Assignment with binary op: 3, =, +, a, b, c
                dest = Operand(instrTuple[3])
                src1 = Operand(instrTuple[4])
                src2 = Operand(instrTuple[5])
                if not dest.isVar():
                    # Error
                    pass
                else:
                    self.Dest = dest
                    self.Src1 = src1
                    self.Src2 = src2
                    self.Op = TACInstr.OpMap[instrTuple[2]]
            else:
                # Error
                pass
        elif self.isIfGoto():
            if len(instrTuple) == 6:    # Tuple: 4, ifgoto, relop, i, j, L
                self.Target = int(instrTuple[5])
                self.Op = TACInstr.OpMap[instrTuple[2]]
                self.Src1 = Operand(instrTuple[3])
                self.Src2 = Operand(instrTuple[4])
            else:
                # Error
                pass
        elif self.isGoto():
            if len(instrTuple) == 3:    # Tuple: 5, goto, L1
                self.Target = int(instrTuple[2])
            else:
                # Error
                pass
        elif self.isCall():
            if len(instrTuple) == 3:    # Tuple: 6, call, foo
                pass
            else:
                # Error
                pass
        elif self.isReturn():
            if len(instrTuple) == 3:    # Tuple: 7, ret, retval
                self.Src1 = int(instrTuple[2])
            else:
                # Error
                pass

    # Types of operations
    ADD, SUB, MULT, DIV, GT, LT, GEQ, LEQ, NEQ, SHL, SHR, AND, NOT, OR, MOD, XOR = range(16)

    # Operation map
    OpMap = {
                "+"     : ADD,      "-"     : SUB,      "*"     : MULT,
                "/"     : DIV,      ">"     : GT,       "<"     : LT,
                ">="    : GEQ,      "<="    : LEQ,      "<>"    : NEQ,
                "<<"    : SHL,      ">>"    : SHR,      "and"   : AND,
                "not"   : NOT,      "or"    : OR,       "mod"   : MOD,
                "xor"   : XOR
            }

    # Types of instructions
    ASSIGN, IFGOTO, GOTO, CALL, RETURN = range(5)

    # Instruction map
    InstrMap = {
                "="     : ASSIGN,      "ifgoto"     : IFGOTO,      "goto"     : GOTO,
                "call"  : CALL,        "ret"        : RETURN
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

    # Auxiliary methods
    def getVarSet(self):
        varSet = set()
        for var in (self.Src1, self.Src2, self.Dest):
            if type(var) == SymTabEntry and var.name:
                varSet.update([var.name])
        return varSet
