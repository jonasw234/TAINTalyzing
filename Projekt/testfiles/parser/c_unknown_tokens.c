int main() {
    // Main function
    printf("hallo, welt");
    for (int i = 0; i < 5; i++) {
        char* delim = "";
        printf("%s%d", delim, i);
        delim = ", ";
    }
    printf("\n");
}
