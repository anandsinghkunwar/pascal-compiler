program p;
function foo() : integer;
var
    b : array[1..5] of integer;
begin
    readln(b[2]);
    foo := 1
end;
begin
    writeln('main');
    foo()
end.
