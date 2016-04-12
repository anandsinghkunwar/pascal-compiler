program p;
function foo(a,b,c : integer; d : char) : integer;
begin
   //a := 5;
    writeln(a);
    writeln(d);
   foo := 7;
end;

var
   d : integer;
    a : integer;
begin
    a := 1;
   d := foo(a,2,3,'f');
   writeln(d)
end.
