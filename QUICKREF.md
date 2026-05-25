# Ado Quick Reference

## File Extension
`.do`

## Basic Syntax

### Functions
```
fn name(param1, param2) {
  return param1 + param2
}
```

### Variables
```
let x = 10
let result = add(5, 3)
```

### Control Flow
```
if x > 0 {
  return x
} else {
  return 0
}
```

### Comments
```
# Single line comment
```

## Operators

### Arithmetic
`+` `-` `*` `/`

### Comparison
`==` `!=` `<` `>` `<=` `>=`

## Types
- Integers: `42`, `-10`
- Arrays: `[1, 2, 3]`
- Booleans: `true`, `false`
- Strings (Limited): `"hello"`

## Built-in Functions
Currently none - all functions are user-defined

## Editor Commands

### Compile and Run
```bash
./doc file.do
```

### Edit with IDE Support
```bash
./ado-edit file.do
```

### REPL
```bash
./doc
```

## LSP Keybindings (in Neovim)

| Key | Action |
|-----|--------|
| `gd` | Go to definition |
| `gr` | Find references |
| `K` | Hover information |
| `<leader>rn` | Rename symbol |
| `<leader>f` | Format document |

## Example Program

```
fn factorial(n) {
  if n <= 1 {
    return 1
  }
  return n * factorial(n - 1)
}

fn main() {
  let result = factorial(5)
  return result
}
```

## Common Patterns

### Recursion
```
fn fib(n) {
  if n <= 1 {
    return n
  }
  return fib(n - 1) + fib(n - 2)
}
```

### Conditional Expression
```
fn max(a, b) {
  if a > b {
    return a
  }
  return b
}
```

### Multiple Parameters
```
fn power(base, exp) {
  if exp == 0 {
    return 1
  }
  return base * power(base, exp - 1)
}
```

## Compilation Process

1. **Lexer** - Tokenizes source code
2. **Parser** - Builds Abstract Syntax Tree (AST)
3. **Code Generator** - Transpiles to C
4. **C Compiler** - Compiles to native binary with `-O2`

## Performance Tips

- Ado compiles to optimized C code
- Recursion is efficient (tail call optimization depends on C compiler)
- Integer arithmetic is fast (native CPU operations)

## Limitations

- No full string support yet
- No structs yet
- No standard library
- No module system

## Getting Help

- See `README.md` for full documentation
- See `SETUP.md` for complete setup guide
- See `lsp/FEATURES.md` for LSP capabilities
- Check `examples/` for code samples
