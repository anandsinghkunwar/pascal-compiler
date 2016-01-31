# Class to define a symbol table entry.
class SymTabEntry(object):
    def __init__(self):
        pass

# Class to define a Three Address Code Instruction (TACInstr).

class TACInstr(object):
    def __init__(self):
        self.InstrType = None
        self.Target = None
        self.Op = None
        self.Src1 = SymTabEntry()
        self.Src2 = SymTabEntry()
        self.Dest = SymTabEntry()
        self.SymTable = None

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
    ASSIGN, IFGOTO, GOTO, CALL, RETURN = range(6)

    # Instruction map
    InstrMap = {
                "="     : ASSIGN,      "ifgoto"     : IFGOTO,      "goto"     : GOTO,
                "call"  : CALL,        "ret"        : RETURN
               }

    # Methods to check type of the instruction 
    def isAssign(self):
        return self.InstrType == ASSIGN
    def isIfGoto(self):
        return self.InstrType == IFGOTO
    def isGoto(self):
        return self.InstrType == GOTO
    def isCall(self):
        return self.InstrType == CALL
    def isReturn(self):
        return self.InstrType == RETURN
