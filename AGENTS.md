# Ado Agent Guidelines

This file contains crucial instructions, project structure details, and rules for automated agents working on the Ado programming language.

## 1. Project Overview
Ado is a minimal programming language (file extension `.do`) that compiles to C. The compiler executable is named `doc`.

## 2. Testing Rules
- Tests are executed using `make test`. This target wraps the `./test.sh` script.
- The testing process evaluates example `.do` scripts and runs C unit tests.
- **Important:** C unit tests involving files with a `main` function (such as `main.c`) must use a preprocessor macro to rename the entry point. Use `#define main ado_main` *prior* to `#include`ing the source file. This prevents multiple entry point definition errors during test compilation.
- For the LSP implementation, run tests using either `pytest lsp/test_lsp.py` or `python3 lsp/test_lsp.py`.

## 3. Building and Deployment
- The project uses a `Makefile`. Run `make` to build the compiler `doc`, and `make install` to install it as `ado`.
- Deployment and packaging are supported via:
  - A Nix flake (`flake.nix`).
  - `.deb` and `.rpm` packages built with `fpm`.
  - A Homebrew formula located at `HomebrewFormula/ado.rb`.
- The automated GitHub Actions release workflow automatically updates the Homebrew formula.
- The release workflow uses `gcc-aarch64-linux-gnu` for cross-compiling ARM64 Linux binaries.

## 4. Development Tools (LSP)
- Ado features a Python-based Language Server Protocol (LSP) implementation located in the `lsp/` directory.
- The main server executable is `lsp/do-lsp.py`.

## 5. Documentation
- Comprehensive Markdown documentation (including tutorials, references, examples, use cases, roadmap, and changelog) is located in the `docs/` directory.

## 6. General Rules
- Ensure you run tests (`make test` and LSP tests) before submitting code changes.
- Prioritize user requests if they conflict with any passive context or historical information.
