#include <stdio.h>

void vuln(char * controlledParam) {
    printf(controlledParam);
}

int main(int argc, char** argv) {
    char userControlled[100];
    printf("Enter format string: ");
    scanf("%s", userControlled);
    char * userControlledToo = userControlled;
    vuln(userControlledToo);
    printf("\n");
    fflush(stdout);

    return 0;
}
