program FPProgT9_1;
uses
  cthreads,
  Classes
var
  x:integer;
begin
  for x:=1 to 10 do
  begin
    writeln(x);
  end;
  writeln;
  writeln;
  writeln('Press <Enter> To Quit');
  readln;
end.
