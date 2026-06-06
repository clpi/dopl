#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "codegen.h"

typedef struct {
    FILE *out;
    int label_count;
} WasmGen;

static int wg_label(WasmGen *g) {
    return g->label_count++;
}

static void wg_expr(WasmGen *g, AST *ast);

static void wg_stmt(WasmGen *g, AST *ast) {
    if (!ast) return;
    switch (ast->type) {
        case AST_LET: {
            fprintf(g->out, "  (local $%s i32)\n", ast->let.name);
            fprintf(g->out, "  ");
            wg_expr(g, ast->let.val);
            fprintf(g->out, "\n  local.set $%s\n", ast->let.name);
            break;
        }
        case AST_RETURN: {
            fprintf(g->out, "  return ");
            wg_expr(g, ast->ret.val);
            fprintf(g->out, "\n");
            break;
        }
        case AST_PRINT: {
            for (int i = 0; i < ast->print.count; i++) {
                fprintf(g->out, "  ");
                wg_expr(g, ast->print.vals[i]);
                fprintf(g->out, "\n  call $print_i32\n");
            }
            break;
        }
        case AST_ASSIGN: {
            fprintf(g->out, "  ");
            wg_expr(g, ast->assign.target);
            fprintf(g->out, "\n  local.tee $tmp\n  ");
            wg_expr(g, ast->assign.val);
            fprintf(g->out, "\n  i32.store align=4\n");
            break;
        }
        case AST_IF: {
            int else_lbl = wg_label(g);
            int end_lbl = wg_label(g);
            fprintf(g->out, "  ;; if\n  ");
            wg_expr(g, ast->if_stmt.cond);
            fprintf(g->out, "\n  i32.eqz\n  br_if $else_%d\n", else_lbl);
            wg_stmt(g, ast->if_stmt.then->block.stmts[0]);
            fprintf(g->out, "  br $end_%d\n$else_%d:\n", end_lbl, else_lbl);
            if (ast->if_stmt.els) {
                wg_stmt(g, ast->if_stmt.els->block.stmts[0]);
            }
            fprintf(g->out, "$end_%d:\n", end_lbl);
            break;
        }
        case AST_WHILE: {
            int loop_lbl = wg_label(g);
            int end_lbl = wg_label(g);
            fprintf(g->out, "$loop_%d:\n  ", loop_lbl);
            wg_expr(g, ast->while_stmt.cond);
            fprintf(g->out, "\n  i32.eqz\n  br_if $end_%d\n", end_lbl);
            wg_stmt(g, ast->while_stmt.body->block.stmts[0]);
            fprintf(g->out, "  br $loop_%d\n$end_%d:\n", loop_lbl, end_lbl);
            break;
        }
        case AST_FOR: {
            int loop_lbl = wg_label(g);
            int end_lbl = wg_label(g);
            fprintf(g->out, "  (local $%s i32)\n", ast->for_stmt.var);
            fprintf(g->out, "  ");
            wg_expr(g, ast->for_stmt.start);
            fprintf(g->out, "\n  local.set $%s\n", ast->for_stmt.var);
            fprintf(g->out, "$loop_%d:\n  ", loop_lbl);
            fprintf(g->out, "local.get $%s\n  ", ast->for_stmt.var);
            wg_expr(g, ast->for_stmt.end);
            fprintf(g->out, "\n  i32.ge_s\n  br_if $end_%d\n", end_lbl);
            wg_stmt(g, ast->for_stmt.body->block.stmts[0]);
            fprintf(g->out, "  local.get $%s\n  i32.const 1\n  i32.add\n  local.set $%s\n",
                    ast->for_stmt.var, ast->for_stmt.var);
            fprintf(g->out, "  br $loop_%d\n$end_%d:\n", loop_lbl, end_lbl);
            break;
        }
        case AST_BLOCK: {
            for (int i = 0; i < ast->block.count; i++) {
                wg_stmt(g, ast->block.stmts[i]);
            }
            break;
        }
        case AST_PUSH: {
            fprintf(g->out, ";; push not yet supported in WASM\n  nop\n");
            break;
        }
        default: {
            fprintf(g->out, "  ;; unsupported stmt\n");
            break;
        }
    }
}

