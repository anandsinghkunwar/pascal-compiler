# Module to implement symbol tables

class SymTabEntry(object):
    def __init__(self, name, type=None, symTab=None):
        self.name = name
        self.type = type
        self.scope = None
        self.symTab = symTab
    
    # Enumeration for types
    # TODO: Pointers
    INT, BOOL, CHAR, STRING, ARRAY, FUNCTION, PROCEDURE, KEYWORD, TYPE = range(9)

    def isInt(self):
        return self.type == SymTabEntry.INT
    def isBool(self):
        return self.type == SymTabEntry.BOOL
    def isChar(self):
        return self.type == SymTabEntry.CHAR
    def isString(self):
        return self.type == SymTabEntry.STRING
    def isArray(self):
        return self.type == SymTabEntry.ARRAY
    def isFunction(self):
        return self.type == SymTabEntry.FUNCTION
    def isProcedure(self):
        return self.type == SymTabEntry.PROCEDURE
    def isKeyword(self):
        return self.type == SymTabEntry.KEYWORD
    def isType(self):
        return self.type == SymTabEntry.TYPE

class SymTab(object):
    def __init__(self, previousTable):
        self.entries = {}
        self.previousTable = previousTable
        self.scope = SymTab.nextScope
        SymTab.nextScope += 1

    # Class variables for allocation
    nextScope = 0

    def addVar(self, varName, varType):
        if not self.entryExists(varName):
            self.entries[varName] = SymTabEntry(varName, varType)
        else:
            # TODO: Handle error?
            pass

    def entryExists(self, varName):
        return varName in self.entries.keys()

    def addProcedure(self, procName):
        if not self.entryExists(procName):
            self.entries[procName] = SymTabEntry(procName, SymTabEntry.PROCEDURE, self)
        else:
            # TODO: Handle error?
            pass

    def addFunction(self, funcName):
        if not self.entryExists(funcName):
            self.entries[funcName] = SymTabEntry(funcName, SymTabEntry.FUNCTION, self)
        else:
            # TODO: Handle error?
            pass
