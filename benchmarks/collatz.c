#include <stdio.h>

int collatz_steps(int n) {
    int steps = 0;
    while (n != 1) {
        if (n % 2 == 0) {
            n = n / 2;
        } else {
            n = 3 * n + 1;
        }
        steps++;
    }
    return steps;
}

int max_collatz(int limit) {
    int max_steps = 0;
    int max_n = 0;
    for (int i = 1; i <= limit; i++) {
        int steps = collatz_steps(i);
        if (steps > max_steps) {
            max_steps = steps;
            max_n = i;
        }
    }
    return max_n;
}

int main(void) {
    int result = max_collatz(100000);
    printf("max collatz n up to 100000: %d\n", result);
    return result;
}
