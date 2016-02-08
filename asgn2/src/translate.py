import machine
import tacinstr
import basicblock
import globjects as G

indent = " "*4

def translateBlock(bb):
    for instr in bb.instrList:
        # If we have reached the last instruction in the basic block, spill all registers.
        if instr == bb.instrList[-1]:
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
                if instr.Op == tacinstr.TACInstr.DIV or instr.Op == tacinstr.TACInstr.MOD:
                    # Saving contents of eax and edx on the stack
                    G.text.string += indent + "pushl %eax\n"
                    G.text.string += indent + "pushl %edx" + indent + "#clearing eax and edx for division\n"

                    # Moving the dividend into eax and the divisor onto the stack top
                    if instr.Src2.isInt():          # z is integer
                        G.text.string += indent + "pushl $" + str(instr.Src2.operand) + "\n"
                    elif instr.Src2.operand.reg:    # z is in register
                        G.text.string += indent + "pushl %" + instr.Src2.operand.reg.name + "\n"
                    else:                           # z is in memory
                        G.text.string += indent + "pushl " + instr.Src2.operand.name + "\n"
                    if instr.Src1.isInt():          # y is integer
                        G.text.string += indent + "movl $" + str(instr.Src1.operand) + ", %eax\n"
                    elif instr.Src1.operand.reg:    # y is in register
                        G.text.string += indent + "movl %" + instr.Src1.operand.reg.name + ", %eax\n"
                    else:                           # y is in memory
                        G.text.string += indent + "movl " + instr.Src1.operand.name + ", %eax\n"
                    G.text.string += indent + "cltd" + indent + "#sign extending eax into edx:eax\n"

                    # Performing the operation
                    G.text.string += indent + "idivl (%esp)\n"

                    # Operation complete. Moving the result into the appropriate place
                    if instr.Op == tacinstr.TACInstr.DIV:
                        if instr.Dest.operand.reg:  # x is in register
                            G.text.string += indent + "movl %eax, %" + instr.Dest.operand.reg.name + "\n"
                        else:                       # x is in memory
                            G.text.string += indent + "movl %eax," + instr.Dest.operand.name + "\n"
                    else:   # instr.op == MOD
                        if instr.Dest.operand.reg:  # x is in register
                            G.text.string += indent + "movl %edx, %" + instr.Dest.operand.reg.name + "\n"
                        else:                       # x is in memory
                            G.text.string += indent + "movl %edx," + instr.Dest.operand.name + "\n"

                    # Restoring the stack and registers
                    G.text.string += indent + indent + "#restoring stack and registers\n"
                    if instr.Dest.operand.reg:
                        if instr.Dest.operand.reg.name == "eax":
                            G.text.string += indent + "addl $4, %esp\n" # restoring stack so that z value on stack can be overwritten
                            G.text.string += indent + "popl %edx\n"     # restoring edx
                            G.text.string += indent + "addl $4, %esp\n" # restoring stack so that eax value on stack can be overwritten
                        elif instr.Dest.operand.reg.name == "edx":
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
                        G.text.string += indent + "movl " + instr.Src1.operand.name + ", %" + loc.name + "\n"

                    # Performing the operation
                    # Case 1: Second operand is an immediate
                    if instr.Src2.isInt():
                        G.text.string += indent + op + " $" + str(instr.Src2.operand) + ", %" + loc.name + "\n"

                    # Case 2: Second operand is a variable in a register
                    elif instr.Src2.operand.reg:    #z exists in a register
                        if instr.Op == tacinstr.TACInstr.SHL or instr.Op == tacinstr.TACInstr.SHR:
                            G.text.string += indent + "xchgl %ecx, %" + instr.Src2.operand.reg.name + "\n"
                            G.text.string += indent + op + " %cl, %" + loc.name + "\n"
                            G.text.string += indent + "xchgl %ecx, %" + instr.Src2.operand.reg.name + "\n"
                        else:
                            G.text.string += indent + op + " %" + instr.Src2.operand.reg.name + ", %" + loc.name + "\n"

                    # Case 3: Second operand is a variable in memory
                    else:   #z doesn't exist in a register
                        if instr.Op == tacinstr.TACInstr.SHL or instr.Op == tacinstr.TACInstr.SHR:
                            G.text.string += indent + "xchgl %ecx, " + instr.Src2.operand.name + "\n"
                            G.text.string += indent + op + " %cl, %" + loc.name + "\n"
                            G.text.string += indent + "xchgl %ecx, " + instr.Src2.operand.name + "\n"
                        else:
                            G.text.string += indent + op + " " + instr.Src2.operand.name + ", %" + loc.name + "\n"

                    # Update register and address descriptors
                    instr.Dest.operand.loadIntoReg(loc.name)

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
                        elif instr.Src1.operand.reg:   # b is in register
                            G.text.string += indent + "movl %" + instr.Src1.operand.reg.name + ", %" + loc.name + "\n"

                        # Case 3: Operand is in memory
                        else:
                            G.text.string += indent + "movl " + instr.Src1.operand.name + ", %" + loc.name + "\n"

                    # Performing the operation
                    if instr.Op == tacinstr.TACInstr.SUB:
                        G.text.string += indent + "negl %" + loc.name + "\n"
                    elif instr.Op == tacinstr.TACInstr.NOT:
                        G.text.string += indent + "notl %" + loc.name + "\n"
                    elif instr.Op == tacinstr.TACInstr.ADD:
                        # This is basically a simple assignment. No asm instruction needed
                        pass
                    else:
                        G.halt(instr.LineNo, "undefined unary operator")

                    # Updating register and address descriptors
                    instr.Dest.operand.loadIntoReg(loc.name)

                elif instr.Op == tacinstr.TACInstr.CALLOP:   # a = call func_name
                    G.text.string += indent + "call " + instr.TargetLabel + "\n"
                    # No need to check if a is in a register or not, since the current
                    # instruction will be the last of this basic block
                    G.text.string += indent + "movl %eax, " + instr.Dest.operand.name + "\n"
                else:
                    G.halt(instr.LineNo, "invalid assignment instruction with unary operator")

            # Basic assignment
            else:   # basic assignment   a = b
                # Case 1: b is an immediate
                if instr.Src1.isInt():  #b is integer
                    if instr.Dest.operand.reg:  #a is in a register
                        G.text.string += indent + "movl $" + str(instr.Src1.operand) + ", %" + instr.Dest.operand.reg.name + "\n"
                    else:   #a is in memory
                        G.text.string += indent + "movl $" + str(instr.Src1.operand) + ", " + instr.Dest.operand.name + "\n"

                # Case 2: b is in a register
                elif instr.Src1.operand.reg:    #b is in a register
                    # No matter where a is stored, its new location will be the
                    # register of b.
                    instr.Dest.operand.loadIntoReg(instr.Src1.operand.reg)

                # Case 3: b is in memory
                else:   # b is in memory
                    # If a is in a register
                    if instr.Dest.operand.reg:
                        G.text.string += indent + "movl " + instr.Src1.operand.name + ", %" + instr.Dest.operand.reg.name + "\n"
                    # both a and b are in memory
                    else:
                        locTuple = bb.getReg()
                        loc = locTuple[0]
                        G.text.string += indent + "movl " + instr.Src1.operand.name + ", %" + loc.name + "\n"
                        instr.Dest.operand.loadIntoReg(loc.name)

