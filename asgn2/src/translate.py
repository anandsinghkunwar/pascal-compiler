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
            if instr.Src2:  #assignment with binary operator    x = y op z
                location = bb.getReg()
                loc = location[0]
                if not type(loc) == machine.Register:
                    loc = machine.getEmptyRegister()
                    if not loc:
                        loc = machine.getOccupiedRegister()
                if instr.Src1.isInt():  # y is integer
                    string +=  indent + "movl $" + instr.Src1.operand + ",%" + loc.name + "\n"
                elif location[1]:   # y is variable and getReg returned y's register. so loc has y's value
                    pass
                else:   # y is a variable and loc dosen't have y's value
                    string += indent + "movl " + instr.Src1.operand.name + ",%" + loc.name + "\n"
                op = getOperator(instr.op)
                if instr.Src2.isInt():
                    string += indent + op + " $" + instr.Src2.operand + ",%" + loc.name + "\n"
                elif instr.Src2.reg:    #z exists in a register
                    flag = False
                    if instr.Src2.reg.name != "ecx" and (op == "sal" or op == "sar"):
                        string += indent + "xchgl %ecx,%" + instr.Src2.operand.reg.name + "\n"
                        flag = True
                    string += indent + op + " %" + instr.Src2.operand.reg.name + ",%" + loc.name + "\n"
                    if flag:
                        string += indent + "xchgl %ecx,%" + instr.Src2.operand.reg.name + "\n"
                else:   #z dosen't exist in a register
                    flag = False
                    if instr.Src2.reg.name != "ecx" and (op == "sal" or op == "sar"):
                        string += indent + "xchgl %ecx," + instr.Src2.operand.name + "\n"
                        flag = True
                    string += indent + op + " " + instr.Src2.operand.name + ",%" + loc.name + "\n"
                    if flag:
                        string += indent + "xchgl %ecx," + instr.Src2.operand.name + "\n"
                instr.Dest.operand.loadIntoRegister(loc.name)
                loc.addVar(instr.Dest.operand.name)
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
        return "sal"
    elif op == 10:
        return "sar"
