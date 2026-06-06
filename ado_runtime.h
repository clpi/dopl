#ifndef ADO_RUNTIME_H
#define ADO_RUNTIME_H

#include <stdlib.h>
#include <string.h>

typedef struct {
    int *data;
    int len;
    int cap;
} AdoArray;

AdoArray ado_make_array(int *init, int count);
void ado_push(AdoArray *arr, int val);

int ado_abs(int x);
int ado_min(int a, int b);
int ado_max(int a, int b);
int ado_clamp(int x, int lo, int hi);
int ado_pow(int base, int exp);

#endif
