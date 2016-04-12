import machine
import ircodegen as IG
import basicblock
import globjects as G

indent = " "*4

def translateBlock(bb):
    for instr in bb.instrList:
        # If we have reached the last instruction in the basic block, spill all registers.
        if instr == bb.instrList[-1] and instr.isJump():
            for regName in G.regNames:
                G.registerMap[regName].spill()
        G.currInstr = instr
        G.text.string += ".LABEL_" + str(instr.LineNo) + ":\n"
######################################################  assignment instruction ###################################################
        if instr.isAssign():
            if instr.Src2:  #assignment with binary operator    x = y op z
                op = getMnemonic(instr.Op)
                # DIV and MOD are special cases in x86. These require the 'idivl' instruction,
                # which in turn, requires the dividend to be placed in edx:eax (64 bits)
                if instr.Op == IG.TACInstr.DIV or instr.Op == IG.TACInstr.MOD:
                    # Saving contents of eax and edx on the stack
                    G.text.string += indent + "pushl %eax\n"
                    G.text.string += indent + "pushl %edx" + indent + "#clearing eax and edx for division\n"

                    # Moving the dividend into eax and the divisor onto the stack top
                    if instr.Src2.isInt():          # z is integer
                        G.text.string += indent + "pushl $" + str(instr.Src2.operand) + "\n"
                    elif instr.Src2.addrDescEntry.reg:    # z is in register
                        G.text.string += indent + "pushl %" + instr.Src2.addrDescEntry.reg.name + "\n"
                    else:                           # z is in memory
                        G.text.string += indent + "pushl " + instr.Src2.addrDescEntry.name + "\n"
                    if instr.Src1.isInt():          # y is integer
                        G.text.string += indent + "movl $" + str(instr.Src1.operand) + ", %eax\n"
                    elif instr.Src1.addrDescEntry.reg:    # y is in register
                        G.text.string += indent + "movl %" + instr.Src1.addrDescEntry.reg.name + ", %eax\n"
                    else:                           # y is in memory
                        G.text.string += indent + "movl " + instr.Src1.addrDescEntry.name + ", %eax\n"
                    G.text.string += indent + "cltd" + indent + "#sign extending eax into edx:eax\n"

                    # Performing the operation
                    G.text.string += indent + "idivl (%esp)\n"

                    # Operation complete. Moving the result into the appropriate place
                    if instr.Op == IG.TACInstr.DIV:
                        if instr.Dest.addrDescEntry.reg:  # x is in register
                            G.text.string += indent + "movl %eax, %" + instr.Dest.addrDescEntry.reg.name + "\n"
                        else:                       # x is in memory
                            G.text.string += indent + "movl %eax," + instr.Dest.addrDescEntry.name + "\n"
                    else:   # instr.op == MOD
                        if instr.Dest.addrDescEntry.reg:  # x is in register
                            G.text.string += indent + "movl %edx, %" + instr.Dest.addrDescEntry.reg.name + "\n"
                        else:                       # x is in memory
                            G.text.string += indent + "movl %edx," + instr.Dest.addrDescEntry.name + "\n"

                    # Restoring the stack and registers
                    G.text.string += indent + indent + "#restoring stack and registers\n"
                    if instr.Dest.addrDescEntry.reg:
                        if instr.Dest.addrDescEntry.reg.name == "eax":
                            G.text.string += indent + "addl $4, %esp\n" # restoring stack so that z value on stack can be overwritten
                            G.text.string += indent + "popl %edx\n"     # restoring edx
                            G.text.string += indent + "addl $4, %esp\n" # restoring stack so that eax value on stack can be overwritten
                        elif instr.Dest.addrDescEntry.reg.name == "edx":
                            G.text.string += indent + "addl $8, %esp\n" # removing z and edx(original value of x) stored on stack
                            G.text.string += indent + "popl %eax\n"     # restoring eax
                        else:
                            G.text.string += indent + "addl $4, %esp\n" # restoring stack so that z value on stack can be overwritten
                            G.text.string += indent + "popl %edx\n"     # restoring edx
                            G.text.string += indent + "popl %eax\n"     # restoring eax
                    else:
                        G.text.string += indent + "addl $4, %esp\n"     # restoring stack so that z value on stack can be overwritten
                        G.text.string += indent + "popl %edx\n"         # restoring edx
                        G.text.string += indent + "popl %eax\n"         # restoring eax

                # Operations other than DIV and MOD
                else:
                    locTuple = bb.getReg()
                    loc = locTuple[0]

                    # Moving the first operand into the destination register
                    if instr.Src1.isInt():  # y is integer
                        G.text.string += indent + "movl $" + str(instr.Src1.operand) + ", %" + loc.name + "\n"
                    elif locTuple[1]:   # y is variable and getReg returned y's register. so loc has y's value
                        pass
                    else:   # y is a variable and loc doesn't have y's value
                        if instr.Src1.addrDescEntry.reg:      # y exists in a non disposable register
                            G.text.string += indent + "movl %" + instr.Src1.addrDescEntry.reg.name + ", %" + loc.name + "\n"
                        else:   # y is a variable only in memory
                            G.text.string += indent + "movl " + instr.Src1.addrDescEntry.name + ", %" + loc.name + "\n"

                    # Performing the operation
                    # Case 1: Second operand is an immediate
                    if instr.Src2.isInt():
                        G.text.string += indent + op + " $" + str(instr.Src2.operand) + ", %" + loc.name + "\n"

                    # Case 2: Second operand is a variable in a register
                    elif instr.Src2.addrDescEntry.reg:    #z exists in a register
                        if instr.Op == IG.TACInstr.SHL or instr.Op == IG.TACInstr.SHR:
                            G.text.string += indent + "xchgl %ecx, %" + instr.Src2.addrDescEntry.reg.name + "\n"
                            G.text.string += indent + op + " %cl, %" + loc.name + "\n"
                            G.text.string += indent + "xchgl %ecx, %" + instr.Src2.addrDescEntry.reg.name + "\n"
                        else:
                            G.text.string += indent + op + " %" + instr.Src2.addrDescEntry.reg.name + ", %" + loc.name + "\n"

                    # Case 3: Second operand is a variable in memory
                    else:   #z doesn't exist in a register
                        if instr.Op == IG.TACInstr.SHL or instr.Op == IG.TACInstr.SHR:
                            G.text.string += indent + "xchgl %ecx, " + instr.Src2.addrDescEntry.name + "\n"
                            G.text.string += indent + op + " %cl, %" + loc.name + "\n"
                            G.text.string += indent + "xchgl %ecx, " + instr.Src2.addrDescEntry.name + "\n"
                        else:
                            G.text.string += indent + op + " " + instr.Src2.addrDescEntry.name + ", %" + loc.name + "\n"

                    # Update register and address descriptors
                    instr.Dest.addrDescEntry.loadIntoReg(loc.name)

            # Unary operator assignment
            elif instr.Op:  #assignment with unary operator a = op b
                # Operation is NOT of the form a = call foo
                if instr.Src1:
                    locTuple = bb.getReg()
                    loc = locTuple[0]

                    if not locTuple[1]:
                        # Moving operand into destination register to perform op
                        # Case 1: Operand is an immediate
                        if instr.Src1.isInt():  # b is integer
                            G.text.string += indent + "movl $" + str(instr.Src1.operand) + ", %" + loc.name + "\n"

                        # Case 2: Operand is in a register
                        elif instr.Src1.addrDescEntry.reg:   # b is in register
                            G.text.string += indent + "movl %" + instr.Src1.addrDescEntry.reg.name + ", %" + loc.name + "\n"

                        # Case 3: Operand is in memory
                        else:
                            G.text.string += indent + "movl " + instr.Src1.addrDescEntry.name + ", %" + loc.name + "\n"

                    # Performing the operation
                    if instr.Op == IG.TACInstr.SUB:
                        G.text.string += indent + "negl %" + loc.name + "\n"
                    elif instr.Op == IG.TACInstr.NOT:
                        G.text.string += indent + "notl %" + loc.name + "\n"
                    elif instr.Op == IG.TACInstr.ADD:
                        # This is basically a simple assignment. No asm instruction needed
                        pass
                    else:
                        G.halt(instr.LineNo, "undefined unary operator")

                    # Updating register and address descriptors
                    instr.Dest.addrDescEntry.loadIntoReg(loc.name)

                elif instr.Op == IG.TACInstr.CALLOP:   # a = call func_name
                    G.text.string += indent + "call " + instr.TargetLabel + "\n"
                    # No need to check if a is in a register or not, since the current
                    # instruction will be the last of this basic block
                    G.text.string += indent + "movl %eax, " + instr.Dest.addrDescEntry.name + "\n"
                else:
                    G.halt(instr.LineNo, "invalid assignment instruction with unary operator")

            # Basic assignment
            else:   # basic assignment   a = b
                # Case 1: b is an immediate
                if instr.Src1.isInt():  #b is integer
                    if instr.Dest.addrDescEntry.reg:  #a is in a register
                        G.text.string += indent + "movl $" + str(instr.Src1.operand) + ", %" + instr.Dest.addrDescEntry.reg.name + "\n"
                    else:   #a is in memory
                        G.text.string += indent + "movl $" + str(instr.Src1.operand) + ", " + instr.Dest.addrDescEntry.name + "\n"

                # Case 2: b is in a register
                elif instr.Src1.addrDescEntry.reg:    #b is in a register
                    # No matter where a is stored, its new location will be the
                    # register of b.
                    instr.Dest.addrDescEntry.loadIntoReg(instr.Src1.addrDescEntry.reg.name)

                # Case 3: b is in memory
                else:   # b is in memory
                    # If a is in a register
                    if instr.Dest.addrDescEntry.reg:
                        G.text.string += indent + "movl " + instr.Src1.addrDescEntry.name + ", %" + instr.Dest.addrDescEntry.reg.name + "\n"
                    # both a and b are in memory
                    else:
                        locTuple = bb.getReg()
                        loc = locTuple[0]
                        G.text.string += indent + "movl " + instr.Src1.addrDescEntry.name + ", %" + loc.name + "\n"
                        instr.Dest.addrDescEntry.loadIntoReg(loc.name)

