program p;
function foo() : integer;
var
    b : array[1..5] of integer;
    i : integer;
begin
    i := 3;
    read(b[i]);
    writeln(b[i]);
    foo := 1
end;
begin
    writeln('main');
    foo()
end.
