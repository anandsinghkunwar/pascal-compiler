# Module to implement symbol tables

# Class to define data types.
class Type(object):
    def __init__(self, name, type, baseType = None, arrayBeginList = [], arrayEndList = [], arrayBaseType = None, strLen = None):
        self.name = name
        self.type = type            # From the enumeration
        self.baseType = baseType    # For custom defined types
        self.arrayBeginList = arrayBeginList
        self.arrayEndList = arrayEndList
        self.arrayBaseType = arrayBaseType   # Array of WHAT?
        self.strLen = strLen

    # Enumeration for types
    # TODO: Pointers
    INT, BOOL, CHAR, STRING, ARRAY, FUNCTION, PROCEDURE, KEYWORD, TYPE, PROGRAM = range(10)

    # TODO: Is this redundant...
    def isBuiltin(self):
        return self.baseType == None

# Class to implement a symbol table entry.
class SymTabEntry(object):
    def __init__(self, name, type, mySymTab, nextSymTab=None, isConst=False):
        self.name = name
        self.type = type
        self.mySymTab = mySymTab
        self.nextSymTab = nextSymTab
        self.isConst = isConst

    def scope(self):
        return self.mySymTab.scope

    # Type checking methods
    def isInt(self):
        return self.type == Type.INT
    def isBool(self):
        return self.type == Type.BOOL
    def isChar(self):
        return self.type == Type.CHAR
    def isString(self):
        return self.type == Type.STRING
    def isArray(self):
        return self.type == Type.ARRAY
    def isFunction(self):
        return self.type == Type.FUNCTION
    def isProcedure(self):
        return self.type == Type.PROCEDURE
    def isKeyword(self):
        return self.type == Type.KEYWORD
    def isType(self):
        return self.type == Type.TYPE
    def isProgram(self):
        return self.type == Type.PROGRAM
    def isConstant(self):
        return self.isConst
    # Predefined = Overridable
    def isPredefined(self):
        return self.type.isBuiltin()

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
            self.entries[varName] = SymTabEntry(varName, varType, self)
        else:
            # TODO: Handle error?
            pass

    def entryExists(self, varName):
        return varName in self.entries.keys()

    def addProcedure(self, procName):
        if not self.entryExists(procName):
            self.entries[procName] = SymTabEntry(procName, Type('procedure', Type.PROCEDURE), self, nextSymTab=SymTab(self))
        else:
            # TODO: Handle error?
            pass

    def addFunction(self, funcName):
        if not self.entryExists(funcName):
            self.entries[funcName] = SymTabEntry(funcName, Type('function', Type.FUNCTION), self, nextSymTab=SymTab(self))
        else:
            # TODO: Handle error?
            pass

# Global variables
# The root symbol table in the tree structure.
rootSymTab = SymTab(None)

# The current symbol table that is being used.
currSymTab = rootSymTab
