#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>
#include "lexer.h"
#include "parser.h"
#include "codegen.h"

#define MAX_PATH_LEN 1024
#define MAX_CMD_LEN 4096
#define MAX_LINE_LEN 4096
#define MAX_BUFFER_LEN 65536

char *read_file(char *path) {
    struct stat st;
    if (stat(path, &st) != 0) return NULL;
    if (st.st_size > 10 * 1024 * 1024) {
        fprintf(stderr, "Error: File too large\n");
        return NULL;
    }
    size_t len = st.st_size;
    FILE *f = fopen(path, "r");
    if (!f) return NULL;
    char *buf = malloc(len + 1);
    size_t read_len = fread(buf, 1, len, f);
    fclose(f);
    if (read_len != len) {
        free(buf);
        fprintf(stderr, "Error: Failed to read file completely\n");
        return NULL;
    }
    buf[len] = '\0';
    return buf;
}

int compile_and_run(AST *ast) {
    char temp_dir[] = "/tmp/ado_XXXXXX";
    if (mkdtemp(temp_dir) == NULL) {
        perror("mkdtemp");
        return -1;
    }

    char src_path[MAX_PATH_LEN];
    char bin_path[MAX_PATH_LEN];
    snprintf(src_path, sizeof(src_path), "%s/out.c", temp_dir);
    snprintf(bin_path, sizeof(bin_path), "%s/out", temp_dir);

    FILE *out = fopen(src_path, "w");
    if (!out) {
        perror("fopen");
        rmdir(temp_dir);
        return -1;
    }
    codegen(ast, out);
    fclose(out);

    char cmd[MAX_CMD_LEN];
    snprintf(cmd, sizeof(cmd), "cc -O1 -o %s %s 2>/dev/null", bin_path, src_path);
    int ret = system(cmd);

    if (ret == 0) {
        snprintf(cmd, sizeof(cmd), "%s", bin_path);
        ret = system(cmd);
    }

    remove(src_path);
    remove(bin_path);
    rmdir(temp_dir);

    return ret;
}

void repl(void) {
    char line[MAX_LINE_LEN];
    char buffer[MAX_BUFFER_LEN];
    size_t buffer_len = 0;
    buffer[0] = '\0';
    int paren_depth = 0;
    int brace_depth = 0;
    
    printf("Ado REPL v1.0\n");
    printf("Type 'quit' to exit, 'help' for commands\n\n");
    
    while (1) {
        printf(paren_depth > 0 || brace_depth > 0 ? "... " : ">>> ");
        if (!fgets(line, sizeof(line), stdin)) break;
        
        if (strncmp(line, "quit", 4) == 0) break;
        if (strncmp(line, "help", 4) == 0) {
            printf("Commands:\n");
            printf("  quit  - Exit REPL\n");
            printf("  clear - Clear buffer\n");
            printf("  run   - Execute current code\n\n");
            printf("Language features:\n");
            printf("  Functions: fn name(params) { body }\n");
            printf("  Variables: let x = value\n");
            printf("  Control: if condition { } else { }, while condition { }, for i in start..end { }\n");
            printf("  I/O: print(expr1, expr2, ...)\n");
            printf("  Operators: + - * / %% == != < > <= >= and or not\n");
            printf("  Arrays: [1, 2, 3], arr[index]\n");
            printf("  Strings: \"hello\\nworld\"\n\n");
            continue;
        }
        if (strncmp(line, "clear", 5) == 0) {
            buffer[0] = '\0';
            buffer_len = 0;
            paren_depth = 0;
            brace_depth = 0;
            continue;
        }
        
        size_t line_len = 0;
        for (int i = 0; line[i]; i++) {
            if (line[i] == '(') paren_depth++;
            if (line[i] == ')') paren_depth--;
            if (line[i] == '{') brace_depth++;
            if (line[i] == '}') brace_depth--;
            line_len++;
        }
        
        if (buffer_len + line_len < sizeof(buffer)) {
            memcpy(buffer + buffer_len, line, line_len + 1);
            buffer_len += line_len;
        } else {
            printf("Error: Input buffer overflow\n");
            buffer[0] = '\0';
            buffer_len = 0;
            paren_depth = 0;
            brace_depth = 0;
            continue;
        }
        
        if (paren_depth <= 0 && brace_depth <= 0) {
            char *src = strdup(buffer);
            
            Lexer *lex = lexer_new(src);
            Parser *p = parser_new(lex);
            AST *ast = parse_program(p);
            
            int ret = compile_and_run(ast);
            if (ret != 0) {
                printf("Error compiling or running code\n");
            }
            
            parser_free(p);
            lexer_free(lex);
            free(src);
            buffer[0] = '\0';
            buffer_len = 0;
        }
    }
}

int main(int argc, char **argv) {
    if (argc < 2) {
        repl();
        return 0;
    }
    
    if (strcmp(argv[1], "-i") == 0 && argc >= 3) {
        // Interactive with file as template
        char *src = read_file(argv[2]);
        if (!src) {
            fprintf(stderr, "Error: Cannot read file %s\n", argv[2]);
            return 1;
        }
        // Execute file then start REPL
        Lexer *lex = lexer_new(src);
        Parser *p = parser_new(lex);
        AST *ast = parse_program(p);
        
        int ret = compile_and_run(ast);
        (void)ret;
        
        parser_free(p);
        lexer_free(lex);
        free(src);
        
        repl();
        return 0;
    }
    
    char *src = read_file(argv[1]);
    if (!src) {
        fprintf(stderr, "Error: Cannot read file %s\n", argv[1]);
        return 1;
    }
    
    Lexer *lex = lexer_new(src);
    Parser *p = parser_new(lex);
    AST *ast = parse_program(p);
    
    int ret = compile_and_run(ast);
    
    parser_free(p);
    lexer_free(lex);
    free(src);
    
    return ret;
}
