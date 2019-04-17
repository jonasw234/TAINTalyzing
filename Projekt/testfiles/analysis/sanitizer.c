#include <stdio.h>

void vuln(char * input) {
    test();
    printf(input);

}

int main(int argc, char** argv) {
    char userControlled[100];
    printf("Enter format string: ");
    scanf("%s", userControlled);
    vuln(userControlled);
    printf("\n");
    fflush(stdout);

    return 0;
}
