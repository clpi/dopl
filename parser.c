#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include "parser.h"

static void advance(Parser *p) { p->cur = lexer_next(p->lex); }
static AST *parse_expr(Parser *p);
static AST *parse_stmt(Parser *p);

Parser *parser_new(Lexer *lex) {
    Parser *p = malloc(sizeof(Parser));
    p->lex = lex;
    advance(p);
    return p;
}

static AST *new_ast(ASTType type) {
    AST *ast = malloc(sizeof(AST));
    memset(ast, 0, sizeof(AST));
    ast->type = type;
    return ast;
}

static char *esc_str(char *s) {
    int len = strlen(s);
    char *out = malloc(len + 1);
    int j = 0;
    for (int i = 0; i < len; i++) {
        if (s[i] == '\\' && i + 1 < len) {
            switch (s[i+1]) {
                case 'n': out[j++] = '\n'; i++; break;
                case 't': out[j++] = '\t'; i++; break;
                case '"': out[j++] = '"'; i++; break;
                case '\\': out[j++] = '\\'; i++; break;
                default: out[j++] = s[i]; break;
            }
        } else {
            out[j++] = s[i];
        }
    }
    out[j] = '\0';
    return out;
}

static AST *parse_primary(Parser *p) {
    if (p->cur.type == TOK_INT) {
        AST *ast = new_ast(AST_INT);
        ast->int_val = atoi(p->cur.value);
        free(p->cur.value);
        advance(p);
        return ast;
    }
    if (p->cur.type == TOK_STR) {
        AST *ast = new_ast(AST_STR);
        ast->str_val = esc_str(p->cur.value);
        free(p->cur.value);
        advance(p);
        return ast;
    }
    if (p->cur.type == TOK_TRUE) {
        AST *ast = new_ast(AST_BOOL);
        ast->bool_val = 1;
        advance(p);
        return ast;
    }
    if (p->cur.type == TOK_FALSE) {
        AST *ast = new_ast(AST_BOOL);
        ast->bool_val = 0;
        advance(p);
        return ast;
    }
    if (p->cur.type == TOK_LBRACKET) {
        advance(p);
        AST *ast = new_ast(AST_ARRAY);
        int cap = 4;
        ast->array.elems = malloc(cap * sizeof(AST*));
        ast->array.count = 0;
        while (p->cur.type != TOK_RBRACKET) {
            if (ast->array.count >= cap) {
                cap *= 2;
                ast->array.elems = realloc(ast->array.elems, cap * sizeof(AST*));
            }
            ast->array.elems[ast->array.count++] = parse_expr(p);
            if (p->cur.type == TOK_COMMA) advance(p);
        }
        advance(p);
        return ast;
    }
    if (p->cur.type == TOK_IDENT) {
        char *name = p->cur.value;
        advance(p);
        if (p->cur.type == TOK_LPAREN) {
            advance(p);
            AST *ast = new_ast(AST_CALL);
            ast->call.name = name;
            ast->call.args = NULL;
            ast->call.argc = 0;
            if (p->cur.type != TOK_RPAREN) {
                int cap = 4;
                ast->call.args = malloc(cap * sizeof(AST*));
                while (1) {
                    if (ast->call.argc >= cap) {
                        cap *= 2;
                        ast->call.args = realloc(ast->call.args, cap * sizeof(AST*));
                    }
                    ast->call.args[ast->call.argc++] = parse_expr(p);
                    if (p->cur.type != TOK_COMMA) break;
                    advance(p);
                }
            }
            advance(p);
            return ast;
        }
        if (p->cur.type == TOK_LBRACKET) {
            advance(p);
            AST *ast = new_ast(AST_INDEX);
            ast->index.arr = new_ast(AST_VAR);
            ast->index.arr->var_name = name;
            ast->index.idx = parse_expr(p);
            advance(p);
            return ast;
        }
        AST *ast = new_ast(AST_VAR);
        ast->var_name = name;
        return ast;
    }
    if (p->cur.type == TOK_LPAREN) {
        advance(p);
        AST *ast = parse_expr(p);
        advance(p);
        return ast;
    }
    if (p->cur.type == TOK_NOT) {
        advance(p);
        AST *ast = new_ast(AST_UNARY);
        ast->unary.op = TOK_NOT;
        ast->unary.operand = parse_primary(p);
        return ast;
    }
    return NULL;
}

