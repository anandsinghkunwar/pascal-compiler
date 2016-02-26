import ply.yacc as yacc

# Get the token map from the lexer.  This is required.
from lexer import tokens

# TODO: PRECEDENCE ERROR

def p_start(p):
    'start : program_statement declarations func_proc_defs block DOT'

def p_program_statement(p):
    '''program_statement : KEYWORD_PROGRAM IDENTIFIER SEMICOLON
                         | empty'''

def p_declarations(p):
    'declarations : const_declarations type_declarations var_declarations'

def p_const_declarations(p):
    '''const_declarations : KEYWORD_CONST const_statements
                          | empty'''

def p_const_statements(p):
    '''const_statements : const_statements const_statement
                        | const_statement'''

def p_const_statement(p):
    'const_statement : IDENTIFIER EQUAL constant SEMICOLON'

def p_constant(p):
    '''constant : CONSTANT_INTEGER
                | CONSTANT_REAL
                | CONSTANT_HEX
                | CONSTANT_BINARY
                | CONSTANT_OCTAL
                | CONSTANT_NIL
                | CONSTANT_BOOLEAN_TRUE
                | CONSTANT_BOOLEAN_FALSE
                | string'''

def p_string(p):
    '''string : CONSTANT_STRING_LEADSPACE substring
              | CONSTANT_STRING_LEADSPACE
              | substring'''

def p_substring(p):
    '''substring : substring substring
                 | CONSTANT_STRING
                 | CONSTANT_SPECIAL_CHAR'''

def p_type_declarations(p):
    '''type_declarations : KEYWORD_TYPE type_statements
                         | empty'''

def p_type_statements(p):
    '''type_statements : type_statements type_statement
                       | type_statement'''

def p_type_statement(p):
    'type_statement : IDENTIFIER EQUAL type SEMICOLON'

def p_func_proc_defs(p):
    pass

def p_block(p):
    'block : KEYWORD_BEGIN statements KEYWORD_END'

def p_statements(p):
    pass

def p_empty(p):
    'empty :'
    pass

# Error rule for syntax errors
def p_error(p):
    print("Syntax error in input!")

# Build the parser
parser = yacc.yacc()

'''while True:
   try:
       s = raw_input('calc > ')
   except EOFError:
       break
   if not s: continue
   result = parser.parse(s)
   print(result)
'''
