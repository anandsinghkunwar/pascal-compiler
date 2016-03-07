Program Test1;
var
    test: array[1..24, 1..5] of integer;
Begin
    test[1, 4] := 5;
    writeln('The value is ' , test[1, 4]);
    test[1][4] := 6;
    writeln('The value is ' , test[1][4])
End.
