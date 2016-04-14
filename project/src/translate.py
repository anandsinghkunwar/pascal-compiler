import machine
import ircodegen as IG
import basicblock
import globjects as G
import symbol_table as ST

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
                    if instr.Src2.isInt() or instr.Src2.isChar():          # z is integer
                        G.text.string += indent + "pushl $" + str(instr.Src2.operand) + "\n"
                    elif instr.Src2.addrDescEntry.reg:    # z is in register
                        G.text.string += indent + "pushl %" + instr.Src2.addrDescEntry.reg.name + "\n"
                    elif instr.Src2.addrDescEntry.isLocal:  # z is local variable or parameter
                        G.text.string += indent + "pushl " + str(instr.Src2.addrDescEntry.offset) + "\n"
                    else:   # z is in memory
                        G.text.string += indent + "pushl " + instr.Src2.addrDescEntry.name + "\n"
                    if instr.Src1.isInt() or instr.Src1.isChar():    # y is integer or char
                        G.text.string += indent + "movl $" + str(instr.Src1.operand) + ", %eax\n"
                    elif instr.Src1.addrDescEntry.reg:    # y is in register
                        G.text.string += indent + "movl %" + instr.Src1.addrDescEntry.reg.name + ", %eax\n"
                    elif instr.Src1.addrDescEntry.isLocal:  # y is local variable or parameter
                        G.text.string += indent + "movl " + str(instr.Src1.addrDescEntry.offset) + "(%ebp), %eax\n"
                    else:   # y is in memory
                        G.text.string += indent + "movl " + instr.Src1.addrDescEntry.name + ", %eax\n"
                    G.text.string += indent + "cltd" + indent + "#sign extending eax into edx:eax\n"

                    # Performing the operation
                    G.text.string += indent + "idivl (%esp)\n"

                    # Operation complete. Moving the result into the appropriate place
                    if instr.Op == IG.TACInstr.DIV:
                        if instr.Dest.addrDescEntry.reg:  # x is in register
                            G.text.string += indent + "movl %eax, %" + instr.Dest.addrDescEntry.reg.name + "\n"
                        elif instr.Dest.addrDescEntry.isLocal:  # x is a local variable or parameter
                            G.text.string += indent + "movl %eax, " + str(instr.Dest.addrDescEntry.offset) + "(%ebp)\n"
                        else:   # x is in memory
                            G.text.string += indent + "movl %eax," + instr.Dest.addrDescEntry.name + "\n"
                    else:   # instr.op == MOD
                        if instr.Dest.addrDescEntry.reg:  # x is in register
                            G.text.string += indent + "movl %edx, %" + instr.Dest.addrDescEntry.reg.name + "\n"
                        elif instr.Dest.addrDescEntry.isLocal:
                            G.text.string += indent + "movl %edx, " + str(instr.Dest.addrDescEntry.offset) + "(%ebp)\n"
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
                    if instr.Src1.isInt() or instr.Src1.isChar():  # y is integer or char
                        G.text.string += indent + "movl $" + str(instr.Src1.operand) + ", %" + loc.name + "\n"
                    elif locTuple[1]:   # y is variable and getReg returned y's register. so loc has y's value
                        pass
                    else:   # y is a variable and loc doesn't have y's value
                        if instr.Src1.addrDescEntry.reg:      # y exists in a non disposable register
                            G.text.string += indent + "movl %" + instr.Src1.addrDescEntry.reg.name + ", %" + loc.name + "\n"
                        elif instr.Src1.addrDescEntry.isLocal:  # y is local variable or parameter
                            G.text.string += indent + "movl " + str(instr.Src1.addrDescEntry.offset) + "(%ebp), %" + loc.name + "\n"
                        else:   # y is a global variable only in memory
                            G.text.string += indent + "movl " + instr.Src1.addrDescEntry.name + ", %" + loc.name + "\n"

                    # Performing the operation
                    # Case 1: Second operand is an immediate
                    if instr.Src2.isInt() or instr.Src2.isChar():
                        G.text.string += indent + op + " $" + str(instr.Src2.operand) + ", %" + loc.name + "\n"

                    # Case 2: Second operand is a variable in a register
                    elif instr.Src2.addrDescEntry.reg:    #z exists in a register
                        if instr.Op == IG.TACInstr.SHL or instr.Op == IG.TACInstr.SHR:
                            G.text.string += indent + "xchgl %ecx, %" + instr.Src2.addrDescEntry.reg.name + "\n"
                            G.text.string += indent + op + " %cl, %" + loc.name + "\n"
                            G.text.string += indent + "xchgl %ecx, %" + instr.Src2.addrDescEntry.reg.name + "\n"
                        else:
                            G.text.string += indent + op + " %" + instr.Src2.addrDescEntry.reg.name + ", %" + loc.name + "\n"

                    # Case 3: Second operand is a local variable or parameter
                    elif instr.Src2.addrDescEntry.isLocal:
                        if instr.Op == IG.TACInstr.SHL or instr.Op == IG.TACInstr.SHR:
                            G.text.string += indent + "xchgl %ecx, " + str(instr.Src2.addrDescEntry.offset) + "(%ebp)\n"
                            G.text.string += indent + op + " %cl, %" + loc.name + "\n"
                            G.text.string += indent + "xchgl %ecx, " + str(instr.Src2.addrDescEntry.offset) + "(%ebp)\n"
                        else:
                            G.text.string += indent + op + " " + str(instr.Src2.addrDescEntry.offset) + "(%ebp), %" + loc.name + "\n"

                    # Case 4: Second operand is a global variable in memory
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
                        if instr.Src1.isInt():
                            G.text.string += indent + "movl $" + str(instr.Src1.operand) + ", %" + loc.name + "\n"

                        # Case 2: Operand is in a register
                        elif instr.Src1.addrDescEntry.reg:
                            G.text.string += indent + "movl %" + instr.Src1.addrDescEntry.reg.name + ", %" + loc.name + "\n"

                        # Case 3: Operand is local varible or parameter
                        elif instr.Src1.addrDescEntry.isLocal:
                            G.text.string += indent + "movl " + str(instr.Src1.addrDescEntry.offset) + "(%ebp), %" + loc.name + "\n"

                        # Case 4: Operand is global variable
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
                    if instr.ParamList is not None:
                        for arg in reversed(instr.ParamList):
                            if type(arg) == ST.SymTabEntry:
                                name = arg.name
                                if name in G.varMap.keys():
                                    addrDescEntry = G.varMap[name]
                                    if addrDescEntry.reg:   # variable exists in a register
                                        G.text.string += indent + "pushl %" + addrDescEntry.reg.name + indent + "# Pushing function parameters\n"
                                    elif addrDescEntry.isLocal: # variable is either local or parameter and dosen't exist in a register
                                        G.text.string += indent + "pushl " + str(addrDescEntry.offset) + "(%ebp)" + indent + "# Pushing function parameters\n"
                                    elif arg.isInt() or arg.isChar():
                                        G.text.string += indent + "pushl " + addrDescEntry.name + indent + "# Pushing function parameters\n"
                                    else:   # TODO what about variables of other types
                                        pass
                                else:   #error - variable without address descriptor entry
                                    pass
                            elif type(arg) == int:
                                G.text.string += indent + "pushl $" + str(arg) + indent + "# Pushing function parameters\n"
                            elif arg == 'true' or arg == 'false': # constant boolean
                                G.text.string += indent + "pushl $"
                                if arg == 'true':
                                    G.text.string += "1" + indent + "# Pushing function parameters\n"
                                else:
                                    G.text.string += "0" + indent + "# Pushing function parameters\n"
                            elif type(arg) == str:
                                if len(arg) == 1:   # constant char
                                    G.text.string += indent + "pushl $" + str(ord(arg)) + indent + "# Pushing function parameters\n" # assuming only print operations on char
                                    # TODO handle other operations for char
                                else: # TODO for constant string
                                    pass
                            elif type(arg) == IG.ArrayElement:  # TODO
                                pass
                            else:   # TODO constant of other types????
                                pass
                    G.text.string += indent + "call " + instr.TargetLabel + "\n"
                    if instr.ParamList is not None:
                        G.text.string += indent + "addl $" + str(len(instr.ParamList) * 4) + ", %esp" + indent + "# Removing parameters from stack\n"
                    # No need to check if a is in a register or not, since the current
                    # instruction will be the last of this basic block
                    if instr.Dest.addrDescEntry.isLocal:
                        G.text.string += indent + "movl %eax, " + str(instr.Dest.addrDescEntry.offset) + "(%ebp)\n"
                    else:
                        G.text.string += indent + "movl %eax, " + instr.Dest.addrDescEntry.name + "\n"
                else:
                    G.halt(instr.LineNo, "invalid assignment instruction with unary operator")

            # Basic assignment
            else:   # basic assignment   a = b
                # Case 1: b is an immediate
                if instr.Src1.isInt() or instr.Src1.isChar():  #b is integer or char
                    if instr.Dest.addrDescEntry.reg:  #a is in a register
                        G.text.string += indent + "movl $" + str(instr.Src1.operand) + ", %" + instr.Dest.addrDescEntry.reg.name + "\n"
                    elif instr.Dest.addrDescEntry.isLocal:  #a is local variable or parameter
                        G.text.string += indent + "movl $" + str(instr.Src1.operand) + ", " + str(instr.Dest.addrDescEntry.offset) + "(%ebp)\n"
                    else:   #a is in memory
                        G.text.string += indent + "movl $" + str(instr.Src1.operand) + ", " + instr.Dest.addrDescEntry.name + "\n"

                # Case 2: b is in a register
                elif instr.Src1.addrDescEntry.reg:    #b is in a register
                    # No matter where a is stored, its new location will be the
                    # register of b.
                    instr.Dest.addrDescEntry.loadIntoReg(instr.Src1.addrDescEntry.reg.name)

                # Case 3: b is local variable or parameter
                elif instr.Src1.addrDescEntry.isLocal:
                    # If a is in a register
                    if instr.Dest.addrDescEntry.reg:
                        G.text.string += indent + "movl " + str(instr.Src1.addrDescEntry.offset) + "(%ebp), %" + instr.Dest.addrDescEntry.reg.name + "\n"
                    else:   # a is either local variable or parameter or is global variable
                        locTuple = bb.getReg()
                        loc = locTuple[0]
                        G.text.string += indent + "movl " + str(instr.Src1.addrDescEntry.offset) + "(%ebp), %" + loc.name + "\n"
                        instr.Dest.addrDescEntry.loadIntoReg(loc.name)

                # Case 4: b is global varibale
                else:
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
            if (instr.Src1.isInt() and instr.Src2.isInt()) or (instr.Src1.isChar() and instr.Src1.isChar()):
                # Just do the comparison
                if instr.Src1.operand > instr.Src2.operand:
                    if instr.Op == IG.TACInstr.GT or instr.Op == IG.TACInstr.GEQ:
                        G.text.string += indent + "jmp " + label + "\n"
                elif instr.Src1.operand < instr.Src2.operand:
                    if instr.Op == IG.TACInstr.LT or instr.Op == IG.TACInstr.LEQ:
                        G.text.string += indent + "jmp " + label + "\n"
                else:
                    if instr.Op == IG.TACInstr.EQ:
                        G.text.string += indent + "jmp " + label + "\n"

            elif (instr.Src1.isInt() or instr.Src1.isChar()) and instr.Src2.isVar():
                if instr.Src2.addrDescEntry.reg:
                    G.text.string += indent + "cmpl $" + str(instr.Src1.operand) + ", %" + instr.Src2.addrDescEntry.reg.name + "\n"
                elif instr.Src2.addrDescEntry.isLocal:  # argument of function
                    G.text.string += indent + "cmpl $" + str(instr.Src1.operand) + ", " + str(instr.Src2.addrDescEntry.offset) + "(%ebp)\n"
                else:
                    G.text.string += indent + "cmpl $" + str(instr.Src1.operand) + ", " + instr.Src2.addrDescEntry.name + "\n"
                op = getReversedMnemonic(instr.Op)
                G.text.string += indent + op + label + "\n"

            elif (instr.Src2.isInt() or instr.Src2.isChar()) and instr.Src1.isVar():
                if instr.Src1.addrDescEntry.reg:
                    G.text.string += indent + "cmpl $" + str(instr.Src2.operand) + ", %" + instr.Src1.addrDescEntry.reg.name + "\n"
                elif instr.Src1.addrDescEntry.isLocal:  # argument of function
                    G.text.string += indent + "cmpl $" + str(instr.Src2.operand) + ", " + str(instr.Src1.addrDescEntry.offset) + "(%ebp)\n"
                else:
                    G.text.string += indent + "cmpl $" + str(instr.Src2.operand) + ", " + instr.Src1.addrDescEntry.name + "\n"
                G.text.string += indent + op + label + "\n"

            elif instr.Src1.isVar() and instr.Src2.isVar():
                if instr.Src2.addrDescEntry.reg:
                    if instr.Src1.addrDescEntry.reg:
                        G.text.string += indent + "cmpl %" + instr.Src2.addrDescEntry.reg.name + ", %" + instr.Src1.addrDescEntry.reg.name + "\n"
                    elif instr.Src1.addrDescEntry.isLocal:
                        G.text.string += indent + "cmpl %" + instr.Src2.addrDescEntry.reg.name + ", " + str(instr.Src1.addrDescEntry.offset) + "(%ebp)\n"
                    else:
                        G.text.string += indent + "cmpl %" + instr.Src2.addrDescEntry.reg.name + ", " + instr.Src1.addrDescEntry.name + "\n"
                    G.text.string += indent + op + label + "\n"
                else:
                    locTuple = bb.getReg()
                    loc = locTuple[0]
                    if instr.Src2.addrDescEntry.isLocal:
                        G.text.string += indent + "movl " + str(instr.Src2.addrDescEntry.offset) + ", %" + loc.name + "\n"
                    else:
                        G.text.string += indent + "movl " + instr.Src2.addrDescEntry.name + ", %" + loc.name + "\n"
                    G.text.string += indent + "cmpl %" + loc.name + "," + instr.Src1.addrDescEntry.name + "\n"
                    G.text.string += indent + op + label + "\n"
                    instr.Src2.addrDescEntry.loadIntoReg(loc.name)

