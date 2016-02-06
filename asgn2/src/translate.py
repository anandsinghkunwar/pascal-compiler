import machine
import tacinstr
import basicblock
import globjects

indent = "    "

def translateBlock(bb):
    for instr in bb:
        globject.currInstr = instr
        string = ""
        if instr.isAssign:
            if instr.Src2:  #assignment with binary operator
                if instr.Src1.isInt():
                    loc = bb.getReg()
                    if not type(loc) == machine.Register:
                        loc = machine.getEmptyRegister()
                        if not loc:
                            loc = machine.getOccupiedRegister()
                    string += "movl $" + instr.Src1.operand + ",%" + loc.name + "\n"
                    op = getOperator(instr.op)
                    if instr.Src2.isInt():
                        string += op + " $" + instr.Src2.operand + ",%" + loc.name + "\n"
                    elif instr.Src2.reg:    #src2 exists in a register
                        string += op + " %" + instr.Src2.operand.reg.name + ",%" + loc.name + "\n"
                    instr.Dest.operand.loadIntoRegister(loc.name)
                    loc.addVar(instr.Dest.operand.name)
                else:   #Src1 is variable
                    pass
            elif instr.Op:  #assignment wirh unary operator
                pass
            else:           #basic assignment
                pass
        elif instr.isIfGoto:
            pass
        elif instr.isGoto:
            pass
        elif instr.isCall:
            pass
        elif instr.isReturn:
            pass
        else:   #error
            pass

def getOperator(op):
    if op == 0:
        return "addl"
    elif op == 1:
        return "subl"
    elif op == 2:
        return "imul"
    elif op == 3:   #div consumes too many registers, will handle later
        pass
    elif op == 9:
        return "shl"
    elif op == 10:
        return "sar"
