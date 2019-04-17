#include <stdio.h>

char * source_return() {
    int character = getchar();
    return character;
}

int main(int argc, char* argv[]) {
    char * source_return = source_return();
    printf(source_return);

    return 0;
}
