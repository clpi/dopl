#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <unistd.h>
#include <sys/wait.h>
#include "lexer.h"
#include "parser.h"
#include "codegen.h"

char *read_file(char *path) {
    FILE *f = fopen(path, "r");
    if (!f) return NULL;

    if (fseek(f, 0, SEEK_END) != 0) {
        fclose(f);
        return NULL;
    }

    long len = ftell(f);
    if (len < 0) {
        fclose(f);
        return NULL;
    }

    if (fseek(f, 0, SEEK_SET) != 0) {
        fclose(f);
        return NULL;
    }

    char *buf = malloc((size_t)len + 1);
    if (!buf) {
        fclose(f);
        return NULL;
    }

    if (fread(buf, 1, (size_t)len, f) != (size_t)len) {
        free(buf);
        fclose(f);
        return NULL;
    }
    buf[len] = '\0';
    fclose(f);
    return buf;
}


static int wait_for_child(pid_t pid, int *status) {
    while (waitpid(pid, status, 0) == -1) {
        if (errno == EINTR) continue;
        return -1;
    }
    return 0;
}

int compile_and_run(const char *out_bin, const char *out_c, int silent) {
    pid_t pid = fork();
    if (pid == -1) {
        perror("fork");
        return -1;
    } else if (pid == 0) {
        if (silent) {
            if (!freopen("/dev/null", "w", stderr)) {
                /* Ignore failure */
            }
        }
        execlp("cc", "cc", "-O2", "-o", out_bin, out_c, NULL);
        perror("execlp cc");
        _exit(1);
    } else {
        int status = 0;
        if (wait_for_child(pid, &status) == -1) {
            perror("waitpid");
            return -1;
        }

        if (WIFEXITED(status) && WEXITSTATUS(status) == 0) {
            pid_t run_pid = fork();
            if (run_pid == -1) {
                perror("fork");
                return -1;
            } else if (run_pid == 0) {
                size_t dot_slash_len = strlen(out_bin) + 3;
                char dot_slash_bin[dot_slash_len];
                snprintf(dot_slash_bin, dot_slash_len, "./%s", out_bin);
                execlp(dot_slash_bin, out_bin, NULL);
                perror("execlp run");
                _exit(1);
            } else {
                if (wait_for_child(run_pid, &status) == -1) {
                    perror("waitpid");
                    return -1;
                }
                if (WIFEXITED(status)) return WEXITSTATUS(status);
                if (WIFSIGNALED(status)) return 128 + WTERMSIG(status);
                return -1;
            }
        } else {
            if (WIFEXITED(status)) return WEXITSTATUS(status);
            if (WIFSIGNALED(status)) return 128 + WTERMSIG(status);
            return -1;
        }
    }
}

void repl(void) {
    char line[4096];
    char buffer[65536];
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
            
            FILE *out = fopen("out.c", "w");
            codegen(ast, out);
            fclose(out);
            
            int ret = compile_and_run("out", "out.c", 1);
            if (ret != 0) {
                printf("Error compiling or running code\n");
            }
            
            ast_free(ast);
            free(p);
            lexer_free(lex);
            free(src);
            
            unlink("out");
            unlink("out.c");
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
        
        FILE *out = fopen("out.c", "w");
        codegen(ast, out);
        fclose(out);
        
        int ret = compile_and_run("out", "out.c", 0);
        (void)ret;
        
        ast_free(ast);
        free(p);
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
    
    FILE *out = fopen("out.c", "w");
    codegen(ast, out);
    fclose(out);
    
    int ret = compile_and_run("out", "out.c", 0);
    if (ret != 0) {
        // Try with more verbose error output
        ret = compile_and_run("out", "out.c", 0);
    }
    
    ast_free(ast);
    free(p);
    lexer_free(lex);
    free(src);
    
    return ret;
}
