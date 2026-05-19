# Ado Language Changelog

All notable changes to the Ado language will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Added
- Comprehensive Markdown documentation (Tutorial, Reference, Examples, Roadmap, Changelog).
- IDE setup documentation updates in `README.md` and `SETUP.md`.
- Refined Neovim configurations.

### Changed
- Standardized file extensions references from `.pl` to `.do` across the codebase.
- Updated language name references from "PL" to "Ado" in LSP documentation and scripts.

## [Initial Release] - 2023-XX-XX

### Added
- Core compiler implementation (`doc`).
- Basic syntax parsing (Functions, `let`, `if/else`, `while`).
- Primitive types (Integer, Boolean, String for printing).
- Code generation to C.
- Interactive REPL.
- Language Server Protocol (LSP) implementation (`do-lsp.py`).
- Tree-sitter grammar support.
- Neovim configuration and wrapper (`ado-edit`).
- Basic test suite.
