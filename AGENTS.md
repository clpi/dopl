# Ado Agents Reference

This file provides context and guidelines for automated agents working on the Ado programming language codebase.

## Project Overview

Ado (file extension `.do`) is a minimal, fast programming language that compiles down to optimized C code (using `-O1`).

- **Compiler Binary:** Built as `doc` via `make` and installed as `ado` via `make install`.
- **LSP Implementation:** A Python-based Language Server Protocol implementation is available in `lsp/do_lsp.py`. Test it via `pytest lsp/test_lsp.py`, `python3 lsp/test_lsp.py`, or `python3 -m unittest lsp.test_lsp`.
  - The LSP implementation routes incoming JSON-RPC requests via explicit `if/elif` statements in the `run()` method.
  - It supports features including semantic tokens, inlay hints, call hierarchy, document highlight, code actions, completions, diagnostics, goto definition, references, hover, formatting, folding ranges, and rename.
  - The LSP tracks lexical block scope for variables and parameters using `brace_count` during text parsing (utilizing a `_mask_text` helper to blank out string literals and `#` comments) to power accurate goto definition, hover, and diagnostics.
  - **Important:** Avoid committing compiled Python bytecode (e.g., `__pycache__` directories or `.pyc` files) to prevent failing code reviews.
  - **Testing Quirk:** When testing the LSP server, mock `sys.stdout` or the server's `send` method (e.g., `self.server.send = lambda msg: None`) to prevent JSON-RPC output from polluting the test console.
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

## Performance Optimizations

- **Optimization level:** Generated C code is compiled with `-O1` instead of `-O2`. On Apple M4 with clang 21, `-O1` produces faster code than `-O2` for recursive patterns like fibonacci (0.38s vs 0.47s) and compiles at the same speed (~0.017s).
- **Pool allocator:** AST nodes are allocated from a pool (`parser->pool`) instead of per-node `malloc`, reducing allocation overhead.
- **Direct integer parsing:** The lexer parses integer literals directly into `Token.int_val`, avoiding `strndup` + `atoi` + `free`.
- **Keyword lookup from source:** The lexer checks keywords via `kw_lookup(s, len)` on the source buffer directly, avoiding `strndup` + `strcmp` for keywords.
- **`stat()` for file size:** `read_file` uses `stat()` instead of `fseek(SEEK_END)` + `ftell` for faster file size detection.

## Benchmark Results (Apple M4)

```
fib:    0.93x Ado vs C  (Ado is 7% faster than C)
prime:  1.44x
collatz:1.43x
TOTAL:  1.12x  (was 1.28x before optimizations)
```

## Packaging and CI/CD

- A Nix flake (`flake.nix`) is provided for Nix ecosystems.
- Additional packages (`.deb`, `.rpm`, `.apk` for Alpine, and `.pkg.tar.zst` for Arch Linux pacman) are built using `fpm`.
- A Homebrew formula is maintained in `HomebrewFormula/ado.rb`.
- Both the Homebrew formula and the flake version are automatically updated via the consolidated GitHub Actions CI/CD workflow in `.github/workflows/ci.yml`.
- The CI/CD workflow also packages the compiled executable (renamed to `ado`) into `.tar.gz` archives for distribution.
- The CI/CD pipeline includes a strict linting job for GitHub Actions workflows (using `actionlint`) and shell scripts (using `shellcheck`). Scripts must pass shellcheck (e.g., direct exit-code checks instead of `$?` and safe globbing like `./*.sh`).
- The CI/CD workflow intentionally uses the `macos-13` runner for macOS x86_64 (`x86_64-darwin`) targets, as newer GitHub-hosted macOS runners (like `macos-14`) are strictly ARM64. Actionlint is configured via `.github/actionlint.yaml` to allow the `macos-13` label to prevent linting failures.

## Documentation

Comprehensive markdown documentation for the language (including tutorials, reference, examples, use cases, roadmap, and changelog) is located in the `docs/` directory.

---
**Note:** Always verify your work by running the relevant tests (`make test`, `python3 lsp/test_lsp.py`, etc.) and ensure compatibility with the existing CI/CD workflow and documentation structure.
