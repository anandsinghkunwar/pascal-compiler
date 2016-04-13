program p;
function foo(a : integer) : integer;
var
    b : integer;
begin
    b := a - 1;
    if a = 1 then
        foo := 1
    else 
    begin
        foo := b * foo(a-1)
    end;
end;

var
    d : integer;
begin
    d := foo(4);
    writeln(d)
end.
