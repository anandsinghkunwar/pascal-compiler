# Module to implement symbol tables

# Class to define data types.
class Type(object):
    def __init__(self, name, type, baseType = None, arrayBeginList = [],
                 arrayEndList = [], arrayBaseType = None, strLen = None,
                 returnType = None, numParams=None, isConst=False,
                 paramList = None, arrayRangeTypeList=None):
        self.name = name
        self.type = type            # From the enumeration
        self.baseType = baseType    # For custom defined types
        self.arrayBeginList = arrayBeginList
        self.arrayEndList = arrayEndList
        self.arrayBaseType = arrayBaseType   # Array of WHAT?
        self.strLen = strLen
        self.returnType = returnType  # Type object: If this is a function, return type of function.
        self.numParams = numParams
        self.paramList = paramList
        self.isConst = isConst
        self.arrayRangeTypeList = arrayRangeTypeList

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

    # def getArrayLength(self):
    #     if self.arrayBaseType == None:
    #         return 1
    #     length = 0
    #     for index in len(arrayBeginList):
    #         if type(arrayBeginList[i]) == chr:
    #             length += ord(arrayEndList[i]) - ord(arrayBeginList[i]) + 1
    #         elif type(arrayBeginList[i]) == int:
    #             length += arrayEndList[i] - arrayBeginList[i] + 1
    #         elif type(arrayBeginList[i]) == 'true' or (type(arrayBeginList[i]) == 'false' and type(arrayEndList[i]) == 'false'):
    #             length += 1
    #         elif type(arrayBeginList[i]) == 'false' and type(arrayEndList[i]) == 'true':
    #             length += 2
    #         else:
    #             # TODO Throw Error FIXME
    #             print 'Yikes!'
    #             pass


    #     if self.arrayBaseType.name == 'array':
    #         return length * getArrayLength(self.arrayBaseType)

# Class to implement a symbol table entry.
class SymTabEntry(object):
    def __init__(self, name, type, mySymTab, nextSymTab=None, isConst=False, isParameter=False, isTemp=False, isOverridable=False, isMyName=False):
        self.name = name
        self.type = type
        self.mySymTab = mySymTab
        self.nextSymTab = nextSymTab
        self.isConst = isConst
        self.isParameter = isParameter
        self.isTemp = isTemp
        self.isOverridable = isOverridable
        self.paramNum = None
        self.offset = None
        self.isMyName = isMyName
        # TODO This is probably not required now
        if self.isParameter:
            self.paramNum = self.mySymTab.paramCount
            self.mySymTab.paramCount += 1

        self.isLocal = self.mySymTab.scope != 0
        if self.isLocal and not (self.isPredefined() or self.name == 'array.' + str(self.mySymTab.scope)):
            if self.isParameter:
                if self.isInt() or self.isBool() or self.isChar() or self.isArray():
                    self.mySymTab.paramOffset = self.mySymTab.paramOffset + 4
                    self.offset = self.mySymTab.paramOffset
                elif self.isString():
                    pass
                    # TODO FIXME
                    # self.offset = self.mySymTab.off
            else:
                if self.isInt() or self.isBool() or self.isChar() or self.isArray():
                    self.mySymTab.offset = self.mySymTab.offset - 4
                    self.offset = self.mySymTab.offset
                elif self.isString():
                    pass
                    # TODO FIXME
                    # self.offset = self.mySymTab.off


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
        self.paramCount = 0
        SymTab.nextScope += 1
        self.offset = 0
        self.paramOffset = 4

        # Add built in types
        self.addVar('integer', Type('integer', Type.TYPE), isOverridable=True)
        self.addVar('boolean', Type('boolean', Type.TYPE), isOverridable=True)
        self.addVar('char', Type('char', Type.TYPE), isOverridable=True)
        self.addVar('string', Type('string', Type.TYPE), isOverridable=True)
        # Array is a keyword, so not overridable
        self.addVar('array', Type('array', Type.TYPE), isOverridable=False)

    # Class variables for allocation
    nextScope = 0

    def addTable(self, symTab):
        self.childrenTables.append(symTab)

    def addVar(self, varName, varType, isParameter=False, isTemp=False, isConst=False, isOverridable=False, isMyName=False):
        if not self.entryExists(varName) or self.entries[varName].isPredefined():
            self.entries[varName] = SymTabEntry(varName + "." + str(self.scope), varType, self, \
                                                isParameter=isParameter, isTemp=isTemp, isConst=isConst, \
                                                isOverridable=isOverridable, isMyName=isMyName)
            return self.entries[varName]
        else:
            return False
    def entryExists(self, varName):
        return varName in self.entries.keys()

    def addProcedure(self, procName, numParams, paramList):
        if not self.entryExists(procName):
            self.entries[procName] = SymTabEntry(procName + "." + str(self.scope), Type('procedure', Type.PROCEDURE, numParams=numParams, paramList=paramList), self,
                                                 nextSymTab=self)
            return self.entries[procName]
        else:
            return False

    def addFunction(self, funcName, returnType, numParams, paramList):
        if not self.entryExists(funcName):
            self.entries[funcName] = SymTabEntry(funcName + "." + str(self.scope), Type('function', Type.FUNCTION, returnType=returnType, numParams=numParams, paramList=paramList),
                                                 self, nextSymTab=self)
            return self.entries[funcName]
        else:
            return False

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

# The current symbol table that is being used.
currSymTab = rootSymTab

# Helper Functions
def lookup(identifier, symTab=None):
    if symTab == None:
        tempSymTab = currSymTab
    else:
        tempSymTab = symTab

    while tempSymTab != None:
        if identifier in tempSymTab.entries.keys():
            return tempSymTab.entries[identifier]   # Found identifier
        tempSymTab = tempSymTab.previousTable
    return None
    # Identifier not found
    # TODO Throw Error

def typeExists(type):
    STEntry = lookup(type.name)
    if type.name == 'array':
        return True
    elif STEntry != None and STEntry.isType():
        return True
    else:
        return False        
