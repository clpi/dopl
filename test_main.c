#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <unistd.h>

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

void test_compile_and_run_child_exit_code() {
    FILE *f = fopen("test_exit_code.c", "w");
    assert(f != NULL);
    fputs("int main(){return 7;}\n", f);
    fclose(f);

    int rc = compile_and_run("test_exit_code_bin", "test_exit_code.c", 1);
    assert(rc == 7);

    unlink("test_exit_code.c");
    unlink("test_exit_code_bin");
}

void test_compile_and_run_compile_failure() {
    FILE *f = fopen("test_bad_compile.c", "w");
    assert(f != NULL);
    fputs("int main( { return 0; }\n", f);
    fclose(f);

    int rc = compile_and_run("test_bad_compile_bin", "test_bad_compile.c", 1);
    assert(rc != 0);

    unlink("test_bad_compile.c");
    unlink("test_bad_compile_bin");
}

void test_compile_and_run_missing_compiler() {
    FILE *f = fopen("test_missing_cc.c", "w");
    assert(f != NULL);
    fputs("int main(){return 0;}\n", f);
    fclose(f);

    char *original_path = getenv("PATH");
    char *saved_path = original_path ? strdup(original_path) : NULL;
    setenv("PATH", "", 1);

    int rc = compile_and_run("test_missing_cc_bin", "test_missing_cc.c", 1);
    assert(rc != 0);

    if (saved_path) {
        setenv("PATH", saved_path, 1);
        free(saved_path);
    } else {
        unsetenv("PATH");
    }

    unlink("test_missing_cc.c");
    unlink("test_missing_cc_bin");
}

int main() {
    test_read_file_success();
    test_read_file_not_found();
    test_compile_and_run_child_exit_code();
    test_compile_and_run_compile_failure();
    test_compile_and_run_missing_compiler();
    printf("main.c tests passed!\n");
    return 0;
}
