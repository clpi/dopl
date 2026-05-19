#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "lexer.h"

int tests_run = 0;
int tests_failed = 0;

#define ASSERT_EQ(actual, expected) \
    do { \
        tests_run++; \
        if ((actual) != (expected)) { \
            fprintf(stderr, "%s:%d: Assertion failed: %s == %s (got %d, expected %d)\n", \
                    __FILE__, __LINE__, #actual, #expected, (int)(actual), (int)(expected)); \
            tests_failed++; \
        } \
    } while (0)

#define ASSERT_STR_EQ(actual, expected) \
    do { \
        tests_run++; \
        if (actual == NULL || expected == NULL || strcmp((actual), (expected)) != 0) { \
            fprintf(stderr, "%s:%d: Assertion failed: %s == %s (got '%s', expected '%s')\n", \
                    __FILE__, __LINE__, #actual, #expected, actual ? actual : "NULL", expected ? expected : "NULL"); \
            tests_failed++; \
        } \
    } while (0)

void test_keywords() {
    Lexer *lex = lexer_new("fn let if else while for return true false and or not print len push");
    Token tok;

    tok = lexer_next(lex); ASSERT_EQ(tok.type, TOK_FN); ASSERT_STR_EQ(tok.value, "fn");
    tok = lexer_next(lex); ASSERT_EQ(tok.type, TOK_LET); ASSERT_STR_EQ(tok.value, "let");
    tok = lexer_next(lex); ASSERT_EQ(tok.type, TOK_IF); ASSERT_STR_EQ(tok.value, "if");
    tok = lexer_next(lex); ASSERT_EQ(tok.type, TOK_ELSE); ASSERT_STR_EQ(tok.value, "else");
    tok = lexer_next(lex); ASSERT_EQ(tok.type, TOK_WHILE); ASSERT_STR_EQ(tok.value, "while");
    tok = lexer_next(lex); ASSERT_EQ(tok.type, TOK_FOR); ASSERT_STR_EQ(tok.value, "for");
    tok = lexer_next(lex); ASSERT_EQ(tok.type, TOK_RETURN); ASSERT_STR_EQ(tok.value, "return");
    tok = lexer_next(lex); ASSERT_EQ(tok.type, TOK_TRUE); ASSERT_STR_EQ(tok.value, "true");
    tok = lexer_next(lex); ASSERT_EQ(tok.type, TOK_FALSE); ASSERT_STR_EQ(tok.value, "false");
    tok = lexer_next(lex); ASSERT_EQ(tok.type, TOK_AND); ASSERT_STR_EQ(tok.value, "and");
    tok = lexer_next(lex); ASSERT_EQ(tok.type, TOK_OR); ASSERT_STR_EQ(tok.value, "or");
    tok = lexer_next(lex); ASSERT_EQ(tok.type, TOK_NOT); ASSERT_STR_EQ(tok.value, "not");
    tok = lexer_next(lex); ASSERT_EQ(tok.type, TOK_PRINT); ASSERT_STR_EQ(tok.value, "print");
    tok = lexer_next(lex); ASSERT_EQ(tok.type, TOK_LEN); ASSERT_STR_EQ(tok.value, "len");
    tok = lexer_next(lex); ASSERT_EQ(tok.type, TOK_PUSH); ASSERT_STR_EQ(tok.value, "push");
    tok = lexer_next(lex); ASSERT_EQ(tok.type, TOK_EOF);

    lexer_free(lex);
}

void test_symbols() {
    Lexer *lex = lexer_new("(){}[] ,:;= +-*/% == != < > <= >=");
    Token tok;

    tok = lexer_next(lex); ASSERT_EQ(tok.type, TOK_LPAREN);
    tok = lexer_next(lex); ASSERT_EQ(tok.type, TOK_RPAREN);
    tok = lexer_next(lex); ASSERT_EQ(tok.type, TOK_LBRACE);
    tok = lexer_next(lex); ASSERT_EQ(tok.type, TOK_RBRACE);
    tok = lexer_next(lex); ASSERT_EQ(tok.type, TOK_LBRACKET);
    tok = lexer_next(lex); ASSERT_EQ(tok.type, TOK_RBRACKET);
    tok = lexer_next(lex); ASSERT_EQ(tok.type, TOK_COMMA);
    tok = lexer_next(lex); ASSERT_EQ(tok.type, TOK_COLON);
    tok = lexer_next(lex); ASSERT_EQ(tok.type, TOK_SEMI);
    tok = lexer_next(lex); ASSERT_EQ(tok.type, TOK_ASSIGN);
    tok = lexer_next(lex); ASSERT_EQ(tok.type, TOK_PLUS);
    tok = lexer_next(lex); ASSERT_EQ(tok.type, TOK_MINUS);
    tok = lexer_next(lex); ASSERT_EQ(tok.type, TOK_STAR);
    tok = lexer_next(lex); ASSERT_EQ(tok.type, TOK_SLASH);
    tok = lexer_next(lex); ASSERT_EQ(tok.type, TOK_PERCENT);
    tok = lexer_next(lex); ASSERT_EQ(tok.type, TOK_EQ);
    tok = lexer_next(lex); ASSERT_EQ(tok.type, TOK_NE);
    tok = lexer_next(lex); ASSERT_EQ(tok.type, TOK_LT);
    tok = lexer_next(lex); ASSERT_EQ(tok.type, TOK_GT);
    tok = lexer_next(lex); ASSERT_EQ(tok.type, TOK_LE);
    tok = lexer_next(lex); ASSERT_EQ(tok.type, TOK_GE);
    tok = lexer_next(lex); ASSERT_EQ(tok.type, TOK_EOF);

    lexer_free(lex);
}

void test_literals() {
    Lexer *lex = lexer_new("42 0 -123 \"hello world\" \"with \\\" escapes\"");
    Token tok;

    tok = lexer_next(lex); ASSERT_EQ(tok.type, TOK_INT); ASSERT_STR_EQ(tok.value, "42");
    tok = lexer_next(lex); ASSERT_EQ(tok.type, TOK_INT); ASSERT_STR_EQ(tok.value, "0");
    tok = lexer_next(lex); ASSERT_EQ(tok.type, TOK_MINUS);
    tok = lexer_next(lex); ASSERT_EQ(tok.type, TOK_INT); ASSERT_STR_EQ(tok.value, "123");
    tok = lexer_next(lex); ASSERT_EQ(tok.type, TOK_STR); ASSERT_STR_EQ(tok.value, "hello world");
    tok = lexer_next(lex); ASSERT_EQ(tok.type, TOK_STR); ASSERT_STR_EQ(tok.value, "with \\\" escapes");
    tok = lexer_next(lex); ASSERT_EQ(tok.type, TOK_EOF);

    lexer_free(lex);
}

void test_identifiers() {
    Lexer *lex = lexer_new("foo bar_baz _priv obj123");
    Token tok;

    tok = lexer_next(lex); ASSERT_EQ(tok.type, TOK_IDENT); ASSERT_STR_EQ(tok.value, "foo");
    tok = lexer_next(lex); ASSERT_EQ(tok.type, TOK_IDENT); ASSERT_STR_EQ(tok.value, "bar_baz");
    tok = lexer_next(lex); ASSERT_EQ(tok.type, TOK_IDENT); ASSERT_STR_EQ(tok.value, "_priv");
    tok = lexer_next(lex); ASSERT_EQ(tok.type, TOK_IDENT); ASSERT_STR_EQ(tok.value, "obj123");
    tok = lexer_next(lex); ASSERT_EQ(tok.type, TOK_EOF);

    lexer_free(lex);
}

void test_comments() {
    Lexer *lex = lexer_new("let x = 1 # this is a comment\n let y = 2");
    Token tok;

    tok = lexer_next(lex); ASSERT_EQ(tok.type, TOK_LET);
    tok = lexer_next(lex); ASSERT_EQ(tok.type, TOK_IDENT); ASSERT_STR_EQ(tok.value, "x");
    tok = lexer_next(lex); ASSERT_EQ(tok.type, TOK_ASSIGN);
    tok = lexer_next(lex); ASSERT_EQ(tok.type, TOK_INT); ASSERT_STR_EQ(tok.value, "1");
    // comment should be skipped
    tok = lexer_next(lex); ASSERT_EQ(tok.type, TOK_LET); ASSERT_EQ(tok.line, 2);
    tok = lexer_next(lex); ASSERT_EQ(tok.type, TOK_IDENT); ASSERT_STR_EQ(tok.value, "y");
    tok = lexer_next(lex); ASSERT_EQ(tok.type, TOK_ASSIGN);
    tok = lexer_next(lex); ASSERT_EQ(tok.type, TOK_INT); ASSERT_STR_EQ(tok.value, "2");
    tok = lexer_next(lex); ASSERT_EQ(tok.type, TOK_EOF);

    lexer_free(lex);
}

int main() {
    printf("Running lexer tests...\n");
    test_keywords();
    test_symbols();
    test_literals();
    test_identifiers();
    test_comments();

    if (tests_failed == 0) {
        printf("All %d tests passed successfully!\n", tests_run);
        return 0;
    } else {
        printf("%d out of %d tests failed.\n", tests_failed, tests_run);
        return 1;
    }
}
