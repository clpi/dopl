# Ado Language Reference

This document serves as the complete reference for the Ado programming language.

## Lexical Structure

- **File Extension**: Ado source files use the `.do` extension.
- **Comments**: Single-line comments start with `#`.
  ```ado
  # This is a comment
  ```

## Data Types

Ado currently supports the following primitive data types:
- **Integers**: Arbitrary whole numbers (e.g., `42`, `-10`).
- **Booleans**: `true` and `false`.
- **Strings**: Text enclosed in double quotes (e.g., `"hello\nworld"`). Primarily used with `print()`.

## Variables

Variables are statically scoped but dynamically typed (in syntax). They are declared using `let`.

```ado
let my_var = 100
my_var = my_var + 50
```

## Functions

Functions are declared using the `fn` keyword followed by an identifier, a comma-separated parameter list, and a block of code.

```ado
fn function_name(param1, param2) {
  # body
  return value
}
```

- Functions can be recursive.
- The `main` function is typically used as the entry point.

## Control Flow

### If / Else

Conditional execution relies on `if` and optionally `else`. The condition expression does not require parentheses, but the body must be enclosed in braces `{}`.

```ado
if condition {
  # execute if condition is true
} else {
  # execute otherwise
}
```

### While Loop

Repeated execution relies on the `while` statement.

```ado
while condition {
  # body
}
```

## Operators

### Arithmetic Operators
| Operator | Description |
|----------|-------------|
| `+` | Addition |
| `-` | Subtraction |
| `*` | Multiplication |
| `/` | Division |
| `%` | Modulo / Remainder |

### Comparison Operators
| Operator | Description |
|----------|-------------|
| `==` | Equal to |
| `!=` | Not equal to |
| `<` | Less than |
| `>` | Greater than |
| `<=` | Less than or equal |
| `>=` | Greater than or equal |

### Logical Operators
| Operator | Description |
|----------|-------------|
| `and` | Logical AND |
| `or` | Logical OR |
| `not` | Logical NOT |

## Built-in Functions

Currently, Ado relies on standard basic I/O:

- `print(expr1, expr2, ...)`: Prints the evaluated expressions to standard output. Multiple arguments are separated by spaces.

## Compilation and Execution

Ado compiles to optimized C code. The compiler (`doc`) handles the conversion and compilation using a C compiler (e.g., `gcc` or `clang`).

- **Compile and Run**: `./doc file.do`
- **REPL**: `./doc`

## IDE Support

Ado has full Language Server Protocol (LSP) support via `do-lsp.py`, providing:
- Go to Definition
- Find References
- Hover Information
- Symbol Renaming
- Document Formatting
- Diagnostics
