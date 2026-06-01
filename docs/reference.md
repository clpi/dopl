# Ado Language Reference

This document acts as a complete reference for the Ado programming language.

## Basic Syntax

Ado uses a C-like structure with curly braces `{}` and implicit semicolons. Statements do not require a trailing semicolon.

```ado
# Ado code is clean and minimalistic
let x = 10
print(x)
```

## Comments

Only single-line comments are supported, starting with `#`.

```ado
# This is a comment
let a = 1 # This is an inline comment
```

## Data Types

Currently, Ado focuses exclusively on numeric processing and primarily supports integers.

- **Integers**: Ado supports positive and negative integer literals (e.g., `42`, `-10`).
- **Arrays**: Ado supports integer arrays. They are zero-indexed and act mostly like C arrays under the hood. You can define arrays with `[val1, val2]`.
- **Strings (Limited)**: Strings like `"hello"` can be used as arguments to the `print` function but cannot currently be assigned to variables or manipulated.
- **Booleans**: `true` and `false` literals exist primarily within `if` and `while` expression evaluation context.

## Variables

Variables are statically bound within their block scopes. They are introduced with the `let` keyword.

```ado
let answer = 42
let default_val = 0
```

## Operators

Ado supports a standard array of operators.

### Arithmetic Operators
- `+` : Addition
- `-` : Subtraction
- `*` : Multiplication
- `/` : Division (integer division)
- `%` : Modulo

### Comparison Operators
- `==` : Equal to
- `!=` : Not equal to
- `<` : Less than
- `>` : Greater than
- `<=` : Less than or equal to
- `>=` : Greater than or equal to

### Logical Operators
- `and` : Logical AND
- `or` : Logical OR
- `not` : Logical NOT

## Control Flow

### If / Else
Ado uses `if` and `else` for branching. Conditionals must be followed by block braces.

```ado
if condition {
  # code block
} else {
  # alternate code block
}
```

### While Loop
The `while` loop repeatedly executes a block as long as a condition evaluates to true.

```ado
while condition {
  # loop body
}
```

### For Loop
The `for` loop iterates over a range of integers. Note that the upper bound is exclusive.

```ado
for i in 1..10 {
  # iterates from 1 to 9
  print(i)
}
```

## Functions

Functions are defined with the `fn` keyword. The `main` function is the entry point of any executable Ado program.
Functions can return values using the `return` keyword.

```ado
fn add(a, b) {
  return a + b
}

fn main() {
  print(add(2, 3))
  return 0
}
```

## Built-in Functions

### `print(...)`
The `print` function takes one or more arguments separated by commas and prints them to the console, followed by a newline.

```ado
print("The value is:", 42)
```

### `len(arr)`
The `len` function returns the length of a given array.

```ado
let arr = [1, 2, 3]
print(len(arr)) # Prints 3
```

### `push(arr, val)`
The `push` function pushes a value onto the end of a given array.

```ado
let arr = []
push(arr, 5)
push(arr, 10)
print(arr[1]) # Prints 10
```

## Compilation Process

1. **Lexing**: Source text is broken into tokens.
2. **Parsing**: Tokens are organized into an Abstract Syntax Tree (AST).
3. **Code Generation**: The AST is transpiled directly to C code.
4. **C Compilation**: A standard C compiler compiles the result to a native executable with `-O2` optimization for speed.

### Nested Control Flow
You can nest `if` statements and loops as needed.

```ado
for i in 1..5 {
  if i % 2 == 0 {
    print(i, "is even")
  } else {
    print(i, "is odd")
  }
}
```
