# Ado Language Examples and Use Cases

This document provides several examples to demonstrate the capabilities of the Ado programming language.

## 1. Prime Number Checker

A simple application that checks if numbers are prime.

```ado
fn is_prime(n) {
  if n < 2 {
    return 0
  }
  let i = 2
  while i * i <= n {
    if n % i == 0 {
      return 0
    }
    i = i + 1
  }
  return 1
}

fn main() {
  print("Prime numbers up to 20:")
  let n = 2
  while n <= 20 {
    if is_prime(n) {
      print(n)
    }
    n = n + 1
  }
  return 0
}
```

## 2. Collatz Conjecture Sequence Length

Calculates the number of steps to reach 1 for a given number using the Collatz rules.

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
  print("Collatz steps for 27:")
  print(collatz_steps(27))
  return 0
}
```

## 3. Euclidean Algorithm (Greatest Common Divisor)

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
  print("GCD of 48 and 18 is:")
  print(gcd(48, 18))
  return 0
}
```

## 4. Number Palindrome Checker

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
  let test_num = 12321
  if is_palindrome(test_num) {
    print("It is a palindrome!")
  } else {
    print("Not a palindrome.")
  }
  return 0
}
```
