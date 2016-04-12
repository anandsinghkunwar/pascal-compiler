// int main(void){
//     int i = 0,a[]={1,2,3};
//     if (i<=3)
//         a[i]++;
//     if (i>=2)
//         a[i]--;
//     else 
//         a[i] = 1;
// }

var
	a : array[0..2] of integer;
	i : integer;

begin
	a[0] := 1;
	a[1] := 2;
	a[2] := 3;
	if (i <= 3) then
		a[i] := a[i] + 1;
	if (i >= 2) then
		a[i] := a[i] - 1
	else
		a[i] := 1;
end.