######################################################  isIfGoto instruction #####################################################

        elif instr.isIfGoto():  # if i relop j jump L
            op = getMnemonic(instr.Op)
            label = " .LABEL_" + str(instr.Target)
            # cmpl instruction:  src1 relop src2 : cmpl src2, src1
            if instr.Src1.isInt() and instr.Src2.isInt():
                # Just do the comparison
                if instr.Src1.operand > instr.Src2.operand:
                    if instr.Op == IG.TACInstr.GT:
                        G.text.string += indent + "jmp " + label + "\n"
                    elif instr.Op == IG.TACInstr.GEQ:
                        G.text.string += indent + "jmp " + label + "\n"
                    else:
                        pass

                elif instr.Src1.operand < instr.Src2.operand:
                    if instr.Op == IG.TACInstr.LT:
                        G.text.string += indent + "jmp " + label + "\n"
                    elif instr.Op == IG.TACInstr.LEQ:
                        G.text.string += indent + "jmp " + label + "\n"
                    else:
                        pass
                else:
                    if instr.Op == IG.TACInstr.EQ:
                        G.text.string += indent + "jmp " + label + "\n"
                    else:
                        pass

            elif instr.Src1.isInt() and instr.Src2.isVar():
                op = getReversedMnemonic(instr.Op)
                if instr.Src2.addrDescEntry.reg:
                    G.text.string += indent + "cmpl $" + str(instr.Src1.operand) + ", %" + instr.Src2.addrDescEntry.reg.name + "\n"
                    G.text.string += indent + op + label + "\n" 
                else:
                    G.text.string += indent + "cmpl $" + str(instr.Src1.operand) + ", " + instr.Src2.addrDescEntry.name + "\n"
                    G.text.string += indent + op + label + "\n" 

            elif instr.Src1.addrDescEntry.reg and instr.Src2.isInt():
                G.text.string += indent + "cmpl $" + str(instr.Src2.operand) + ", %" + instr.Src1.addrDescEntry.reg.name + "\n"
                G.text.string += indent + op + label + "\n"

            elif instr.Src1.addrDescEntry.reg and instr.Src2.isVar():
                if instr.Src2.addrDescEntry.reg:
                    G.text.string += indent + "cmpl %" + instr.Src2.addrDescEntry.reg.name + ", %" + instr.Src1.addrDescEntry.reg.name + "\n"
                    G.text.string += indent + op + label + "\n"
                else:
                    G.text.string += indent + "cmpl " + instr.Src2.addrDescEntry.name + ", %" + instr.Src1.addrDescEntry.reg.name + "\n"
                    G.text.string += indent + op + label + "\n"

            elif instr.Src1.isVar() and instr.Src2.isInt():
                G.text.string += indent + "cmpl $" + str(instr.Src2.operand) + ", " + instr.Src1.addrDescEntry.name + "\n"
                G.text.string += indent + op + label + "\n"

            elif instr.Src1.isVar() and instr.Src2.isVar():
                if instr.Src2.addrDescEntry.reg:
                    G.text.string += indent + "cmpl %" + instr.Src2.addrDescEntry.reg.name + ", " + instr.Src1.addrDescEntry.name + "\n"
                    G.text.string += indent + op + label + "\n"
                else:
                    locTuple = bb.getReg()
                    loc = locTuple[0]
                    G.text.string += indent + "movl " + instr.Src2.addrDescEntry.name + ", %" + loc.name + "\n"
                    G.text.string += indent + "cmpl %" + loc.name + "," + instr.Src1.addrDescEntry.name + "\n"
                    G.text.string += indent + op + label + "\n"
                    instr.Src2.addrDescEntry.loadIntoReg(loc.name)

