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
int ado_sign(int x);
int ado_is_even(int x);
int ado_is_odd(int x);
int ado_gcd(int a, int b);
int ado_lcm(int a, int b);
int ado_factorial(int n);
int ado_fib(int n);
int ado_sum(AdoArray a);
int ado_avg(AdoArray a);
int ado_contains(AdoArray a, int val);
int ado_count_if(AdoArray a, int val);
int ado_find(AdoArray a, int val);
int ado_all(AdoArray a);
int ado_any(AdoArray a);
int ado_pop(AdoArray *arr);
int ado_reverse(AdoArray *arr);
int ado_remove(AdoArray *arr, int idx);
int ado_insert(AdoArray *arr, int idx, int val);
AdoArray ado_take(AdoArray a, int n);
AdoArray ado_drop(AdoArray a, int n);
AdoArray ado_concat(AdoArray a, AdoArray b);
AdoArray ado_fill(int n, int v);
AdoArray ado_filter(AdoArray a, int v);

#endif
