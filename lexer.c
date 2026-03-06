#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include "lexer.h"

Lexer *lexer_new(char *src) {
    Lexer *lex = malloc(sizeof(Lexer));
    lex->src = src;
    lex->pos = 0;
    lex->line = 1;
    return lex;
}

void lexer_free(Lexer *lex) { free(lex); }

static void skip_ws(Lexer *lex) {
    while (lex->src[lex->pos] == ' ' || lex->src[lex->pos] == '\t' || 
           lex->src[lex->pos] == '\n' || lex->src[lex->pos] == '\r') {
        if (lex->src[lex->pos] == '\n') lex->line++;
        lex->pos++;
    }
}

static void skip_comment(Lexer *lex) {
    skip_ws(lex);
    while (lex->src[lex->pos] == '#') {
        while (lex->src[lex->pos] != '\n' && lex->src[lex->pos] != '\0') lex->pos++;
        if (lex->src[lex->pos] == '\n') { lex->line++; lex->pos++; }
        skip_ws(lex);
    }
}

Token lexer_next(Lexer *lex) {
    skip_comment(lex);
    Token tok = {.line = lex->line, .value = NULL};
    char c = lex->src[lex->pos];
    
    if (c == '\0') { tok.type = TOK_EOF; return tok; }
    
    if (isdigit(c)) {
        int start = lex->pos;
        while (isdigit(lex->src[lex->pos])) lex->pos++;
        int len = lex->pos - start;
        tok.value = strndup(lex->src + start, len);
        tok.type = TOK_INT;
        return tok;
    }
    
    if (c == '"') {
        lex->pos++;
        int start = lex->pos;
        while (lex->src[lex->pos] != '"' && lex->src[lex->pos] != '\0') {
            if (lex->src[lex->pos] == '\\') lex->pos++;
            lex->pos++;
        }
        int len = lex->pos - start;
        tok.value = strndup(lex->src + start, len);
        tok.type = TOK_STR;
        lex->pos++;
        return tok;
    }
    
    if (isalpha(c) || c == '_') {
        int start = lex->pos;
        while (isalnum(lex->src[lex->pos]) || lex->src[lex->pos] == '_') lex->pos++;
        int len = lex->pos - start;
        tok.value = strndup(lex->src + start, len);
        
        if (strcmp(tok.value, "fn") == 0) tok.type = TOK_FN;
        else if (strcmp(tok.value, "let") == 0) tok.type = TOK_LET;
        else if (strcmp(tok.value, "if") == 0) tok.type = TOK_IF;
        else if (strcmp(tok.value, "else") == 0) tok.type = TOK_ELSE;
        else if (strcmp(tok.value, "while") == 0) tok.type = TOK_WHILE;
        else if (strcmp(tok.value, "for") == 0) tok.type = TOK_FOR;
        else if (strcmp(tok.value, "return") == 0) tok.type = TOK_RETURN;
        else if (strcmp(tok.value, "true") == 0) tok.type = TOK_TRUE;
        else if (strcmp(tok.value, "false") == 0) tok.type = TOK_FALSE;
        else if (strcmp(tok.value, "and") == 0) tok.type = TOK_AND;
        else if (strcmp(tok.value, "or") == 0) tok.type = TOK_OR;
        else if (strcmp(tok.value, "not") == 0) tok.type = TOK_NOT;
        else if (strcmp(tok.value, "print") == 0) tok.type = TOK_PRINT;
        else if (strcmp(tok.value, "len") == 0) tok.type = TOK_LEN;
        else if (strcmp(tok.value, "push") == 0) tok.type = TOK_PUSH;
        else tok.type = TOK_IDENT;
        return tok;
    }
    
    lex->pos++;
    switch (c) {
        case '(': tok.type = TOK_LPAREN; break;
        case ')': tok.type = TOK_RPAREN; break;
        case '{': tok.type = TOK_LBRACE; break;
        case '}': tok.type = TOK_RBRACE; break;
        case '[': tok.type = TOK_LBRACKET; break;
        case ']': tok.type = TOK_RBRACKET; break;
        case ',': tok.type = TOK_COMMA; break;
        case ':': tok.type = TOK_COLON; break;
        case ';': tok.type = TOK_SEMI; break;
        case '+': tok.type = TOK_PLUS; break;
        case '-': tok.type = TOK_MINUS; break;
        case '*': tok.type = TOK_STAR; break;
        case '/': tok.type = TOK_SLASH; break;
        case '%': tok.type = TOK_PERCENT; break;
        case '=':
            if (lex->src[lex->pos] == '=') { lex->pos++; tok.type = TOK_EQ; }
            else tok.type = TOK_ASSIGN;
            break;
        case '!':
            if (lex->src[lex->pos] == '=') { lex->pos++; tok.type = TOK_NE; }
            break;
        case '<':
            if (lex->src[lex->pos] == '=') { lex->pos++; tok.type = TOK_LE; }
            else tok.type = TOK_LT;
            break;
        case '>':
            if (lex->src[lex->pos] == '=') { lex->pos++; tok.type = TOK_GE; }
            else tok.type = TOK_GT;
            break;
    }
    return tok;
}