######################################################  isIfGoto instruction #####################################################

        elif instr.isIfGoto():  # if i relop j jump L
            op = getMnemonic(instr.Op)
            # cmpl instruction:  src1 relop src2 : cmpl src2, src1
            if instr.Src1.isInt():  # i is integer. cmpl should not have immediate as first argument
                # Push the immediate on the stack
                G.text.string += indent + "pushl $" + str(instr.Src1.operand) + "\n"

                # Perform the comparison
                if instr.Src2.isInt():
                    G.text.string += indent + "cmpl $" + str(instr.Src2.operand) + ", (%esp)\n"
                elif instr.Src2.operand.reg:
                    G.text.string += indent + "cmpl %" + instr.Src2.operand.reg.name + ", (%esp)\n"
                else:
                    locTuple = bb.getReg()
                    loc = locTuple[0]
                    G.text.string += indent + "movl " + instr.Src2.operand.name + ", %" + loc.name + "\n"
                    G.text.string += indent + "cmpl %" + loc.name + ", (%esp)\n"
                    instr.Src2.operand.loadIntoReg(loc.name)

                # Remove the immediate from the stack
                G.text.string += indent + "addl $4, %esp\n"

            # If i is in a register
            elif instr.Src1.operand.reg:
                if instr.Src2.isInt():
                    G.text.string += indent + "cmpl $" + str(instr.Src2.operand)
                elif instr.Src2.operand.reg:
                    G.text.string += indent + "cmpl %" + instr.Src2.operand.reg.name
                else:
                    G.text.string += indent + "cmpl " + instr.Src2.operand.name
                G.text.string += ", %" + instr.Src1.operand.reg.name + "\n"

            # If i is in memory
            else:
                if instr.Src2.isInt():
                    G.text.string += indent + "cmpl $" + str(instr.Src2.operand) + "," + instr.Src1.operand.name + "\n"
                elif instr.Src2.operand.reg:
                    G.text.string += indent + "cmpl %" + instr.Src2.operand.reg.name + "," + instr.Src1.operand.name + "\n"
                else:
                    locTuple = bb.getReg()
                    loc = locTuple[0]
                    G.text.string += indent + "movl " + instr.Src2.operand.name + ",%" + loc.name + "\n"
                    G.text.string += indent + "cmpl %" + loc.name + "," + instr.Src1.operand.name + "\n"
                    instr.Src2.operand.loadIntoReg(loc.name)

            # Perform the jump
            G.text.string += indent + op + " .LABEL_" + str(instr.Target) + "\n"

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
                elif instr.Src1.operand.reg:
                    G.text.string += indent + "movl %" + instr.Src1.operand.reg.name + ", %eax\n"
                else:
                    G.text.string += indent + "movl " + instr.Src1.operand.name + ", %eax\n"

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
                    if arg.operand.reg:
                        G.text.string += indent + "pushl %" + arg.operand.reg.name  + indent + "# Pushing argument\n"
                    else:
                        G.text.string += indent + "pushl " + arg.operand.name + indent + "# Pushing argument\n"
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
                    arg.operand.removeReg()
                    G.text.string += indent + "pushl $" + arg.operand.name + indent + "# Pushing argument\n"
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
    elif op == tacinstr.TACInstr.GEQ:
        return "jge"
    elif op == tacinstr.TACInstr.GT:
        return "jg"
    elif op == tacinstr.TACInstr.LEQ:
        return "jle"
    elif op == tacinstr.TACInstr.LT:
        return "jl"
    elif op == tacinstr.TACInstr.EQ:
        return "je"
    elif op == tacinstr.TACInstr.NEQ:
        return "jne"
    else:
        pass
