#include <stdio.h>

int main(int argc, char** argv) {
    char userControlled[100];
    printf("Enter format string: ");
    scanf("%s", userControlled);
    char * userControlledToo = userControlled;
    test();
    printf(userControlledToo);
    printf("\n");
    fflush(stdout);

    return 0;
}
