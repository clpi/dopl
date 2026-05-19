#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>

#define main ado_main
#include "main.c"
#undef main

void test_read_file_success() {
    FILE *f = fopen("test_dummy.txt", "w");
    if (!f) {
        fprintf(stderr, "Failed to create test file\n");
        assert(0);
    }
    fputs("hello world\n", f);
    fclose(f);

    char *content = read_file("test_dummy.txt");
    assert(content != NULL);
    assert(strcmp(content, "hello world\n") == 0);
    free(content);

    remove("test_dummy.txt");
}

void test_read_file_not_found() {
    char *content = read_file("nonexistent_file_12345.txt");
    assert(content == NULL);
}

int main() {
    test_read_file_success();
    test_read_file_not_found();
    printf("read_file tests passed!\n");
    return 0;
}
