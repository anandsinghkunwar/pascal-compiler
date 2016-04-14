program p;
type
    foo = integer;
    bar = foo;
    baz = bar;

    myCoolType = char;
    coolCoolType = myCoolType;
    soCoolType = coolCoolType;
var
    a : integer;
    b : foo;
    c : bar;
    d : baz;
    
    e : char;
    f : myCoolType;
    g : coolCoolType;
    h : soCoolType;

begin
    e := 'a';
    f := e;
    g := f;
    h := g;
    readln(e);
    readln(f);
    a := 1 + 1;
    b := a + 1;
    c := b + 1;
    d := c + 1;
    writeln(b);
    writeln(c);
    writeln(d);
    writeln(e);
    writeln(f);
    writeln(g);
    writeln(h);

end.
