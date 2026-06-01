# Ado Examples

This document demonstrates common algorithms and design patterns implemented in Ado.

## Collatz Sequence Calculator (`examples/collatz.do`)

The Collatz conjecture is one of the most famous unsolved problems in mathematics. This program calculates the number of steps required to reach `1` for various starting values. It demonstrates recursion, arithmetic, and `if` conditionals.

```ado
# Collatz sequence length calculator
fn collatz(n) {
  if n == 1 {
    return 0
  }
  if n % 2 == 0 {  # Equivalent to checking if n is even
    return 1 + collatz(n / 2)
  }
  return 1 + collatz(3 * n + 1)
}

fn main() {
  print("Collatz sequence lengths:")
  let i = 1
  while i <= 20 {
    print(i, collatz(i))
    i = i + 1
  }
  print("")
  print("Collatz(27) =", collatz(27), "steps")
  return 0
}
```

## Conditional Expressions (`examples/conditionals.do`)

Ado has comprehensive conditional support. These examples show how to build common utility functions like `max`, `min`, `abs`, and `clamp`.

```ado
# Conditional expressions demonstration

fn max(a, b) {
  if a > b {
    return a
  }
  return b
}

fn min(a, b) {
  if a < b {
    return a
  }
  return b
}

fn abs(n) {
  if n < 0 {
    return 0 - n
  }
  return n
}

fn sign(n) {
  if n < 0 {
    return -1
  }
  if n > 0 {
    return 1
  }
  return 0
}

fn clamp(val, lo, hi) {
  return max(lo, min(hi, val))
}

fn main() {
  print("clamp(150, 0, 100) =", clamp(150, 0, 100)) # Output: 100
  return 0
}
```

## Math Functions (`examples/math.do`)

Because Ado compiles directly to C with optimization, it handles heavy mathematical recurrence relations very well.

```ado
# Math functions demonstration

fn power(base, exp) {
  if exp == 0 {
    return 1
  }
  return base * power(base, exp - 1)
}

fn sum(n) {
  if n <= 0 {
    return 0
  }
  return n + sum(n - 1)
}

fn factorial(n) {
  if n <= 1 {
    return 1
  }
  return n * factorial(n - 1)
}

fn main() {
  print("2^10 =", power(2, 10))
  print("Sum 1 to 100 =", sum(100))
  print("Factorial(10) =", factorial(10))
  return 0
}
```

## Arrays (`examples/arrays.do`)

Arrays can be mutated and expanded easily in Ado using `push` and indexed assignments.

```ado
# Array usage demonstration

fn main() {
  let arr = [1, 2]
  print("Initial length:", len(arr))

  push(arr, 3)
  push(arr, 4)

  print("Length after push:", len(arr))

  let i = 0
  while i < len(arr) {
    print("arr[", i, "] =", arr[i])
    i = i + 1
  }

  return 0
}
```
