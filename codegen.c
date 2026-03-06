#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "codegen.h"

static void gen_expr(AST *ast, FILE *out);

static void gen_str_escape(const char *s, FILE *out) {
    while (*s) {
        switch (*s) {
            case '\n': fprintf(out, "\\n"); break;
            case '\t': fprintf(out, "\\t"); break;
            case '"': fprintf(out, "\\\""); break;
            case '\\': fprintf(out, "\\\\"); break;
            case '%': fprintf(out, "%%"); break;
            default: fputc(*s, out);
        }
        s++;
    }
}

static void gen_expr(AST *ast, FILE *out) {
    if (!ast) {
        fprintf(out, "0/*null*/");
        return;
    }
    switch (ast->type) {
        case AST_INT:
            fprintf(out, "%d", ast->int_val);
            break;
        case AST_STR:
            fprintf(out, "\"");
            gen_str_escape(ast->str_val, out);
            fprintf(out, "\"");
            break;
        case AST_BOOL:
            fprintf(out, "%d", ast->bool_val);
            break;
        case AST_VAR:
            fprintf(out, "%s", ast->var_name);
            break;
        case AST_BINOP:
            fprintf(out, "(");
            gen_expr(ast->binop.left, out);
            switch (ast->binop.op) {
                case TOK_PLUS: fprintf(out, "+"); break;
                case TOK_MINUS: fprintf(out, "-"); break;
                case TOK_STAR: fprintf(out, "*"); break;
                case TOK_SLASH: fprintf(out, "/"); break;
                case TOK_PERCENT: fprintf(out, "%%"); break;
                case TOK_EQ: fprintf(out, "=="); break;
                case TOK_NE: fprintf(out, "!="); break;
                case TOK_LT: fprintf(out, "<"); break;
                case TOK_GT: fprintf(out, ">"); break;
                case TOK_LE: fprintf(out, "<="); break;
                case TOK_GE: fprintf(out, ">="); break;
                case TOK_AND: fprintf(out, "&&"); break;
                case TOK_OR: fprintf(out, "||"); break;
                default: break;
            }
            gen_expr(ast->binop.right, out);
            fprintf(out, ")");
            break;
        case AST_UNARY:
            fprintf(out, "(!");
            gen_expr(ast->unary.operand, out);
            fprintf(out, ")");
            break;
        case AST_CALL:
            fprintf(out, "%s(", ast->call.name);
            for (int i = 0; i < ast->call.argc; i++) {
                gen_expr(ast->call.args[i], out);
                if (i < ast->call.argc - 1) fprintf(out, ",");
            }
            fprintf(out, ")");
            break;
        case AST_ARRAY:
            fprintf(out, "(int[]){");
            for (int i = 0; i < ast->array.count; i++) {
                gen_expr(ast->array.elems[i], out);
                if (i < ast->array.count - 1) fprintf(out, ",");
            }
            fprintf(out, "}");
            break;
        case AST_INDEX:
            gen_expr(ast->index.arr, out);
            fprintf(out, "[");
            gen_expr(ast->index.idx, out);
            fprintf(out, "]");
            break;
        case AST_LEN:
            fprintf(out, "sizeof(");
            gen_expr(ast->len.arr, out);
            fprintf(out, ")/sizeof(int)");
            break;
        default:
            break;
    }
}

static void gen_stmt(AST *ast, FILE *out, int indent);

static void gen_block(AST *ast, FILE *out, int indent) {
    for (int i = 0; i < ast->block.count; i++) {
        gen_stmt(ast->block.stmts[i], out, indent);
    }
}

static void gen_indent(FILE *out, int indent) {
    for (int i = 0; i < indent; i++) fprintf(out, "  ");
}

