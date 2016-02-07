import machine
import tacinstr
import basicblock
import globjects

indent = "    "

def translateBlock(bb):
    for instr in bb.instrList:
        globjects.currInstr = instr
        string = ".LABEL_" + str(instr.LineNo) + ":\n"
######################################################  assignment instruction ###################################################
        if instr.isAssign():
            if instr.Src2:  #assignment with binary operator    x = y op z
                op = getMnemonic(instr.Op)
                if instr.Op == tacinstr.TACInstr.DIV or instr.Op == tacinstr.TACInstr.MOD:
                    string += indent + "pushl %eax\n" + indent + "pushl %edx" + " "*4 +";clearing eax and edx for division\n"
                    if instr.Src2.isInt():  # z is integer
                        string += indent + "pushl $" + str(instr.Src2.operand) + "\n"
                    elif instr.Src2.operand.reg:    # z is in register
                        string += indent + "pushl %" + instr.Src2.operand.reg.name + "\n"
                    else:   # z is in memory
                        string += indent + "pushl " + instr.Src2.operand.name + "\n"
                    if instr.Src1.isInt():  # y is integer
                        string += indent + "movl $" + str(instr.Src1.operand) + ",%eax\n"
                    elif instr.Src1.operand.reg:    # y is in register
                        string += indent + "movl %" + instr.Src1.operand.reg.name + ",%eax\n"
                    else:   # y is in memory
                        string += indent + "movl " + instr.Src1.operand.name + ",%eax\n"
                    string += indent + "cltd" + " "*4 +";splitting eax into edx:eax\n"  # split eax into edx:eax for division
                    string += indent + "idiv (%esp)\n"
                    if instr.Op == tacinstr.TACInstr.DIV:
                        if instr.Dest.operand.reg:  # x is in register
                            string += indent + "movl %eax,%" + instr.Dest.operand.reg.name + "\n"
                        else:   # x is in memory
                            string += indent + "movl %eax," + instr.Dest.operand.name + "\n"
                    else:   # op == "mod"
                        if instr.Dest.operand.reg:  # x is in register
                            string += indent + "movl %edx,%" + instr.Dest.operand.reg.name + "\n"
                        else:   # x is in memory
                            string += indent + "movl %edx," + instr.Dest.operand.name + "\n"
                    # restoring the stack and registers
                    string += indent + " "*4 + ";restoring stack and registers\n"
                    if instr.Dest.operand.reg:
                        if instr.Dest.operand.reg.name == "eax":
                            string += indent + "addl $4,%esp\n" # restoring stack so that z value on stack can be overwritten
                            string += indent + "popl %edx\n"    # restoring edx
                            string += indent + "addl $4,%esp\n" # restoring stack so that eax value on stack can be overwritten
                        elif instr.Dest.operand.reg.name == "edx":
                            string += indent + "addl $8,%esp\n" # removing z and edx(original value of x) stored on stack
                            string += indent + "popl %eax\n"    # restoring eax
                        else:
                            string += indent + "addl $4,%esp\n" # restoring stack so that z value on stack can be overwritten
                            string += indent + "popl %edx\n"    # restoring edx
                            string += indent + "popl %eax\n"    # restoring eax
                    else:
                        string += indent + "addl $4,%esp\n" # restoring stack so that z value on stack can be overwritten
                        string += indent + "popl %edx\n"    # restoring edx
                        string += indent + "popl %eax\n"    # restoring eax
                else:
                    location = bb.getReg()
                    loc = location[0]
                    if instr.Src1.isInt():  # y is integer
                        string += indent + "movl $" + str(instr.Src1.operand) + ",%" + loc.name + "\n"
                    elif location[1]:   # y is variable and getReg returned y's register. so loc has y's value
                        pass
                    else:   # y is a variable and loc doesn't have y's value
                        string += indent + "movl " + instr.Src1.operand.name + ",%" + loc.name + "\n"
                    if instr.Src2.isInt():
                        string += indent + op + " $" + str(instr.Src2.operand) + ",%" + loc.name + "\n"
                    elif instr.Src2.operand.reg:    #z exists in a register
                        if instr.Src2.operand.reg.name != "ecx" and (instr.Op == tacinstr.TACInstr.SHL or instr.Op == tacinstr.TACInstr.SHR):
                            string += indent + "xchgl %ecx,%" + instr.Src2.operand.reg.name + "\n"
                        string += indent + op + " %" + instr.Src2.operand.reg.name + ",%" + loc.name + "\n"
                        if instr.Src2.operand.reg.name != "ecx" and (oinstr.Op == tacinstr.TACInstr.SHL or instr.Op == tacinstr.TACInstr.SHR):
                            string += indent + "xchgl %ecx,%" + instr.Src2.operand.reg.name + "\n"
                    else:   #z doesn't exist in a register
                        if instr.Src2.operand.reg.name != "ecx" and (instr.Op == tacinstr.TACInstr.SHL or instr.Op == tacinstr.TACInstr.SHR):
                            string += indent + "xchgl %ecx," + instr.Src2.operand.name + "\n"
                        string += indent + op + " " + instr.Src2.operand.name + ",%" + loc.name + "\n"
                        if instr.Src2.operand.reg.name != "ecx" and (instr.Op == tacinstr.TACInstr.SHL or instr.Op == tacinstr.TACInstr.SHR):
                            string += indent + "xchgl %ecx," + instr.Src2.operand.name + "\n"
                    instr.Dest.operand.loadIntoReg(loc.name)
            elif instr.Op:  #assignment wirh unary operator a = op b
                if instr.Src1:
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
                elif instr.Op == tacinstr.TACInstr.CALL:   # a = call func_name
                    string += indent + "call " + instr.TargetLabel + "\n"
                    if instr.Dest.operand.reg:
                        string += indent + "movl %eax,%" + instr.Dest.operand.reg.name + "\n"
                    else:
                        string += indent + "movl %eax," + instr.Dest.operand.name + "\n"
                else:   #error
                    pass                
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
######################################################  isIfGoto instruction #####################################################
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
######################################################  isGoto instruction #######################################################
        elif instr.isGoto():    #goto line_no
            string += indent + "jmp .LABEL_" + str(instr.Target) + "\n"
######################################################  isCall instruction #######################################################
        elif instr.isCall():    #call func_name
            string += indent + "call " + instr.TargetLabel + "\n"
######################################################  isReturn instruction #####################################################
        elif instr.isReturn():
            if instr.Src1:
                globjects.registerMap["eax"].spill()
                if instr.Src1.isInt():
                    string += indent + "movl $" + str(instr.Src1.operand) + ",%eax\n"
                elif instr.Src1.operand.reg:
                    string += indent + "movl %" + instr.Src1.operand.reg.name + ",%eax\n"
                else:
                    string += indent + "movl " + instr.Src1.operand.name + ",%eax\n"
                string += indent + "ret\n"
            else:
                string += indent + "ret\n"
######################################################  isLabel instruction ######################################################
        elif instr.isLabel():   #label func_name
            string = instr.Label + ":\n"
        else:   #error
            pass
        print string

def getMnemonic(op):
    if op == tacinstr.TACInstr.ADD:
        return "addl"
    elif op == tacinstr.TACInstr.SUB:
        return "subl"
    elif op == tacinstr.TACInstr.MULT:
        return "imul"
    elif op == tacinstr.TACInstr.DIV:
        return "idiv"
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
    elif op == tacinstr.TACInstr.MOD:
        return "idiv"
