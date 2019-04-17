#include <stdio.h>

char * source_return_direct() {
    return getchar();
}

int main(int argc, char* argv[]) {
    char * source_return_direct = source_return_direct();
    printf(source_return_direct);

    return 0;
}
