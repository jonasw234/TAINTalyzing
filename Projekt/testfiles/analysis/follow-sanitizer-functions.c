#include <stdio.h>

void sanitize(int value) {
    int value2 = value;
    test();
}

int main(int argc, char** argv) {
    char userControlled[100];
    printf("Enter format string: ");
    scanf("%s", userControlled);
    char * userControlledToo = userControlled;
    sanitize(5);
    printf(userControlledToo);
    printf("\n");
    fflush(stdout);

    return 0;
}
