function func(a, b: integer; c: char) : integer;
    var
        local : integer;
begin
   func := 123;
end;
procedure proc(a, b: integer; c: char);
    const
        localConst = 23;
begin
    writeln('Hello ', localConst);
end;
procedure proc2();
    const
        localConst = 23;
begin
    writeln('Hello ', localConst);
end;

begin
    a := func(1, 2, 'c');
    proc(1, 2, 'd');
    proc2;
end.