######################################################  isGoto instruction #######################################################

        elif instr.isGoto():    #goto line_no
            G.text.string += indent + "jmp .LABEL_" + str(instr.Target) + "\n"

######################################################  isCall instruction #######################################################

        elif instr.isCall():    #call func_name
            G.text.string += indent + "call " + instr.TargetLabel + "\n"

######################################################  isReturn instruction #####################################################

        elif instr.isReturn():
            # If there is a value to return
            if instr.Src1:
                G.registerMap["eax"].spill()
                if instr.Src1.isInt():
                    G.text.string += indent + "movl $" + str(instr.Src1.operand) + ", %eax\n"
                elif instr.Src1.addrDescEntry.reg:
                    G.text.string += indent + "movl %" + instr.Src1.addrDescEntry.reg.name + ", %eax\n"
                else:
                    G.text.string += indent + "movl " + instr.Src1.addrDescEntry.name + ", %eax\n"

            # Issue the ret instruction
            G.text.string += indent + "ret\n"

######################################################  isLabel instruction #####################################################

        elif instr.isLabel():   #label func_name
            G.text.string += instr.Label + ":\n"

######################################################  Printf instruction ######################################################

        elif instr.isPrintf():  # printf fmt args
            # Preserve the value of eax, ecx and edx registers, since printf
            # considers these as trashable registers.
            G.text.string += indent + "pushl %eax" + indent + "# Saving register on stack\n"
            G.text.string += indent + "pushl %ecx" + indent + "# Saving register on stack\n"
            G.text.string += indent + "pushl %edx" + indent + "# Saving register on stack\n"

            # Push arguments in reverse order
            for arg in reversed(instr.IOArgList):
                if arg.isVar():
                    if arg.addrDescEntry.reg:
                        G.text.string += indent + "pushl %" + arg.addrDescEntry.reg.name  + indent + "# Pushing argument\n"
                    else:
                        G.text.string += indent + "pushl " + arg.addrDescEntry.name + indent + "# Pushing argument\n"
                elif arg.isInt():
                    G.text.string += indent + "pushl $" + str(arg.operand) + indent + "# Pushing argument\n"
            G.text.string += indent + "pushl $" + instr.IOFmtStringAddr + indent + "# Pushing argument\n"
            G.text.string += indent + "call printf\n"
            G.text.string += indent + "addl $" + str(4 * (len(instr.IOArgList) + 1)) + ", %esp\n"

            # Restore the value of registers saved before the call
            G.text.string += indent + "popl %edx" + indent + "# Restoring register from stack\n"
            G.text.string += indent + "popl %ecx" + indent + "# Restoring register from stack\n"
            G.text.string += indent + "popl %eax" + indent + "# Restoring register from stack\n"

