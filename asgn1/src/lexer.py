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
    'false':'CONSTANT_BOOLEAN_FALSE',
    'file':'KEYWORD_FILE',
    'for':'KEYWORD_FOR',
    'function':'KEYWORD_FUNCTION',
    'if':'KEYWORD_IF',
    'in':'KEYWORD_IN',
    'mod':'OP_MOD',
    'nil':'CONSTANT_NIL',
    'not':'OP_NOT',
    'of':'KEYWORD_OF',
    'or':'OP_OR',
    'procedure':'KEYWORD_PROCEDURE',
    'program':'KEYWORD_PROGRAM',
    'record':'KEYWORD_RECORD',
    'repeat':'KEYWORD_REPEAT',
    'shl':'OP_SHIFTLEFT',
    'shr':'OP_SHIFTRIGHT',
    'string':'KEYWORD_STRING',
    'then':'KEYWORD_THEN',
    'to':'KEYWORD_TO',
    'true':'CONSTANT_BOOLEAN_TRUE',
    'type':'KEYWORD_TYPE',
    'until':'KEYWORD_UNTIL',
    'uses':'KEYWORD_USES',
    'var':'KEYWORD_VAR',
    'while':'KEYWORD_WHILE',
    'with':'KEYWORD_WITH',
    'xor':'OP_XOR'
    }
tokens = [
    'IDENTIFIER','TYPE','ERRONEOUS_IDENTIFIER',
#literals
    'CONSTANT_INTEGER','CONSTANT_STRING','CONSTANT_REAL','ERRONEOUS_CONSTANT_REAL',
    'CONSTANT_STRING_LEADSPACE','CONSTANT_ESCAPE_STRING', #for handling escaping apostrophe
    'CONSTANT_BINARY', 'CONSTANT_OCTAL', 'CONSTANT_HEX',
#operators
    'OP_PLUS','OP_MINUS','OP_MULT','OP_DIV_REAL',
    'OP_NEQ','OP_GT','OP_LT','OP_GEQ','OP_LEQ',
    'OP_POINTER','OP_ADDRESS',
    'COMMA','SEMICOLON','COLON','COLON_EQUAL','LEFT_PARENTHESIS','RIGHT_PARENTHESIS','LEFT_SQUARE_BRACKETS','RIGHT_SQUARE_BRACKETS','EQUAL','DOT',
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
t_OP_SHIFTLEFT = r'<<'
t_OP_SHIFTRIGHT = r'>>'
t_COMMA = r','
t_SEMICOLON = r';'
t_COLON = r':'
t_COLON_EQUAL = r':='
t_LEFT_PARENTHESIS = r'\('
t_RIGHT_PARENTHESIS = r'\)'
t_LEFT_SQUARE_BRACKETS = r'\['
t_RIGHT_SQUARE_BRACKETS = r'\]'
t_EQUAL = r'='
t_ignore_SPACE = r'\s'
t_DOT = r'\.'
t_DOTDOT = r'\.\.'
t_OP_POINTER = r'\^'
t_OP_ADDRESS = r'@'

def t_ERRONEOUS_IDENTIFIER(t):
    r'[0-9][a-zA-Z_]+'
    error(t)
def t_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.value = t.value.lower()
    t.type = reserved.get(t.value,'IDENTIFIER')    # Check for reserved words
    return t
def t_ERRONEOUS_CONSTANT_REAL(t):
    r'[0-9]+\.[0-9]+(\.[0-9]*)+' # Checked for form 123.123 123.123e-123 123e-231
    error(t)
def t_CONSTANT_REAL(t):
    r'(?i)([0-9]+(\.[0-9]+)(e[\+-]?[0-9]+)?)|([0-9]+(e[\+-]?[0-9]+))' # Checked for form 123.123 123.123e-123 123e-231
    t.value = float(t.value)
    return t
def t_CONSTANT_INTEGER(t):
    r'[0-9]+'
    t.value = int(t.value)
    return t
def t_CONSTANT_HEX(t):
    r'(?i)\$[0-9a-f]+'
    t.value = int(t.value[1:len(t.value)], 16)
    return t
def t_CONSTANT_BINARY(t):
    r'%[0-1]+'
    t.value = int(t.value[1:len(t.value)], 2)
    return t
def t_CONSTANT_OCTAL(t):
    r'&[0-7]+'
    t.value = int(t.value[1:len(t.value)], 8)
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
        error(t)
    else:
        return t
def t_COMMENTS(t):
    r'(\(\*.*\*\))|({.*})|(//.*)'
    if (t.value[len(t.value)-1]=='\n'):
        t.value='\n'
        t_NEWLINE(t)
def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
def error(t):
    print("\nERROR: Illegal input '%s' on line number %d\n" % (t.value, t.lineno))
def t_error(t):
    print("\nERROR: Illegal input '%s' on line number %d\n" % (t.value[0], t.lineno))
    t.lexer.skip(1)
lexer = lex.lex()
