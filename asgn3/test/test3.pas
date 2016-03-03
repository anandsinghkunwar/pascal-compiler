Program Test3;
var
    a : integer;
    b : char;
    x : boolean;

Begin
    // For Loop Construct
    for a := 10  to 20 do
    begin
        writeln('value of a: ', a);
        b := 'a'
    end;

    // While Loop Construct
    a := 5;
    while a < 6 do
    begin
        writeln (a);
        a := a + 1
    end;

    // Repeat Loop Construct
    x := 1;
    repeat
    begin
        x := x + 1;
    end;
    until x = 10;

End.