import machine
import tacinstr
import basicblock
import globjects as G

indent = " "*4

def translateBlock(bb):
    for instr in bb.instrList:
        G.currInstr = instr
        G.text.string = ".LABEL_" + str(instr.LineNo) + ":\n"
######################################################  assignment instruction ###################################################
        if instr.isAssign():
            if instr.Src2:  #assignment with binary operator    x = y op z
                op = getMnemonic(instr.Op)
                if instr.Op == tacinstr.TACInstr.DIV or instr.Op == tacinstr.TACInstr.MOD:
                    G.text.string += indent + "pushl %eax\n" + indent + "pushl %edx" + " "*4 +";clearing eax and edx for division\n"
                    if instr.Src2.isInt():  # z is integer
                        G.text.string += indent + "pushl $" + str(instr.Src2.operand) + "\n"
                    elif instr.Src2.operand.reg:    # z is in register
                        G.text.string += indent + "pushl %" + instr.Src2.operand.reg.name + "\n"
                    else:   # z is in memory
                        G.text.string += indent + "pushl " + instr.Src2.operand.name + "\n"
                    if instr.Src1.isInt():  # y is integer
                        G.text.string += indent + "movl $" + str(instr.Src1.operand) + ",%eax\n"
                    elif instr.Src1.operand.reg:    # y is in register
                        G.text.string += indent + "movl %" + instr.Src1.operand.reg.name + ",%eax\n"
                    else:   # y is in memory
                        G.text.string += indent + "movl " + instr.Src1.operand.name + ",%eax\n"
                    G.text.string += indent + "cltd" + " "*4 +";splitting eax into edx:eax\n"  # split eax into edx:eax for division
                    G.text.string += indent + "idiv (%esp)\n"
                    if instr.Op == tacinstr.TACInstr.DIV:
                        if instr.Dest.operand.reg:  # x is in register
                            G.text.string += indent + "movl %eax,%" + instr.Dest.operand.reg.name + "\n"
                        else:   # x is in memory
                            G.text.string += indent + "movl %eax," + instr.Dest.operand.name + "\n"
                    else:   # op == "mod"
                        if instr.Dest.operand.reg:  # x is in register
                            G.text.string += indent + "movl %edx,%" + instr.Dest.operand.reg.name + "\n"
                        else:   # x is in memory
                            G.text.string += indent + "movl %edx," + instr.Dest.operand.name + "\n"
                    # restoring the stack and registers
                    G.text.string += indent + " "*4 + ";restoring stack and registers\n"
                    if instr.Dest.operand.reg:
                        if instr.Dest.operand.reg.name == "eax":
                            G.text.string += indent + "addl $4,%esp\n" # restoring stack so that z value on stack can be overwritten
                            G.text.string += indent + "popl %edx\n"    # restoring edx
                            G.text.string += indent + "addl $4,%esp\n" # restoring stack so that eax value on stack can be overwritten
                        elif instr.Dest.operand.reg.name == "edx":
                            G.text.string += indent + "addl $8,%esp\n" # removing z and edx(original value of x) stored on stack
                            G.text.string += indent + "popl %eax\n"    # restoring eax
                        else:
                            G.text.string += indent + "addl $4,%esp\n" # restoring stack so that z value on stack can be overwritten
                            G.text.string += indent + "popl %edx\n"    # restoring edx
                            G.text.string += indent + "popl %eax\n"    # restoring eax
                    else:
                        G.text.string += indent + "addl $4,%esp\n" # restoring stack so that z value on stack can be overwritten
                        G.text.string += indent + "popl %edx\n"    # restoring edx
                        G.text.string += indent + "popl %eax\n"    # restoring eax
                else:
                    location = bb.getReg()
                    loc = location[0]
                    if instr.Src1.isInt():  # y is integer
                        G.text.string += indent + "movl $" + str(instr.Src1.operand) + ",%" + loc.name + "\n"
                    elif location[1]:   # y is variable and getReg returned y's register. so loc has y's value
                        pass
                    else:   # y is a variable and loc doesn't have y's value
                        G.text.string += indent + "movl " + instr.Src1.operand.name + ",%" + loc.name + "\n"
                    if instr.Src2.isInt():
                        G.text.string += indent + op + " $" + str(instr.Src2.operand) + ",%" + loc.name + "\n"
                    elif instr.Src2.operand.reg:    #z exists in a register
                        if instr.Src2.operand.reg.name != "ecx" and (instr.Op == tacinstr.TACInstr.SHL or instr.Op == tacinstr.TACInstr.SHR):
                            G.text.string += indent + "xchgl %ecx,%" + instr.Src2.operand.reg.name + "\n"
                        G.text.string += indent + op + " %" + instr.Src2.operand.reg.name + ",%" + loc.name + "\n"
                        if instr.Src2.operand.reg.name != "ecx" and (instr.Op == tacinstr.TACInstr.SHL or instr.Op == tacinstr.TACInstr.SHR):
                            G.text.string += indent + "xchgl %ecx,%" + instr.Src2.operand.reg.name + "\n"
                    else:   #z doesn't exist in a register
                        if instr.Src2.operand.reg.name != "ecx" and (instr.Op == tacinstr.TACInstr.SHL or instr.Op == tacinstr.TACInstr.SHR):
                            G.text.string += indent + "xchgl %ecx," + instr.Src2.operand.name + "\n"
                        G.text.string += indent + op + " " + instr.Src2.operand.name + ",%" + loc.name + "\n"
                        if instr.Src2.operand.reg.name != "ecx" and (instr.Op == tacinstr.TACInstr.SHL or instr.Op == tacinstr.TACInstr.SHR):
                            G.text.string += indent + "xchgl %ecx," + instr.Src2.operand.name + "\n"
                    instr.Dest.operand.loadIntoReg(loc.name)
            elif instr.Op:  #assignment wirh unary operator a = op b
                if instr.Src1:
                    if instr.Src1.operand.reg:  #b exists in a register
                        loc = instr.Src1.operand.reg
                    else:
                        loc = bb.getReg()
                        loc = loc[0]
                    if instr.Src1.isInt():  #b is integer
                        G.text.string += indent + "movl $" + str(instr.Src1.operand) + ",%" + loc.name + "\n"
                    elif not instr.Src1.operand.reg:   #b is in memory
                        G.text.string += indent + "movl " + instr.Src1.operand.name + ",%" + loc.name + "\n"
                    if instr.Op == tacinstr.TACInstr.SUB:
                        G.text.string += indent + "imul $-1,%" + loc.name + "\n"
                    elif instr.Op == tacinstr.TACInstr.NOT:
                        G.text.string += indent + "notl %" + loc.name + "\n"
                    elif instr.Op == tacinstr.TACInstr.ADD:
                        pass
                    else:
                        G.halt(instr.LineNo, "undefined unary operator")
                    instr.Dest.operand.loadIntoReg(loc.name)
                elif instr.Op == tacinstr.TACInstr.CALL:   # a = call func_name
                    G.text.string += indent + "call " + instr.TargetLabel + "\n"
                    G.text.string += indent + "movl %eax," + instr.Dest.operand.name + "\n"
                else:
                    G.halt(instr.LineNo, "invalid assignment instruction with unary operator")
            else:   #basic assignment   a = b
                if instr.Src1.isInt():  #b is integer
                    if instr.Dest.operand.reg:  #a is in a register
                        G.text.string += indent + "movl $" + str(instr.Src1.operand) + ",%" + instr.Dest.operand.reg.name + "\n"
                    else:   #a is in memory
                        G.text.string += indent + "movl $" + str(instr.Src1.operand) + "," + instr.Dest.operand.name + "\n"
                elif instr.Src1.operand.reg:    #b is in a register
                    if instr.Dest.operand.reg:  #a is also in register. So spill a's register and indicate in b's that a is also stored there
                        instr.Dest.operand.reg.removeVar(instr.Dest.operand.name)
                        instr.Src1.operand.reg.addVar(instr.Dest.operand.name)
                    else:   #a is in memory
                        instr.Dest.operand.loadIntoReg(instr.Src1.operand.reg)
                else:   #b is in memory
                    if instr.Dest.operand.reg:
                        G.text.string += indent + "movl " + instr.Src1.operand.name + ",%" + instr.Dest.operand.reg.name + "\n"
                    else:   # both a and b are in memory
                        loc = bb.getReg()
                        loc = loc[0]
                        G.text.string += indent + "movl " + instr.Src1.operand.name + ",%" + loc.name + "\n"
                        instr.Dest.operand.loadIntoReg(loc.name)
