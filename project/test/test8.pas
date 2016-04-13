program p;
function foo(a : integer) : integer;
    function bar(b : integer) : integer;
    begin
        writeln('Bar Here')
    end;
begin
    writeln('Foo Here');
    bar(1);
end;

var
    d : integer;
begin
//    bar(1);
    foo(1);
end.
