#include <stdio.h>

int main(int argc, char* argv[]) {
    if (0) {
        test();
    } else if (2) {
        printf(argv[1]);
    } else if (3) {
        printf("hallo\n");
    } else {
        printf("bye!\n");
    }
    return 0;
}
