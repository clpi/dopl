#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include "parser.h"

static void advance(Parser *p) { p->cur = lexer_next(p->lex); }
static AST *parse_expr(Parser *p);
static AST *parse_stmt(Parser *p);
static TypeHint *parse_optional_type(Parser *p) {
    if (p->cur.type == TOK_COLON || p->cur.type == TOK_COLONCOLON) {
        int is_required = (p->cur.type == TOK_COLONCOLON);
        advance(p);
        if (p->cur.type == TOK_IDENT) {
            TypeHint *hint = malloc(sizeof(TypeHint));
            hint->name = p->cur.value;
            advance(p);
            hint->is_optional = !is_required;
            return hint;
        }
    }
    return NULL;
}

#define POOL_CHUNK 512

Parser *parser_new(Lexer *lex) {
    Parser *p = malloc(sizeof(Parser));
    p->lex = lex;
    p->pool = NULL;
    p->pool_count = 0;
    p->pool_cap = 0;
    advance(p);
    return p;
}

static AST *new_ast(Parser *p, ASTType type) {
    if (p->pool_count >= p->pool_cap) {
        p->pool_cap = p->pool_cap ? p->pool_cap * 2 : POOL_CHUNK;
        p->pool = realloc(p->pool, p->pool_cap * sizeof(AST));
    }
    AST *ast = &p->pool[p->pool_count++];
    memset(ast, 0, sizeof(AST));
    ast->type = type;
    return ast;
}

static char *esc_str(char *s) {
    int len = strlen(s);
    char *out = malloc(len + 1);
    char *p = s;
    char *q = out;

    while (1) {
        char *next_bs = strchr(p, '\\');
        if (!next_bs) {
            strcpy(q, p);
            break;
        }

        size_t dist = next_bs - p;
        memcpy(q, p, dist);
        q += dist;
        p = next_bs;

        if (*(p+1)) {
            switch (*(p+1)) {
                case 'n': *q++ = '\n'; p += 2; break;
                case 't': *q++ = '\t'; p += 2; break;
                case '"': *q++ = '"'; p += 2; break;
                case '\\': *q++ = '\\'; p += 2; break;
                default: *q++ = *p; p += 1; break;
            }
        } else {
            *q++ = *p++;
        }
    }
    return out;
}

static AST *parse_primary(Parser *p) {
    if (p->cur.type == TOK_INT) {
        AST *ast = new_ast(p, AST_INT);
        ast->int_val = p->cur.int_val;
        free(p->cur.value);
        p->cur.value = NULL;
        advance(p);
        return ast;
    }
    if (p->cur.type == TOK_STR) {
        AST *ast = new_ast(p, AST_STR);
        ast->str_val = esc_str(p->cur.value);
        free(p->cur.value);
        p->cur.value = NULL;
        advance(p);
        return ast;
    }
    if (p->cur.type == TOK_TRUE) {
        AST *ast = new_ast(p, AST_BOOL);
        ast->bool_val = 1;
        advance(p);
        return ast;
    }
    if (p->cur.type == TOK_FALSE) {
        AST *ast = new_ast(p, AST_BOOL);
        ast->bool_val = 0;
        advance(p);
        return ast;
    }
    if (p->cur.type == TOK_LBRACKET) {
        advance(p);
        AST *ast = new_ast(p, AST_ARRAY);
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
            AST *ast = new_ast(p, AST_CALL);
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
            AST *idx = parse_expr(p);
            if (p->cur.type == TOK_DOTDOT) {
                // This is a slice: arr[start..end]
                advance(p); // consume first ..
                AST *ast = new_ast(p, AST_SLICE);
                ast->slice.arr = new_ast(p, AST_VAR);
                ast->slice.arr->var_name = name;
                ast->slice.start = idx;
                ast->slice.end = parse_expr(p);
                advance(p); // consume ]
                return ast;
            }
            // Regular index: arr[index]
            AST *ast = new_ast(p, AST_INDEX);
            ast->index.arr = new_ast(p, AST_VAR);
            ast->index.arr->var_name = name;
            ast->index.idx = idx;
            advance(p); // consume ]
            return ast;
        }
        AST *ast = new_ast(p, AST_VAR);
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
        AST *ast = new_ast(p, AST_UNARY);
        ast->unary.op = TOK_NOT;
        ast->unary.operand = parse_primary(p);
        return ast;
    }
    if (p->cur.type == TOK_LEN) {
        advance(p);
        advance(p);
        AST *ast = new_ast(p, AST_LEN);
        ast->len.arr = parse_expr(p);
        advance(p);
        return ast;
    }
    return NULL;
}

