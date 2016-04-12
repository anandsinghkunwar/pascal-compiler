program p;
function foo(a : integer; b : integer; c : integer;) : integer;
begin
   a := 5;
   foo := 7;
end;

var
   d : integer;

begin
   d := foo(1,2,3);
   writeln(d)
end.