static AST *parse_term(Parser *p) {
    AST *left = parse_primary(p);
    while (p->cur.type == TOK_STAR || p->cur.type == TOK_SLASH || p->cur.type == TOK_PERCENT) {
        TokenType op = p->cur.type;
        advance(p);
        AST *ast = new_ast(AST_BINOP);
        ast->binop.left = left;
        ast->binop.op = op;
        ast->binop.right = parse_primary(p);
        left = ast;
    }
    return left;
}

static AST *parse_arith(Parser *p) {
    AST *left = parse_term(p);
    while (p->cur.type == TOK_PLUS || p->cur.type == TOK_MINUS) {
        TokenType op = p->cur.type;
        advance(p);
        AST *ast = new_ast(AST_BINOP);
        ast->binop.left = left;
        ast->binop.op = op;
        ast->binop.right = parse_term(p);
        left = ast;
    }
    return left;
}

static AST *parse_expr(Parser *p) {
    AST *left = parse_arith(p);
    while (p->cur.type >= TOK_EQ && p->cur.type <= TOK_GE) {
        TokenType op = p->cur.type;
        advance(p);
        AST *ast = new_ast(AST_BINOP);
        ast->binop.left = left;
        ast->binop.op = op;
        ast->binop.right = parse_arith(p);
        left = ast;
    }
    while (p->cur.type == TOK_AND || p->cur.type == TOK_OR) {
        TokenType op = p->cur.type;
        advance(p);
        AST *ast = new_ast(AST_BINOP);
        ast->binop.left = left;
        ast->binop.op = op;
        ast->binop.right = parse_expr(p);
        left = ast;
    }
    return left;
}

static AST *parse_block(Parser *p) {
    advance(p);
    AST *ast = new_ast(AST_BLOCK);
    int cap = 64;
    ast->block.stmts = malloc(cap * sizeof(AST*));
    ast->block.count = 0;
    while (p->cur.type != TOK_RBRACE && p->cur.type != TOK_EOF) {
        if (ast->block.count >= cap) {
            cap *= 2;
            ast->block.stmts = realloc(ast->block.stmts, cap * sizeof(AST*));
        }
        ast->block.stmts[ast->block.count++] = parse_stmt(p);
    }
    advance(p);
    return ast;
}

