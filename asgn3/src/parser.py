import ply.yacc as yacc

# Get the token map from the lexer.  This is required.
from lexer import tokens

def p_start(p):
    'start : program_statement declarations KEYWORD_BEGIN statement_list KEYWORD_END DOT'
def p_program_statement(p):
    'KEYWORD_PROGRAM IDENTIFIER SEMICOLON'
def p_expression_plus(p):
    'expression : expression PLUS term'
    p[0] = p[1] + p[3]

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
