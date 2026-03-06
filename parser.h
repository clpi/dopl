#ifndef PARSER_H
#define PARSER_H

#include "lexer.h"

typedef enum {
    AST_INT, AST_STR, AST_BOOL, AST_VAR, AST_BINOP, AST_CALL, AST_LET,
    AST_IF, AST_WHILE, AST_FOR, AST_RETURN, AST_BLOCK, AST_FN,
    AST_ARRAY, AST_INDEX, AST_ASSIGN, AST_PRINT, AST_LEN, AST_PUSH,
    AST_UNARY
} ASTType;

typedef struct AST {
    ASTType type;
    union {
        int int_val;
        char *str_val;
        int bool_val;
        char *var_name;
        struct { struct AST *left, *right; TokenType op; } binop;
        struct { struct AST *operand; TokenType op; } unary;
        struct { char *name; struct AST **args; int argc; } call;
        struct { char *name; struct AST *val; } let;
        struct { struct AST *cond, *then, *els; } if_stmt;
        struct { struct AST *cond, *body; } while_stmt;
        struct { char *var; struct AST *start, *end, *body; } for_stmt;
        struct { struct AST *val; } ret;
        struct { struct AST **stmts; int count; } block;
        struct { char *name; char **params; int paramc; struct AST *body; } fn;
        struct { struct AST **elems; int count; } array;
        struct { struct AST *arr; struct AST *idx; } index;
        struct { struct AST *target; struct AST *val; } assign;
        struct { struct AST **vals; int count; } print;
        struct { struct AST *arr; } len;
        struct { struct AST *arr; struct AST *val; } push;
    };
} AST;

typedef struct {
    Lexer *lex;
    Token cur;
} Parser;

Parser *parser_new(Lexer *lex);
AST *parse_program(Parser *p);
void ast_free(AST *ast);

#endif