static void gen_stmt(AST *ast, FILE *out, int indent) {
    switch (ast->type) {
        case AST_LET:
            gen_indent(out, indent);
            fprintf(out, "int %s=", ast->let.name);
            gen_expr(ast->let.val, out);
            fprintf(out, ";\n");
            break;
        case AST_IF:
            gen_indent(out, indent);
            fprintf(out, "if(");
            gen_expr(ast->if_stmt.cond, out);
            fprintf(out, "){\n");
            gen_block(ast->if_stmt.then, out, indent + 1);
            gen_indent(out, indent);
            fprintf(out, "}");
            if (ast->if_stmt.els) {
                fprintf(out, "else{\n");
                gen_block(ast->if_stmt.els, out, indent + 1);
                gen_indent(out, indent);
                fprintf(out, "}");
            }
            fprintf(out, "\n");
            break;
        case AST_WHILE:
            gen_indent(out, indent);
            fprintf(out, "while(");
            gen_expr(ast->while_stmt.cond, out);
            fprintf(out, "){\n");
            gen_block(ast->while_stmt.body, out, indent + 1);
            gen_indent(out, indent);
            fprintf(out, "}\n");
            break;
        case AST_FOR:
            gen_indent(out, indent);
            fprintf(out, "for(int %s=", ast->for_stmt.var);
            gen_expr(ast->for_stmt.start, out);
            fprintf(out, ";%s<", ast->for_stmt.var);
            gen_expr(ast->for_stmt.end, out);
            fprintf(out, ";%s++){\n", ast->for_stmt.var);
            gen_block(ast->for_stmt.body, out, indent + 1);
            gen_indent(out, indent);
            fprintf(out, "}\n");
            break;
        case AST_RETURN:
            gen_indent(out, indent);
            fprintf(out, "return ");
            gen_expr(ast->ret.val, out);
            fprintf(out, ";\n");
            break;
        case AST_PRINT:
            gen_indent(out, indent);
            // Build format string first
            fprintf(out, "printf(\"");
            for (int i = 0; i < ast->print.count; i++) {
                if (i > 0) fprintf(out, " ");
                AST *val = ast->print.vals[i];
                if (val->type == AST_STR) {
                    gen_str_escape(val->str_val, out);
                } else if (val->type == AST_BOOL) {
                    fprintf(out, "%%s");
                } else {
                    fprintf(out, "%%d");
                }
            }
            fprintf(out, "\\n\"");
            // Now output arguments
            for (int i = 0; i < ast->print.count; i++) {
                AST *val = ast->print.vals[i];
                if (val->type == AST_STR) {
                    // Strings are in format string, skip
                } else if (val->type == AST_BOOL) {
                    fprintf(out, ",");
                    fprintf(out, "(");
                    gen_expr(val, out);
                    fprintf(out, ")?\"true\":\"false\"");
                } else {
                    fprintf(out, ",");
                    gen_expr(val, out);
                }
            }
            fprintf(out, ");\n");
            break;
        case AST_PUSH: {
            gen_indent(out, indent);
            fprintf(out, "/* push to array */\n");
            break;
        }
        case AST_ASSIGN:
            gen_indent(out, indent);
            gen_expr(ast->assign.target, out);
            fprintf(out, "=");
            gen_expr(ast->assign.val, out);
            fprintf(out, ";\n");
            break;
        case AST_BLOCK:
            gen_block(ast, out, indent);
            break;
        default:
            gen_indent(out, indent);
            gen_expr(ast, out);
            fprintf(out, ";\n");
            break;
    }
}

void codegen(AST *ast, FILE *out) {
    fprintf(out, "#include <stdio.h>\n");
    fprintf(out, "#include <stdlib.h>\n");
    fprintf(out, "#include <string.h>\n\n");
    
    int has_main = 0;
    
    for (int i = 0; i < ast->block.count; i++) {
        AST *node = ast->block.stmts[i];
        if (node->type == AST_FN) {
            if (strcmp(node->fn.name, "main") == 0) has_main = 1;
            fprintf(out, "int %s(", node->fn.name);
            for (int j = 0; j < node->fn.paramc; j++) {
                fprintf(out, "int %s", node->fn.params[j]);
                if (j < node->fn.paramc - 1) fprintf(out, ",");
            }
            fprintf(out, "){\n");
            gen_block(node->fn.body, out, 1);
            if (strcmp(node->fn.name, "main") != 0) {
                fprintf(out, "  return 0;\n");
            }
            fprintf(out, "}\n\n");
        }
    }
    
    // Generate wrapper main if no main function exists
    if (!has_main) {
        fprintf(out, "int main(void) {\n");
        fprintf(out, "  return 0;\n");
        fprintf(out, "}\n");
    }
}
