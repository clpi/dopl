# Changelog

All notable changes to the Ado programming language will be documented in this file.

## [Unreleased]

### Added
- Comprehensive Markdown documentation including tutorial, reference, examples, use cases, and roadmap.
- `AGENTS.md` file to help automated agents navigate and develop the project.

## [v0.1.0] - Initial Release

### Added
- Initial language implementation (Lexer, Parser, Code Generator).
- Compilation to C with standard `-O2` optimizations.
- Core syntax features: variables (`let`), functions (`fn`), control flow (`if`, `else`, `while`).
- Arithmetic, logical, and comparison operators.
- Language Server Protocol (LSP) server in Python (`lsp/do-lsp.py`) for IDE support.
- `ado-edit` helper script for launching Neovim with full IDE capabilities.
- Basic interactive REPL.
- Deployment and packaging support via `flake.nix` and `HomebrewFormula/ado.rb`.
- Cross-compiling for ARM64 Linux via GitHub actions.