static AST *parse_stmt(Parser *p) {
    if (p->cur.type == TOK_LET) {
        advance(p);
        AST *ast = new_ast(AST_LET);
        ast->let.name = p->cur.value;
        advance(p);
        advance(p);
        ast->let.val = parse_expr(p);
        return ast;
    }
    if (p->cur.type == TOK_IF) {
        advance(p);
        AST *ast = new_ast(AST_IF);
        ast->if_stmt.cond = parse_expr(p);
        ast->if_stmt.then = parse_block(p);
        ast->if_stmt.els = NULL;
        if (p->cur.type == TOK_ELSE) {
            advance(p);
            ast->if_stmt.els = parse_block(p);
        }
        return ast;
    }
    if (p->cur.type == TOK_WHILE) {
        advance(p);
        AST *ast = new_ast(AST_WHILE);
        ast->while_stmt.cond = parse_expr(p);
        ast->while_stmt.body = parse_block(p);
        return ast;
    }
    if (p->cur.type == TOK_FOR) {
        advance(p);
        AST *ast = new_ast(AST_FOR);
        ast->for_stmt.var = p->cur.value;
        advance(p);
        if (p->cur.type == TOK_IN) advance(p);
        ast->for_stmt.start = parse_expr(p);
        if (p->cur.type == TOK_DOTDOT) advance(p);
        ast->for_stmt.end = parse_expr(p);
        ast->for_stmt.body = parse_block(p);
        return ast;
    }
    if (p->cur.type == TOK_RETURN) {
        advance(p);
        AST *ast = new_ast(AST_RETURN);
        ast->ret.val = parse_expr(p);
        return ast;
    }
    if (p->cur.type == TOK_PRINT) {
        advance(p);
        advance(p);
        AST *ast = new_ast(AST_PRINT);
        int cap = 4;
        ast->print.vals = malloc(cap * sizeof(AST*));
        ast->print.count = 0;
        while (p->cur.type != TOK_RPAREN) {
            if (ast->print.count >= cap) {
                cap *= 2;
                ast->print.vals = realloc(ast->print.vals, cap * sizeof(AST*));
            }
            ast->print.vals[ast->print.count++] = parse_expr(p);
            if (p->cur.type == TOK_COMMA) advance(p);
        }
        advance(p);
        return ast;
    }
    if (p->cur.type == TOK_LEN) {
        advance(p);
        advance(p);
        AST *ast = new_ast(AST_LEN);
        ast->len.arr = parse_expr(p);
        advance(p);
        return ast;
    }
    if (p->cur.type == TOK_PUSH) {
        advance(p);
        advance(p);
        AST *ast = new_ast(AST_PUSH);
        ast->push.arr = new_ast(AST_VAR);
        ast->push.arr->var_name = p->cur.value;
        advance(p);
        advance(p);
        ast->push.val = parse_expr(p);
        advance(p);
        advance(p);
        return ast;
    }
    if (p->cur.type == TOK_LBRACE) {
        return parse_block(p);
    }
    if (p->cur.type == TOK_IDENT) {
        char *name = p->cur.value;
        Parser saved_parser = *p;
        advance(p);
        if (p->cur.type == TOK_ASSIGN) {
            advance(p);
            AST *ast = new_ast(AST_ASSIGN);
            ast->assign.target = new_ast(AST_VAR);
            ast->assign.target->var_name = name;
            ast->assign.val = parse_expr(p);
            return ast;
        }
        if (p->cur.type == TOK_LBRACKET) {
            advance(p);
            AST *idx = parse_expr(p);
            advance(p);
            if (p->cur.type == TOK_ASSIGN) {
                advance(p);
                AST *ast = new_ast(AST_ASSIGN);
                ast->assign.target = new_ast(AST_INDEX);
                ast->assign.target->index.arr = new_ast(AST_VAR);
                ast->assign.target->index.arr->var_name = name;
                ast->assign.target->index.idx = idx;
                ast->assign.val = parse_expr(p);
                return ast;
            }
            AST *ast = new_ast(AST_INDEX);
            ast->index.arr = new_ast(AST_VAR);
            ast->index.arr->var_name = name;
            ast->index.idx = idx;
            return ast;
        }
        if (p->cur.type == TOK_LPAREN) {
            // Function call
            advance(p);
            AST *ast = new_ast(AST_CALL);
            ast->call.name = name;
            ast->call.args = NULL;
            ast->call.argc = 0;
            if (p->cur.type != TOK_RPAREN) {
                int cap = 4;
                ast->call.args = malloc(cap * sizeof(AST*));
                while (1) {
                    if (ast->call.argc >= cap) {
                        cap *= 2;
                        ast->call.args = realloc(ast->call.args, cap * sizeof(AST*));
                    }
                    ast->call.args[ast->call.argc++] = parse_expr(p);
                    if (p->cur.type != TOK_COMMA) break;
                    advance(p);
                }
            }
            advance(p);
            return ast;
        }
        *p = saved_parser;
        return parse_expr(p);
    }
    return parse_expr(p);
}