######################################################  Scanf instruction ######################################################

        elif instr.isScanf():  # scanf fmt args
            # Preserve the value of eax register, since scanf
            # considers these as trashable registers.
            G.text.string += indent + "pushl %eax" + indent + "# Saving register on stack\n"
            G.text.string += indent + "pushl %ecx" + indent + "# Saving register on stack\n"
            G.text.string += indent + "pushl %edx" + indent + "# Saving register on stack\n"

            # Push arguments in reverse order
            for arg in reversed(instr.IOArgList):
                if arg.isVar():
                    # Discard the register value for arg
                    arg.addrDescEntry.removeReg()
                    G.text.string += indent + "pushl $" + arg.addrDescEntry.name + indent + "# Pushing argument\n"
            G.text.string += indent + "pushl $" + instr.IOFmtStringAddr + indent + "# Pushing argument\n"
            G.text.string += indent + "call scanf\n"
            G.text.string += indent + "addl $" + str(4 * (len(instr.IOArgList) + 1)) + ", %esp\n"

            # Restore the value of registers saved before the call
            G.text.string += indent + "popl %edx" + indent + "# Restoring register from stack\n"
            G.text.string += indent + "popl %ecx" + indent + "# Restoring register from stack\n"
            G.text.string += indent + "popl %eax" + indent + "# Restoring register from stack\n"

