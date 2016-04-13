program p;
function foo(a : integer) : integer;
begin
    if a = 1 then
        foo := 1
    else 
    begin
        foo := a * foo(a - 1)
    end;
end;

var
    d : integer;
begin
    read(d);
    d := foo(d);
    writeln(d)
end.