######################################################  isIfGoto instruction #####################################################
        elif instr.isIfGoto():  # if i relop j jump L
            if instr.Src1.isInt():  # i is integer. cmpl should not have immediate as first argument
                G.text.string += indent + "pushl $" + str(instr.Src1.operand) + "\n"
                if instr.Src2.isInt():
                    G.text.string += indent + "cmpl $" + str(instr.Src2.operand) + ",(%esp)\n"
                elif instr.Src2.operand.reg:
                    G.text.string += indent + "cmpl %" + instr.Src2.operand.reg.name + ",(%esp)\n"
                else:
                    G.text.string += indent + "cmpl " + instr.Src2.operand.name + ",(%esp)\n"
                G.text.string += indent + "addl $4,%esp\n"
            elif instr.Src1.operand.reg:
                if instr.Src2.isInt():
                    G.text.string += indent + "cmpl $" + str(instr.Src2.operand)
                elif instr.Src2.operand.reg:
                    G.text.string += indent + "cmpl %" + instr.Src2.operand.reg.name
                else:
                    G.text.string += indent + "cmpl " + instr.Src2.operand.name
                G.text.string += ",%" + instr.Src1.operand.reg.name + "\n"
            else:
                if instr.Src2.isInt():
                    G.text.string += indent + "cmpl $" + str(instr.Src2.operand)
                elif instr.Src2.operand.reg:
                    G.text.string += indent + "cmpl %" + instr.Src2.operand.reg.name
                else:
                    G.text.string += indent + "cmpl " + instr.Src2.operand.name
                G.text.string += "," + instr.Src1.operand.name + "\n"
            if instr.Op == tacinstr.TACInstr.GEQ:
                G.text.string += indent + "jge "
            elif instr.Op == tacinstr.TACInstr.GT:
                G.text.string += indent + "jg "
            elif instr.Op == tacinstr.TACInstr.LEQ:
                G.text.string += indent + "jle "
            elif instr.Op == tacinstr.TACInstr.LT:
                G.text.string += indent + "jl "
            elif instr.Op == tacinstr.TACInstr.EQ:
                G.text.string += indent + "je "
            elif instr.Op == tacinstr.TACInstr.NEQ:
                G.text.string += indent + "jne "
            else:
                G.halt(instr.LineNo, "undefined relational operator")
            G.text.string += ".LABEL_" + str(instr.Target) + "\n"
