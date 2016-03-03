Program Test3;
var
    a : integer = 1;
    b : array [1..25] of integer;
    c : array ['a'..'z'] of integer;
Begin
    // Dangling Else Checking
    if a >= 1 then
        if a > 1 then
            writeln('Done')
        else
            if a = 1 then
                writeln('Dangling')

    c['s'] := 123;
    b[a+23-3*3] := 12332;

End.