program Test5;
var
  a:integer;
  y:real;
begin
  a := 5;
  while a < 6 do
  begin
    writeln (a);
    a := a + 1 //This is a comment inline
  end;
  writeln;
  writeln;
  a := a<<1;
  a := a>>1;
  a := a shl 1;
  a := a+1-32+a*234  
  (*This is another comment*)
  writeln('Press <Enter> To Quit');
  readln
end.
{This is the third comment}