######################################################  isGoto instruction #######################################################
        elif instr.isGoto():    #goto line_no
            G.text.string += indent + "jmp .LABEL_" + str(instr.Target) + "\n"
######################################################  isCall instruction #######################################################
        elif instr.isCall():    #call func_name
            G.text.string += indent + "call " + instr.TargetLabel + "\n"
######################################################  isReturn instruction #####################################################
        elif instr.isReturn():
            if instr.Src1:
                G.registerMap["eax"].spill()
                if instr.Src1.isInt():
                    G.text.string += indent + "movl $" + str(instr.Src1.operand) + ",%eax\n"
                elif instr.Src1.operand.reg:
                    G.text.string += indent + "movl %" + instr.Src1.operand.reg.name + ",%eax\n"
                else:
                    G.text.string += indent + "movl " + instr.Src1.operand.name + ",%eax\n"
                G.text.string += indent + "ret\n"
            else:
                G.text.string += indent + "ret\n"
######################################################  isLabel instruction #####################################################
        elif instr.isLabel():   #label func_name
            G.text.string = instr.Label + ":\n"
######################################################  Printf instruction ######################################################
        elif instr.isPrintf():  # printf fmt args
            for arg in reversed(instr.IOArgList):
                if arg.isVar():
                    G.text.string += indent + "pushl " + arg.operand.name + "\n"
                elif arg.isInt():
                    G.text.string += indent + "pushl $" + str(arg.operand) + "\n"
            G.text.string += indent + "pushl $" + instr.IOFmtStringAddr + "\n"
            G.text.string += indent + "call printf\n"
            G.text.string += indent + "addl $" + str(4 * (len(instr.IOArgList) + 1)) + "%esp\n"
######################################################  Scanf instruction ######################################################
        elif instr.isPrintf():  # scanf fmt args
            for arg in reversed(instr.IOArgList):
                if arg.isVar():
                    G.text.string += indent + "pushl $" + arg.operand.name + "\n"
            G.text.string += indent + "pushl $" + instr.IOFmtStringAddr + "\n"
            G.text.string += indent + "call scanf\n"
            G.text.string += indent + "addl $" + str(4 * (len(instr.IOArgList) + 1)) + "%esp\n"
##################################################### Unsupported instruction ##################################################
        else:
            G.halt(instr.LineNo, "unsupported instruction")

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
