# Ado Tutorial

Welcome to the Ado programming language! Ado is a minimal, performant language that compiles to C, enabling high execution speeds while keeping the syntax clean and simple.

This tutorial will guide you through the basics of Ado.

## 1. Getting Started

To compile and run Ado code, you will need the `doc` compiler. Once you've written your script, you can run it:

```bash
./doc my_script.do
```

Alternatively, you can start the interactive REPL:

```bash
./doc
```

## 2. Your First Program

Let's start with a simple entry point. In Ado, execution starts at the `main` function (if provided) or runs from top to bottom.

```ado
fn main() {
  print("Hello, World!")
  return 0
}
```

## 3. Variables and Types

Variables are declared using the `let` keyword. Currently, Ado primarily supports integers and booleans (`true`/`false`).

```ado
let x = 10
let is_active = true
let name = "Ado" # String literals are supported for basic I/O
```

Variables can be re-assigned without `let`:

```ado
let count = 0
count = count + 1
```

## 4. Control Flow

### If/Else

Ado supports standard `if` and `else` branches. Curly braces `{}` are required.

```ado
let age = 18

if age >= 18 {
  print("Adult")
} else {
  print("Minor")
}
```

### While Loops

The `while` loop continues executing as long as the condition is true.

```ado
let i = 0
while i < 5 {
  print(i)
  i = i + 1
}
```

## 5. Functions

Functions are defined using the `fn` keyword.

```ado
fn add(a, b) {
  return a + b
}

fn main() {
  let result = add(5, 7)
  print(result) # Output: 12
  return 0
}
```

Ado supports recursion efficiently:

```ado
fn factorial(n) {
  if n <= 1 {
    return 1
  }
  return n * factorial(n - 1)
}
```

## 6. Operators

Ado provides standard operators:
- Arithmetic: `+`, `-`, `*`, `/`, `%`
- Comparison: `==`, `!=`, `<`, `>`, `<=`, `>=`
- Logical: `and`, `or`, `not`

```ado
if (5 > 3) and not (10 == 20) {
  print("Math works!")
}
```

## 7. Next Steps

Now that you know the basics, check out:
- [Language Reference](reference.md) for full syntax details.
- [Examples](examples.md) for complete working programs.
