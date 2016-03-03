Program Test3;
var
    a : integer = 1;
Begin
    // Dangling Else Checking
    if a >= 1 then
        if a > 1 then
            writeln('Done');
        else
            if a = 1 then
                writeln('Dangling');
            


End.