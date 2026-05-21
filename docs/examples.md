# Ado Examples

This page provides various code examples demonstrating the capabilities and syntax of the Ado programming language. You can find more executable examples in the `examples/` directory of the project repository.

## 1. Fibonacci Sequence

Demonstrates efficient recursion and basic control flow.

```ado
fn fib(n) {
  if n <= 1 {
    return n
  }
  return fib(n - 1) + fib(n - 2)
}

fn main() {
  print("Fibonacci of 10 is:", fib(10))
  return 0
}
```

## 2. Factorial

A standard demonstration of recursion.

```ado
fn factorial(n) {
  if n <= 1 {
    return 1
  }
  return n * factorial(n - 1)
}

fn main() {
  print("Factorial of 7 is:", factorial(7))
  return 0
}
```

## 3. Prime Number Checker

Demonstrates `while` loops, modulo arithmetic, and variable updating.

```ado
fn is_prime(n) {
  if n < 2 {
    return false
  }
  let i = 2
  while i * i <= n {
    if n % i == 0 {
      return false
    }
    i = i + 1
  }
  return true
}

fn main() {
  print("Prime numbers up to 30:")
  let n = 2
  while n <= 30 {
    if is_prime(n) {
      print(n)
    }
    n = n + 1
  }
  return 0
}
```

## 4. Collatz Conjecture

A complex loop demonstrating both `if/else` and `while`. Calculates the number of steps required to reach 1.

```ado
fn collatz_steps(n) {
  let steps = 0
  while n != 1 {
    if n % 2 == 0 {
      n = n / 2
    } else {
      n = 3 * n + 1
    }
    steps = steps + 1
  }
  return steps
}

fn main() {
  print("Collatz steps for 27:", collatz_steps(27))
  return 0
}
```

## 5. Greatest Common Divisor (GCD)

Uses the Euclidean algorithm to find the greatest common divisor.

```ado
fn gcd(a, b) {
  while b != 0 {
    let temp = b
    b = a % b
    a = temp
  }
  return a
}

fn main() {
  print("GCD of 48 and 18 is:", gcd(48, 18))
  return 0
}
```

## 6. Reverse a Number and Palindrome Check

Demonstrates mathematical manipulation of integer digits.

```ado
fn reverse_num(n) {
  let rev = 0
  while n != 0 {
    rev = rev * 10 + n % 10
    n = n / 10
  }
  return rev
}

fn is_palindrome(n) {
  return n == reverse_num(n)
}

fn main() {
  if is_palindrome(12321) {
    print("12321 is a palindrome")
  } else {
    print("12321 is not a palindrome")
  }
  return 0
}
```
