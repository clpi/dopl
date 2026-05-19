# Ado Language Tutorial

Welcome to the Ado language tutorial. Ado is a minimal, lightweight programming language designed to be easy to learn while compiling directly to C for optimal performance.

## 1. Getting Started

Before we start coding, let's create our first Ado program.

```ado
# hello.do
fn main() {
  print("Hello, World!")
  return 0
}
```

Save this as `hello.do` and run it:
```bash
./doc hello.do
```

## 2. Variables and Types

Ado supports integers, strings, and booleans. Use the `let` keyword to declare variables:

```ado
fn main() {
  let count = 42
  let message = "Hello"
  let is_ready = true

  print(message)
  print(count)

  return 0
}
```

## 3. Control Flow

### If/Else Statements

```ado
fn check_number(n) {
  if n > 0 {
    print("Positive")
  } else {
    if n < 0 {
      print("Negative")
    } else {
      print("Zero")
    }
  }
  return 0
}
```

### While Loops

```ado
fn countdown(n) {
  let i = n
  while i > 0 {
    print(i)
    i = i - 1
  }
  print("Blastoff!")
  return 0
}
```

## 4. Functions

Functions in Ado are defined using the `fn` keyword.

```ado
# A simple function
fn add(a, b) {
  return a + b
}

# A recursive function
fn fibonacci(n) {
  if n <= 1 {
    return n
  }
  return fibonacci(n - 1) + fibonacci(n - 2)
}

fn main() {
  let sum = add(5, 10)
  print(sum)

  print("Fibonacci of 10:")
  print(fibonacci(10))
  return 0
}
```

## 5. Operators

Ado supports standard arithmetic and logical operators:

- **Arithmetic:** `+`, `-`, `*`, `/`, `%`
- **Comparison:** `==`, `!=`, `<`, `>`, `<=`, `>=`
- **Logical:** `and`, `or`, `not`

```ado
fn logic_demo() {
  let x = 10
  let y = 20

  if x < y and not false {
    print("x is less than y")
  }
  return 0
}
```

## Next Steps
Now that you know the basics, check out the [Reference](REFERENCE.md) for full language details or see [Examples](EXAMPLES.md) for more complex programs.
