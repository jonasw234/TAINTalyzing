#include <stdio.h>

char editor[20];

int main(int argc, char* argv[]) {
    char * env_editor = getenv("EDITOR");
    if( env_editor == NULL)
        sprintf(editor, "%s", "vim");
    else
        sprintf(editor, "%s", env_editor);

    return 0;
}
