# Main code generator module. Contains description of the
# symbol table, register descriptor, address descriptor.

import tacinstr, basicblock, machine

# Class to define the code generator
class Codegen(object):
    def __init__(self, program):
        self.program = program
        self.basicBlocks = []
    # Method to compute basic blocks from the IR program
    def getBasicBlocks(self):
        for instr in program:
