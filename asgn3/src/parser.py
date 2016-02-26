import ply.yacc as yacc

# Get the token map from the lexer.  This is required.
from lexer import tokens

def p_start(p):
    'start : program_statement block DOT'

def p_program_statement(p):
    '''program_statement : KEYWORD_PROGRAM IDENTIFIER SEMICOLON
                         | empty'''

def p_block(p):
    'block : declarations func_proc_defs KEYWORD_BEGIN statements KEYWORD_END'

def p_declarations(p):
    ''

def p_func_proc_defs(p):
    ''

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