######################################################  isGoto instruction #######################################################

        elif instr.isGoto():    #goto line_no
            G.text.string += indent + "jmp .LABEL_" + str(instr.Target) + "\n"

######################################################  isCall instruction #######################################################

        elif instr.isCall():    #call func_name
            if instr.ParamList is not None:
                for arg in reversed(instr.ParamList):
                    if type(arg) == ST.SymTabEntry:
                        name = arg.name
                        if name in G.varMap.keys():
                            addrDescEntry = G.varMap[name]
                            if addrDescEntry.reg:   # variable exists in a register
                                G.text.string += indent + "pushl %" + addrDescEntry.reg.name + indent + "# Pushing function parameters\n"
                            elif addrDescEntry.isLocal: # variable is either local or parameter and dosen't exist in a register
                                G.text.string += indent + "pushl " + str(addrDescEntry.offset) + "(%ebp)" + indent + "# Pushing function parameters\n"
                            elif arg.isInt() or arg.isChar():
                                G.text.string += indent + "pushl " + addrDescEntry.name + indent + "# Pushing function parameters\n"
                            else:   # TODO what about variables of other types
                                pass
                        else:   #error - variable without address descriptor entry
                            pass
                    elif type(arg) == int:
                        G.text.string += indent + "pushl $" + str(arg) + indent + "# Pushing function parameters\n"
                    elif arg == 'true' or arg == 'false': # constant boolean
                        G.text.string += indent + "pushl $"
                        if arg == 'true':
                            G.text.string += "1" + indent + "# Pushing function parameters\n"
                        else:
                            G.text.string += "0" + indent + "# Pushing function parameters\n"
                    elif type(arg) == str:
                        if len(arg) == 1:   # constant char
                            G.text.string += indent + "pushl $" + str(ord(arg)) # assuming only print operations on char
                            # TODO handle other operations for char
                        else: # TODO for constant string
                            pass
                    elif type(arg) == IG.ArrayElement:  # TODO
                        pass
                    else:   # TODO constant of other types????
                        pass
                    G.text.string += indent + "#pushing function parameters\n"
            G.text.string += indent + "call " + instr.TargetLabel + "\n"
            if instr.ParamList is not None:
                G.text.string += indent + "addl $" + str(len(instr.ParamList) * 4) + ", %esp" + indent + "# Removing parameters from stack\n"

