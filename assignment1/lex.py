from src import lexer as lexerModule
# Test it out
data = '''program exPointers;
var
   number: integer;
   iptr: ^integer;
   y: ^word;

begin
   number := 100;
   writeln('Number is: ', number);
   iptr := @number;
   writeln('iptr points to a value: ', iptr^);
   
   iptr ^ := 200;
   writeln('Number is: ', number);
   writeln('iptr points to a value: ', iptr^);
   y := addr(iptr);
   writeln(y ^); 
end.'''

# Give the lexer some input
lexerModule.lexer.input(data)

# Tokenize
while True:
    tok = lexerModule.lexer.token()
    if not tok: 
        break      # No more input
    print tok