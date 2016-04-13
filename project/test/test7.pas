program p;
function foo(a : integer) : integer;
var
    b : integer;
begin
    if a = 1 then
        foo := 1
    else 
    begin
        foo := foo(a-1)
    end;
end;

var
    d : integer;
begin
    d := foo(4);
    writeln(d)
end.
