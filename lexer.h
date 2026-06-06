#ifndef LEXER_H
#define LEXER_H

typedef enum {
    TOK_EOF, TOK_INT, TOK_IDENT, TOK_STR, TOK_TRUE, TOK_FALSE,
    TOK_FN, TOK_LET, TOK_IF, TOK_ELSE, TOK_WHILE, TOK_FOR, TOK_IN, TOK_DOTDOT, TOK_RETURN,
    TOK_LPAREN, TOK_RPAREN, TOK_LBRACE, TOK_RBRACE, TOK_LBRACKET, TOK_RBRACKET,
    TOK_COMMA, TOK_COLON, TOK_SEMI, TOK_ASSIGN, TOK_PLUS, TOK_MINUS, TOK_STAR,
    TOK_SLASH, TOK_PERCENT, TOK_EQ, TOK_NE, TOK_LT, TOK_GT, TOK_LE, TOK_GE,
    TOK_AND, TOK_OR, TOK_NOT, TOK_PRINT, TOK_LEN, TOK_PUSH
} TokenType;

typedef struct {
    TokenType type;
    char *value;
    int int_val;
    int line;
} Token;

typedef struct {
    char *src;
    int pos;
    int line;
} Lexer;

Lexer *lexer_new(char *src);
Token lexer_next(Lexer *lex);
void lexer_free(Lexer *lex);

#endif
