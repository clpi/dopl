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

int ado_sign(int x) {
    return x > 0 ? 1 : (x < 0 ? -1 : 0);
}

int ado_is_even(int x) {
    return x % 2 == 0;
}

int ado_is_odd(int x) {
    return x % 2 != 0;
}

int ado_gcd(int a, int b) {
    while (b) {
        int t = b;
        b = a % b;
        a = t;
    }
    return a;
}

int ado_lcm(int a, int b) {
    return a / ado_gcd(a, b) * b;
}

int ado_factorial(int n) {
    int r = 1;
    for (int i = 2; i <= n; i++) r *= i;
    return r;
}

int ado_fib(int n) {
    int a = 0, b = 1;
    for (int i = 0; i < n; i++) {
        int t = b;
        b = a + b;
        a = t;
    }
    return a;
}

int ado_sum(AdoArray a) {
    int s = 0;
    for (int i = 0; i < a.len; i++) s += a.data[i];
    return s;
}

int ado_avg(AdoArray a) {
    return a.len ? ado_sum(a) / a.len : 0;
}

int ado_contains(AdoArray a, int val) {
    for (int i = 0; i < a.len; i++) {
        if (a.data[i] == val) return 1;
    }
    return 0;
}

int ado_count_if(AdoArray a, int val) {
    int c = 0;
    for (int i = 0; i < a.len; i++) {
        if (a.data[i] == val) c++;
    }
    return c;
}

int ado_find(AdoArray a, int val) {
    for (int i = 0; i < a.len; i++) {
        if (a.data[i] == val) return i;
    }
    return -1;
}

int ado_all(AdoArray a) {
    for (int i = 0; i < a.len; i++) {
        if (!a.data[i]) return 0;
    }
    return 1;
}

int ado_any(AdoArray a) {
    for (int i = 0; i < a.len; i++) {
        if (a.data[i]) return 1;
    }
    return 0;
}

int ado_pop(AdoArray *arr) {
    return arr->data[--arr->len];
}

int ado_reverse(AdoArray *arr) {
    for (int i = 0; i < arr->len / 2; i++) {
        int t = arr->data[i];
        arr->data[i] = arr->data[arr->len - 1 - i];
        arr->data[arr->len - 1 - i] = t;
    }
    return 0;
}

int ado_remove(AdoArray *arr, int idx) {
    for (int i = idx; i < arr->len - 1; i++) {
        arr->data[i] = arr->data[i + 1];
    }
    arr->len--;
    return 0;
}

int ado_insert(AdoArray *arr, int idx, int val) {
    if (arr->len >= arr->cap) {
        arr->cap = arr->cap ? arr->cap * 2 : 4;
        arr->data = realloc(arr->data, arr->cap * sizeof(int));
    }
    for (int i = arr->len; i > idx; i--) {
        arr->data[i] = arr->data[i - 1];
    }
    arr->data[idx] = val;
    arr->len++;
    return 0;
}

AdoArray ado_take(AdoArray a, int n) {
    int c = n < a.len ? n : a.len;
    AdoArray r = ado_make_array((int[]){}, c);
    for (int i = 0; i < c; i++) r.data[i] = a.data[i];
    return r;
}

AdoArray ado_drop(AdoArray a, int n) {
    int c = n < a.len ? a.len - n : 0;
    AdoArray r = ado_make_array((int[]){}, c);
    for (int i = 0; i < c; i++) r.data[i] = a.data[i + n];
    return r;
}

AdoArray ado_concat(AdoArray a, AdoArray b) {
    AdoArray r = ado_make_array((int[]){}, a.len + b.len);
    for (int i = 0; i < a.len; i++) r.data[i] = a.data[i];
    for (int j = 0; j < b.len; j++) r.data[a.len + j] = b.data[j];
    return r;
}

AdoArray ado_fill(int n, int v) {
    AdoArray a;
    a.len = n;
    a.cap = n > 0 ? n : 4;
    a.data = malloc(a.cap * sizeof(int));
    for (int i = 0; i < n; i++) a.data[i] = v;
    return a;
}

AdoArray ado_filter(AdoArray a, int v) {
    AdoArray r = ado_make_array((int[]){}, 0);
    for (int i = 0; i < a.len; i++) {
        if (a.data[i] != v) {
            ado_push(&r, a.data[i]);
        }
    }
    return r;
}
