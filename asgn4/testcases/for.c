// #include <stdio.h>
// int main(){
//     int i=6;
//     for (;i<= 8 && i>= 6 && i!= 7; i++){
//         if (i>=0){
//             printf("yes\n");
//         }
//         else 
//             printf("no\n");
//     }
//     return 0;
// }

var 
	i : integer;


begin
	i := 6;
	while ((i <= 8) and (i >= 6) and (i <> 7)) do
	begin
        if (i >= 0) then
		  writeln('yes')
		else
            writeln('no');
        i := i+1
	end;
end.