#include "ado_runtime.h"

AdoArray ado_make_array(int *init, int count) {
    AdoArray arr;
    arr.len = count;
    arr.cap = count > 0 ? count : 4;
    arr.data = malloc(arr.cap * sizeof(int));
    for (int i = 0; i < count; i++) {
        arr.data[i] = init[i];
    }
    return arr;
}

void ado_push(AdoArray *arr, int val) {
    if (arr->len >= arr->cap) {
        arr->cap = arr->cap ? arr->cap * 2 : 4;
        arr->data = realloc(arr->data, arr->cap * sizeof(int));
    }
    arr->data[arr->len++] = val;
}

int ado_abs(int x) {
    return x < 0 ? -x : x;
}

int ado_min(int a, int b) {
    return a < b ? a : b;
}

int ado_max(int a, int b) {
    return a > b ? a : b;
}

int ado_clamp(int x, int lo, int hi) {
    if (x < lo) return lo;
    if (x > hi) return hi;
    return x;
}

int ado_pow(int base, int exp) {
    int result = 1;
    for (int i = 0; i < exp; i++) {
        result *= base;
    }
    return result;
}
