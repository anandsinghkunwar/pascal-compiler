# Module for IR code generation.
import symbol_table as ST

# Dummy class to enable parser to use attributes
class Node(object):
    def __init__(self):
        self.value = None
        self.code = ''
        self.place = None
        self.items = []
        self.type = None
        self.arrayBeginList = []
        self.arrayEndList = []
