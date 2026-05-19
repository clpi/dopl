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


void test_ast_free() {
    // Test NULL guard
    ast_free(NULL);

    // Test a basic leaf node
    AST *int_ast = calloc(1, sizeof(AST));
    assert(int_ast != NULL);
    int_ast->type = AST_INT;
    int_ast->int_val = 42;
    ast_free(int_ast);

    // Test a recursive node (AST_BINOP)
    AST *binop_ast = malloc(sizeof(AST));
    binop_ast->type = AST_BINOP;
    binop_ast->binop.op = TOK_PLUS;
    binop_ast->binop.left = malloc(sizeof(AST));
    binop_ast->binop.left->type = AST_INT;
    binop_ast->binop.left->int_val = 1;
    binop_ast->binop.right = malloc(sizeof(AST));
    binop_ast->binop.right->type = AST_INT;
    binop_ast->binop.right->int_val = 2;
    ast_free(binop_ast);

    // Test a node with dynamic allocations (AST_BLOCK)
    AST *block_ast = malloc(sizeof(AST));
    block_ast->type = AST_BLOCK;
    block_ast->block.count = 2;
    block_ast->block.stmts = malloc(sizeof(AST*) * 2);

    AST *s1 = malloc(sizeof(AST));
    s1->type = AST_INT;
    s1->int_val = 10;
    block_ast->block.stmts[0] = s1;

    AST *s2 = malloc(sizeof(AST));
    s2->type = AST_INT;
    s2->int_val = 20;
    block_ast->block.stmts[1] = s2;

    ast_free(block_ast);
}

int main() {
    test_read_file_success();
    test_read_file_not_found();
    test_ast_free();
    printf("read_file and ast_free tests passed!\n");
    return 0;
}
