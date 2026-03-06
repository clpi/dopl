# Ado - A Minimal Programming Language

A lightweight, performant programming language that compiles to C.

**File Extension:** `.do` | **Compiler:** `doc` | **Language Server:** `do-lsp`

## Features

- Simple, intuitive syntax inspired by modern languages
- Compiles to C for maximum performance with -O2 optimization
- Minimal runtime overhead
- Interactive REPL for rapid development
- Full IDE support via LSP and Tree-sitter

### Language Features
- Functions with parameters and recursion
- Variables with `let`
- Control flow: `if/else`, `while` loops
- Rich operators: arithmetic, comparison, logical
- Built-in I/O with `print()`
- Comments with `#`

### IDE Features (via LSP)
- **Completion** - Functions, variables, keywords, snippets
- **Go to Definition** - Jump to symbol definitions
- **Find References** - Find all usages
- **Hover** - Type information and documentation
- **Signature Help** - Function parameter hints
- **Rename** - Symbol renaming across files
- **Diagnostics** - Real-time error detection
- **Code Actions** - Quick fixes and refactorings
- **Code Lenses** - Reference counts
- **Formatting** - Auto-format code

## Quick Start

```bash
# Build compiler
./build.sh

# Set up development environment
./setup-dev.sh

# Launch IDE
./ado-edit example.do

# Or compile and run directly
./doc example.do

# Interactive REPL
./doc
```

## Syntax

```ado
# Comment
fn factorial(n) {
  if n <= 1 {
    return 1
  }
  return n * factorial(n - 1)
}

fn main() {
  print("Factorial of 10:", factorial(10))
  
  let i = 0
  while i < 10 {
    print(i)
    i = i + 1
  }
  
  return 0
}
```

## Build

```bash
./build.sh
```

## Usage

```bash
# Run a file
./doc example.do

# Interactive REPL
./doc

# Run file then enter REPL
./doc -i example.do
```

## REPL Commands

- `quit` - Exit REPL
- `help` - Show available commands
- `clear` - Clear the current buffer

## Development Setup

Run the setup script for a complete IDE experience:

```bash
./setup-dev.sh
./ado-edit example.do
```

This launches Neovim with:
- LSP server (completion, diagnostics, go-to-definition)
- Tree-sitter syntax highlighting (if installed)
- Auto-formatting
- Symbol renaming

### Neovim Key Bindings

| Key | Action |
|-----|--------|
| `gd` | Go to definition |
| `gD` | Go to type definition |
| `gr` | Find references |
| `K` | Show hover info |
| `<leader>rn` | Rename symbol |
| `<leader>f` | Format document |
| `<leader>ca` | Code actions |
| `<C-k>` | Signature help |
| `[d` / `]d` | Navigate diagnostics |

## Language Reference

### Functions
```ado
fn name(params) { body }
```

### Variables
```ado
let name = value
```

### Control Flow
```ado
if condition { } else { }
while condition { }
```

### Return
```ado
return value
```

### I/O
```ado
print(expr1, expr2, ...)  # Print values
```

### Operators
- Arithmetic: `+`, `-`, `*`, `/`, `%`
- Comparison: `==`, `!=`, `<`, `>`, `<=`, `>=`
- Logical: `and`, `or`, `not`

### Literals
- Integers: `42`, `-10`
- Booleans: `true`, `false`
- Strings: `"hello\nworld"`

### Comments
```ado
# Single line comment
```

## Examples

See the `examples/` directory:
- `example.do` - Comprehensive feature demo
- `collatz.do` - Collatz sequence calculator
- `math.do` - Math functions
- `conditionals.do` - Conditional expressions

## Architecture

```
Source (.do) → Lexer → Parser → AST → Codegen → C → Binary
                                        ↓
                                      LSP Server
```

## Directory Structure

```
.
├── doc                 # Compiler binary
├── build.sh            # Build script
├── setup-dev.sh        # IDE setup script
├── ado-edit            # Neovim launcher
├── main.c              # Main entry point
├── lexer.c/h           # Lexer
├── parser.c/h          # Parser
├── codegen.c/h         # Code generator
├── lsp/
│   └── do-lsp.py       # Language server
├── nvim/
│   └── init.lua        # Neovim config
├── tree-sitter-do/     # Tree-sitter grammar
├── vim/                # Vim syntax files
└── examples/           # Example programs
```

## Performance

Ado compiles to optimized C code with `-O2`, running at near-native speed. The generated C code is clean and readable.
