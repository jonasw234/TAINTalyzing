#include <stdio.h>

int main(int argc, char* argv[]) {
    char * userControlled = "Hallo, Welt!";
    if (argc < 2) {
        scanf("%s", userControlled);
    } else {
        printf(userControlled);
    }

    return 0;
}