######################################################  isReturn instruction #####################################################

        elif instr.isReturn():
            # If there is a value to return
            if instr.Src1:
                G.registerMap["eax"].spill()
                if instr.Src1.isInt() or instr.Src1.isChar():
                    G.text.string += indent + "movl $" + str(instr.Src1.operand) + ", %eax\n"
                elif instr.Src1.addrDescEntry.reg:
                    G.text.string += indent + "movl %" + instr.Src1.addrDescEntry.reg.name + ", %eax\n"
                elif instr.Src1.addrDescEntry.isLocal:
                    G.text.string += indent + "movl " + str(instr.Src1.addrDescEntry.offset) + "(%ebp), %eax\n"
                else:
                    G.text.string += indent + "movl " + instr.Src1.addrDescEntry.name + ", %eax\n"
            if instr.SymTableParser.offset != 0:
                G.text.string += indent + "subl $" + str(instr.SymTableParser.offset) + ", %esp" + indent + "# Releasing space for local variables\n"
            G.text.string += indent + "movl %ebp, %esp" + indent + "#standard function protocol\n"
            G.text.string += indent + "popl %ebp" + indent + "#standard function protocol\n"
            # Issue the ret instruction
            G.text.string += indent + "ret\n"

######################################################  isLabel instruction #####################################################

        elif instr.isLabel():   #label func_name
            G.text.string += instr.Label + ":\n"
            G.text.string += indent + "pushl %ebp" + indent + "#Standard function protocol\n"
            G.text.string += indent + "movl %esp, %ebp" + indent + "#Standard function protocol\n"
            if instr.SymTableParser.offset != 0:
                G.text.string += indent + "addl $" + str(instr.SymTableParser.offset) + ", %esp" + indent + "# Allocating space for local variables\n"
            # TODO map parameters to location on stack

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
                    elif arg.addrDescEntry.isLocal:
                        G.text.string += indent + "pushl " + str(arg.addrDescEntry.offset) + "(%ebp)" + indent + "# Pushing argument\n"
                    else:
                        G.text.string += indent + "pushl " + arg.addrDescEntry.name + indent + "# Pushing argument\n"
                elif arg.isInt() or arg.isChar():
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
                    if arg.isArrayElement():
                        locTuple = bb.getReg()  # FIXME check compatibility
                        loc = locTuple[0]
                        addrDescEntry = G.varMap[arg.operand.array.name]
                        if addrDescEntry.isLocal:   # local array
                            G.text.string += indent + "movl " + str(addrDescEntry.offset) + "(%ebp), %" + loc.name + indent + "# moving array base address in " + loc.name + "\n"
                        else:   # global arrat
                            G.text.string += indent + "movl " + addrDescEntry.name + ", %" + loc.name + indent + "# moving array base address in" + loc.name + "\n"
                        # FIXME is this the address or the value being pushed and what about base index
                        G.text.string += indent + "pushl " + str(arg.operand.index * 4) + "(%" + loc.name + ")" + indent + "# Pushing argument\n"
                    elif arg.addrDescEntry.isLocal:
                        G.text.string += indent + "pushl " + str(arg.addrDescEntry.offset) + "(%ebp)" + indent + "# Pushing argument\n"
                    else:
                        G.text.string += indent + "pushl $" + arg.addrDescEntry.name + indent + "# Pushing argument\n"
            G.text.string += indent + "pushl $" + instr.IOFmtStringAddr + indent + "# Pushing argument\n"
            G.text.string += indent + "call scanf\n"
            G.text.string += indent + "addl $" + str(4 * (len(instr.IOArgList) + 1)) + ", %esp\n"

            # Restore the value of registers saved before the call
            G.text.string += indent + "popl %edx" + indent + "# Restoring register from stack\n"
            G.text.string += indent + "popl %ecx" + indent + "# Restoring register from stack\n"
            G.text.string += indent + "popl %eax" + indent + "# Restoring register from stack\n"

###################################################### isDeclare instruction ###################################################

        elif instr.isDeclare():
            G.text.string += indent + "pushl %eax" + indent + "# Saving register on stack\n"
            G.text.string += indent + "pushl $" + str(instr.ArrayLength * 4) + indent + "# Pushing argument\n"
            G.text.string += indent + "call malloc\n"
            if instr.Array.addrDescEntry.isLocal: # local array
                G.text.string += indent + "movl %eax, " + str(instr.Array.addrDescEntry.offset) + "(%ebp)" + indent + "# Storing location of array\n"
            else:   # global array
                G.text.string += indent + "movl %eax, " + instr.Array.operand + indent + "# Storing location of array\n"
            G.text.string += indent + "addl $4, %esp" + indent + "# Removing pushed arguments\n"
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
