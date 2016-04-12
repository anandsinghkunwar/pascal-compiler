program p;
function foo(a : integer; d : char) : integer;
begin
    while a < 6 do
    begin
        writeln(d);
    end;
    foo := 6;
end;

var
    a : integer;
begin
    a := 1;
    d := foo(1,'f');
    writeln(d)
end.
