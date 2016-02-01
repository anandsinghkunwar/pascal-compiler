# Class to define a symbol table entry.
class SymTabEntry(object):
    def __init__(self, name):
        self.name = name

# Class to define a Three Address Code Instruction (TACInstr).

class TACInstr(object):
    def __init__(self, instrTuple):
        self.InstrType = None
        self.Target = None
        self.Op = None
        self.Src1 = SymTabEntry('')
        self.Src2 = SymTabEntry('')
        self.Dest = SymTabEntry('')
        self.SymTable = None

        # Process the instrTuple to populate the member fields
        self.InstrType = TACInstr.InstrMap[instrTuple[1]]
        # Now, the parsing diverges for each type
        if self.isAssign():
            if   len(instrTuple) == 4:   # Basic assignment: 1, =, a, b
                pass
            elif len(instrTuple) == 5:   # Assignment with unary op: 2, =, -, g, f
                pass
            elif len(instrTuple) == 6:   # Assignment with binary op: 3, =, +, a, b, c
                pass
            else:
                # Error
                pass
        elif self.isIfGoto():
            if len(instrTuple) == 6:    # Tuple: 4, ifgoto, relop, i, j, L
                self.Target = int(instrTuple[5])
                pass
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
                pass
            else:
                # Error
                pass

    # Types of operations
    ADD, SUB, MULT, DIV, GT, LT, GEQ, LEQ, NEQ, SHL, SHR, AND, NOT, OR, MOD, XOR = range(16)

    # Operation map
    OpMap = {
                "+"     : ADD,      "-"     : SUB,      "*"     : MULT,
                "/"     : DIV,      ">"     : GT,       "<"     : LT,
                ">=",   : GEQ,      "<="    : LEQ,      "<>"    : NEQ,
                "<<",   : SHL,      ">>"    : SHR,      "and"   : AND,
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
            if var.name:
                varSet.update([var.name])
        return varSet
