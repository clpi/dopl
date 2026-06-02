# Ado Agents Reference

This file provides context and guidelines for automated agents working on the Ado programming language codebase.

## Project Overview

Ado (file extension `.do`) is a minimal, fast programming language that compiles down to highly optimized C code (using `-O2`).

- **Compiler Binary:** Built as `doc` via `make` and installed as `ado` via `make install`.
- **LSP Implementation:** A Python-based Language Server Protocol implementation is available in `lsp/do_lsp.py`. Test it via `pytest lsp/test_lsp.py` or `python3 lsp/test_lsp.py`.
- **Tree-sitter Grammar:** The `tree-sitter-do/` directory contains the Tree-sitter grammar. It can be compiled by running `tree-sitter generate` inside that directory.
- **IDE Support:** Use the `./do-edit` helper script to launch Neovim with full IDE capabilities (LSP, Tree-sitter) for `.do` files.

## Language Specifics

- **Comments:** Single-line comments start with `#`.
- **Types:** The language supports integer types, integer arrays, and booleans (`true`, `false`).
- **Arrays:** Arrays are zero-indexed and accessed via standard bracket notation (e.g. `arr[0]`). Supported array operations include `push(arr, val)` and `len(arr)`.
- **Strings:** Limited string literal support exists, primarily for use as arguments to the built-in `print()` function.
- **Control Flow:** `if` / `else` conditionals, `while` loops, and `for` loops (using range syntax like `for i in start..end { ... }`).

## Build and Testing

- **C Compiler:** The primary CI/CD workflow cross-compiles ARM64 Linux binaries using `gcc-aarch64-linux-gnu`.
- **Testing:** Tests are executed via `make test`, which internally wraps the `./test.sh` script to test example `.do` scripts and run C unit tests.
- **Unit Test Quirk:** C unit tests interacting with files that have a `main` function (like `main.c`) must use a preprocessor macro `#define main ado_main` before `#include`ing the source file to prevent multiple entry point definition errors.

## Packaging and CI/CD

- A Nix flake (`flake.nix`) is provided for Nix ecosystems.
- Additional packages (`.deb`, `.rpm`, `.apk` for Alpine, and `.pkg.tar.zst` for Arch Linux pacman) are built using `fpm`.
- A Homebrew formula is maintained in `HomebrewFormula/ado.rb`.
- Both the Homebrew formula and the flake version are automatically updated via the consolidated GitHub Actions CI/CD workflow in `.github/workflows/ci.yml`.
- The CI/CD workflow also packages the compiled executable (renamed to `ado`) into `.tar.gz` archives for distribution.

## Documentation

Comprehensive markdown documentation for the language (including tutorials, reference, examples, use cases, roadmap, and changelog) is located in the `docs/` directory.

Additionally, the project root contains two very helpful setup and reference documents:
- **`SETUP.md`**: Complete and comprehensive setup guide, detailing the IDE setup and features, running commands, and general configuration.
- **`QUICKREF.md`**: Contains a quick reference for the Ado language syntax, examples, patterns, and editor commands.

---
**Note:** Always verify your work by running the relevant tests (`make test`, `python3 lsp/test_lsp.py`, etc.) and ensure compatibility with the existing CI/CD workflow and documentation structure.
