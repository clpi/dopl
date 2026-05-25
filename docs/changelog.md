# Changelog

All notable changes to the Ado language will be documented in this file.

## [Unreleased]

### Added
- **Arrays**: Integer arrays support (`[]`), with indexing, `push()`, and `len()` functions.
- **Booleans**: Support for `true` and `false` literals in expressions.
- **Strings**: Partial support for string literals inside the `print` function.
- Comprehensive markdown documentation inside the `docs/` folder, including `tutorial.md`, `examples.md`, `reference.md`, `use_cases.md`, and `roadmap.md`.

## [0.1.0] - Initial Release

### Added
- **Compiler**: Basic compiler (`doc`) transpiling `.do` files to C code, and automatically executing via native C compilers with `-O2`.
- **REPL**: Interactive Read-Eval-Print Loop for testing small expressions and statements.
- **LSP Integration**: Python-based Language Server (`do-lsp`) supporting code completion, diagnostics, formatting, and definition jumping.
- **Tree-sitter Grammar**: Custom Tree-sitter grammar definition for syntax highlighting.
- **Neovim setup**: Utility scripts (`setup-dev.sh`, `ado-edit`) for quick NeoVim IDE setup.
- **Core language features**:
  - `fn` for function declaration.
  - `let` for variable binding.
  - Standard arithmetic (`+`, `-`, `*`, `/`, `%`) and comparison (`==`, `<`, `>`, `<=`, `>=`, `!=`) operators.
  - Conditional `if` / `else` blocks, `while` loops, and `for` loops.
  - Internal `print` function for I/O operations.
