# Module to implement a symbol table

class SymTabEntry(object):
    def __init__(self):
        self.name = ""
        self.type = None
        self.scope = None
    
    # Enumeration for types
    # TODO: Pointers
    INT, BOOL, CHAR, STRING, ARRAY, FUNCTION, PROCEDURE, KEYWORD, TYPE = range(9)

    def isInt(self):
        return self.type == INT
    def isBool(self):
        return self.type == BOOL
    def isChar(self):
        return self.type == CHAR
    def isString(self):
        return self.type == STRING
    def isArray(self):
        return self.type == ARRAY
    def isFunction(self):
        return self.type == FUNCTION
    def isProcedure(self):
        return self.type == PROCEDURE
    def isKeyword(self):
        return self.type == KEYWORD
    def isType(self):
        return self.type == TYPE
