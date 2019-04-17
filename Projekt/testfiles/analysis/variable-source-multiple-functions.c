#include <stdio.h>

void vuln(char * userInput) {
    char * userInputUsed = userInput;
    printf(userInputUsed);
}

int main(int argc, char** argv) {
    char userControlled[100];
    printf("Enter format string: ");
    scanf("%s", userControlled);
    char * userControlledToo = userControlled * userControlled;
    vuln(userControlledToo);
    printf("\n");
    fflush(stdout);

    return 0;
}
