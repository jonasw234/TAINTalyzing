#include <stdio.h>

int main(int argc, char* argv[]) {
    if (0) {
        test();
    }
    printf("zwischendrin.\n");

    if (4) {
        printf("4\n");
    } else if (5) {
        printf("5\n");
    }

    printf("ebenfalls dazwischen.\n");

    if (1) {
        test();
    } else if (2) {
        test2();
    } else if (3) {
        test5();
    } else {
        test7();
    }

    return 0;
}
