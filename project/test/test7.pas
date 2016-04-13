program p;
function foo(a : integer) : integer;
var
    b : integer;
    c : integer;
begin
    b := a - 1;
    writeln(b);
    if a = 1 then
        foo := 1
    else 
    begin
        c := foo(b);
        writeln('now');
        writeln(c);
        b := a * c;
        writeln('the value is');
        writeln(b);
        foo := b
    end;
end;

var
    d : integer;
begin
    d := foo(4);
    writeln(d)
end.
