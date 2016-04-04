Program Test1;
var
    test: array[1..24] of integer;
Begin
    test[1] := 5;
    writeln('The value is ');
    writeln(test[1]);
    test[1] := 6;
    writeln('The value is ');
    writeln(test[1])
End.
