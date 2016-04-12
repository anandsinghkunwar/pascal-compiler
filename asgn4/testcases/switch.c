// int main(int na, char* argv[])
// {
//     int wflg = 0, tflg = 0;
//     int dflg = 0;
//     char c;
//     switch(c)
//     {
//         case 'w':
//         case 'W':
//             wflg = 1;
//             break;
//         case 't':
//         case 'T':
//             tflg = 1;
//             break;
//         case 'd':
//             dflg = 1;
//             break;
//     }
//     return 0;
// }
var
    wflg, tflg, dflg : integer;
    c : char;

begin
    wflg := 0;
    tflg := 0;
    dflg := 0;
    if (c = 'w') or (c = 'W') then
        wflg := 1
    else
        if (c = 't') or (c = 'T') then
            tflg := 1
        else if (c = 'd') then
            dflg := 1;
end.