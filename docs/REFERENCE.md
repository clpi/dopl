# Ado Language Reference

## Lexical Structure

### Comments
Comments in Ado start with `#` and continue to the end of the line.

```ado
# This is a comment
let x = 5 # This is also a comment
```

### Keywords
The following keywords are reserved in Ado:
- `fn`
- `let`
- `if`, `else`
- `while`
- `return`
- `print`
- `and`, `or`, `not`
- `true`, `false`

### Identifiers
Identifiers must start with a letter and can contain letters, numbers, and underscores (`_`).

## Data Types

Ado currently has three primitive data types:

1. **Integer**: 32-bit signed integers (e.g., `42`, `-10`, `0`)
2. **Boolean**: `true` or `false`
3. **String**: Used primarily for the `print` function (e.g., `"Hello World"`)

## Variables

Variables are block-scoped and must be declared using the `let` keyword before use.

```ado
let a = 10
let b = a + 5
```

## Control Flow

### `if` Statement
Executes a block of code if the condition is true. An optional `else` block can follow.

```ado
if condition {
  # executed if condition is true
} else {
  # executed if condition is false
}
```

### `while` Loop
Repeatedly executes a block of code as long as the condition evaluates to true.

```ado
while condition {
  # executed while condition is true
}
```

## Functions

Functions are defined using the `fn` keyword. All programs must have a `main` function to be executable.

```ado
fn function_name(param1, param2) {
  # function body
  return result
}
```

## Operators

### Arithmetic Operators
- `+` Addition
- `-` Subtraction
- `*` Multiplication
- `/` Division
- `%` Modulo

### Relational Operators
- `==` Equal
- `!=` Not Equal
- `<` Less Than
- `>` Greater Than
- `<=` Less Than or Equal
- `>=` Greater Than or Equal

### Logical Operators
- `and` Logical AND
- `or` Logical OR
- `not` Logical NOT

## I/O

The `print` function can output strings, integers, or booleans to standard output. It automatically appends a newline.

```ado
print("Result:")
print(42)
```
