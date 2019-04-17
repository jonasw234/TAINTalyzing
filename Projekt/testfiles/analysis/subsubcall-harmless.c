#include <stdio.h>

char editor[20];

void test(char * input) {
    printf("Hallo!");
}

char * return_input(char * input) {
    return input;
}

int main(int argc, char* argv[]) {
    if( getenv("EDITOR") == NULL)
        sprintf(editor, "%s", "vim");
    else
        sprintf(editor, "%s", return_input(test("EDITOR")));

    return 0;
}
