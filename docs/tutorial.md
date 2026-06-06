# Ado Tutorial

Welcome to the Ado tutorial! Ado is a minimal, performant programming language that compiles to C. This guide will help you write your first Ado program.

## Prerequisites

Before we start, make sure you have the Ado compiler built and installed, or run directly from the repository.

```bash
# Build the compiler
./build.sh
```

## Hello World

Let's start by writing a simple program that prints some values. Ado focuses on simplicity, so built-in functions like `print()` make it easy to get started.

Create a file named `hello.do`:

```ado
fn main() {
  print("Hello, World from Ado!")
  return 0
}
```

Now, compile and run the file:

```bash
./doc hello.do
```

You should see:
```text
Hello, World from Ado!
```

## Comments

Ado supports single-line comments. Any text following a `#` on a line is ignored by the compiler.

```ado
# This is a comment
fn main() {
  let a = 1 # This is an inline comment
  return 0
}
```

## Variables and Types

Currently, Ado primarily supports integer types and arrays. Variables are declared using the `let` keyword.
Ado leverages type inference behind the scenes to give you powerful granular control, which means arrays and complex expressions are as fast as native C implicitly-typed variables!

```ado
fn main() {
  # Define an integer
  let a = 10
  let b = 20
  let sum = a + b
  print("The sum of a and b is:", sum)

  # Define an array (internally points to memory like a C array)
  let arr = [1, 2, 3, 4]

  # Read from an array
  print(arr[2]) # Prints 3

  return 0
}
```

## Functions

Functions in Ado are declared using the `fn` keyword. Functions can take parameters and return values.

```ado
fn square(n) {
  return n * n
}

fn main() {
  let num = 5
  print("Square of 5 is:", square(num))
  return 0
}
```

## Control Flow

Ado supports `if` / `else` conditional statements and `while` loops.

### If / Else

```ado
fn is_even(n) {
  if n % 2 == 0 {
    return true
  } else {
    return false
  }
}
```

### For Loop

The `for` loop in Ado gives you a unique but intuitive syntax to iterate over ranges:

```ado
fn sum_to_ten() {
  let sum = 0
  for i in 0 .. 10 {
      sum = sum + i
  }
  print("Sum is: ", sum)
}
```

### While Loop

```ado
fn count_to_five() {
  let i = 1
  while i <= 5 {
    print("Count:", i)
    i = i + 1
  }
}
```

## Interactive REPL

Ado also provides an interactive REPL (Read-Eval-Print Loop) for quick experiments.

Start the REPL by running `./doc` without arguments:

```bash
./doc
```

Try typing:
```ado
> let x = 42
> print(x)
42
```

Use `quit` to exit the REPL.

## Next Steps

Now that you know the basics of Ado, check out the `docs/examples.md` for more advanced features like recursion, or refer to `docs/reference.md` for the complete language syntax!

## Array Operations

Ado supports dynamic-like operations on arrays using built-in functions such as `len()` and `push()`.

```ado
fn main() {
  let my_array = [10, 20]

  # Push a new element
  push(my_array, 30)

  # Get the length
  let length = len(my_array)
  print("Array length is:", length) # Prints 3
  print("Last element is:", my_array[2]) # Prints 30

  return 0
}
```