static void wg_expr(WasmGen *g, AST *ast) {
    if (!ast) {
        fprintf(g->out, "i32.const 0");
        return;
    }
    switch (ast->type) {
        case AST_INT:
            fprintf(g->out, "i32.const %d", ast->int_val);
            break;
        case AST_BOOL:
            fprintf(g->out, "i32.const %d", ast->bool_val ? 1 : 0);
            break;
        case AST_VAR:
            fprintf(g->out, "local.get $%s", ast->var_name);
            break;
        case AST_BINOP:
            wg_expr(g, ast->binop.left);
            fprintf(g->out, "\n    ");
            wg_expr(g, ast->binop.right);
            fprintf(g->out, "\n    ");
            switch (ast->binop.op) {
                case TOK_PLUS: fprintf(g->out, "i32.add"); break;
                case TOK_MINUS: fprintf(g->out, "i32.sub"); break;
                case TOK_STAR: fprintf(g->out, "i32.mul"); break;
                case TOK_SLASH: fprintf(g->out, "i32.div_s"); break;
                case TOK_PERCENT: fprintf(g->out, "i32.rem_s"); break;
                case TOK_EQ: fprintf(g->out, "i32.eq"); break;
                case TOK_NE: fprintf(g->out, "i32.ne"); break;
                case TOK_LT: fprintf(g->out, "i32.lt_s"); break;
                case TOK_GT: fprintf(g->out, "i32.gt_s"); break;
                case TOK_LE: fprintf(g->out, "i32.le_s"); break;
                case TOK_GE: fprintf(g->out, "i32.ge_s"); break;
                case TOK_AND: fprintf(g->out, "i32.and"); break;
                case TOK_OR: fprintf(g->out, "i32.or"); break;
                default: fprintf(g->out, "i32.const 0"); break;
            }
            break;
        case AST_UNARY:
            wg_expr(g, ast->unary.operand);
            fprintf(g->out, "\n    i32.const 0\n    i32.eq\n    i32.const 1\n    i32.xor ;; not\n");
            break;
        case AST_CALL: {
            const char *name = ast->call.name;
            if (strcmp(name, "abs") == 0) name = "ado_abs";
            else if (strcmp(name, "min") == 0) name = "ado_min";
            else if (strcmp(name, "max") == 0) name = "ado_max";
            else if (strcmp(name, "pow") == 0) name = "ado_pow";
            else if (strcmp(name, "factorial") == 0) name = "ado_factorial";
            else if (strcmp(name, "fib") == 0) name = "ado_fib";
            else if (strcmp(name, "sum") == 0) name = "ado_sum";
            else if (strcmp(name, "count_if") == 0) name = "ado_count_if";
            else if (strcmp(name, "find") == 0) name = "ado_find";
            else if (strcmp(name, "all") == 0) name = "ado_all";
            else if (strcmp(name, "any") == 0) name = "ado_any";
            fprintf(g->out, "call $%s", name);
            for (int i = 0; i < ast->call.argc; i++) {
                fprintf(g->out, "\n    ");
                wg_expr(g, ast->call.args[i]);
            }
            break;
        }
        case AST_INDEX: {
            fprintf(g->out, ";; index not yet supported in WASM");
            break;
        }
        case AST_LEN: {
            fprintf(g->out, "i32.const 0 ;; len not yet supported");
            break;
        }
        case AST_ARRAY: {
            int count = ast->array.count;
            fprintf(g->out, ";; array literal\n    i32.const %d\n    call $malloc\n    local.tee $arr_tmp",
                    (count + 1) * 4);
            for (int i = 0; i < count; i++) {
                fprintf(g->out, "\n    local.get $arr_tmp\n    ");
                wg_expr(g, ast->array.elems[i]);
                fprintf(g->out, "\n    i32.const %d\n    i32.store align=4", (i + 1) * 4);
            }
            fprintf(g->out, "\n    local.get $arr_tmp");
            break;
        }
        default:
            fprintf(g->out, "i32.const 0");
            break;
    }
}

void codegen_wasm(AST *ast, FILE *out) {
    WasmGen g;
    g.out = out;
    g.label_count = 0;

    fprintf(out, "(module\n");
    fprintf(out, "  (import \"env\" \"print_i32\" (func $print_i32 (param i32)))\n");
    fprintf(out, "  (import \"env\" \"memcpy\" (func $memcpy (param i32 i32 i32) (result i32)))\n");
    fprintf(out, "  (import \"env\" \"malloc\" (func $malloc (param i32) (result i32)))\n");
    fprintf(out, "  (memory (export \"memory\") 1 256)\n");

    // Stdlib: abs
    fprintf(out, "  (func $ado_abs (param $x i32) (result i32)\n");
    fprintf(out, "    local.get $x\n");
    fprintf(out, "    i32.const 0\n");
    fprintf(out, "    i32.lt_s\n");
    fprintf(out, "    if (result i32)\n");
    fprintf(out, "      i32.const 0\n");
    fprintf(out, "      local.get $x\n");
    fprintf(out, "      i32.sub\n");
    fprintf(out, "    else\n");
    fprintf(out, "      local.get $x\n");
    fprintf(out, "    end\n");
    fprintf(out, "  )\n");

    // Stdlib: min
    fprintf(out, "  (func $ado_min (param $a i32) (param $b i32) (result i32)\n");
    fprintf(out, "    local.get $a\n");
    fprintf(out, "    local.get $b\n");
    fprintf(out, "    i32.gt_s\n");
    fprintf(out, "    if\n");
    fprintf(out, "      local.get $b\n");
    fprintf(out, "    else\n");
    fprintf(out, "      local.get $a\n");
    fprintf(out, "    end\n");
    fprintf(out, "  )\n");

    // Stdlib: max
    fprintf(out, "  (func $ado_max (param $a i32) (param $b i32) (result i32)\n");
    fprintf(out, "    local.get $a\n");
    fprintf(out, "    local.get $b\n");
    fprintf(out, "    i32.lt_s\n");
    fprintf(out, "    if\n");
    fprintf(out, "      local.get $b\n");
    fprintf(out, "    else\n");
    fprintf(out, "      local.get $a\n");
    fprintf(out, "    end\n");
    fprintf(out, "  )\n");

    // User-defined functions
    for (int i = 0; i < ast->block.count; i++) {
        AST *node = ast->block.stmts[i];
        if (node->type == AST_FN && strcmp(node->fn.name, "main") != 0) {
            fprintf(out, "  (func $%s (param $%s i32)", node->fn.name, node->fn.params[0]);
            for (int j = 1; j < node->fn.paramc; j++) {
                fprintf(out, " (param $%s i32", node->fn.params[j]);
            }
            fprintf(out, ") (result i32)\n");
            wg_stmt(&g, node->fn.body);
            fprintf(out, "    i32.const 0\n    return\n  )\n\n");
        }
    }

    // Main function
    fprintf(out, "  (func $main (export \"_start\") (result i32)\n");
    wg_stmt(&g, ast);
    fprintf(out, "    i32.const 0\n    return\n  )\n");
    fprintf(out, ")\n");
}
