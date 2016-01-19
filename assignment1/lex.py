from src import lexer as lexerModule
# Test it out
data = '''
Hello=anand'''

# Give the lexer some input
lexerModule.lexer.input(data)
tokenCountDict = {}
tokenDict = {}

# Tokenize
while True:
    tok = lexerModule.lexer.token()
    if not tok: 
        break      # No more input
    tokenCountDict.update({tok.type: tokenCountDict.get(tok.type,0)+1 })
    tokenDict.update({tok.type: tokenDict.get(tok.type,set())|{tok.value}})
print tokenDict
print tokenCountDict