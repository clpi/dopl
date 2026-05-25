# Ado - Complete Setup Guide

## Overview

Ado is a minimal, performant programming language that compiles to C. It features a complete development environment with IDE support.

## File Extension

All Ado source files use the `.do` extension.

## Quick Start

```bash
# 1. Build the compiler
./build.sh

# 2. Edit with full IDE support
./ado-edit example.do

# 3. Or compile and run
./doc example.do
```

## Development Environment

### Integrated Editor (`./ado-edit`)

Launch Neovim with:
- **LSP Server**: Autocomplete, diagnostics, go-to-definition, find references
- **Tree-sitter**: Advanced syntax highlighting and code understanding
- **Syntax Highlighting**: Keyword and operator coloring
- **Auto-formatting**: Proper indentation

**Keybindings:**
- `gd` - Go to definition
- `gr` - Find references
- `K` - Hover information
- `<leader>rn` - Rename symbol
- `<leader>f` - Format document

### LSP Server (`lsp/pl-lsp.py`)

Comprehensive Language Server Protocol implementation:
- Code completion with snippets
- Real-time diagnostics
- Symbol navigation
- Workspace-wide refactoring
- Multi-file support

Works with any LSP-compatible editor (Neovim, VS Code, Vim, Emacs, etc.)

### Tree-sitter Grammar (`tree-sitter-do/`)

Advanced parser for:
- Semantic highlighting
- Better indentation
- Code folding
- Fast incremental parsing

Build with:
```bash
cd tree-sitter-do
./build.sh
```

## Project Structure

```
ado/
├── doc                    # Compiler executable
├── ado-edit              # Neovim launcher with full IDE support
├── build.sh              # Build compiler
├── example.do            # Main example file
├── examples/             # Example programs
│   ├── math.do
│   ├── collatz.do
│   └── conditionals.do
├── lsp/                  # Language Server
│   ├── pl-lsp.py        # LSP implementation
│   ├── test_lsp.py      # Test suite
│   ├── README.md
│   └── FEATURES.md
├── tree-sitter-do/       # Tree-sitter grammar
│   ├── grammar.js
│   ├── queries/
│   └── build.sh
├── nvim/                 # Neovim configuration
│   ├── init.lua         # Custom config
│   └── README.md
└── vim/                  # Vim syntax files
    ├── syntax/do.vim
    └── ftplugin/do.vim
```

## Language Features

- Functions with parameters
- Variables with `let`
- Arrays with `[]` and `push()`, `len()` functions
- Control flow: `if/else`
- Arithmetic and comparison operators
- Function calls
- Recursion
- Integer arithmetic

## Compiler Features

- Compiles to C with `-O2` optimization
- Clean, readable C output
- Fast compilation
- Interactive REPL mode

## Editor Support

### Neovim (Recommended)
Use `./ado-edit` for full integration

### Vim
```bash
cp vim/syntax/do.vim ~/.vim/syntax/
cp vim/ftplugin/do.vim ~/.vim/ftplugin/
```

Add to `.vimrc`:
```vim
au BufRead,BufNewFile *.do set filetype=do
```

### VS Code
Configure LSP in `settings.json` (see `lsp/README.md`)

### Other Editors
Any LSP-compatible editor can use the Ado LSP server

## Testing

```bash
# Test compiler
./test.sh

# Test LSP
python3 lsp/test_lsp.py

# Test Tree-sitter
cd tree-sitter-do && tree-sitter test
```

## Documentation

- [README.md](README.md) - Main documentation
- [lsp/README.md](lsp/README.md) - LSP setup
- [lsp/FEATURES.md](lsp/FEATURES.md) - LSP feature showcase
- [nvim/README.md](nvim/README.md) - Neovim setup
- [tree-sitter-do/README.md](tree-sitter-do/README.md) - Grammar details
- [vim/README.md](vim/README.md) - Vim setup

## Requirements

### Compiler
- C compiler (gcc/clang)
- Standard C library

### Editor (Optional)
- Neovim 0.8+ (for `./do-edit`)
- Python 3 (for LSP)
- nvim-treesitter plugin (for Tree-sitter)
- tree-sitter CLI (for building grammar)

## Examples

See `examples/` directory for:
- `math.do` - Mathematical functions
- `collatz.do` - Collatz conjecture
- `conditionals.do` - Control flow examples
- `example.do` - Comprehensive demo

## Performance

Ado compiles to optimized C code, providing near-native performance. The generated C code is clean and readable, making it easy to understand the compilation process.
