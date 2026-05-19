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

void test_parse_program_empty() {
    Lexer *lex = lexer_new("");
    Parser *p = parser_new(lex);
    AST *prog = parse_program(p);

    assert(prog != NULL);
    assert(prog->type == AST_BLOCK);
    assert(prog->block.count == 0);

    ast_free(prog);
    free(p);
    lexer_free(lex);
}

void test_parse_program_fn() {
    Lexer *lex = lexer_new("fn add(a, b) { return a + b }");
    Parser *p = parser_new(lex);
    AST *prog = parse_program(p);

    assert(prog != NULL);
    assert(prog->type == AST_BLOCK);
    assert(prog->block.count == 1);

    AST *fn = prog->block.stmts[0];
    assert(fn->type == AST_FN);
    assert(strcmp(fn->fn.name, "add") == 0);
    assert(fn->fn.paramc == 2);
    assert(strcmp(fn->fn.params[0], "a") == 0);
    assert(strcmp(fn->fn.params[1], "b") == 0);

    ast_free(prog);
    free(p);
    lexer_free(lex);
}

void test_parse_program_stmt() {
    Lexer *lex = lexer_new("let x = 10 print(x)");
    Parser *p = parser_new(lex);
    AST *prog = parse_program(p);

    assert(prog != NULL);
    assert(prog->type == AST_BLOCK);
    assert(prog->block.count == 2);

    AST *stmt1 = prog->block.stmts[0];
    assert(stmt1->type == AST_LET);
    assert(strcmp(stmt1->let.name, "x") == 0);

    AST *stmt2 = prog->block.stmts[1];
    assert(stmt2->type == AST_PRINT);

    ast_free(prog);
    free(p);
    lexer_free(lex);
}

int main() {
    test_read_file_success();
    test_read_file_not_found();
    printf("read_file tests passed!\n");

    test_parse_program_empty();
    test_parse_program_fn();
    test_parse_program_stmt();
    printf("parse_program tests passed!\n");

    return 0;
}
