# Class to define a Three Address Code Instruction (TACInstr).

class TACInstr(object):
    def __init__(self):
        self.InstrType = None
        self.Target = None


    # Types of instructions
    ASSIGN, IFGOTO, GOTO, CALL, RETURN, NONE = xrange(6)

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
