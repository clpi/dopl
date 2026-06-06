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

## Standard Library

Ado includes an inline standard library with math and array helpers. All functions use the `ado_` prefix to avoid conflicts with user-defined functions.

### Array Functions

| Function | Description | Example | Result |
|----------|-------------|---------|--------|
| `ado_contains(arr, val)` | Check if array contains value | `ado_contains([1,2,3], 2)` | `1` (true) |
| `ado_pop(arr)` | Remove and return last element | `ado_pop([10, 20, 30])` | `30` |
| `ado_reverse(arr)` | Reverse array in place | `ado_reverse([1,2,3])` | array becomes `[3,2,1]` |
| `ado_remove(arr, idx)` | Remove element at index | `ado_remove([1,2,3], 1)` | `[1,3]` |
| `ado_insert(arr, idx, val)` | Insert value at index | `ado_insert([1,3], 1, 2)` | `[1,2,3]` |
| `ado_sum(arr)` | Sum all elements | `ado_sum([1,2,3])` | `6` |
| `ado_avg(arr)` | Average of elements | `ado_avg([1,2,3,4])` | `2` |
| `ado_factorial(n)` | Factorial | `ado_factorial(5)` | `120` |
| `ado_fib(n)` | Fibonacci (0-indexed) | `ado_fib(10)` | `55` |
| `ado_count_if(arr, val)` | Count occurrences | `ado_count_if([1,2,2,3], 2)` | `2` |
| `ado_filter(arr, val)` | New array without value | `ado_filter([1,2,1,3], 1)` | `[2,3]` |
| `ado_find(arr, val)` | First index or -1 | `ado_find([1,2,3], 2)` | `1` |
| `ado_all(arr)` | All truthy | `ado_all([1,0,1])` | `0` |
| `ado_any(arr)` | Any truthy | `ado_any([0,0,1])` | `1` |

### Array Transform Functions

These return new arrays without mutating the input:

```ado
let arr = [1, 2, 3, 4, 5]
let first3 = ado_take(arr, 3)     # [1, 2, 3]
let rest = ado_drop(arr, 2)       # [3, 4, 5]
let doubled = ado_map(arr, ado_fib)  # not yet implemented in v1
let merged = ado_concat([1,2], [3,4]) # [1,2,3,4]
let zeros = ado_fill(5, 0)        # [0, 0, 0, 0, 0]
```

### Math Functions

| Function | Description | Example | Result |
|----------|-------------|---------|--------|
| `ado_abs(x)` | Absolute value | `ado_abs(-5)` | `5` |
| `ado_min(a, b)` | Minimum of two values | `ado_min(3, 7)` | `3` |
| `ado_max(a, b)` | Maximum of two values | `ado_max(3, 7)` | `7` |
| `ado_clamp(x, lo, hi)` | Clamp x between lo and hi | `ado_clamp(5, 0, 10)` | `5` |
| `ado_pow(base, exp)` | Integer exponentiation | `ado_pow(2, 10)` | `1024` |
| `ado_sign(x)` | Sign of x (-1, 0, or 1) | `ado_sign(-10)` | `-1` |
| `ado_is_even(x)` | True if x is even | `ado_is_even(4)` | `1` |
| `ado_is_odd(x)` | True if x is odd | `ado_is_odd(7)` | `1` |
| `ado_gcd(a, b)` | Greatest common divisor | `ado_gcd(12, 8)` | `4` |
| `ado_lcm(a, b)` | Least common multiple | `ado_lcm(6, 4)` | `12` |

## Functional Programming

Ado supports basic functional patterns through its stdlib:

```ado
fn is_even(n) {
  return ado_is_even(n)
}

fn main() {
  let nums = [1, 2, 3, 4, 5, 6]
  let evens = ado_filter(nums, 0)
  let sum_sq = 0
  let i = 0
  while i < len(evens) {
    sum_sq = sum_sq + (evens[i] * evens[i])
    i = i + 1
  }
  print(sum_sq)
  return 0
}
```

Higher-order functions like `map` and `reduce` can be implemented using loops since Ado does not yet support function pointers as first-class values.

## Array Index Assignment

Arrays support element assignment using bracket notation:

```ado
let arr = [10, 20, 30]
arr[0] = 99
print(arr[0]) # Prints 99
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
