# Ado Language Roadmap

This document outlines the planned features and improvements for the Ado programming language.

## Short-term Goals

### Standard Library
- Develop a comprehensive standard library.
- String manipulation functions.
- Array and List data structures.
- Math library additions (sin, cos, pow, etc.).

### Type System Improvements
- Static typing enhancements.
- Introduction of Floating-point types (e.g., `float`, `double`).
- Structs and user-defined types.

### IDE Integration
- Improve VS Code extension.
- Enhance Language Server (LSP) features:
  - Advanced refactoring tools.
  - Better semantic token highlighting.
  - Real-time linting and style checking.

## Medium-term Goals

### Memory Management
- Implement automatic memory management (Garbage Collection) or manual memory controls (e.g., pointers/references) depending on design goals.

### Module System
- Ability to import/export functions and variables across multiple `.do` files.
- Package manager for dependency management.

### Advanced Language Features
- Closures and anonymous functions.
- Enums and Pattern Matching.
- Error handling (e.g., `try`/`catch` or Result types).

## Long-term Goals

### Compiler Optimizations
- LLVM backend integration for advanced optimizations.
- Cross-compilation support for multiple architectures (ARM, WebAssembly).

### Ecosystem
- Web framework and standard networking libraries.
- Database connectivity.
- Ado package registry.
