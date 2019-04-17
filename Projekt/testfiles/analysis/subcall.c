#include <stdio.h>

char editor[20];

int main(int argc, char* argv[]) {
    if( getenv("EDITOR") == NULL)
        sprintf(editor, "%s", "vim");
    else
        sprintf(editor, "%s", getenv("EDITOR"));

    return 0;
}
