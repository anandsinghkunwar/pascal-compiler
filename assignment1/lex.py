import ply.lex as lex

#tokens
reserved = {
    'and':'OP_AND',
    'array':'KEYWORD_ARRAY',
    'begin':'KEYWORD_BEGIN',
    'break':'KEYWORD_BREAK',
    'case':'KEYWORD_CASE',
    'const':'KEYWORD_CONST',
    'continue':'KEYWORD_CONTINUE',
    'div':'OP_DIV',
    'do':'KEYWORD_DO',
    'downto':'KEYWORD_DOWNTO',
    'else':'KEYWORD_ELSE',
    'end':'KEYWORD_END',
    'file':'KEYWORD_FILE',
    'for':'KEYWORD_FOR',
    'function':'KEYWORD_FUNCTION',
    'if':'KEYWORD_IF',
    'in':'KEYWORD_IN',
    'mod':'OP_MOD',
    'not':'OP_NOT',
    'of':'KEYWORD_OF',
    'or':'OP_OR',
    'procedure':'KEYWORD_PROCEDURE',
    'program':'KEYWORD_PROGRAM',
    'record':'KEYWORD_RECORD',
    'repeat':'KEYWORD_REPEAT',
    'string':'KEYWORD_STRING',
    'then':'KEYWORD_THEN',
    'to':'KEYWORD_TO',
    'type':'KEYWORD_TYPE',
    'until':'KEYWORD_UNTIL',
    'uses':'KEYWORD_USES',
    'var':'KEYWORD_VAR',
    'while':'KEYWORD_WHILE',
    'with':'KEYWORD_WITH',
    'xor':'KEYWORD_XOR'
    }
tokens = [
    'IDENTIFIER','TYPE',
#literals
    'CONSTANT_INTEGER','CONSTANT_STRING','CONSTANT_REAL','CONSTANT_CHARACTER','CONSTANT_BOOLEAN','CONSTANT_STRING_LEADSPACE','CONSTANT_ESCAPE_STRING', #for handling escaping apostrophe
#operators
    'OP_PLUS','OP_MINUS','OP_MULT','OP_DIV_REAL',
    'OP_NEQ','OP_GT','OP_LT','OP_GEQ','OP_LEQ',
    'COMMA','SEMICOLON','COLON','COLON_EQUAL','LEFT_PARENTHESIS','RIGHT_PARENTHESIS','EQUAL','DOT',
    'COMMENTS', 'NEWLINE','SPACE'
    ] + list(reserved.values())
#have to take care of comments

t_OP_PLUS = r'\+'
t_OP_MINUS = r'-'
t_OP_MULT = r'\*'
t_OP_DIV_REAL = r'/'
t_OP_NEQ = r'<>'
t_OP_GT = r'>'
t_OP_LT = r'<'
t_OP_GEQ = r'>='
t_OP_LEQ = r'<='
t_COMMA = r','
t_SEMICOLON = r';'
t_COLON_EQUAL = r':='
t_LEFT_PARENTHESIS = r'\('
t_RIGHT_PARENTHESIS = r'\)'
t_EQUAL = r'='
t_NEWLINE = r'\n'
t_ignore_SPACE = r'[ \t\f\v]'
t_DOT = r'\.'

def t_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value,'IDENTIFIER')    # Check for reserved words
    return t
def t_CONSTANT_REAL(t):
    r'([0-9]+(\.[0-9]+)(e[\+-]?[0-9]+)?)|([0-9]+(e[\+-]?[0-9]+))' # Checked for form 123.123 123.123e-123 123e-231
    t.value = float(t.value)
    return t
def t_CONSTANT_INTEGER(t):
    r'[0-9]+'
    t.value = int(t.value)
    return t
def t_CONSTANT_STRING_LEADSPACE(t):
    r'\s+\'.*?\''
    t.value = t.value.split('\'')[1]
    return t
def t_CONSTANT_STRING(t):
    r'\'.*?\''
    t.value = t.value.split('\'')[1]
    return t
def t_CONSTANT_ESCAPE_STRING(t):
    r'\s*\#[0-9]+'
    if(t.value[0]!='#'):
        t_error(t)
    else:
        return t

def t_error(t):
    print("\n>>>>>>>>>>>>>>!!!!!!!!\n Illegal string '%s'\n>>>>>>>>>>>>>>!!!!!!!!\n" % t.value)
    exit()

lexer = lex.lex()
# Test it out
data = '''program Test
'''

# Give the lexer some input
lexer.input(data)

# Tokenize
while True:
    tok = lexer.token()
    if not tok: 
        break      # No more input
    print(tok)