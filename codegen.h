#ifndef CODEGEN_H
#define CODEGEN_H

#include "parser.h"
#include <stdio.h>

void codegen(AST *ast, FILE *out);
void codegen_wasm(AST *ast, FILE *out);

#endif
