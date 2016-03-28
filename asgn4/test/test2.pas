Program Test2;
var
    a : integer;
    b : char;
    c : boolean;
    d : boolean;

Begin
    c := true;
    d := false;
    // Checking for left associativity
    a := 1 + 1 - 34;
    b := a * 123 / 21 * 123;

    // Checking for operator preceedence
    a := a / 123 + 123 * 123 - 123;
    b := a * (a+b) - 123;
    if c = d or c or not d then;

End.