static AST *parse_term(Parser *p) {
    AST *left = parse_primary(p);
    while (p->cur.type == TOK_STAR || p->cur.type == TOK_SLASH || p->cur.type == TOK_PERCENT) {
        TokenType op = p->cur.type;
        advance(p);
        AST *ast = new_ast(p, AST_BINOP);
        ast->binop.left = left;
        ast->binop.op = op;
        ast->binop.right = parse_primary(p);
        left = ast;
    }
    return left;
}

static AST *parse_arith(Parser *p) {
    AST *left = parse_term(p);
    /* Range literals: n..m creates array [n, n+1, ..., m] */
    if (left && left->type == AST_INT && p->cur.type == TOK_DOTDOT) {
        advance(p);
        AST *end = parse_expr(p);
        AST *range = new_ast(p, AST_RANGE);
        range->range.start = left;
        range->range.end = end;
        left = range;
    }
    while (p->cur.type == TOK_PLUS || p->cur.type == TOK_MINUS) {
        TokenType op = p->cur.type;
        advance(p);
        AST *ast = new_ast(p, AST_BINOP);
        ast->binop.left = left;
        ast->binop.op = op;
        ast->binop.right = parse_term(p);
        left = ast;
    }
    return left;
}

static AST *parse_expr(Parser *p) {
    AST *left = parse_arith(p);
    /* Chained comparisons: a < b < c becomes a < b && b < c */
    AST *chain_left = left;
    AST *chain_result = NULL;
    while (p->cur.type >= TOK_EQ && p->cur.type <= TOK_GE) {
        TokenType op = p->cur.type;
        advance(p);
        AST *mid = parse_arith(p);
        AST *cmp = new_ast(p, AST_BINOP);
        cmp->binop.left = chain_left;
        cmp->binop.op = op;
        cmp->binop.right = mid;
        if (chain_result) {
            AST *chain = new_ast(p, AST_BINOP);
            chain->binop.left = chain_result;
            chain->binop.op = TOK_AND;
            chain->binop.right = cmp;
            chain_result = chain;
        } else {
            chain_result = cmp;
        }
        chain_left = mid;
    }
    if (chain_result) left = chain_result;
    while (p->cur.type == TOK_AND || p->cur.type == TOK_OR || p->cur.type == TOK_PIPE) {
        TokenType op = p->cur.type;
        advance(p);
        if (op == TOK_PIPE) {
            AST *ast = new_ast(p, AST_PIPE);
            if (p->cur.type == TOK_IDENT) {
                ast->call.name = p->cur.value;
                advance(p);
            } else {
                ast->call.name = "ado_pipe";
            }
            ast->call.args = malloc(sizeof(AST*));
            ast->call.args[0] = left;
            ast->call.argc = 1;
            left = ast;
        } else {
            AST *ast = new_ast(p, AST_BINOP);
            ast->binop.left = left;
            ast->binop.op = op;
            ast->binop.right = parse_expr(p);
            left = ast;
        }
    }
    return left;
}

