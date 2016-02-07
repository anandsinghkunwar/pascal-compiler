import machine
import tacinstr
import basicblock
import globjects

indent = "    "

def translateBlock(bb):
    for instr in bb.instrList:
        globjects.currInstr = instr
        string = ".LABEL_" + str(instr.LineNo) + ":\n"
        if instr.isAssign():
            if instr.Src2:  #assignment with binary operator    x = y op z
                location = bb.getReg()
                loc = location[0]
                if instr.Src1.isInt():  # y is integer
                    string +=  indent + "movl $" + str(instr.Src1.operand) + ",%" + loc.name + "\n"
                elif location[1]:   # y is variable and getReg returned y's register. so loc has y's value
                    pass
                else:   # y is a variable and loc doesn't have y's value
                    string += indent + "movl " + instr.Src1.operand.name + ",%" + loc.name + "\n"
                op = getOperator(instr.Op)
                if instr.Src2.isInt():
                    string += indent + op + " $" + str(instr.Src2.operand) + ",%" + loc.name + "\n"
                elif instr.Src2.operand.reg:    #z exists in a register
                    if instr.Src2.operand.reg.name != "ecx" and (op == "sal" or op == "sar"):
                        string += indent + "xchgl %ecx,%" + instr.Src2.operand.reg.name + "\n"
                    string += indent + op + " %" + instr.Src2.operand.reg.name + ",%" + loc.name + "\n"
                    if instr.Src2.operand.reg.name != "ecx" and (op == "sal" or op == "sar"):
                        string += indent + "xchgl %ecx,%" + instr.Src2.operand.reg.name + "\n"
                else:   #z doesn't exist in a register
                    if instr.Src2.operand.reg.name != "ecx" and (op == "sal" or op == "sar"):
                        string += indent + "xchgl %ecx," + instr.Src2.operand.name + "\n"
                    string += indent + op + " " + instr.Src2.operand.name + ",%" + loc.name + "\n"
                    if instr.Src2.operand.reg.name != "ecx" and (op == "sal" or op == "sar"):
                        string += indent + "xchgl %ecx," + instr.Src2.operand.name + "\n"
                instr.Dest.operand.loadIntoReg(loc.name)
            elif instr.Op:  #assignment wirh unary operator a = op b
                if instr.Src1.operand.reg:  #b exists in a register
                    loc = instr.Src1.operand.reg
                else:
                    loc = bb.getReg()
                    loc = loc[0]
                if instr.Src1.isInt():  #b is integer
                    string += indent + "movl $" + str(instr.Src1.operand) + ",%" + loc.name + "\n"
                elif not instr.Src1.operand.reg:   #b is in memory
                    string += indent + "movl " + instr.Src1.operand.name + ",%" + loc.name + "\n"
                if instr.Op == tacinstr.TACInstr.SUB:
                    string += indent + "imul $-1,%" + loc.name + "\n"
                elif instr.Op == tacinstr.TACInstr.NOT:
                    string += indent + "notl %" + loc.name + "\n"
                else:   #error
                    pass
                instr.Dest.operand.loadIntoReg(loc.name)
            else:   #basic assignment   a = b
                if instr.Src1.isInt():  #b is integer
                    if instr.Dest.operand.reg:  #a is in a register
                        string += indent + "movl $" + str(instr.Src1.operand) + ",%" + instr.Dest.operand.reg.name + "\n"
                    else:   #a is in memory
                        string += indent + "movl $" + str(instr.Src1.operand) + "," + instr.Dest.operand.name + "\n"
                elif instr.Src1.operand.reg:    #b is in a register
                    if instr.Dest.operand.reg:  #a is also in register. So spill a's register and indicate in b's that a is also stored there
                        instr.Dest.operand.reg.removeVar(instr.Dest.operand.name)
                        instr.Src1.operand.reg.addVar(instr.Dest.operand.name)
                    else:   #a is in memory
                        instr.Dest.operand.loadIntoReg(instr.Src1.operand.reg)
                else:   #b is in memory
                    if instr.Dest.operand.reg:
                        string += indent + "movl " + instr.Src1.operand.name + ",%" + instr.Dest.operand.reg.name + "\n"
                    else:   # both a and b are in memory
                        loc = bb.getReg()
                        loc = loc[0]
                        string += indent + "movl " + instr.Src1.operand.name + ",%" + loc.name + "\n"
                        instr.Dest.operand.loadIntoReg(loc.name)
        elif instr.isIfGoto():  # if i relop j jump L
            if instr.Src1.isInt():  # i is integer. cmpl should not have immediate as first argument
                string += indent + "pushl $" + str(instr.Src1.operand) + "\n"
                if instr.Src2.isInt():
                    string += indent + "cmpl $" + str(instr.Src2.operand) + ",(%esp)\n"
                elif instr.Src2.operand.reg:
                    string += indent + "cmpl %" + instr.Src2.operand.reg.name + ",(%esp)\n"
                else:
                    string += indent + "cmpl " + instr.Src2.operand.name + ",(%esp)\n"
                string += indent + "addl $4,%esp\n"
            elif instr.Src1.operand.reg:
                if instr.Src2.isInt():
                    string += indent + "cmpl $" + str(instr.Src2.operand)
                elif instr.Src2.operand.reg:
                    string += indent + "cmpl %" + instr.Src2.operand.reg.name
                else:
                    string += indent + "cmpl " + instr.Src2.operand.name
                string += ",%" + instr.Src1.operand.reg.name + "\n"
            else:
                if instr.Src2.isInt():
                    string += indent + "cmpl $" + str(instr.Src2.operand)
                elif instr.Src2.operand.reg:
                    string += indent + "cmpl %" + instr.Src2.operand.reg.name
                else:
                    string += indent + "cmpl " + instr.Src2.operand.name
                string += "," + instr.Src1.operand.name + "\n"
            if instr.Op == tacinstr.TACInstr.GEQ:
                string += indent + "jge "
            elif instr.Op == tacinstr.TACInstr.GT:
                string += indent + "jg "
            elif instr.Op == tacinstr.TACInstr.LEQ:
                string += indent + "jle "
            elif instr.Op == tacinstr.TACInstr.LT:
                string += indent + "jl "
            elif instr.Op == tacinstr.TACInstr.EQ:
                string += indent + "je "
            elif instr.Op == tacinstr.TACInstr.NEQ:
                string += indent + "jne "
            else:   #error
                pass
            string += ".LABEL_" + str(instr.Target) + "\n"
        elif instr.isGoto():    #goto line_no
            string += "jmp .LABEL_" + str(instr.Target) + "\n"
        elif instr.isCall():    #call func_name
            string += "call " + instr.TargetLabel + "\n"
        elif instr.isReturn():
            pass
        elif instr.isLabel():   #label func_name
            string = instr.Label + ":\n"
        else:   #error
            pass
        print string

def getOperator(op):
    if op == tacinstr.TACInstr.ADD:
        return "addl"
    elif op == tacinstr.TACInstr.SUB:
        return "subl"
    elif op == tacinstr.TACInstr.MULT:
        return "imul"
    elif op == tacinstr.TACInstr.DIV:   #div consumes too many registers, will handle later
        pass
    elif op == tacinstr.TACInstr.SHL:
        return "sal"
    elif op == tacinstr.TACInstr.SHR:
        return "sar"
    elif op == tacinstr.TACInstr.AND:
        return "andl"
    elif op == tacinstr.TACInstr.OR:
        return "orl"
    elif op == tacinstr.TACInstr.XOR:
        return "xorl"
    elif op == tacinstr.TACInstr.MOD:    #use div and get result from edx
        pass