##################################################### Unsupported instruction ##################################################

        else:
            G.halt(instr.LineNo, "unsupported instruction")

        # If last instruction is not jump, spill registers now.
        if instr == bb.instrList[-1] and not instr.isJump():
            for regName in G.regNames:
                G.registerMap[regName].spill()


def getMnemonic(op):
    if op == IG.TACInstr.ADD:
        return "addl"
    elif op == IG.TACInstr.SUB:
        return "subl"
    elif op == IG.TACInstr.MULT:
        return "imul"
    elif op == IG.TACInstr.DIV:
        return "idiv"
    elif op == IG.TACInstr.SHL:
        return "sal"
    elif op == IG.TACInstr.SHR:
        return "sar"
    elif op == IG.TACInstr.AND:
        return "andl"
    elif op == IG.TACInstr.OR:
        return "orl"
    elif op == IG.TACInstr.XOR:
        return "xorl"
    elif op == IG.TACInstr.MOD:
        return "idiv"
    elif op == IG.TACInstr.GEQ:
        return "jge"
    elif op == IG.TACInstr.GT:
        return "jg"
    elif op == IG.TACInstr.LEQ:
        return "jle"
    elif op == IG.TACInstr.LT:
        return "jl"
    elif op == IG.TACInstr.EQ:
        return "je"
    elif op == IG.TACInstr.NEQ:
        return "jne"
    else:
        pass

def getReversedMnemonic(op):
    if op == IG.TACInstr.EQ:
        return "je"
    elif op == IG.TACInstr.NEQ:
        return "jne"
    elif op == IG.TACInstr.GEQ:
        return "jle"
    elif op == IG.TACInstr.GT:
        return "jl"
    elif op == IG.TACInstr.LEQ:
        return "jge"
    elif op == IG.TACInstr.LT:
        return "jg"
    else:
        pass
