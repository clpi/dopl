#include <stdio.h>

int is_prime(int n) {
    if (n < 2) return 0;
    for (int i = 2; i * i <= n; i++) {
        if (n % i == 0) return 0;
    }
    return 1;
}

int count_primes(int limit) {
    int count = 0;
    for (int n = 2; n <= limit; n++) {
        if (is_prime(n)) count++;
    }
    return count;
}

int main(void) {
    int result = count_primes(100000);
    printf("primes up to 100000: %d\n", result);
    return result;
}
