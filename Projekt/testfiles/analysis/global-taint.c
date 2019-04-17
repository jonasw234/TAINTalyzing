#include <stdio.h>

char tainted[20];
char * untainted = "hallo, welt!\n";
char * sinkMe = "%x";

void source() {
    scanf("%s", tainted);
}

void sink() {
    printf(tainted);
}

void sink_me() {
    printf(sinkMe);
}

void untainted_print() {
    printf("%s", untainted);
}

int main(int argc, char* argv[]) {
    source();
    sink();
    sink_me();
    untainted_print();
    printf("\n");
    return 0;
}
