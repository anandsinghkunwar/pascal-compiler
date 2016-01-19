from src import lexer as lexerModule
# Test it out
data = '''
<<shl'''

# Give the lexer some input
lexerModule.lexer.input(data)

# Tokenize
while True:
    tok = lexerModule.lexer.token()
    if not tok: 
        break      # No more input
    print tok