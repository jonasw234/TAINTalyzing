#include <stdio.h>

void source(char * input) {
    scanf("%s", input);
}

int main(int argc, char* argv[]) {
    char userControlled[100];
    source(userControlled);
    printf(userControlled);

    return 0;
}
