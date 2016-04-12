program p;
function foo(a,b,c : integer; d : char) : integer;
begin
   //a := 5;
    writeln(a);
    writeln(c);
   foo := 7;
end;

var
   d : integer;

begin
   d := foo(1,2,3,'f');
   writeln(d)
end.
