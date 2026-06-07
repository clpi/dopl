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
        case AST_CALL: {
            const char *name = ast->call.name;
            if (strcmp(name, "abs") == 0) name = "ado_abs";
            else if (strcmp(name, "min") == 0) name = "ado_min";
            else if (strcmp(name, "max") == 0) name = "ado_max";
            else if (strcmp(name, "clamp") == 0) name = "ado_clamp";
            else if (strcmp(name, "pow") == 0) name = "ado_pow";
            fprintf(out, "%s(", name);
            for (int i = 0; i < ast->call.argc; i++) {
                gen_expr(ast->call.args[i], out);
                if (i < ast->call.argc - 1) fprintf(out, ",");
            }
            fprintf(out, ")");
            break;
        }
        case AST_ARRAY:
            fprintf(out, "ado_make_array((int[]){");
            for (int i = 0; i < ast->array.count; i++) {
                gen_expr(ast->array.elems[i], out);
                if (i < ast->array.count - 1) fprintf(out, ",");
            }
            fprintf(out, "},%d)", ast->array.count);
            break;
        case AST_INDEX:
            gen_expr(ast->index.arr, out);
            fprintf(out, ".data[");
            gen_expr(ast->index.idx, out);
            fprintf(out, "]");
            break;
        case AST_SLICE:
            // Create a compound literal for the slice array
            // ado_slice creates a new array with elements from arr[start..end] (exclusive)
            fprintf(out, "({ int _s=");
            gen_expr(ast->slice.start, out);
            fprintf(out, ", _e=");
            gen_expr(ast->slice.end, out);
            fprintf(out, ", _len=_e>_s?_e-_s:0, _i; AdoArray _slice=ado_make_array((int[]){},_len); for(_i=0;_i<_len;_i++) _slice.data[_i]=");
            gen_expr(ast->slice.arr, out);
            fprintf(out, ".data[_s+_i]; _slice; })");
            break;
        case AST_RANGE:
            fprintf(out, "({ int _f=");
            gen_expr(ast->range.start, out);
            fprintf(out, ", _t=");
            gen_expr(ast->range.end, out);
            fprintf(out, ", _n, _i; _n=_t>=_f?_t-_f+1:0; AdoArray _r=ado_make_array((int[]){},_n); for(_i=0;_i<_n;_i++)_r.data[_i]=_f+_i; _r;})");
            break;
        case AST_LEN:
            gen_expr(ast->len.arr, out);
            fprintf(out, ".len");
            break;
        case AST_PIPE:
            fprintf(out, "%s(", ast->call.name);
            gen_expr(ast->call.args[0], out);
            fprintf(out, ")");
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
            fprintf(out, "__auto_type %s=", ast->let.name);
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
            fprintf(out, "ado_push(&");
            gen_expr(ast->push.arr, out);
            fprintf(out, ",");
            gen_expr(ast->push.val, out);
            fprintf(out, ");\n");
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
        case AST_MATCH:
            gen_indent(out, indent);
            fprintf(out, "if(0){/*match stub*/}\n");
            break;
        case AST_ENUM:
            gen_indent(out, indent);
            fprintf(out, "/* enum %s: ", ast->enum_def.enum_name);
            for (int i = 0; i < ast->enum_def.variant_count; i++) {
                fprintf(out, "%s", ast->enum_def.variants[i]->var_name);
                if (i < ast->enum_def.variant_count - 1) fprintf(out, ", ");
            }
            fprintf(out, " */\n");
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
    fprintf(out, "#include <string.h>\n");
    // Runtime library (inline)
    fprintf(out, "typedef struct { int *data; int len; int cap; } AdoArray;\n");
    fprintf(out, "static AdoArray ado_make_array(int *init, int c) {\n");
    fprintf(out, "  AdoArray a; a.len=c; a.cap=c>0?c:4; a.data=malloc(a.cap*sizeof(int));\n");
    fprintf(out, "  for(int i=0;i<c;i++) a.data[i]=init[i]; return a;\n");
    fprintf(out, "}\n");
    fprintf(out, "static void ado_push(AdoArray *a, int v) {\n");
    fprintf(out, "  if(a->len>=a->cap){a->cap=a->cap?a->cap*2:4;a->data=realloc(a->data,a->cap*sizeof(int));}\n");
    fprintf(out, "  a->data[a->len++]=v;\n");
    fprintf(out, "}\n");
    fprintf(out, "static int ado_abs(int x) { return x<0?-x:x; }\n");
    fprintf(out, "static int ado_min(int a, int b) { return a<b?a:b; }\n");
    fprintf(out, "static int ado_max(int a, int b) { return a>b?a:b; }\n");
    fprintf(out, "static int ado_clamp(int x, int l, int h) { return x<l?l:(x>h?h:x); }\n");
    fprintf(out, "static int ado_pow(int b, int e) { int r=1; for(int i=0;i<e;i++) r*=b; return r; }\n");
    fprintf(out, "static int ado_sign(int x) { return x>0?1:(x<0?-1:0); }\n");
    fprintf(out, "static int ado_is_even(int x) { return x%%2==0; }\n");
    fprintf(out, "static int ado_is_odd(int x) { return x%%2!=0; }\n");
    fprintf(out, "static int ado_gcd(int a, int b) { while(b){int t=b;b=a%%b;a=t;} return a; }\n");
    fprintf(out, "static int ado_lcm(int a, int b) { return a/ado_gcd(a,b)*b; }\n");
    fprintf(out, "static int ado_contains(AdoArray a, int v) { for(int i=0;i<a.len;i++){if(a.data[i]==v)return 1;} return 0; }\n");
    fprintf(out, "static int ado_pop(AdoArray *a) { return a->data[--a->len]; }\n");
    fprintf(out, "static int ado_reverse(AdoArray *a) { for(int i=0;i<a->len/2;i++){int t=a->data[i];a->data[i]=a->data[a->len-1-i];a->data[a->len-1-i]=t;} return 0; }\n");
    fprintf(out, "static int ado_remove(AdoArray *a, int i) { for(int j=i;j<a->len-1;j++)a->data[j]=a->data[j+1]; a->len--; return 0; }\n");
    fprintf(out, "static int ado_insert(AdoArray *a, int i, int v) { if(a->len>=a->cap){a->cap=a->cap?a->cap*2:4;a->data=realloc(a->data,a->cap*sizeof(int));} for(int j=a->len;j>i;j--)a->data[j]=a->data[j-1]; a->data[i]=v; a->len++; return 0; }\n");
    fprintf(out, "static int ado_factorial(int n) { int r=1; for(int i=2;i<=n;i++) r*=i; return r; }\n");
    fprintf(out, "static int ado_fib(int n) { int a=0,b=1; for(int i=0;i<n;i++){int t=b;b=a+b;a=t;} return a; }\n");
    fprintf(out, "static int ado_sum(AdoArray a) { int s=0; for(int i=0;i<a.len;i++) s+=a.data[i]; return s; }\n");
    fprintf(out, "static int ado_avg(AdoArray a) { return a.len?ado_sum(a)/a.len:0; }\n");
    fprintf(out, "static AdoArray ado_take(AdoArray a, int n) { int c=n<a.len?n:a.len; AdoArray r=ado_make_array((int[]){},c); for(int i=0;i<c;i++) r.data[i]=a.data[i]; return r; }\n");
    fprintf(out, "static AdoArray ado_drop(AdoArray a, int n) { int c=n<a.len?a.len-n:0; AdoArray r=ado_make_array((int[]){},c); for(int i=0;i<c;i++) r.data[i]=a.data[i+n]; return r; }\n");
    fprintf(out, "static AdoArray ado_concat(AdoArray a, AdoArray b) { AdoArray r=ado_make_array((int[]){},a.len+b.len); for(int i=0;i<a.len;i++) r.data[i]=a.data[i]; for(int j=0;j<b.len;j++) r.data[a.len+j]=b.data[j]; return r; }\n");
    fprintf(out, "static AdoArray ado_fill(int n, int v) { AdoArray a; a.len=n; a.cap=n>0?n:4; a.data=malloc(a.cap*sizeof(int)); for(int i=0;i<n;i++) a.data[i]=v; return a; }\n");
    fprintf(out, "static int ado_count_if(AdoArray a, int v) { int c=0; for(int i=0;i<a.len;i++) if(a.data[i]==v) c++; return c; }\n");
    fprintf(out, "static AdoArray ado_filter(AdoArray a, int v) { AdoArray r=ado_make_array((int[]){},0); for(int i=0;i<a.len;i++) if(a.data[i]!=v){ado_push(&r,a.data[i]);} return r; }\n");
    fprintf(out, "static int ado_find(AdoArray a, int v) { for(int i=0;i<a.len;i++) if(a.data[i]==v) return i; return -1; }\n");
    fprintf(out, "static int ado_all(AdoArray a) { for(int i=0;i<a.len;i++) if(!a.data[i]) return 0; return 1; }\n");
    fprintf(out, "static int ado_any(AdoArray a) { for(int i=0;i<a.len;i++) if(a.data[i]) return 1; return 0; }\n");
    fprintf(out, "#include <curl/curl.h>\n");
    fprintf(out, "static size_t ado_http_write(void *contents, size_t size, size_t nmemb, void *userp) { size_t total=size*nmemb; char **buf=(char**)userp; size_t cur=*buf?strlen(*buf):0; size_t new_total=cur+total; if(new_total>=4096) total=4096-cur; if(total>0){*buf=realloc(*buf,new_total+1); memcpy(*buf+cur,contents,total); (*buf)[new_total]=0; } return size*nmemb; }\n");
    fprintf(out, "static long ado_http_perform(const char *url, const char *method, const char *post_data) { CURL *curl=curl_easy_init(); if(!curl) return -1; char *resp=NULL; curl_easy_setopt(curl,CURLOPT_URL,url); curl_easy_setopt(curl,CURLOPT_WRITEFUNCTION,ado_http_write); curl_easy_setopt(curl,CURLOPT_WRITEDATA,&resp); curl_easy_setopt(curl,CURLOPT_FOLLOWLOCATION,1L); curl_easy_setopt(curl,CURLOPT_MAXREDIRS,3L); if(method && strcmp(method,\"POST\")==0){curl_easy_setopt(curl,CURLOPT_POST,1L); if(post_data) curl_easy_setopt(curl,CURLOPT_POSTFIELDS,post_data);} else if(method && strcmp(method,\"PUT\")==0){curl_easy_setopt(curl,CURLOPT_CUSTOMREQUEST,\"PUT\"); if(post_data) curl_easy_setopt(curl,CURLOPT_POSTFIELDS,post_data);} else if(method && strcmp(method,\"DELETE\")==0){curl_easy_setopt(curl,CURLOPT_CUSTOMREQUEST,\"DELETE\");} else {curl_easy_setopt(curl,CURLOPT_HTTPGET,1L);} CURLcode rc=curl_easy_perform(curl); long code=-1; if(rc==CURLE_OK) curl_easy_getinfo(curl,CURLINFO_RESPONSE_CODE,&code); curl_easy_cleanup(curl); if(resp){fprintf(stderr,\"%%s\",resp); free(resp);} if(rc!=CURLE_OK){fprintf(stderr,\"ado_http: %%s: %%s\\n\",url,curl_easy_strerror(rc)); return -1;} return code; }\n");
    fprintf(out, "static int ado_http_get(const char *url) { long code=ado_http_perform(url,\"GET\",NULL); return (int)code; }\n");
    fprintf(out, "static int ado_http_post(const char *url, const char *body) { long code=ado_http_perform(url,\"POST\",body); return (int)code; }\n");
    fprintf(out, "static int ado_http_put(const char *url, const char *body) { long code=ado_http_perform(url,\"PUT\",body); return (int)code; }\n");
    fprintf(out, "static int ado_http_delete(const char *url) { long code=ado_http_perform(url,\"DELETE\",NULL); return (int)code; }\n");
    fprintf(out, "static int ado_http_status(const char *url) { long code=ado_http_perform(url,\"GET\",NULL); return (int)code; }\n");
    fprintf(out, "#include <time.h>\n");
    fprintf(out, "#include <unistd.h>\n");
    fprintf(out, "static int ado_getenv(const char *name) { char *val=getenv(name); if(!val) return 0; printf(\"%%s\",val); return 1; }\n");
    fprintf(out, "static int ado_exit(int code) { exit(code); return 0; }\n");
    fprintf(out, "static int ado_read_file(const char *path) { FILE *f=fopen(path,\"r\"); if(!f) return -1; char buf[4096]; size_t n; while((n=fread(buf,1,sizeof(buf)-1,f))){ buf[n]=0; printf(\"%%s\",buf);} fclose(f); return 0; }\n");
    fprintf(out, "static int ado_write_file(const char *path, int content) { FILE *f=fopen(path,\"w\"); if(!f) return -1; fprintf(f,\"%%d\",content); fclose(f); return 0; }\n");
    fprintf(out, "static int ado_file_exists(const char *path) { FILE *f=fopen(path,\"r\"); if(f){fclose(f);return 1;} return 0; }\n");
    fprintf(out, "static int ado_sleep(int ms) { usleep(ms*1000); return 0; }\n");
    fprintf(out, "static int ado_time(void) { return (int)time(NULL); }\n");
    fprintf(out, "static int ado_random(int max) { return rand()%%max; }\n");
    fprintf(out, "static int ado_capacity(AdoArray a) { return a.cap; }\n");
    fprintf(out, "static int ado_reserve(AdoArray *a, int c) { if(c>a->cap){a->cap=c;a->data=realloc(a->data,c*4);} return 0; }\n");
    fprintf(out, "static int ado_shrink_to_fit(AdoArray *a) { if(a->cap>a->len){a->cap=a->len;a->data=realloc(a->data,a->cap*4);} return 0; }\n");
    fprintf(out, "static int ado_sort(AdoArray a) { for(int i=0;i<a.len-1;i++){for(int j=i+1;j<a.len;j++){if(a.data[i]>a.data[j]){int t=a.data[i];a.data[i]=a.data[j];a.data[j]=t;}}} return 0; }\n");
    fprintf(out, "static AdoArray ado_unique(AdoArray a) { AdoArray r=ado_make_array((int[]){},a.len); for(int i=0;i<a.len;i++){int f=0;for(int j=0;j<r.len;j++){if(r.data[j]==a.data[i]){f=1;break;}} if(!f)r.data[r.len++]=a.data[i];} return r; }\n");
    fprintf(out, "static int ado_reflect(AdoArray a) { printf(\"Array(len=%%d,cap=%%d)\",a.len,a.cap); return 0; }\n");
    
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
