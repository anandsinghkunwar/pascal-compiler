program Test3;
uses
  cthreads,
  Classes
var
  x:integer;
  y:real;
begin
  for x:=1 to 10 do
  begin
    writeln(x);
  end;

  writeln;
  writeln;
  y := 1.23E-2;
  y := 423E2
  y := 33.3;
  y := 32;
  writeln('Press <Enter> To Quit');
  readln
end.
