# Module to implement symbol tables

# Class to define data types.
class Type(object):
    def __init__(self, name, type, baseType = None, arrayBeginList = [],
                 arrayEndList = [], arrayBaseType = None, strLen = None,
                 returnType = None, numParams=None, isConst=False):
        self.name = name
        self.type = type            # From the enumeration
        self.baseType = baseType    # For custom defined types
        self.arrayBeginList = arrayBeginList
        self.arrayEndList = arrayEndList
        self.arrayBaseType = arrayBaseType   # Array of WHAT?
        self.strLen = strLen
        self.returnType = returnType  # Type object: If this is a function, return type of function.
        self.numParams = numParams
        self.isConst = isConst

    def __eq__(self, other):
        if other is None:
            return False
        # TODO FIXME Why was this here?
        # if self.isConst and not other.isConst:
        #     return self.type == other.baseType
        return self.getDeepestType() == other.getDeepestType()

    # Enumeration for types
    # TODO: Pointers
    INT, BOOL, CHAR, STRING, ARRAY, FUNCTION, PROCEDURE, KEYWORD, TYPE, PROGRAM = range(10)

    def getDeepestType(self):
        if self.baseType is None:
            return self.name
        else:
            return self.baseType.getDeepestType()

# Class to implement a symbol table entry.
class SymTabEntry(object):
    def __init__(self, name, type, mySymTab, nextSymTab=None, isConst=False, isParameter=False, isTemp=False, isOverridable=False):
        self.name = name
        self.type = type
        self.mySymTab = mySymTab
        self.nextSymTab = nextSymTab
        self.isConst = isConst
        self.isParameter = isParameter
        self.isTemp = isTemp
        self.isOverridable = isOverridable

    def scope(self):
        return self.mySymTab.scope

    def printEntry(self):
        print "\t" + self.name + "\t|\t" + self.type.name

    # TODO Test Type checking methods
    def isInt(self):
        return self.type.getDeepestType() == 'integer'
    def isBool(self):
        return self.type.getDeepestType() == 'boolean'
    def isChar(self):
        return self.type.getDeepestType() == 'char'
    def isString(self):
        return self.type.getDeepestType() == 'string'
    def isArray(self):
        return self.type.getDeepestType() == 'array'
    def isFunction(self):
        return self.type.getDeepestType() == 'function'
    def isProcedure(self):
        return self.type.getDeepestType() == 'procedure'
    def isKeyword(self):
        return self.type.getDeepestType() == 'keyword'
    def isType(self):
        return self.type.type == Type.TYPE
    def isProgram(self):
        return self.type.getDeepestType() == 'program'
    def isConstant(self):
        return self.isConst
    # Predefined = Overridable
    def isPredefined(self):
        return self.isOverridable

class SymTab(object):
    def __init__(self, previousTable):
        self.entries = {}
        self.previousTable = previousTable
        self.scope = SymTab.nextScope
        self.childrenTables = []
        SymTab.nextScope += 1

    # Class variables for allocation
    nextScope = 0

    def addTable(self, symTab):
        self.childrenTables.append(symTab)

    def addVar(self, varName, varType, isParameter=False, isTemp=False, isConst=False, isOverridable=False):
        if not self.entryExists(varName):
            self.entries[varName] = SymTabEntry(varName + "." + str(self.scope), varType, self, isParameter=isParameter, isTemp=isTemp, isConst=isConst, isOverridable=isOverridable)
            return self.entries[varName]
        else:
            # TODO: Handle error?
            pass

    def entryExists(self, varName):
        return varName in self.entries.keys()

    def addProcedure(self, procName, numParams):
        if not self.entryExists(procName):
            self.entries[procName] = SymTabEntry(procName, Type('procedure', Type.PROCEDURE, numParams=numParams), self, nextSymTab=self)
        else:
            # TODO: Handle error?
            pass

    def addFunction(self, funcName, returnType, numParams):
        if not self.entryExists(funcName):
            self.entries[funcName] = SymTabEntry(funcName, Type('function', Type.FUNCTION, returnType=returnType, numParams=numParams),
                                                 self, nextSymTab=self)
        else:
            # TODO: Handle error?
            pass

    def printTable(self):
        print "#"*20 + str(self.scope) + "#"*20
        if self.previousTable:
            print "Scope: " + str(self.scope) + "\tParent's Scope: " + str(self.previousTable.scope)
        else:
            print "Scope: " + str(self.scope)
        print "\tName\t|\tType"
        print "\t----\t \t----"
        for key, value in self.entries.iteritems():
            value.printEntry()
        print "#"*41 + "\n"
        for table in self.childrenTables:
            table.printTable()

# Global variables
# The root symbol table in the tree structure.
rootSymTab = SymTab(None)

# Add built in types
rootSymTab.addVar('integer', Type('integer', Type.TYPE), isOverridable=True)
rootSymTab.addVar('boolean', Type('boolean', Type.TYPE), isOverridable=True)
rootSymTab.addVar('char', Type('char', Type.TYPE), isOverridable=True)
rootSymTab.addVar('array', Type('array', Type.TYPE), isOverridable=True)
rootSymTab.addVar('string', Type('string', Type.TYPE), isOverridable=True)

# The current symbol table that is being used.
currSymTab = rootSymTab

# Helper Functions
def lookup(identifier):
    tempSymTab = currSymTab

    while tempSymTab != None:
        tempSymTab.entryExists(identifier):
            return tempSymTab.entries[identifier]   # Found identifier
        tempSymTab = tempSymTab.previousTable
    return None
    # Identifier not found
    # TODO Throw Error