static AST *parse_block(Parser *p) {
    advance(p);
    AST *ast = new_ast(p, AST_BLOCK);
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
    if (p->cur.type == TOK_AT) {
        advance(p);
        AST *ast = new_ast(p, AST_HINT);
        if (p->cur.type == TOK_IDENT) {
            ast->hint_stmt.name = p->cur.value;
            advance(p);
        }
        return ast;
    }
    if (p->cur.type == TOK_IDENT) {
        char *saved_name = p->cur.value;
        Parser saved_parser = *p;
        advance(p);
        if (p->cur.type == TOK_COLONCOLON || p->cur.type == TOK_COLON) {
            int is_required = (p->cur.type == TOK_COLONCOLON);
            advance(p);
            if (p->cur.type == TOK_IDENT) {
                char *type_name = p->cur.value;
                advance(p);
                AST *ast = new_ast(p, AST_LET);
                ast->let.name = saved_name;
                ast->hint = malloc(sizeof(TypeHint));
                ast->hint->name = type_name;
                ast->hint->is_optional = !is_required;
                if (p->cur.type == TOK_ASSIGN) advance(p);
                ast->let.val = parse_expr(p);
                return ast;
            }
        }
        if (p->cur.type == TOK_ASSIGN) {
            advance(p);
            AST *ast = new_ast(p, AST_ASSIGN);
            ast->assign.target = new_ast(p, AST_VAR);
            ast->assign.target->var_name = saved_name;
            ast->assign.val = parse_expr(p);
            return ast;
        }
        if (p->cur.type == TOK_LBRACKET) {
            advance(p);
            AST *idx = parse_expr(p);
            advance(p);
            if (p->cur.type == TOK_ASSIGN) {
                advance(p);
                AST *ast = new_ast(p, AST_ASSIGN);
                ast->assign.target = new_ast(p, AST_INDEX);
                ast->assign.target->index.arr = new_ast(p, AST_VAR);
                ast->assign.target->index.arr->var_name = saved_name;
                ast->assign.target->index.idx = idx;
                ast->assign.val = parse_expr(p);
                return ast;
            }
            AST *ast = new_ast(p, AST_INDEX);
            ast->index.arr = new_ast(p, AST_VAR);
            ast->index.arr->var_name = saved_name;
            ast->index.idx = idx;
            return ast;
        }
        if (p->cur.type == TOK_LPAREN) {
            advance(p);
            AST *ast = new_ast(p, AST_CALL);
            ast->call.name = saved_name;
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
    }
    if (p->cur.type == TOK_LET) {
        advance(p);
        AST *ast = new_ast(p, AST_LET);
        ast->let.name = p->cur.value;
        advance(p);
        if (p->cur.type == TOK_COLON || p->cur.type == TOK_COLONCOLON) {
            ast->hint = parse_optional_type(p);
        }
        if (p->cur.type == TOK_ASSIGN) advance(p);
        ast->let.val = parse_expr(p);
        return ast;
    }
    if (p->cur.type == TOK_IF) {
        advance(p);
        AST *ast = new_ast(p, AST_IF);
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
        AST *ast = new_ast(p, AST_WHILE);
        ast->while_stmt.cond = parse_expr(p);
        ast->while_stmt.body = parse_block(p);
        return ast;
    }
    if (p->cur.type == TOK_FOR) {
        advance(p);
        AST *ast = new_ast(p, AST_FOR);
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
        AST *ast = new_ast(p, AST_RETURN);
        ast->ret.val = parse_expr(p);
        return ast;
    }
    if (p->cur.type == TOK_PRINT) {
        advance(p);
        advance(p);
        AST *ast = new_ast(p, AST_PRINT);
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
        AST *ast = new_ast(p, AST_LEN);
        ast->len.arr = parse_expr(p);
        advance(p);
        return ast;
    }
    if (p->cur.type == TOK_PUSH) {
        advance(p);
        advance(p);
        AST *ast = new_ast(p, AST_PUSH);
        ast->push.arr = new_ast(p, AST_VAR);
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
    if (p->cur.type == TOK_MATCH) {
        advance(p);
        advance(p);
        AST *ast = new_ast(p, AST_MATCH);
        ast->match_stmt.expr = parse_expr(p);
        advance(p);
        int cap = 4;
        ast->match_stmt.arms = malloc(cap * sizeof(AST*));
        ast->match_stmt.arm_count = 0;
        while (p->cur.type == TOK_IDENT || p->cur.type == TOK_INT || p->cur.type == TOK_TRUE || p->cur.type == TOK_FALSE) {
            if (ast->match_stmt.arm_count >= cap) {
                cap *= 2;
                ast->match_stmt.arms = realloc(ast->match_stmt.arms, cap * sizeof(AST*));
            }
            ast->match_stmt.arms[ast->match_stmt.arm_count++] = parse_stmt(p);
            if (p->cur.type == TOK_COMMA) advance(p);
        }
        advance(p);
        return ast;
    }
    if (p->cur.type == TOK_ENUM) {
        advance(p);
        AST *ast = new_ast(p, AST_ENUM);
        ast->enum_def.enum_name = p->cur.value;
        advance(p);
        int cap = 4;
        ast->enum_def.variants = malloc(cap * sizeof(AST*));
        ast->enum_def.variant_count = 0;
        while (p->cur.type == TOK_IDENT) {
            if (ast->enum_def.variant_count >= cap) {
                cap *= 2;
                ast->enum_def.variants = realloc(ast->enum_def.variants, cap * sizeof(AST*));
            }
            AST *v = new_ast(p, AST_VAR);
            v->var_name = p->cur.value;
            ast->enum_def.variants[ast->enum_def.variant_count++] = v;
            advance(p);
            if (p->cur.type == TOK_COMMA) advance(p);
        }
        advance(p);
        return ast;
    }
    return parse_expr(p);
}

AST *parse_program(Parser *p) {
    AST *prog = new_ast(p, AST_BLOCK);
    int cap = 64;
    prog->block.stmts = malloc(cap * sizeof(AST*));
    prog->block.count = 0;
    
    while (p->cur.type != TOK_EOF) {
        if (p->cur.type == TOK_FN) {
            advance(p);
            AST *fn = new_ast(p, AST_FN);
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


static void ast_free_children(AST *ast);

static void free_ast_binop(AST *ast) {
    ast_free_children(ast->binop.left);
    ast_free_children(ast->binop.right);
}

static void free_ast_unary(AST *ast) {
    ast_free_children(ast->unary.operand);
}

static void free_ast_call(AST *ast) {
    for (int i = 0; i < ast->call.argc; i++) ast_free_children(ast->call.args[i]);
    free(ast->call.args);
}

static void free_ast_let(AST *ast) {
    free(ast->let.name);
    ast_free_children(ast->let.val);
    if (ast->hint) free(ast->hint);
}

static void free_ast_if(AST *ast) {
    ast_free_children(ast->if_stmt.cond);
    ast_free_children(ast->if_stmt.then);
    ast_free_children(ast->if_stmt.els);
}

static void free_ast_while(AST *ast) {
    ast_free_children(ast->while_stmt.cond);
    ast_free_children(ast->while_stmt.body);
}

static void free_ast_for(AST *ast) {
    free(ast->for_stmt.var);
    ast_free_children(ast->for_stmt.start);
    ast_free_children(ast->for_stmt.end);
    ast_free_children(ast->for_stmt.body);
}

static void free_ast_return(AST *ast) {
    ast_free_children(ast->ret.val);
}

static void free_ast_block(AST *ast) {
    for (int i = 0; i < ast->block.count; i++) ast_free_children(ast->block.stmts[i]);
    free(ast->block.stmts);
}

static void free_ast_fn(AST *ast) {
    free(ast->fn.name);
    for (int i = 0; i < ast->fn.paramc; i++) free(ast->fn.params[i]);
    free(ast->fn.params);
    ast_free_children(ast->fn.body);
}

static void free_ast_array(AST *ast) {
    for (int i = 0; i < ast->array.count; i++) ast_free_children(ast->array.elems[i]);
    free(ast->array.elems);
}

static void free_ast_index(AST *ast) {
    ast_free_children(ast->index.arr);
    ast_free_children(ast->index.idx);
}

static void free_ast_slice(AST *ast) {
    ast_free_children(ast->slice.arr);
    ast_free_children(ast->slice.start);
    ast_free_children(ast->slice.end);
}

static void free_ast_assign(AST *ast) {
    ast_free_children(ast->assign.target);
    ast_free_children(ast->assign.val);
}

static void free_ast_print(AST *ast) {
    for (int i = 0; i < ast->print.count; i++) ast_free_children(ast->print.vals[i]);
    free(ast->print.vals);
}

static void free_ast_len(AST *ast) {
    ast_free_children(ast->len.arr);
}

static void free_ast_push(AST *ast) {
    ast_free_children(ast->push.arr);
    ast_free_children(ast->push.val);
}

static void free_ast_hint(AST *ast) {
    free(ast->hint_stmt.name);
    ast_free_children(ast->hint_stmt.args);
}

static void free_ast_var(AST *ast) {
    free(ast->var_name);
}

static void free_ast_str(AST *ast) {
    free(ast->str_val);
}

static void free_ast_match(AST *ast) {
    ast_free_children(ast->match_stmt.expr);
    for (int i = 0; i < ast->match_stmt.arm_count; i++) ast_free_children(ast->match_stmt.arms[i]);
    free(ast->match_stmt.arms);
}

static void free_ast_enum(AST *ast) {
    free(ast->enum_def.enum_name);
    for (int i = 0; i < ast->enum_def.variant_count; i++) free(ast->enum_def.variants[i]);
    free(ast->enum_def.variants);
}

static void free_ast_range(AST *ast) {
    ast_free_children(ast->range.start);
    ast_free_children(ast->range.end);
}

static void ast_free_children(AST *ast) {
    if (!ast) return;
    switch (ast->type) {
        case AST_BINOP: free_ast_binop(ast); break;
        case AST_UNARY: free_ast_unary(ast); break;
        case AST_CALL: free_ast_call(ast); break;
        case AST_LET: free_ast_let(ast); break;
        case AST_IF: free_ast_if(ast); break;
        case AST_WHILE: free_ast_while(ast); break;
        case AST_FOR: free_ast_for(ast); break;
        case AST_RETURN: free_ast_return(ast); break;
        case AST_BLOCK: free_ast_block(ast); break;
        case AST_FN: free_ast_fn(ast); break;
        case AST_ARRAY: free_ast_array(ast); break;
        case AST_INDEX: free_ast_index(ast); break;
        case AST_SLICE: free_ast_slice(ast); break;
        case AST_ASSIGN: free_ast_assign(ast); break;
        case AST_PRINT: free_ast_print(ast); break;
        case AST_LEN: free_ast_len(ast); break;
        case AST_PUSH: free_ast_push(ast); break;
        case AST_HINT: free_ast_hint(ast); break;
        case AST_VAR: free_ast_var(ast); break;
        case AST_STR: free_ast_str(ast); break;
        case AST_MATCH: free_ast_match(ast); break;
        case AST_ENUM: free_ast_enum(ast); break;
        case AST_RANGE: free_ast_range(ast); break;
        default: break;
    }
}
void ast_free(AST *ast) {
    ast_free_children(ast);
    free(ast);
}

void parser_free(Parser *p) {
    if (!p) return;
    if (p->pool_count > 0) {
        ast_free_children(&p->pool[0]);
    }
    free(p->pool);
    free(p->cur.value);
    free(p);
}
