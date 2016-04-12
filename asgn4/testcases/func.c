function foo (a : integer; b: char): integer;
var 
	i : integer;
begin
	i := 1;
	foo := 0
end;

var
	i : integer;
	a : integer;
	b : char;
begin
	a := 1;
	b := 'a';
	i := foo(a,b);

end.