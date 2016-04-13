program p;
function foo(a : integer) : integer;
var
    b : integer;
begin
    b := a - 1;
    b := a * foo(b);
    foo := b;
end;

var
    d : integer;
begin
    d := foo(4);
end.