AST *parse_program(Parser *p) {
    AST *prog = new_ast(AST_BLOCK);
    int cap = 64;
    prog->block.stmts = malloc(cap * sizeof(AST*));
    prog->block.count = 0;
    
    while (p->cur.type != TOK_EOF) {
        if (p->cur.type == TOK_FN) {
            advance(p);
            AST *fn = new_ast(AST_FN);
            fn->fn.name = p->cur.value;
            advance(p);
            advance(p);
            
            int pcap = 4;
            fn->fn.params = malloc(pcap * sizeof(char*));
            fn->fn.paramc = 0;
            while (p->cur.type != TOK_RPAREN) {
                if (fn->fn.paramc >= pcap) {
                    pcap *= 2;
                    fn->fn.params = realloc(fn->fn.params, pcap * sizeof(char*));
                }
                fn->fn.params[fn->fn.paramc++] = p->cur.value;
                advance(p);
                if (p->cur.type == TOK_COMMA) advance(p);
            }
            advance(p);
            fn->fn.body = parse_block(p);
            
            if (prog->block.count >= cap) {
                cap *= 2;
                prog->block.stmts = realloc(prog->block.stmts, cap * sizeof(AST*));
            }
            prog->block.stmts[prog->block.count++] = fn;
        } else {
            if (prog->block.count >= cap) {
                cap *= 2;
                prog->block.stmts = realloc(prog->block.stmts, cap * sizeof(AST*));
            }
            prog->block.stmts[prog->block.count++] = parse_stmt(p);
        }
    }
    return prog;
}

void ast_free(AST *ast) {
    if (!ast) return;
    switch (ast->type) {
        case AST_BINOP:
            ast_free(ast->binop.left);
            ast_free(ast->binop.right);
            break;
        case AST_UNARY:
            ast_free(ast->unary.operand);
            break;
        case AST_CALL:
            for (int i = 0; i < ast->call.argc; i++) ast_free(ast->call.args[i]);
            free(ast->call.args);
            break;
        case AST_LET:
            free(ast->let.name);
            ast_free(ast->let.val);
            break;
        case AST_IF:
            ast_free(ast->if_stmt.cond);
            ast_free(ast->if_stmt.then);
            ast_free(ast->if_stmt.els);
            break;
        case AST_WHILE:
            ast_free(ast->while_stmt.cond);
            ast_free(ast->while_stmt.body);
            break;
        case AST_FOR:
            free(ast->for_stmt.var);
            ast_free(ast->for_stmt.start);
            ast_free(ast->for_stmt.end);
            ast_free(ast->for_stmt.body);
            break;
        case AST_RETURN:
            ast_free(ast->ret.val);
            break;
        case AST_BLOCK:
            for (int i = 0; i < ast->block.count; i++) ast_free(ast->block.stmts[i]);
            free(ast->block.stmts);
            break;
        case AST_FN:
            free(ast->fn.name);
            for (int i = 0; i < ast->fn.paramc; i++) free(ast->fn.params[i]);
            free(ast->fn.params);
            ast_free(ast->fn.body);
            break;
        case AST_ARRAY:
            for (int i = 0; i < ast->array.count; i++) ast_free(ast->array.elems[i]);
            free(ast->array.elems);
            break;
        case AST_INDEX:
            ast_free(ast->index.arr);
            ast_free(ast->index.idx);
            break;
        case AST_ASSIGN:
            ast_free(ast->assign.target);
            ast_free(ast->assign.val);
            break;
        case AST_PRINT:
            for (int i = 0; i < ast->print.count; i++) ast_free(ast->print.vals[i]);
            free(ast->print.vals);
            break;
        case AST_LEN:
            ast_free(ast->len.arr);
            break;
        case AST_PUSH:
            ast_free(ast->push.arr);
            ast_free(ast->push.val);
            break;
        case AST_VAR:
            free(ast->var_name);
            break;
        case AST_STR:
            free(ast->str_val);
            break;
        default:
            break;
    }
    free(ast);
}
